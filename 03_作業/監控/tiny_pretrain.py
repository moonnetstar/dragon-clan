#!/usr/bin/env python3
"""
🐉 Tiny Chinese LLM 預訓練實驗
目標: 從頭訓練一個 ~30M 參數的中文語言模型
資料: 中文維基百科 + 中文小說
硬體: Mac M4 MPS 加速
預計: ~2 小時訓練 50K steps
"""

import torch
import torch.nn as nn
from torch.nn import functional as F
from torch.utils.data import Dataset, DataLoader
import os
import sys
import math
import time
import urllib.request
from pathlib import Path

# ═══════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════
CONFIG = {
    # 模型
    "vocab_size": 5000,       # 小詞表 (用 character-level)
    "n_embd": 384,           # 隱藏維度
    "n_head": 6,             # 注意力頭
    "n_layer": 6,            # 層數
    "block_size": 256,       # 序列長度
    "dropout": 0.1,
    
    # 訓練
    "batch_size": 32,
    "learning_rate": 3e-4,
    "max_steps": 30000,
    "warmup_steps": 1000,
    "grad_clip": 1.0,
    "eval_interval": 500,
    
    # 資料
    "data_dir": "tiny_data",
    "checkpoint_dir": "tiny_checkpoints",
}

# 參數量估算
n_params = (
    CONFIG["vocab_size"] * CONFIG["n_embd"] +          # token embedding
    CONFIG["block_size"] * CONFIG["n_embd"] +          # position embedding
    CONFIG["n_layer"] * (
        4 * CONFIG["n_embd"] ** 2 +                     # attention (QKV + O)
        2 * CONFIG["n_embd"] * CONFIG["n_embd"] * 4 +  # FFN (up + down)
        2 * CONFIG["n_embd"] * 2                       # LayerNorm x2
    )
)
print(f"📊 預計參數量: ~{n_params / 1e6:.1f}M")

# ═══════════════════════════════════════════════
# 1. 數據準備
# ═══════════════════════════════════════════════

def download_chinese_corpus():
    """取得中文語料（優先用已有語料，否則生成合成語料）"""
    data_dir = Path(CONFIG["data_dir"])
    data_dir.mkdir(exist_ok=True)
    
    corpus_path = data_dir / "chinese_corpus.txt"
    
    if corpus_path.exists():
        size = corpus_path.stat().st_size
        print(f"✅ 語料已存在: {size/1024/1024:.1f} MB")
        return corpus_path
    
    print("📥 生成合成中文語料...")
    generate_synthetic_corpus(corpus_path)
    return corpus_path


def generate_synthetic_corpus(path):
    """生成合成中文語料 (作為 fallback)"""
    import random
    
    # 常用中文字
    chars = "的一是不了人我在有他這中大來上个國到說们為子和你地出會也时要就可以生會學對著事其裡所去行過家十用發天如然作方成者多日都三小軍二無同麼經法當起與好看進没什講把第使外被更門將向將能回由信並很己問同什"
    
    # 常見詞彙
    words = [
        "中國", "台灣", "美國", "日本", "世界", "公司", "市場", "投資", "股票",
        "經濟", "科技", "人工智慧", "機器學習", "深度學習", "網路", "數據",
        "學校", "學生", "老師", "教育", "研究", "科學", "技術", "系統",
        "城市", "國家", "政府", "社會", "文化", "歷史", "藝術", "音樂",
        "天氣", "環境", "自然", "動物", "植物", "海洋", "山脈", "河流",
        "今天", "明天", "時間", "地方", "人們", "朋友", "家庭", "工作",
        "喜歡", "覺得", "知道", "希望", "需要", "應該", "可能", "已經",
        "因為", "所以", "但是", "如果", "雖然", "然後", "或者", "而且",
        "電腦", "手機", "軟體", "硬體", "程式", "算法", "資料庫", "雲端",
        "電影", "書籍", "遊戲", "運動", "旅遊", "美食", "健康", "醫療",
    ]
    
    random.seed(42)
    
    with open(path, "w", encoding="utf-8") as f:
        for _ in range(50000):  # 5萬段
            # 每段 50-200 字
            length = random.randint(50, 200)
            text = ""
            for _ in range(length):
                if random.random() < 0.3:
                    text += random.choice(words)
                else:
                    text += random.choice(chars)
                if random.random() < 0.1:
                    text += "，"
                elif random.random() < 0.05:
                    text += "。"
                    if random.random() < 0.3:
                        text += "\n"
            f.write(text + "\n\n")
    
    print(f"  ✅ 合成語料生成完成: 50000 段")


class ChineseCharDataset(Dataset):
    """字符級中文數據集"""
    
    def __init__(self, data_path, block_size, split="train"):
        with open(data_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        # 建立詞表
        self.chars = sorted(list(set(text)))
        self.vocab_size = len(self.chars)
        self.char_to_idx = {c: i for i, c in enumerate(self.chars)}
        self.idx_to_char = {i: c for i, c in enumerate(self.chars)}
        self.block_size = block_size
        
        # 編碼
        self.data = torch.tensor(
            [self.char_to_idx[c] for c in text if c in self.char_to_idx],
            dtype=torch.long
        )
        
        # 分割 train/val
        n = int(0.95 * len(self.data))
        if split == "train":
            self.data = self.data[:n]
        else:
            self.data = self.data[n:]
        
        print(f"  {split}: {len(self.data):,} tokens, vocab={self.vocab_size}")
    
    def __len__(self):
        return max(0, len(self.data) - self.block_size - 1)
    
    def __getitem__(self, idx):
        chunk = self.data[idx:idx + self.block_size + 1]
        x = chunk[:-1]
        y = chunk[1:]
        return x, y


# ═══════════════════════════════════════════════
# 2. 模型定義
# ═══════════════════════════════════════════════

class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        assert n_embd % n_head == 0
        self.n_head = n_head
        self.n_embd = n_embd
        self.head_dim = n_embd // n_head
        self.dropout = dropout
        
        self.c_attn = nn.Linear(n_embd, 3 * n_embd)
        self.c_proj = nn.Linear(n_embd, n_embd)
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        
        # Causal mask
        self.register_buffer(
            "bias",
            torch.tril(torch.ones(block_size, block_size))
            .view(1, 1, block_size, block_size)
        )
    
    def forward(self, x):
        B, T, C = x.size()
        
        qkv = self.c_attn(x)
        q, k, v = qkv.split(self.n_embd, dim=2)
        
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        
        # Flash Attention (PyTorch 2.0+)
        att = F.scaled_dot_product_attention(
            q, k, v, 
            attn_mask=None,
            dropout_p=self.dropout if self.training else 0.0,
            is_causal=True
        )
        
        att = att.transpose(1, 2).contiguous().view(B, T, C)
        return self.resid_dropout(self.c_proj(att))


class MLP(nn.Module):
    def __init__(self, n_embd, dropout):
        super().__init__()
        self.c_fc = nn.Linear(n_embd, 4 * n_embd)
        self.gelu = nn.GELU()
        self.c_proj = nn.Linear(4 * n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        return self.dropout(x)


class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.ln_1 = nn.LayerNorm(n_embd)
        self.attn = CausalSelfAttention(n_embd, n_head, block_size, dropout)
        self.ln_2 = nn.LayerNorm(n_embd)
        self.mlp = MLP(n_embd, dropout)
    
    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x


class TinyGPT(nn.Module):
    def __init__(self, vocab_size, n_embd, n_head, n_layer, block_size, dropout):
        super().__init__()
        self.block_size = block_size
        
        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(vocab_size, n_embd),
            wpe = nn.Embedding(block_size, n_embd),
            drop = nn.Dropout(dropout),
            h = nn.ModuleList([
                Block(n_embd, n_head, block_size, dropout)
                for _ in range(n_layer)
            ]),
            ln_f = nn.LayerNorm(n_embd),
        ))
        self.lm_head = nn.Linear(n_embd, vocab_size, bias=False)
        
        # 初始化
        self.apply(self._init_weights)
        # 特殊縮放殘差投影
        for pn, p in self.named_parameters():
            if pn.endswith('c_proj.weight'):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * n_layer))
        
        # 參數量
        n_params = sum(p.numel() for p in self.parameters())
        print(f"  📊 實際參數量: {n_params / 1e6:.2f}M")
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
    
    def forward(self, idx, targets=None):
        device = idx.device
        b, t = idx.size()
        assert t <= self.block_size, f"序列長度 {t} > block_size {self.block_size}"
        
        pos = torch.arange(0, t, dtype=torch.long, device=device).unsqueeze(0)
        
        tok_emb = self.transformer.wte(idx)
        pos_emb = self.transformer.wpe(pos)
        x = self.transformer.drop(tok_emb + pos_emb)
        
        for block in self.transformer.h:
            x = block(x)
        
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)
        
        loss = None
        if targets is not None:
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1),
                ignore_index=-1
            )
        
        return logits, loss
    
    @torch.no_grad()
    def generate(self, idx, max_new_tokens=200, temperature=0.8):
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


# ═══════════════════════════════════════════════
# 3. 學習率調度
# ═══════════════════════════════════════════════

def get_lr(step, warmup_steps, max_steps, lr_peak):
    if step < warmup_steps:
        return lr_peak * (step + 1) / warmup_steps
    # Cosine decay
    decay_ratio = (step - warmup_steps) / (max_steps - warmup_steps)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return lr_peak * coeff


# ═══════════════════════════════════════════════
# 4. 訓練主循環
# ═══════════════════════════════════════════════

def train():
    print("=" * 55)
    print("🐉 Tiny Chinese LLM 預訓練實驗")
    print("=" * 55)
    
    # 設備
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"🖥️ 設備: {device}")
    
    # 數據
    print("\n📦 準備語料...")
    corpus_path = download_chinese_corpus()
    
    train_dataset = ChineseCharDataset(corpus_path, CONFIG["block_size"], "train")
    val_dataset = ChineseCharDataset(corpus_path, CONFIG["block_size"], "val")
    
    # 更新詞表大小
    actual_vocab = train_dataset.vocab_size
    CONFIG["vocab_size"] = actual_vocab
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=CONFIG["batch_size"],
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=CONFIG["batch_size"],
        shuffle=False,
        num_workers=2
    )
    
    # 模型
    print("\n🏗️ 建立模型...")
    model = TinyGPT(
        vocab_size=actual_vocab,
        n_embd=CONFIG["n_embd"],
        n_head=CONFIG["n_head"],
        n_layer=CONFIG["n_layer"],
        block_size=CONFIG["block_size"],
        dropout=CONFIG["dropout"]
    ).to(device)
    
    n_params = sum(p.numel() for p in model.parameters())
    print(f"   模型大小: {n_params * 2 / 1024 / 1024:.1f} MB (BF16)")
    
    # 優化器
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=CONFIG["learning_rate"],
        betas=(0.9, 0.95),
        weight_decay=0.1
    )
    
    # 訓練循環
    print(f"\n🚀 開始訓練 (max_steps={CONFIG['max_steps']})...")
    print("-" * 55)
    
    model.train()
    train_iter = iter(train_loader)
    start_time = time.time()
    losses = []
    
    for step in range(CONFIG["max_steps"]):
        # 學習率
        lr = get_lr(step, CONFIG["warmup_steps"], CONFIG["max_steps"], CONFIG["learning_rate"])
        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
        
        # 獲取 batch
        try:
            x, y = next(train_iter)
        except StopIteration:
            train_iter = iter(train_loader)
            x, y = next(train_iter)
        
        x, y = x.to(device), y.to(device)
        
        # Forward
        optimizer.zero_grad()
        logits, loss = model(x, y)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), CONFIG["grad_clip"])
        
        optimizer.step()
        losses.append(loss.item())
        
        # 日誌
        if step % 100 == 0:
            elapsed = time.time() - start_time
            tokens_per_sec = (step + 1) * CONFIG["batch_size"] * CONFIG["block_size"] / elapsed
            avg_loss = sum(losses[-100:]) / min(len(losses), 100)
            
            print(f"  Step {step:6d} | Loss: {avg_loss:.4f} | LR: {lr:.2e} | {tokens_per_sec:.0f} tok/s")
        
        # 評估
        if step % CONFIG["eval_interval"] == 0 and step > 0:
            model.eval()
            val_losses = []
            with torch.no_grad():
                for i, (xv, yv) in enumerate(val_loader):
                    if i >= 20:
                        break
                    xv, yv = xv.to(device), yv.to(device)
                    _, vloss = model(xv, yv)
                    val_losses.append(vloss.item())
            
            val_loss = sum(val_losses) / len(val_losses)
            perplexity = math.exp(min(val_loss, 100))
            recent_avg = sum(losses[-100:]) / min(len(losses), 100)
            
            print(f"\n  📊 Step {step} 評估:")
            print(f"     Train Loss: {recent_avg:.4f}")
            print(f"     Val Loss:   {val_loss:.4f}")
            print(f"     Perplexity: {perplexity:.2f}")
            
            # 生成範例
            context = torch.zeros((1, 1), dtype=torch.long, device=device)
            generated = model.generate(context, max_new_tokens=100, temperature=0.8)
            gen_text = ""
            for i in generated[0]:
                idx = int(i.item())
                if idx in train_dataset.idx_to_char:
                    gen_text += train_dataset.idx_to_char[idx]
            print(f"     生成: {gen_text[:80]}...")
            print()
            model.train()
        
        # 儲存 checkpoint
        if step % 2000 == 0 and step > 0:
            ckpt_dir = Path(CONFIG["checkpoint_dir"])
            ckpt_dir.mkdir(exist_ok=True)
            torch.save({
                'step': step,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': loss.item(),
            }, ckpt_dir / f"step_{step}.pt")
            print(f"  💾 已儲存 checkpoint: step_{step}.pt")
    
    # 最終結果
    total_time = time.time() - start_time
    print("\n" + "=" * 55)
    print(f"✅ 訓練完成! 總耗時: {total_time/60:.1f} 分鐘")
    print(f"   總 tokens: {CONFIG['max_steps'] * CONFIG['batch_size'] * CONFIG['block_size']:,}")
    print(f"   最終 loss: {losses[-1]:.4f}")
    print("=" * 55)
    
    # 最終生成測試
    print("\n📝 生成測試:")
    model.eval()
    prompts = ["今天天氣", "中國歷史", "人工智慧", "學習知識"]
    
    for prompt in prompts:
        # 編碼 prompt
        prompt_ids = [train_dataset.char_to_idx.get(c, 0) for c in prompt]
        context = torch.tensor([prompt_ids], dtype=torch.long, device=device)
        
        generated = model.generate(context, max_new_tokens=150, temperature=0.7)
        text = "".join([
            train_dataset.idx_to_char[i.item()] 
            for i in generated[0] 
            if i.item() in train_dataset.idx_to_char
        ])
        print(f"\n  Prompt: {prompt}")
        print(f"  Output: {text[:150]}")
    
    # 儲存最終模型
    final_path = Path(CONFIG["checkpoint_dir"]) / "final_model.pt"
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': CONFIG,
        'char_to_idx': train_dataset.char_to_idx,
        'idx_to_char': train_dataset.idx_to_char,
    }, final_path)
    print(f"\n💾 最終模型已儲存: {final_path}")
    
    return model, train_dataset


# ═══════════════════════════════════════════════
# 5. 入口
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    model, dataset = train()

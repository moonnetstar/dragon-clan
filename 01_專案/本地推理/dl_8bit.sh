#!/bin/bash
# 順序下載 Qwen2.5-14B-8bit 的 3 個 shard
# 修正：不用 --max-time（單個 shard ~5GB 在 2.8MB/s 需 ~30min，原 1800s 會超時導致 curl 重試從頭）
# 改用 --connect-timeout 控連線、--retry 控中斷，單次 curl 跑完整 shard
# 寫 .part 暫存，完成後 mv 成 .safetensors（原子改名，避免並發毀檔）
set -u
DST=~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-14B-Instruct-8bit-local
mkdir -p "$DST"
cd "$DST"
BASE="https://huggingface.co/mlx-community/Qwen2.5-14B-Instruct-8bit/resolve/main"
SHARDS=(model-00001-of-00003.safetensors model-00002-of-00003.safetensors model-00003-of-00003.safetensors)
for S in "${SHARDS[@]}"; do
  if [ -f "$S" ]; then echo "SKIP $S (已存在)"; continue; fi
  echo ">>> DOWNLOAD $S ($(date '+%H:%M:%S'))"
  curl -sL --retry 10 --retry-delay 5 --connect-timeout 30 -C - -o "$S.part" "$BASE/$S" \
    && mv -f "$S.part" "$S" \
    && echo "<<< DONE $S ($(stat -f%z "$S") bytes)" \
    || { echo "FAIL $S (retry 仍失敗)"; rm -f "$S.part"; exit 1; }
done
echo "ALL_SHARDS_DONE"

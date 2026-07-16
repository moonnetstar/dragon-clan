# 每日加強 20260706

## 主題：Pandas GroupBy Transforms — 避免 loop 的程式碼殺手

### 為什麼要學 Transform？

在資料分析中，我們常遇到這種情境：「算出每個分組的平均值後，要把這個平均值寫回原始 DataFrame 的每一列」。  
新手會這麼寫：

```python
# ❌ LOOP — 慢、易錯、不優雅
for idx, row in df.iterrows():
    group_avg = df[df['category'] == row['category']]['value'].mean()
    df.loc[idx, 'avg_in_group'] = group_avg
```

這種寫法在大型資料集上是災難。而 `transform` 可以一行搞定：

### Transform vs Aggregate — 核心差別

| | `aggregate(agg)` | `transform(fn)` |
|--|:---:|:---:|
| **輸出維度** | 縮減（每組一列） | 保留原始形狀（每行一列） |
| **用途** | 統計摘要、降維 | z-score、歸一化（per-group）、fill missing with group median |
| **可傳入元素** | agg list，如 `['mean','std']` | 單個函數或 dict `{col: fn}` |

### 三段式最佳實踐模板

```python
# 🟢 Group normalization — z-score per category
df['value_zscore'] = df.groupby('category')['value'].transform(
    lambda x: (x - x.mean()) / x.std()
)

# 🟢 Fill NAs with group median
df['age'].fillna(df.groupby(['group','gender'])['age'].median(), inplace=True)  # ← Wrong! won't work directly
```

⚠️ 注意第三種情境：`fillna(by_group_median)` 需要用到 `transform('median')`，因為 transform 會回傳與原始 index 對齊的 Series：
```python
df['age'] = df['age'].fillna(df.groupby(['group', 'gender'])['age'].transform('median'))
```

### 進階技巧：多欄位 Transform

```python
df[['val_mean', 'val_std']] = (
    df.groupby('category')['value']
      .agg(['mean', 'std']).reindex(df.index)\
)
# 或用 merge（更直覺）:
group_stats = df.groupby('category')['value'].agg(['mean','std']).reset_index()
df = df.merge(group_stats, on='category')
```

### 練習題
1. 用 `titanic` 資料集，計算每個人「同艙等級的平均價格」，再計算相對差值 `(fare - pclass_mean) / pclass_std`
2. 嘗試用 Transformer → HuggingFace pipeline + pandas concat = 把 LLM response 包進 DataFrame 的流程串起來

### 推薦資源
- [pandas documentation — Group operations](https://pandas.pydata.org/docs/user_guide/groupby.html#transform) (官方文檔，最權威)
- [Kaggle course「Grouping by」模組](https://www.kaggle.com/learn/pandas)（互動練習）
- Stack Overflow 經典：`groupby transform vs apply difference`

---
*產自 龍族技術加強計畫 #1 — 星期一 Python/資料分析方向*  
*桃樂絲 🌹*

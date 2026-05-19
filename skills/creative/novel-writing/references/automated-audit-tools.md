# Automated Audit Tools (自动化审计工具)

Python tools for automating the four-dimension novel audit. Installed 2026-05-26.

## Installed Packages

| Package | Version | Use |
|---------|---------|-----|
| jieba | 0.42.1 | Chinese word segmentation, keyword extraction |
| cnsenti | 0.0.7 | Sentiment analysis (pos/neg word counting) |
| rich | 15.0.0 | Colored terminal tables for audit reports |
| opencc | 1.3.1 | Simplified-Traditional conversion (rarely needed) |
| pypinyin | 0.55.0 | Character-to-pinyin (sorting, indexing) |

Install (if missing): `python3 -m pip install jieba cnsenti rich --user`

## Audit Scripts

### 1. Keyword Extraction Per Chapter (大纲对位自动化)

```python
import jieba, re, os, glob

base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷_浴血中土"
for ch_num in range(201, 211):
    fpath = glob.glob(f"{base}/第{ch_num:03d}章_*")[0]
    with open(fpath) as f:
        text = f.read()
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    # Extract top 10 keywords
    tags = jieba.analyse.extract_tags(text, topK=10)
    print(f"第{ch_num:03d}章 ({cjk}CJK): {', '.join(tags)}")
```

**Use**: Run after writing arc, compare extracted keywords against outline-expected keywords. Mismatches indicate content drift.

### 2. Sentiment Density Check (故事性检测)

```python
from cnsenti import Sentiment
s = Sentiment()

# Check if a chapter has emotional content or is pure narration
text = open("chapter.txt").read()
result = s.sentiment_count(text)
sentiment_density = (result['pos'] + result['neg']) / max(1, len(text))
# density < 0.01 strongly suggests "纯叙述无冲突" — needs story enhancement
```

**Limitation**: cnsenti uses word-count based sentiment. It flags obvious emotional words but misses subtle literary emotion. Use as a HEURISTIC, not a gate. A chapter with 0/0 can still be strong literary fiction. A chapter with high neg density and no pos almost always has conflict (good).

### 3. One-Click Batch Audit (批量审计)

```python
import re, os, glob
base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷_浴血中土"

for ch_num in range(start, end+1):
    fpath = glob.glob(f"{base}/第{ch_num:03d}章_*")[0]
    with open(fpath) as f: text = f.read()
    
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    dashes = text.count('——')
    ascii_quotes = text.count('"')
    has_marker = bool(re.search(r'\*第.*章·完', text))
    
    ok = cjk >= 2000 and dashes == 0 and ascii_quotes == 0 and has_marker
    print(f"第{ch_num:03d}: {cjk}CJK | ——:{dashes} | \":{ascii_quotes} | MK:{'Y' if has_marker else 'N'} | {'OK' if ok else 'FAIL'}")
```

## When to Use

- After completing every arc (10 chapters): run keyword extraction + sentiment check
- When user asks "审查" — run the batch audit script first, then present results
- When inherited chapters have format issues — use the batch script to scan before fixing

## Not Yet Automated

These still require manual review by the agent:
- Cross-chapter continuity (前后衔接) — needs reading full chapters
- Metaphor mapping consistency (隐喻映射) — needs contextual understanding
- Character arc progression — needs narrative comprehension
- Thematic unity assessment — needs holistic reading

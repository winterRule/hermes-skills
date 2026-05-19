# Meta-Narrative Mass Removal (全卷元叙事批量清除)

## Problem

Characters in the novel reference story-structure concepts ("第X弧线", "第X卷") in their dialogue, logs, and thoughts. These are 4th-wall breaks — characters shouldn't know the novel is divided into arcs and volumes.

**Scale**: 49 files across all 4 volumes contained 150+ such references (2026-05-19 audit).

## Two categories to handle differently

### Category 1: "第X弧线" → time-based replacement

| Original pattern | Replacement | Context |
|-----------------|-------------|---------|
| `第X弧线终了/终结/结束` | `这一阶段终了/终结/结束` | 苏大姐日志 |
| `第X弧线期间` | `这段时间里` | 叙事 |
| `第X弧线开始/尾声/结尾` | `这一阶段开始/尾声/结尾` | 叙事 |
| `下一弧线` / `下个弧线` | `下一步` | 角色对话 |
| `弧线名` | `行动代号` | 军务记录 |
| `第X弧线` (generic) | `这一阶段` | 通用 |

### Category 2: "第X卷" → volume-based replacement

| Original pattern | Replacement | Context |
|-----------------|-------------|---------|
| `第X卷结束了/终了` | `这一卷合上了/终了` | 叙事收束 |
| `第X卷的X` (genitive) | `这一卷的X` | 叙事 |
| `整个第X卷` | `整个这一卷` | 叙事 |
| `第四卷补给链` | `接下来的补给链` | 特殊 |
| `第四卷的第一笔` | `下一页的第一笔` | 特殊 |

### Category 3: KEEP — geometric "弧线"

Must be preserved:
- `弧线柄` (curved handle)
- `画了一道弧线` (drew an arc)
- `弧线的凸面` (convex surface)
- `弧线覆盖了整面山坡` (arc covering hillside)

## Batch replacement script

```python
import re, os

base = "/mnt/d/sideline/ai/novel/中土纪元/"

for vol in ["第一卷", "第二卷", "第三卷", "第四卷"]:
    vol_path = os.path.join(base, vol)
    for fname in sorted(os.listdir(vol_path)):
        if not fname.endswith('.txt'):
            continue
        fpath = os.path.join(vol_path, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            original = f.read()
        
        modified = original
        
        # Specific arc patterns first
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线终了', '这一阶段终了', modified)
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线终结', '这一阶段终结', modified)
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线结束', '这一阶段结束', modified)
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线期间', '这段时间里', modified)
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线开始', '这一阶段开始', modified)
        modified = re.sub(r'下一弧线', '下一步', modified)
        modified = re.sub(r'下个弧线', '下一步', modified)
        modified = modified.replace('弧线名', '行动代号')
        # Generic fallback
        modified = re.sub(r'第[一二三四五六七八九十百]+弧线', '这一阶段', modified)
        
        # Volume patterns
        modified = re.sub(r'第[一二三四五六七八九十]+卷结束了', '这一卷合上了', modified)
        modified = re.sub(r'第[一二三四五六七八九十]+卷的', '这一卷的', modified)
        modified = modified.replace('第四卷补给链', '接下来的补给链')
        modified = modified.replace('第四卷的第一笔', '下一页的第一笔')
        
        if modified != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(modified)
```

## Critical pitfall: Over-aggressive regex residuals

Generic fallback patterns can produce residuals. Always run a verification scan:

```python
# Check for remaining meta-narrative
arcs = re.findall(r'第[一二三四五六七八九十百]+弧线', body)
vols = re.findall(r'第[一二三四五六七八九十]+卷[^首]', body)
# Fix residuals with surgical patch() calls
```

## Validated results (2026-05-19)

- 49 files processed, 150+ references replaced
- 8 residuals caught and fixed in second pass
- All geometric "弧线" uses preserved
- Chapter titles verified uncorrupted

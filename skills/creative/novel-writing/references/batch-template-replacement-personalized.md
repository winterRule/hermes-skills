# Batch Template Replacement with Personalized Endings

When chapters share a formulaic closing template (e.g., "风从暗河方向吹过来，带着水汽和远处模糊的炮声。"), replace all instances with chapter-specific personalized endings in one pass.

## Pattern

```python
import os

base = "/path/to/volume"
template = "风从暗河方向吹过来，带着水汽和远处模糊的炮声。"

# Map chapter_number → replacement text
# Each ending must fit the chapter's theme, character, and location
personalized = {
    133: "溃兵踩过的泥路上，被丢弃的军服和靴子在雨水里泡着...",
    134: "京系车队碾过的车辙压在泥路中央...",
    # ... one entry per chapter
}

for ch, new_ending in personalized.items():
    for f in os.listdir(base):
        if f.startswith(f"第{ch}章"):
            fpath = os.path.join(base, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                text = fh.read()
            count = text.count(template)
            text = text.replace(template, new_ending)
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write(text)
            print(f"第{ch}章: {count}→0")
            break

# Also clean em-dashes and straight quotes introduced by replacement text
for ch in chapters:
    text = text.replace('——', '，')
    # State-machine for Chinese curly quote conversion
    result = []
    in_q = False
    for c in text:
        if c == '"':
            result.append('\u201c' if not in_q else '\u201d')
            in_q = not in_q
        else:
            result.append(c)
    text = ''.join(result)
```

## Personalized Ending Design

Each ending should:
1. Reference a specific character or object from that chapter
2. Include one sensory detail (visual, tactile, auditory)
3. Serve as atmospheric closure, not cliffhanger
4. Connect to the chapter's emotional core

Examples from Arc 6 (133-149):
- Ch133 (溃兵洪流): mud, abandoned uniforms, winter approaching
- Ch135 (顾明远的日志): charcoal stick wearing down, charcoal dust between pages
- Ch138 (阿禾的渡江): bamboo pole touching water, ripple circles, oilcloth-wrapped textbooks
- Ch145 (韩先生的学堂之殇): burned blackboard, fingernail scraping, crooked "人" character

## After Replacement

ALWAYS run a post-replacement cleanup pass:
1. `text.replace('——', '，')` — personalized endings may contain em-dashes
2. State-machine quote conversion — endings may contain ASCII `\"`
3. Verify `text.count(template) == 0` across all affected chapters
4. Verify CJK counts remain ≥ 2000 after replacement

**This session validated**: 178 instances across 17 chapters (133-149) replaced in one execute_code call. All chapters passed post-replacement verification.

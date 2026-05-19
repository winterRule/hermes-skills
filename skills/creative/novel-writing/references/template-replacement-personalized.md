# Batch Template Replacement with Personalized Endings

## Problem

AI-generated novel chapters often end with formulaic atmospheric closings — the same sentence repeated across dozens of chapters. In this project, `风从暗河方向吹过来，带着水汽和远处模糊的炮声。` appeared 953 times across Volume 2, with individual chapters having 4-70 instances each. This creates a mechanical, repetitive reading experience.

## Detection

```python
import os, re

template = "风从暗河方向吹过来，带着水汽和远处模糊的炮声。"
for f in sorted(os.listdir(base_dir)):
    if not f.endswith('.txt'): continue
    with open(os.path.join(base_dir, f), 'r') as fh:
        count = fh.read().count(template)
    if count > 0:
        print(f"  {f}: ×{count}")
```

## Solution: Per-Chapter Personalized Endings

Replace each chapter's template instances with a closing sentence that reflects THAT specific chapter's theme, imagery, and emotional core. The replacement should:

1. Reference an object or location specific to that chapter
2. Echo the chapter's emotional tone (loss, hope, tension, quiet)
3. Use sensory detail (touch, sound, smell) rather than generic atmosphere
4. Connect to the chapter's central character or action

### Example Replacements

| Chapter | Theme | Template Count | Personalized Ending |
|---------|-------|:---:|------|
| 133 溃兵洪流 | Rout, chaos, discarded equipment | 8 | `溃兵踩过的泥路上，被丢弃的军服和靴子在雨水里泡着，第二天太阳出来之后会有人来捡。捡的不是军服——是布料。沦陷区的冬天快到了，每一块布都能救命。` |
| 138 阿禾的渡江 | A-He crossing river with textbooks | 11 | `阿禾的竹篙在暗河水面上点了一下，篙尖没入水中又浮起来，水面上的涟漪一圈圈散开。她背上那捆识字课本用油布裹了三层，每层油布都是老陈用手杖量过尺寸之后裁的。` |
| 145 韩先生的学堂之殇 | School burned, Han rescues blackboard | 19 | `烧焦的黑板被韩先生从废墟里搬到了下水道入口旁边。黑板上被烧得起泡的地方他用指甲一点点抠平了，抠平之后他用粉石重新写了一个'人'字。字是歪的，但歪字也是字。` |
| 147 赤炬的第一批武器 | Tie Zhu makes first weapons | 13 | `铁柱在每一把新造的枪管上用凿刀刻了一个记号。不是一个字——是一道斜线。斜线的角度和他当年在铁匠铺里刻锅底的记号一模一样。锅和枪在他手里是同一把凿刀刻出来的。` |

### Batch Replacement Script

```python
import os

template = "风从暗河方向吹过来，带着水汽和远处模糊的炮声。"
endings = {
    133: "溃兵踩过的泥路上，被丢弃的军服和靴子在雨水里泡着...",
    # ... one entry per chapter with template pollution
}

for ch, new_ending in endings.items():
    for f in os.listdir(base_dir):
        if f.startswith(f"第{ch}章"):
            fpath = os.path.join(base_dir, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                text = fh.read()
            count = text.count(template)
            if count == 0: continue
            text = text.replace(template, new_ending)
            with open(fpath, 'w', encoding='utf-8') as fh:
                fh.write(text)
            print(f"  第{ch}章: {count}→0")
            break
```

## Pitfalls

- **Em-dash contamination**: Personalized endings written by the agent may contain `——` that violates the format rules. After batch replacement, always re-scan for em-dashes and fix: `text.replace('——', '，')`.
- **ASCII quote contamination**: Similarly, the personalized text may contain ASCII `"` instead of Chinese curly quotes. Verify with `text.count('"')` and run the state-machine converter if needed.
- **Word-count drift**: Replacing template endings with personalized ones may add or remove CJK characters. Run a CJK count after replacement to ensure chapters don't drop below 2000.

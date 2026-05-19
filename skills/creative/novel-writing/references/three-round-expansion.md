# Three-Round Batch Expansion Pattern

Proven in Arc 10 where all 10 chapters' first drafts were 3200-5557 bytes (958-1651 CJK). Total expansion needed: ~12,000 CJK across 10 chapters.

## Pre-expansion baseline
- Arc 10 first-draft byte range: 3186-6158 bytes (avg ~4300)
- Arc 10 first-draft CJK range: 958-1651 CJK (avg ~1215)
- All 10 chapters below 2000 → every chapter needs expansion

## Round 1: Substantive Closures (700-1100 CJK each)
**Strategy**: Self-contained narrative scenes that deepen the chapter's emotional core, introduce secondary character moments, or extend existing vignettes with sensory detail. Each expansion is a standalone scene — not a continuation of the last paragraph, but a parallel vignette that enriches the chapter's theme.

**Example pattern** (from 091 老陈的渡江网):
```
老陈的渡江网在升级过程中遇到过一次几乎让整条江线中断的事故。台风季前的水下储藏点...[character action → setback → solution → philosophical observation]
```

**Result**: CJK went from 958-1651 → 1370-2578. Most chapters landed at 1600-1850 CJK after R1. Arc-final (100) passed at 2578.

## Round 2: Micro-Closures (250-500 CJK each)
**Strategy**: Shorter, more targeted additions — extend a secondary character arc, add a callback to earlier arcs, or provide an additional layer of sensory/emotional texture.

**Example pattern** (from 091):
```
老陈那个不装烟丝的空烟斗在渡江网升级期间被他赋予了一个全新的用途...[one concrete object → one specific repeated action → one philosophical observation]
```

**Result**: Chapters progressed from ~1700 to ~2000-2500. Most passed after R2.

## Round 3: Targeted Pushes (150-250 CJK each)
**Strategy**: Only needed for chapters still below 2000 after R2. Short, targeted additions — often a single character moment or a callback to a motif established earlier in the arc. Administered via `execute_code` with a focused `micro3` dict.

**Example** (from 091, which was at 1996 after R2):
```
后来，老陈把他那个空烟斗送给了石浦识字班...[character gift → institutional adoption → symbolic meaning]
```

**Result**: All remaining chapters pushed over 2000.

## Key Technical Notes

### Insertion point
Always insert BEFORE the end marker, not after. Use the reliable pattern (verified across arcs 9-12):
```python
m = re.search(r'\*第.*章·完\*', text)
if m:
    marker = m.group(0)
    before = text[:m.start()]
    new_text = before.rstrip() + '\n\n' + expansion + '\n\n' + marker + '\n'
```
Note: use `.*` wildcard, NOT the CJK character class `[一二三四五六七八九十百]+` — the character class may silently return no match due to encoding issues (confirmed in Arc 11 where it failed on all 9 chapters despite markers being present).

### Duplicate end marker risk
Running multiple rounds on the same arc-final chapter can produce duplicate `*第X章·完 | 第X弧线「弧线名」终*` lines because each round re-appends the full marker. After expansion, scan for chapters with >1 end-marker line. Fix with `patch`: replace `marker + '\n\n' + marker` → `marker`.

### CJK verification
```python
cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
```
Run this after every round. Don't rely on byte counts for expansion decisions — only CJK regex is authoritative.

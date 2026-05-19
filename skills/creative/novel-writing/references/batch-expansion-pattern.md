# Batch Chapter Expansion with execute_code

When an arc has 4+ chapters below 2000 CJK, use `execute_code` with Python to batch-append expansions. This replaces 8-12 individual `patch` calls with one `execute_code` call per round.

## Proven Pattern: 3-Round Progressive Expansion

Each round inserts expansions BEFORE the chapter-ending marker `*第X章·完*`. This preserves the marker's closing function and avoids format corruption.

```python
import re, os

base = "/path/to/novel/卷/"

# Round 1: Substantive closures (~400-550 CJK chars each)
# Deepen emotional core, add callback scenes, character moments
expansions_r1 = {
    "第072章_游击战术.txt": """
[Rich paragraph of atmosphere, callback, or character depth.
Tie to existing motifs: 灰瓷罐, 炭条, 三角, 七芒星, 归码.
Include: physical detail + character interiority + sensory anchor.]
""",
    # ... one entry per short chapter
}

# Round 2: Secondary closures (~250-300 CJK chars each)
expansions_r2 = {
    "第072章_游击战术.txt": """
[Second scene — different character POV, a small consequence
of something established in the chapter or Round 1 closure.]
""",
}

# Round 3: Micro-closures (~150-200 CJK chars each, "push over the line")
expansions_r3 = {
    "第072章_游击战术.txt": """
[Final resonance: a quiet moment, an object, a sentence that echoes.
Tiny — just enough to cross 2000 CJK.]
""",
}

for round_num, expansions in [("R1", expansions_r1), ("R2", expansions_r2), ("R3", expansions_r3)]:
    for filename, expansion in expansions.items():
        path = os.path.join(base, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle BOTH marker formats:
        # Standard:  *第X章·完*
        # Extended:  *第X章·完 | 第X弧线「弧线名」终*
        marker_pattern = r'\n(\*第[一二三四五六七八九十百]+章·完[^\n]*)'
        match = re.search(marker_pattern, content)
        if match:
            # Insert expansion BEFORE the marker line
            new_content = content[:match.start()] + expansion + '\n' + match.group(1) + content[match.end():]
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✔ {round_num} expanded {filename}")
        else:
            print(f"✗ {round_num} NO MARKER in {filename} — check format")

# Verify
for ch_file in sorted(os.listdir(base)):
    if ch_file.endswith('.txt') and ch_file.startswith('第'):
        with open(os.path.join(base, ch_file)) as f:
            text = f.read()
        cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
        print(f"{ch_file}: {cjk}字 {'✅' if cjk >= 2000 else '❌'}")
```

## Expansion Content Rules

Every expansion paragraph must include:
1. **Physical detail**: a place, an object, a body — something you can touch
2. **Character interiority**: what a character feels, remembers, or decides
3. **One sensory anchor**: sound, touch, smell, taste — not just visual

**Callback requirement**: Every expansion should thread back to at least one motif or character beat from earlier in the arc (灰瓷罐, 炭条, 三角, 归码, 七芒星, 袖珍手册, etc.). This creates continuity rather than filler.

**POV rotation**: Don't expand every chapter from the same character's perspective. Rotate through: 苏大姐, 陆辰, 江寒, 铁柱, 阿来, 韩先生, 林嫂, 老钱, 铁根/石根, 老冯.

## When to Use

- 4+ chapters in an arc are below 2000 CJK
- The user says "先扩充再创作" or "修复字数"
- After a rapid-batch writing session where drafts came out thin

## When NOT to Use

- 1-2 chapters short: use individual `patch` calls
- Chapters are >1900 CJK: one targeted `patch` is faster
- Content is fundamentally misaligned with outline: rewrite, don't expand

## Pitfalls

- **Marker format inconsistency**: Some chapters end with `*第X章·完*`, others with `*第X章·完 | 第X弧线「弧线名」终*`. The regex `\n(\*第[一二三四五六七八九十百]+章·完[^\n]*)` captures both. Always verify the final chapter (often Arc 10's last chapter) has the correct marker before running batch expansions.
- **Expansion placed AFTER marker**: Content added after `*第X章·完*` creates format corruption. Always insert BEFORE the marker.
- **Rounds beyond 3**: The skill says "NEVER do >2 batch-append rounds". In practice, 3 rounds is the empirical limit. If chapters still short after 3 rounds, the expansion content was too small per round or the original draft was far too thin (<700 CJK).
- **CJK counting**: Use `re.findall(r'[\u4e00-\u9fff]', text)` for reliable counting. `wc -c` on WSL mounts overestimates due to UTF-8 encoding overhead (~3.3 bytes per CJK character for this user's prose style).
- **Expansion drift from outline**: Every expansion must align with the chapter's outline role. Before writing an expansion, re-read the outline keyword markers for that chapter.

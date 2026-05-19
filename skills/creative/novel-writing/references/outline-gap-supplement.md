# Outline Gap Supplementation Workflow

When the main outline has missing detailed per-chapter entries for certain arcs, follow this workflow. Validated on 《玄烬战盟》 arcs 9-16 (chapters 201-460).

## Detection

```bash
# Extract all chapter numbers from outline
grep -oP '\|\s*\d+\s*\|' 全书大纲文件.txt | grep -oP '\d+' | sort -n > /tmp/outline_chaps.txt

# Check for gaps against 1-800
python3 -c "
have = set(map(int, open('/tmp/outline_chaps.txt').read().split()))
missing = sorted(set(range(1,801)) - have)
print(f'Missing: {len(missing)} chapters')
for s,e in gaps(missing): print(f'  {s}-{e} ({e-s+1}章)')
"
```

## Supplementation

### When the outline has arc headers but no per-chapter entries
Read existing chapters on disk for the arc to infer the narrative thread. Use chapter titles as anchors. Fill gaps by bridging between existing chapters.

### When arcs are entirely missing
Infer from:
1. Volume-level metaphor (e.g., Vol 2 "浴血中土" = 1937-1941)
2. Adjacent arcs' themes (what comes before and after)
3. Per-character arc summaries in the outline
4. 物码体系 continuity (what objects are in play)

### Format
Follow the main outline's exact format:
```
| 章号 | 标题 | 状态 | 内容要点 |
|----|------|:--:|------|
| NNN | 标题 | 🆕 | 要点→要点→要点 |
```

### Title style
Titles should be:
- Short (2-5 characters ideal)
- Concrete nouns or verbs (not abstract concepts)
- Match the existing chapter title style in that volume

## Merging

User prefers a SINGLE authoritative outline file. After supplementing:
1. Find the gap insertion point in the main outline
2. Insert supplementary content
3. Normalize `##` headers to `###`
4. Resolve chapter range overlaps between volumes
5. Verify: all 800 chapters have entries, all 30 arcs have `###` headers
6. Delete intermediate supplement files

## Chapter Range Conflicts

The original outline may have range overlaps (e.g., arc 17 labeled "421-460" but Volume 4 should start at 461). When merging, adjust chapter ranges to match actual file numbering on disk. Document the mapping clearly.

## 240-301 Gap (Validated Case)

The main outline (v4) jumped from arc 8 (181-210) directly to arc 13 (301-330), omitting arcs 9-12 entirely. The supplements added:
- Arc 9: 反扫荡 (201-210, 10 chapters)
- Arc 10: 西迁与分裂 (211-240, 30 chapters)
- Arc 11: 汇聚力量 (241-270, 30 chapters)
- Arc 12: 抗烬盟约 (271-300, 30 chapters)
- Arcs 13-16: 301-460, 160 chapters (Vol 3 complete)

Result: single merged file `全书大纲_完整版_v5_终极合并版.txt` covering all 800 chapters.

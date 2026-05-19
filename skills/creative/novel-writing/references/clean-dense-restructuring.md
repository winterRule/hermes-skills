# Clean-Dense Chapter Restructuring

When inherited chapters from prior writing sessions are **format-clean** (zero dashes,
zero split quotes, CJK ≥ 2000) but **structurally dense** (few paragraphs, long blocks,
paragraph count well below target), a different approach is needed — pure semantic
paragraph breaking without the three-phase repair pipeline.

## Diagnosis

Run a quick scan to identify this pattern:

```python
# Per chapter: paragraph count, CJK, dashes, quote count
paras = len([l for l in text.split('\n') if l.strip()])
dashes = text.count('——')
quotes = text.count('"')
```

**Clean-dense signature**: `dashes == 0 AND quotes < 10 AND paras < 25 AND cjk >= 2000`

This means the chapter needs structural breaking only — no format repair required.

## Processing Approach

For clean-dense chapters, skip the three-phase repair (merge dialogue→fix punctuation→comma flow)
and go directly to semantic paragraph breaking:

### Step 1: Read and identify semantic boundaries

Time shifts, location changes, character/speaker switches, event phase transitions,
emotional tone shifts — each is a paragraph break point.

### Step 2: Restructure with write_file

Maintain ALL content while inserting paragraph breaks at semantic boundaries.
The text between breaks stays as-is with internal commas — no need to convert
internal periods because the chapter was already written with proper comma flow.

### Step 3: Batch-verify with execute_code

After writing 3-5 chapters, run one `execute_code` call that:
1. Fixes any `——` → `，` (rare in clean chapters but possible)  
2. Converts ASCII `"` → curly `""` with state machine
3. Reports paragraph count, CJK, dash count, quote balance

```python
text = text.replace('\u2014\u2014', '\uff0c')
flip = True
chars = list(text)
for i, c in enumerate(chars):
    if c == '"':
        chars[i] = '\u201c' if flip else '\u201d'
        flip = not flip
text = ''.join(chars)
```

### Step 4: Verify per chapter

| Check | Threshold |
|-------|-----------|
| Paragraphs | ≥ 25 (target 40+, but 25+ is acceptable for dense war narrative) |
| CJK | ≥ 2000 |
| Dashes | 0 |
| Quote balance | left == right |
| End marker | `*第N章·完*` present |

## Efficiency Pattern

For clean-dense chapters, process in batches of 4-5:
1. Read all chapters in the batch
2. Restructure each mentally, noting semantic boundaries
3. Write all with `write_file` 
4. One `execute_code` call to fix quotes/dashes and verify all

This avoids the per-chapter verify overhead that's needed for format-broken chapters.
Clean chapters rarely introduce new dashes or ASCII quotes during restructuring —
the main risk is `write_file` converting curly quotes to ASCII, which the batch
fix handles.

## When NOT to use this workflow

If the scan reveals: dashes > 0, odd quote counts, or `NNN|` line number artifacts —
use the full three-phase repair in `references/paragraph-reformatting.md` instead.
Clean-dense restructuring assumes the text is already well-formed at the sentence level.

## Real example: 中土纪元 Volume 2 (121-130)

- Pre-scan: 10 chapters, avg 19.3 paragraphs, 0 dashes, 0 quotes, all CJK ≥ 2000
- Clean-dense signature: ✓ (all 10 chapters match)
- Processing: read → restructure → write_file → batch verify
- Post-scan: avg 31.1 paragraphs (+61%), 0 dashes, balanced quotes, all CJK ≥ 2000
- Time: ~4 tool calls per batch of 4 chapters (vs 3-5 calls/chapter for broken chapters)

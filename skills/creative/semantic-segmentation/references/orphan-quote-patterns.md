# Orphan Quote Fragment Patterns

Documented 2026-05-19 from 中土纪元 Volume 2 re-segmentation (chapters 121-240, 12 batches).

## Three Patterns

### Pattern ① — Orphan Opening Quote (`" ` prefix)
- **Detection**: Paragraph starts with `\u201c ` (LEFT DOUBLE QUOTATION MARK + space) but has no `\u201d` in the same paragraph
- **Cause**: Segmentation split a dialogue+narration continuous text at a period before the closing quote, leaving the opening quote orphaned on the next paragraph
- **Fix**: Remove the `\u201c ` prefix — the text is narration, not dialogue
- **Actual cases**: ch074 L117, ch238 L76

### Pattern ② — Empty Quote Pair (`" "`)
- **Detection**: `\u201c \u201d` appears consecutively in text
- **Cause**: A paragraph was split producing `\u201c\ntext\n\u201d`, then a rogue opening+closing pair got inserted during mechanical split
- **Fix**: `text.replace('\u201c \u201d', '')` — remove the empty pair
- **Actual cases**: ch198 L20/L22, ch221 L102, ch223 L110/L148, ch228 L112, ch230 L84, ch232 L132, ch234 L14/L24, ch236 L118
- **Frequency spike**: Chapters 221-240 had significantly more empty pairs than 121-220, suggesting quality degradation in later Volume 2 chapters

### Pattern ③ — Orphan Closing Quote (`" ` at start, no `"` nearby)
- **Detection**: Paragraph starts with `\u201d ` and no `\u201c` within first 3 characters
- **Cause**: Segmentation fragmentation of dialogue
- **Fix**: Full-chapter quote normalization (all quotes → ASCII `"` → state machine back to `\u201c`/`\u201d`)
- **Actual cases**: ch074 (original orphan close quote), ch238 (required full-chapter re-normalization)

## Detection Code (Python)

```python
ep = '\u201c \u201d'
paras = [l for l in text.split('\n') if l.strip() 
         and not l.strip().startswith('第') 
         and not l.strip().startswith('*第')]

orphan_open  = sum(1 for l in paras if l.strip().startswith('\u201c ') and '\u201d' not in l)
orphan_empty = text.count(ep)
orphan_close = sum(1 for l in paras if l.strip().startswith('\u201d ') and '\u201c' not in l[:3])
```

All three must be zero. Report chapter+line number for any findings.

## False Positive Patterns from scan_multi_speaker.py

After scanning 120 chapters, these false positive categories emerged:

| Category | Example | Why False |
|----------|---------|-----------|
| 术语引号 | `"羊毫"`, `"扫荡"` | Quoted terms, not dialogue |
| 叙事"写道" | `条目下面写道："...` | Narrator describing writing, same speaker |
| 同一人连续 | `"志不是写...是写..."` | Speaker verb appears in content, not a change |
| 同一人动作 | `"然后他问学生:"` | Same character acting then speaking |
| 误匹配动词 | `"底肥不写"`, `"务没有回答"` | Regex picks up fragments that look like speaker+verb |

True positive rate: ~5% (5 actual fixes out of ~100 flags across 120 chapters).

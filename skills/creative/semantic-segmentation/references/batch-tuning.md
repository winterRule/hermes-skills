# max_cjk Parameter Tuning

Data from 中土纪元 Volume 2 batch semantic re-segmentation (40 chapters, 121-160).

## Default Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `--target-paras` | 70 | Forces aggressive initial boundary detection |
| `max_cjk` (internal) | 65 | Sweet spot for 2000-2500 CJK chapters |
| Window size | 4 | sentences per similarity comparison |
| Keywords | 8 | top jieba keywords per window |

## Tuning Decision Tree

```
Run with max_cjk=65, target-paras=70
    │
    ├─ Paragraphs < 40 → decrease max_cjk to 55, rerun
    ├─ Paragraphs 40-80 → DONE ✅
    └─ Paragraphs > 80 → increase max_cjk to 75, rerun
```

## Batch Data (121-160)

| Batch | CJK Range | max_cjk | Target | Result (段) | Notes |
|-------|-----------|---------|--------|-------------|-------|
| 121-130 | 2002-2359 | 65 | 70 | 40-52 | 123/130 needed max_cjk=60 for 40+ |
| 131-140 | 2019-2173 | 65 | 70 | 42-74 | 135 needed max_cjk=55 for 40+ |
| 141-150 | 2028-2234 | 65 | 65 | 63-75 | Dense dialogue chapters, naturally high |
| 151-160 | 2109-2522 | 65 | 70 | 70-80 | Very dense prose, hit ceiling |

## Comma Flow Verification

After every batch, run:
```python
# Check forbidden patterns
bad = '。。' in text or '，，' in text
bad |= bool(re.search('。[，]', text))  # period before comma
bad |= bool(re.search('，。(?=.)', text))  # comma-period mid-paragraph
```
Zero violations across all 40 chapters using max_cjk=65 + target=70.

## Mechanical Split Behavior

With `max_cjk=65`:
- Paragraphs containing 65+ CJK are split at the nearest comma boundary
- Each resulting chunk is ~50-65 CJK
- Comma flow is re-cleaned after mechanical split
- Edge case: very long sentences with few commas may produce chunks > max_cjk

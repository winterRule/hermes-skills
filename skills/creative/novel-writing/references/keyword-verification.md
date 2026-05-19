# Two-Pass Keyword Verification (关键词双重验证)

## Why Two Passes

Keyword-based outline alignment checks frequently produce false positives — chapters that cover the required concept but use different vocabulary. In the Volume 1 audit (50 chapters), 21 initial keyword flags reduced to 12 genuine gaps after fuzzy semantic pass. Single-pass exact matching would have caused 9 unnecessary patches, each risking content disruption.

## Pass 1: Exact Match

Run first. Define 3-4 keywords per chapter from the outline. Use `kw in text` for each.

```python
keywords = ["身世", "父母", "独自求生"]
hits = sum(1 for kw in keywords if kw in text)
missed = [kw for kw in keywords if kw not in text]
```

Flag `missed` as candidates for Pass 2.

## Pass 2: Fuzzy Semantic Match

For each "missed" keyword, check a list of semantic variants — synonyms, related terms, or concept-level equivalents that would indicate the required idea IS present even if the exact word isn't.

### Building Variant Lists

For each keyword, list 2-4 alternatives:

```python
fuzzy_variants = {
    "身世": ["身世", "来历", "出身", "部落"],
    "父母": ["父母", "爹娘", "双亲", "父亲", "母亲", "家人"],
    "独自求生": ["独自", "求生", "一个人", "活下来"],
    "化解危机": ["化解", "解围", "脱险", "摆脱"],
    "现代思维": ["现代", "思维", "分析", "方法"],
    "奢靡": ["奢靡", "奢华", "奢侈", "挥霍", "酒", "宴"],
    "探子": ["探子", "间谍", "密探", "眼线", "监视"],
    "汉奸": ["汉奸", "投敌", "通敌", "叛", "傀儡"],
    "走私": ["走私", "偷运", "暗", "秘密交易"],
    "火药": ["火药", "炸药", "硫磺", "军火"],
    "停止内斗": ["停止", "内斗", "联合", "共同", "合作"],
    "排挤": ["排挤", "冷落", "边缘", "孤立", "视而不见"],
    "敌占区交界": ["交界", "边界", "石埂", "分界线"],
    "夜校": ["夜校", "识字班", "学校", "教室"],
    "互助": ["互助", "互帮", "帮助", "合作"],
    "士气高昂": ["士气", "高昂", "斗志", "精神", "不缺"],
    "拒绝": ["拒绝", "否决", "不同意", "反对"],
}
```

### Fuzzy Match Logic

```python
def fuzzy_match(keyword, text):
    variants = fuzzy_variants.get(keyword, [keyword])
    return any(v in text for v in variants)
```

Apply to each missed keyword. If ALL missed keywords pass fuzzy check, the chapter passes keyword alignment. Only chapters with genuinely missing concepts after Pass 2 need patches.

## Batch Keyword Patch Pattern

When multiple chapters need keyword patches (this session: 12 chapters), use `execute_code` with a single Python script rather than individual `patch` calls:

```python
patches = {
    14: {
        "insert_before": "\n\n---\n\n",  # marker to insert BEFORE
        "content": """...paragraph naturally incorporating missing keywords..."""
    },
    # ... more chapters
}

for ch_num, patch_data in patches.items():
    fpath = find_chapter(ch_num)
    with open(fpath) as f:
        text = f.read()
    
    idx = text.rfind(patch_data["insert_before"])
    if idx == -1:
        # Fallback: insert before end marker
    end_match = re.search(r'\*第.*章·完\*', text)  # .* pattern is reliable; avoid CJK char class
    if end_match:
        idx = end_match.start()
    
    new_text = text[:idx] + patch_data["content"] + '\n' + text[idx:]
    with open(fpath, 'w') as f:
        f.write(new_text)
```

Key rules for keyword patches:
1. **Integrate naturally**: The added paragraph should flow from existing content, not feel bolted-on
2. **Use existing character voices**: Echo the chapter's established tone
3. **Insert before end marker**, not after
4. **150-300 CJK chars** is usually sufficient for 2-3 missing keywords
5. **Verify end marker format** — arc-final chapters use `*第X章·完 | 第X弧线「弧线名」终*`

## Audit Sequence (Full-Volume)

The effective sequence proven in this session:

1. **Structure scan all chapters** — fix post-marker residue (changes CJK counts!)
2. **Pass 1 — exact keyword match** — flag candidates
3. **Pass 2 — fuzzy semantic match** — identify genuine gaps
4. **Batch patch genuine gaps** — one execute_code for all chapters
5. **Final sweep** — verify CJK, structure, format for all chapters

Running passes 1+2 in a single execute_code script avoids repeated file reads.

# Temp-File Expansion Pattern

When expanding chapters that are below 2000 CJK, use this pattern to avoid the two major failure modes: `execute_code` Unicode escape issues in sandbox, and `patch()` converting Chinese curly quotes to ASCII.

## Why This Pattern

| Method | Failure Mode |
|--------|-------------|
| `patch(action='patch', new_string=...)` | Converts `""` (curly) → `\"` (ASCII) every time |
| `execute_code` with Chinese in Python strings | Unicode escape issues, SyntaxError on `""` (U+201C/U+201D) |
| `execute_code` with `\u`escapes | Doubly-escaped `\\u` breaks string literals |

## The Pattern

### Step 1: Write expansion text to a temp file via `write_file`
```
write_file(path="/tmp/hermes_exp_{ch_num}.txt", content="...")
```
The `write_file` tool accepts raw Chinese text with `""` curly quotes but systematically converts them to ASCII `"` — this is expected and handled in step 3.

### Step 2: Merge with execute_code
```python
import re

base = "/path/to/volume"
fpath = base + "/第221章_标题.txt"
with open(fpath, 'r', encoding='utf-8') as f:
    text = f.read()
with open("/tmp/hermes_exp_221.txt", 'r', encoding='utf-8') as f:
    expansion = f.read()

# Insert before end marker
m = re.search(r'\*第.*章·完', text)
if m:
    before = text[:m.start()].rstrip()
    marker = m.group(0)
    new_text = before + "\n\n" + expansion.strip() + "\n\n" + marker + "\n"
```

### Step 3: Post-merge format fix (ALWAYS run)
The expansion text from `write_file` contains ASCII `"` quotes. Run the state machine fixer:
```python
result = []
flip = True
for ch in new_text:
    if ch == '"':
        result.append('\u201c' if flip else '\u201d')
        flip = not flip
    else:
        result.append(ch)
new_text = ''.join(result)

# Also fix any —— that sneaked in
new_text = new_text.replace('\u2014\u2014', '\uff0c')
```

### Step 4: Verify
```python
cjk = len(re.findall(r'[\u4e00-\u9fff]', new_text))
# Should be >= 2000
```

## Batch Multi-Chapter Pattern

For 2-3 chapters at once:
1. Write all expansion temp files via separate `write_file` calls
2. One `execute_code` call that reads all temp files, merges, fixes quotes/dashes, and prints CJK results

## Cost
- 2-3 `write_file` calls for expansion text (one per chapter)
- 1 `execute_code` call for merge + fix + verify
- Total: ~3-4 tool calls per batch of 2-3 chapters

## Validated In
Arc 10 (221-230): expanded 6 short chapters (221, 222, 224, 225, 228, 230) with temp files, 100% success rate on format cleanliness after merge+fix step.

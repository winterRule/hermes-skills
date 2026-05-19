# Anomaly Scanning for Novel Chapters

Systematic quality scan for batches of novel chapters. Run this as part of the post-arc audit to catch issues that word-count checks alone miss.

## When to Run

- After completing any arc of 10+ chapters
- When the user reports "不明意义的数字" or content errors
- Before reporting an arc as complete

## The Scan Pattern

Run from the novel's volume directory using `execute_code` with Python (avoid `terminal` for large scans — `/mnt/` paths may timeout):

```python
from hermes_tools import terminal, read_file
import re

base = "/mnt/d/sideline/ai/novel/{书名}/{卷名}"
files = ["第060章_xxx.txt", ...]  # or glob from terminal

for fname in files:
    text = read_file(f"{base}/{fname}")
    
    # Check 1: Standalone multi-digit numbers (possible corruption)
    for i, line in enumerate(text.split('\n')):
        digits = re.sub(r'[^\d]', '', line)
        if len(digits) > 10 and len(line.strip()) > 5:
            print(f"  {fname}:{i+1}: MANY-DIGITS({len(digits)})")
    
    # Check 2: Suspicious "/数字" patterns (user-reported issue)
    if re.search(r'，/\d', text):
        print(f"  {fname}: ，/数字 pattern found!")
    
    # Check 3: Duplicate lines (adjacent identical lines of significant length)
    lines = text.split('\n')
    for i in range(len(lines)-1):
        if len(lines[i].strip()) > 30 and lines[i].strip() == lines[i+1].strip():
            print(f"  {fname}:{i+1}: DUPLICATE LINE")
    
    # Check 4: Chinese character count
    cn = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))
    if cn < 2000:
        print(f"  {fname}: UNDER 2000字 ({cn})")
```

## Common Findings & Fixes

| Finding | Fix |
|---------|-----|
| DUPLICATE LINE | Remove the duplicate with `patch` using unique surrounding context |
| UNDER 2000字 | Expand with `patch` — append one scene, not rewrite entire file |
| MANY-DIGITS | Usually false-positive (chapter numbers like "第081-090章") — verify manually |
| ，/数字 pattern | Read the full line in context. May be encoded data format (legitimate) or genuine corruption |

## Duplicate Content Detection (Critical)

Duplicate paragraphs are a silent quality failure — they bloat the chapter, confuse the reader, and don't show up in word-count checks. They happen when:
- Multiple `patch` operations overlap on the same file region
- A prior session's rewrite left stale content that a later `patch` didn't clean up
- The agent writes a full paragraph, then writes the same paragraph again thinking it's different

**Detection**: In addition to the exact-duplicate check above, also scan for near-duplicates — paragraphs where >80% of the text is identical but small variations exist. These are harder to catch with grep but easier to spot by eye when re-reading.

**Fix**: When duplicate content is found, use `patch` with the unique content immediately before/after the duplicate block to target the removal precisely. Do NOT rewrite the entire file — you risk introducing new errors in content that was fine.

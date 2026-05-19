# Volume-Start Workflow: Old Chapter Title Alignment

When starting work on a new volume (especially after v4 outline reorganization), existing chapters from previous sessions often have titles that DON'T match the current outline. This is a structural issue, not a content issue.

## Detection

Run a title scan comparing file names against the outline:

```python
import re, glob

outline_titles = {
    161: '下水道的学堂', 162: '林嫂的灰瓷罐', 163: '铁柱的秘密工棚', ...
}

for num in range(volume_start, volume_end + 1):
    result = glob.glob(f'{vol_path}/第{num:03d}章_*.txt')
    if not result: continue
    fname = result[0].split('/')[-1].replace('.txt', '')
    expected = outline_titles.get(num, '')
    if expected and expected not in fname:
        print(f"  MISMATCH: 第{num:03d}章: outline'{expected}' vs file'{fname}'")
```

## Fix: Batch Rename

```python
import os

renames = {
    '第163章_地下火种.txt': '第163章_铁柱的秘密工棚.txt',
    '第166章_陆辰的见证.txt': '第166章_苏大姐的日志（二）.txt',
    # ... all mismatches
}

for old, new in renames.items():
    old_path = f'{vol_path}/{old}'
    new_path = f'{vol_path}/{new}'
    if old != new and os.path.exists(old_path):
        if os.path.exists(new_path):
            # Target exists — read old content, write to new, remove old
            with open(old_path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            with open(new_path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            os.remove(old_path)
        else:
            os.rename(old_path, new_path)
```

## Pitfalls

1. **Renaming doesn't fix internal content**: The file name changes but the chapter's first-line title may still use the old title. This is usually acceptable since the content matches what was written, only the label changed.

2. **Don't rename blindly**: Verify the chapter content actually matches the outline's intended topic before renaming.

3. **Priority**: Do renaming BEFORE writing new chapters so the directory is clean for the todo list.

## When This Happens

Most common in Volume 2+ of v4-reorganized novels where arcs 1-6 (Volume 1) were rewritten fresh but arcs 7+ (Volume 2) have old chapters from pre-v4 sessions.

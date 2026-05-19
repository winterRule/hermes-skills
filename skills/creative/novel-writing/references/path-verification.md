# Path Verification Checklist

The single most expensive typo in novel sessions: a missing/extra letter in the
directory path causes ALL new chapters to land in a silent fork directory that
looks real but isn't.

## The `sidline` → `sideline` Case

User's project root: `D:\sideline\ai\novel\` (WSL: `/mnt/d/sideline/ai/novel/`)

One-character error: `sidline` (missing `e`) creates `/mnt/d/sidline/ai/novel/`
which is a valid, writable, empty-directory-creating path. 22 chapters were
written there before the divergence was caught.

## Mandatory Verification (before write_file in a novel session)

```bash
# 1. Confirm the project root exists and contains expected files
ls /mnt/d/sideline/ai/novel/中土纪元/全书大纲_完整版.txt

# 2. Confirm prior chapters are present
ls /mnt/d/sideline/ai/novel/中土纪元/第一卷/ | tail -5

# 3. After writing the FIRST chapter of a session:
wc -c /mnt/d/sideline/ai/novel/中土纪元/第一卷/第XXX章_*.txt
# The file should show >5000 bytes AND appear alongside prior chapters in ls output
```

## Recovery (if chapters went to wrong path)

```bash
# Copy from wrong path to correct path
cp /mnt/d/sidline/ai/novel/中土纪元/第一卷/第0*章*.txt \
   /mnt/d/sideline/ai/novel/中土纪元/第一卷/

# Verify count matches
ls /mnt/d/sidline/.../第一卷/ | wc -l   # wrong
ls /mnt/d/sideline/.../第一卷/ | wc -l   # correct

# Delete wrong path ONLY after confirming copy succeeded
rm -rf /mnt/d/sidline/ai/novel/中土纪元/
```

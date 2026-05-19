# Volume Migration Workflow

When a volume folder contains chapters that belong to a different volume per the official outline, migrate them before starting any content work.

## Detection
```python
# Scan actual chapter range per volume folder
# Compare to outline's declared range
# If overlap or mismatch, flag for migration
```

## Migration Steps

1. **Confirm the correct division** from the outline file (`全书大纲_完整版_v4_终极版.txt`)
   - 第一卷: 001-120章
   - 第二卷: 121-300章
   
2. **Move files** between volume directories:
   ```bash
   cd /mnt/d/sideline/ai/novel/中土纪元/
   mv 第一卷_星火初燃/第12[1-9]*.txt 第一卷_星火初燃/第1[3-5][0-9]*.txt 第一卷_星火初燃/第160*.txt 第二卷_浴血中土/
   ```

3. **Verify**: Count chapters in each volume folder after migration
   ```bash
   ls 第一卷_星火初燃/*.txt | wc -l  # Should be 120
   ls 第二卷_浴血中土/*.txt | wc -l     # Will include migrated chapters
   ```

## Post-Migration: Two-Tier Quality Scan

After migration, run a full quality scan across the migrated range. The diagnostic signal to watch for:

**"Clean wrong-numbered" vs "Correct-numbered but template-polluted"**: When some chapters have wrong internal numbers but clean formatting, while others have correct numbers but heavy template endings (风从暗河方向吹过来 ×5-70 per chapter), this means the volume was assembled from inconsistent prior sessions. The wrong-numbered chapters were manually written (clean prose), then file-renamed without updating content. The correct-numbered chapters were AI batch-generated (template-heavy endings).

This signal demands full audit before any content work — do not skip to fixing individual chapters.

## Post-Migration: Title-Outline Deviation

Moved chapters may have file titles that DON'T match the current official outline. Compare file titles vs outline titles for every chapter in the range. If >30% mismatch, the chapters were written to an older outline version. Two options:
1. Rewrite content to match current outline titles (preferred for small batches, ≤10 chapters)
2. Rename files to match content (only if user confirms old titles are the correct ones)

**This session validated**: 9/10 chapters in 151-160 had different titles — all were rewritten to match the current outline.

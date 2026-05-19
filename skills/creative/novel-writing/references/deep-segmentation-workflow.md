# Deep Segmentation Workflow (深度语义分段)

Validated on Volume 1, chapters 061-080 (20 chapters). This is the CORRECT way to segment chapters — NOT mechanical period-splitting.

## The 3-Phase Fix

### Phase 1: Merge Split Dialogue (合并裂引号)
Problem: Previous "fix" mechanically split at periods, breaking dialogue. One person's speech became 3-5 fragments with unclosed quotes.

Fix: Merge consecutive paragraphs with unbalanced quotes. Within merged dialogue, replace internal periods with commas.

V1: 29 chapters (030-058), 436 splits → 0.

### Phase 2: Comma-Flow Within Paragraphs (段落内逗号流)
Problem: Paragraphs had internal periods breaking semantic flow. User rule: period only at paragraph end.

Fix: Replace all periods with commas except the last one per paragraph.

V1: 120 chapters, 8,603 periods → commas.

### Phase 3: Deep Semantic Segmentation (深度语义拆分)
Problem: Chapters had 12-30 paragraphs vs Chapter 001 benchmark of 65.

Correct approach:
1. Read the full chapter
2. Identify semantic boundaries: time/location/event-phase/content/emotion changes
3. Break at those boundaries — never at arbitrary punctuation
4. Dialogue: one person = one paragraph
5. Scene transitions = paragraph breaks

Signals for breaks: time markers, location changes, character switches, event phase changes, emotion/register shifts.

## CJK Loss from Dedup
When duplicates removed, add meaningful content at natural insertion points (sensory detail, internal monologue, backstory). V1: 061-064 went 1908→2087, 1902→2011, 1918→2037, 1896→2020.

**V2 discovery (2026-05-20, 中土纪元第二卷)**: Inherited chapters from prior writing sessions had MASSIVE template pollution. Three patterns identified:
1. **跨章模板**: "暗河的水在远处无声地流着。从北岭发源..." large paragraph repeated across chapters 134-143
2. **跨章复用段**: "在下水道网络的运转过程中，老陈发现了一个规律..." reused in 141-143
3. **章末机械重复**: Same closing paragraph duplicated 5-25 times within a single chapter (e.g. "灰瓷罐的盖子旋紧之后..." ×12 in 142, "京系车队碾过的车辙..." ×8 in 134, "在" character paragraph ×25 in 191)

These inflated CJK from actual 760-1,300 to apparent 2,000-7,000. After dedup, ALL chapters need significant expansion (500-1,200 CJK each). Budget 3-5 expansion rounds per chapter, not 1-2.

## Paragraph Density Target (HARDENED 2026-05-20)
对标第001章: 65段/2,074CJK. Target 40-65 paragraphs per chapter. Below 25 = severely under-segmented. Below 15 = unreadable wall of text.

Segmentation does NOT reduce CJK — it only adds paragraph breaks and converts internal periods to commas. If CJK drops after segmentation, it's because the original was inflated by template duplication.

## Prevention
Write new chapters already segmented: comma-flow, semantic breaks, target 40+ paragraphs/chapter. Verify: splits=0, internal_periods=0, CJK>=2000.

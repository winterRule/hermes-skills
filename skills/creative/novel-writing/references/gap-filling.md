# Gap-Filling Workflow (章节补写模式)

When chapters need to be inserted between already-written content (e.g., expanding a 10-chapter arc to 20 chapters in v4.0 outline), follow this workflow specifically.

## Trigger

Use this when:
- Existing chapters 030 and 041 are complete, but 031-040 need to be created
- The outline was rewritten (v2→v3→v4) and existing chapters were mapped to new numbers with gaps
- Any scenario where chapters must bridge between pre-existing content

## Workflow

### 1. Read Both Sides (MANDATORY)
Before writing a single word, read the LAST chapter before the gap AND the FIRST chapter after the gap. This is not optional — the gap chapters must connect cleanly on both ends.

```
read_file(path=last_chapter_before_gap)  # e.g., 030
read_file(path=first_chapter_after_gap)   # e.g., 041
```

### 2. Map Continuity Points
Extract from the surrounding chapters:
- **Physical state**: Where is the protagonist? What do they possess?
- **Knowledge state**: What do they know? What have they just learned?
- **物件体系**: What objects are in play (碗片, 炭纸, 短铳, etc.)?
- **Character relationships**: Who are they with? Who have they just met or parted from?
- **Tone/theme**: What emotional register ends the previous chapter? What begins the next?

### 3. Write in Sub-Batches
For gaps of 10-15 chapters, write in sub-batches of 3-5 chapters. Verify CJK ≥ 2000 per chapter after each sub-batch. Do NOT write all 10-15 in one go — the short-chapter problem compounds.

### 4. Handle Outline Contradictions
The v4.0 outline was written as a planning document, not from execution. It may contain contradictions with existing chapters:

**Example**: Outline says 老陈 accompanies 陆辰 on journey (新011-020), but existing 新010 has 老陈 staying behind in 东海郡.

**Fix pattern**: Adapt, don't force. Have 老陈 catch up mid-journey (瀛烬提前到达 forced him to evacuate). This preserves existing canon while following the outline's spirit.

**Rule**: Existing chapters are canon. The outline is a guide. When they conflict, the existing chapter wins. Bridge the gap creatively.

### 5. Verify Gap Closure
After writing the final gap chapter, confirm:
- The last line/scene naturally leads into the first line of the next existing chapter
- No plot threads are dropped mid-gap
- 物件体系 continuity is unbroken
- Character knowledge is consistent (they don't know things they learned in chapters that haven't happened yet)

## Pitfalls

- **Forgetting what the protagonist possesses**: If 新030 ends with 陆辰 holding leverage over 钱伯钧, and 新041 starts with him receiving 顾明远's invitation, the gap chapters must show how that leverage was used or banked, not forgotten.
- **Timeline drift**: Five chapters of gap may represent days or weeks. Ensure time passage is consistent with surrounding chapters.
- **Mood whiplash**: If chapter 030 ends on tension and 041 opens on tension, the gap chapters shouldn't be pure exposition. Maintain narrative momentum.
- **Object system breaks**: If the 碎碗片 is with 陆辰 in 030 and has been placed in 仁济堂 by 041, the gap must show the handover. Objects don't teleport.
- **Content-vs-filename mismatch at scale (Vol 2 validated, 13 chapters)**: When earlier writing sessions produced chapters with old internal titles/numbers that were later renamed, BOTH the internal first-line header AND the content may match the OLD title, not the new filename. The `arc-audit-full-scan.py` catches this. Decision rule: if 3+ chapters in a gap have content matching old titles, rewrite them to match new titles (don't rename files — the filenames match the current outline).

## Cross-Reference Technique (前向+后向钩子)

When writing chapters to fill gaps, each chapter MUST connect to BOTH the preceding and following chapter. This creates a narrative weave that makes the gap feel like it was always there.

**Forward hook**: Plant a detail, object, or observation that pays off in a later (already-written) chapter.
- Example: 163 (铁柱的秘密工棚) ends with 阿来 finding the workshop → 164 (阿来的归码网) begins with 阿来 improving his guide-marks. The seed in 163 makes 164 feel foreshadowed.
- Example: 175 (赵元朗的演讲) has 藤原秀 in the audience observing → 178 (藤原秀的反省) opens with 藤原秀 acting on what he saw. The observation in 175 creates continuity.

**Backward hook**: Call back to a detail from a preceding chapter.
- Example: 172 (营救行动) references the 告密者 from 170 and the arrest from 171, grounding the rescue plan in established events.
- Example: 169 (焦老农的粮道) references 江寒's guerrilla battle in 168 (the grain feeds his fighters).

**Technique**: Before writing a gap chapter, list 2-3 specific details from the chapter before and 2-3 specific details the chapter after will need. Weave at least one from each list into the new chapter.

**Validation**: Vol 2 arcs 7-8, 6 chapters rewritten with this technique — all 6 passed narrative continuity review on first pass.

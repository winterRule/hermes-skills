# Metaphor Novel Quick-Start (新隐喻小说启动流程)

When a user provides a complete novel prompt and says "开始创作", follow this exact deliverable sequence. This workflow was validated on a 200万字/5卷/隐喻历史小说 project.

## Phase 1: Foundation (3 files, before any chapters)

### 1.1 全书大纲 (Full Outline)
- Parse prompt for: 字数目标, 卷数, 隐喻对照表, 风格约束, 禁止元素
- Structure as cumulative word-count milestones per volume (e.g. 1-50万字/51-100万字)
- Plan chapters in arcs of ~10 chapters each, not individual chapter titles
- Each arc entry: number range, historical correspondence, key events, subplot intersections
- Confirm total chapters × average word count ≈ target word count

### 1.2 核心人物人设 (Character Profiles)
- One profile card per core character: name, age, appearance, personality, abilities, arc, historical prototype, iconic quotes, fate
- Organize by faction (主角→赤炬会→天衡盟→瀛烬→星火盟→伪衡→配角群像)
- Include character count summary table at end

### 1.3 支线剧情大纲 (Subplot Outlines)
- One section per subplot, each with: through-line, key beats, character arcs
- Include a cross-reference timeline table showing when each subplot intersects main plot
- Subplots must serve the core theme — no standalone side stories

## Phase 2: First 3 Chapters (sample chapters)

### Writing Rules
- 2000-3000 CJK characters per chapter (verify with `re.findall(r'[\u4e00-\u9fff]', text)`)
- 四段式 structure: Opening Hook → Plot + Development → Climax → Closing Hook
- 热血动漫风: short punchy sentences, concrete sensory details, em-dashes (——) for dramatic pauses
- No exposition dumps — reveal world through character experience, not narration
- Strict metaphor compliance: no real names, no 4th-wall breaks, no protagonist knowing chapter numbers

### Delivery Format
- Files named: `第XXX章_标题.txt`
- After writing all 3, run batch word-count verification
- Run humanizer scan (ignore em-dash flag for 热血动漫风 — genre convention)
- Present word-count table with ✅/❌

## Phase 3: Verification Checklist

After Phase 1+2 complete, verify:
- [ ] Outline word-count budget matches target (chapters × avg字 ≈ 总目标)
- [ ] All factions from prompt have character profiles
- [ ] Metaphor mapping table is complete and consistent
- [ ] All 3 chapters ≥ 2000 CJK characters
- [ ] No AI writing patterns (humanizer scan, excluding em-dash convention)
- [ ] No 4th-wall breaks, no real names, no "第X章" meta-narrative in content
- [ ] Project directory structure correct (全书大纲 + 人设 + 支线 + 第一卷/)

## Pitfalls

- **Old files in directory**: When creating a new project, the target directory may contain chapters from a previous novel. Always verify which files are new vs. pre-existing. The batch word-count script will scan ALL .txt files — filter output to only the new chapters.
- **CivNode integration optional**: CivNode MCP tools (243 writing tools) can enhance world-building but have rate limits on character creation. Don't block chapter writing on CivNode setup — proceed with flat files and add CivNode later.
- **Em-dash false positive**: The humanizer's em-dash pattern fires on Chinese web novel dialogue breaks (——). See humanizer skill §14 exception. Do not strip em-dashes from 热血动漫风 text.
- **Cursor drifting**: When writing in rapid succession, chapters can drift shorter. After writing 3 chapters, always run word-count verification before reporting completion.

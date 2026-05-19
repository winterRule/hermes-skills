# Chapter Expansion Patterns (章节扩写模式)

When a chapter falls below the 2000字硬地板, use these expansion patterns (one or two per short chapter). They are ranked by effectiveness based on real usage data from an 18-chapter writing session.

## Pattern 1: Secondary character callback (配角情感呼应) — MOST EFFECTIVE
Take a secondary character from an earlier chapter and show them reacting to or being affected by the current chapter's events. Example from 第014章:
```
阿禾低头描"等"字 → 白薇写《征兵令》课文 → 阿禾问"阿栗哥要被拉去哪里？" → 下课跑到灵讯台旁描"征兵令"
```
This works because it: (a) reinforces an existing emotional thread, (b) shows ripple effects, (c) adds word count organically.

## Pattern 2: Environmental + sensory grounding (环境/感官细节)
Add a paragraph of environmental description that serves a thematic purpose, not just filler. Example from 第015章:
```
铁匠学徒锄地 → 手被磨出血痂 → 渔民递湿布 → 铁匠学徒说"这块布比铁匠铺的淬火布软" → 老赵说"活下去先"
```
The key: sensory detail (blood scab, wet cloth, cold mud) that connects to character growth.

## Pattern 3: Extend the closing beat (延长结尾情绪)
The chapter ends on a single line or image. Add a second beat — a contrasting or deepening moment. Example from 第022章:
```
Original end: 老赵说"算不了"
Extended: 深夜 → 老钱教阿九拆枪 → 阿九超基准 → 老钱拍后脑勺
```

## Pattern 4: News travels (消息扩散)
Show how the chapter's key event reaches someone else — a different location, a different character. Example from 第017章:
```
Original end: 矿工立石板罢工
Extended: 阿火截获加密通讯 → 陆辰破译"秘密采样" → 矿脉仍安静
```

## Pattern 5: Bridge to past (连接过往)
Use an object, a smell, or a memory to connect the current scene to an earlier one. Example from 第023章:
```
老魏问"你是从别的地方来的吧？" → 陆辰答"是" → 老魏说"那就别白来"
Extended: 天亮 → 老魏在哨石上目送 → 阿火留纸条 → 白薇刻"传之" → 黑板上教"各"字
```

## Pattern 6: Parallel action (并行动作)
Show what another character is doing simultaneously. Example from 第016章:
```
Original end: 老赵说"你往后就知道了"
Extended: 陆辰看帐篷外 → 老钱教阿九 → 老赵教阿九用地的劲握枪 → 老魏在岗哨石上全看在眼里
```

## Expansion technique (using patch)
Always use `skill_manage(action='patch')` or `patch()` to APPEND content at the end of the chapter. Never rewrite the entire file. This is faster, preserves existing prose, and avoids introducing new errors.

1. Read the last paragraph of the chapter
2. Identify which pattern(s) fit naturally
3. Write the expansion as a continuation (not a separate scene)
4. Patch at the end, using the chapter's last sentence as the `old_string` anchor
5. Verify the patched file's byte count passes the ~5,000 byte threshold

## Pattern 7: Reflective contrast (主角视角对比) — RELIABLE FOR DUAL-WORLD NOVELS
This pattern is specific to novels where the protagonist has experienced two different worlds/systems (e.g., Tianheng Alliance bureaucracy vs. Red Torch base area). When the chapter falls short, insert a paragraph where the protagonist mentally contrasts what he's seeing NOW against what he saw/learned BEFORE in the other system. This works because it: (a) deepens the protagonist's internal arc, (b) organically reinforces the novel's thematic conflict, (c) requires no new characters or plot events, and (d) always yields 150-250 CJK characters per paragraph.

Example from 第034章 — after witnessing the salt-making process:
```
陆辰把掌心合拢，盐粒硌在虎口刚磨破的伤口上——一阵刺辣之后，他反而觉得这种痛是某种确认。他想起天衡盟军务处档案里赤炬会根据地的条目——分类是"非正规控制区"、经济评级是"不具备自给能力"……如果那个写档案的人也在今天下午亲手在这块乱石坡上挥过一个时辰的锄头……这份档案一个字都不会那么写。
```

Example from 第038章 — after the day of manual labor:
```
他在天衡盟写过的报告中，每次论及赤炬会都写成"兵源素质低下、后勤供给困难、缺乏建制规模"。但现在他意识到，这份报告漏掉了最重要的东西：那些赤炬会的民兵，连面粉都没得吃，连枪管都在炸，连受伤之后都没有麻药——但他们还在打。
```

Key triggers for this pattern: (a) Lu Chen witnesses something that contradicts a Tianheng Alliance report/assessment he wrote, (b) Lu Chen experiences physical labor/sensory input that his desk-job never gave him, (c) Lu Chen observes an organizational practice (voting, resource-sharing) that differs fundamentally from Tianheng Alliance norms.

## Pattern 8: Object symbolism callback (物件意象回扣)
Take a physical object introduced earlier in the chapter/arc and reinvest it with new meaning in the expansion paragraph. Example from 第037章: the charcoal stub (炭条) that was originally just a writing tool becomes the symbol of the letter that takes 5 months to deliver, and later becomes a physical token exchanged between Lu Chen and Alai at the mountain pass. This works because objects carry emotional weight without requiring new exposition.

## Minimum target
After expansion, the file should be at least ~5,500 bytes (~2,200字). This provides a 10% buffer above the 2000字硬地板 to account for byte-to-char estimation variance.

# 分批重分段工作流 (Batch Re-Segmentation Workflow)

四阶段流水线，用于处理从旧AI批量创作会话继承的欠分段+模板污染章节。**第二卷139-218（80章，8批次）单会话全验证。**

## 脚本位置 (Script Locations)

关键脚本的实际存放位置（非项目 `tools/` 目录）：
| 脚本 | 路径 |
|------|------|
| `semantic_split.py` | `~/.hermes/skills/creative/semantic-segmentation/scripts/` |
| `scan_multi_speaker.py` | `~/.hermes/skills/creative/novel-writing/scripts/` |
| `fix-internal-periods.py` | `~/.hermes/skills/creative/novel-writing/scripts/` |
| `fix-dialogue-splits.py` | `~/.hermes/skills/creative/novel-writing/scripts/` |

在 `execute_code` 中使用 `sys.path.insert(0, '<path>')` 导入，或在 terminal 中直接调用完整路径。compaction summary 可能引用旧路径（如 `scripts/` 或 `tools/`）——以 skill 目录中的实际文件为准。

## 阶段0：全卷扫描

```python
import re, glob, os
base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷_浴血中土/"
files = sorted(glob.glob(os.path.join(base, "第*.txt")))
for fpath in files:
    with open(fpath) as f: text = f.read()
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    dashes = text.count('\u2014\u2014')
    ascii_q = text.count('"')
    tmpl = '水伯的竹篙' in text or '暗河的水在远处无声地流着' in text
    # Report: CJK / 段数 / 破折号 / ASCII引号 / 模板污染
```

优先级：
- **优先**：段数<25 + 模板污染标记=True
- **次优先**：段数<25 + 格式干净
- **已OK**：段数≥25 + CJK≥2000

## 阶段1：模板去重（每批10章）

### 模板污染七模式（80章全验证）

1. **跨章大模板**：`暗河的水在远处无声地流着。从北岭发源...水位的湿痕在篙身上画出了战争段的全部水文记录...`（134-143, 161-168）
2. **短模板复读**：`水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。暗河的水在远处无声地流着。`（161/162/164/165/167/168/170/171/173/174/176/177，每章5-12次）
3. **短模板变体**：`水伯的竹篙上又多了一道湿痕。`（同样范围，每章5-19次）
4. **长模板带风偏**：`暗河的水在远处无声地流着，带着从北岭冲下来的松针和从采石场滴下来的水珠。水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。`
5. **跨章复用场景**：`科目002/升格符号/苏大姐点评` 出现在162/164/165/167/168/170/171/173/174/176/177
6. **跨章复用分析段**：`科目002运行到第三个月的时候出现了一个陆辰没有预料到的问题。记录员不够...` 出现在170-198范围
7. **章末句内重复**：同一句子在一段内重复5-25次（如`烧焦的黑板...`×19次、`版图上的绿色...`×5次）

### 去重执行代码

```python
def clean_chapter(text, ch_num):
    # Step 1: Remove template blocks
    text = re.sub(r'暗河的水在远处无声地流着\..*?水位的变化在篙身上留着。', '', text, flags=re.DOTALL)
    text = re.sub(r'水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。暗河的水在远处无声地流着[，。]*', '', text)
    text = re.sub(r'水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。\n', '', text)
    text = re.sub(r'水伯的竹篙上又多了一道湿痕。', '', text)
    
    # Step 2: Remove cross-chapter duplicates (keep in canonical chapter only)
    if ch_num not in [162]:
        text = re.sub(r'这件事后来被陆辰记录在科目002.*?没有人把情报变成可用的分析。', '', text, flags=re.DOTALL)
        text = re.sub(r'科目002运行到第.*?没有人把情报变成可用的分析。', '', text, flags=re.DOTALL)
        text = re.sub(r'苏大姐在磨盘前看到了这个符号.*?丁仓管无名，符号有主。', '', text, flags=re.DOTALL)
    
    # Step 3: Intra-paragraph dedup (sentence repetition within one paragraph)
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s: cleaned.append(line); continue
        sents = re.split(r'(?<=[。])', s)
        if len(sents) > 5:
            seen = {}; unique = []; dup = 0
            for sent in sents:
                sc = sent.strip()
                if not sc: continue
                sig = sc[:20]
                if sig not in seen: seen[sig]=1; unique.append(sent)
                else: dup += 1
            if dup >= 3: cleaned.append(''.join(unique)); continue
        cleaned.append(line)
    text = '\n'.join(cleaned)
    
    # Step 4: Cleanup
    text = re.sub(r'\n{3,}', '\n\n', text)
    marker = '*第{:03d}章·完*'.format(ch_num)
    text = re.sub(r'\*第\d+章·完\*', '', text)
    text = text.rstrip() + '\n\n' + marker + '\n'
    return text
```

### 去重后CJK崩塌预算（80章验证）

| 污染程度 | 模板占比 | CJK下降 | 典型章号 | 需扩充轮次 |
|---------|---------|---------|---------|-----------|
| 轻度 | <30% | -200~500 | 139-140 | 0-1轮 |
| 中度 | 30-50% | -500~1000 | 170-177 | 1-3轮 |
| 重度 | 50-70% | -1000~1800 | 145-168 | 2-4轮 |
| 严重 | >70% | -1500~2500 | 164-168, 179-198 | 4-5轮 |

## 阶段2：语义分段

详见 `semantic-segmentation` 技能。使用分层参数：

| 原段数 | max_cjk | target-paras |
|--------|---------|-------------|
| < 25 (文本墙) | 40 | 75 |
| 25–40 (欠分段) | 45 | 70 |
| 41–50 (可接受) | 50 | 65 |
| > 50 (较好) | 55 | 60 |

```bash
python3 scripts/semantic_split.py <file> --target-paras 70 --max-cjk 40 -i
```

### 阶段2a：分段后引号修复（必做）

```python
text = text.replace('\u201c', '"').replace('\u201d', '"')
text = text.replace('——', '，')
chars = list(text); flip = True
for i, c in enumerate(chars):
    if c == '"':
        chars[i] = '\u201c' if flip else '\u201d'
        flip = not flip
text = ''.join(chars)
# Verify: left == right
```

### 阶段2b：孤儿引号扫描（必做，三项全检）

`max_cjk ≤ 40` 或语义拆分时，可能在 `。"` 边界断开会话，产生三种孤儿引号碎片。每批分段后三项全检，任意一项>0即为质量问题——定位行号→手动修复→重新验证。

**三项检测代码（每次分段后必跑）**：
```python
paras = [l for l in text.split('\n') if l.strip() and not l.strip().startswith('第') and not l.strip().startswith('*第')]

# Type A — 孤儿关引号：段落以 \u201d 开头且前3字内无非段首开引号
orphan_close = sum(1 for l in paras if l.strip().startswith('\u201d ') and '\u201c' not in l[:3])

# Type B — 孤儿开引号：段落以 \u201c 开头但段内没有关引号（引号被拆走）
orphan_open = sum(1 for l in paras if l.strip().startswith('\u201c ') and '\u201d' not in l)

# Type C — 空引号对：\u201c \u201d 连续出现（在对话末尾句号处拆分后留下的空壳）
orphan_empty = text.count('\u201c \u201d')

# Must all be 0. Non-zero = print L numbers and fix.
```

**修复模式**：
| 类型 | 检测 | 修复 |
|------|------|------|
| A 孤儿关引号 | `\u201d ` 段首 | 与上一段合并（同一人连续对话），或移除前缀 |
| B 孤儿开引号 | `\u201c ` 段首无关引号 | 移除 `\u201c ` 前缀（纯叙事被误标为对话） |
| C 空引号对 | `\u201c \u201d` 连续 | `text.replace('\u201c \u201d', '')` |

**本会话验证的孤儿引号实例**：
| 章节 | 行号 | 类型 | 模式 |
|------|------|------|------|
| ch074 | L117 | B 孤儿开引号 | `\u201c 陆辰看了...` 前缀 |
| ch074 | L129 | C 空引号对 | `\u201c \u201d这个编号...` 空壳 |
| ch198 | L20, L22 | C 空引号对 | `\u201c \u201d记录的内容...` / `\u201c \u201d我不确定...` |
| ch128 | L90 | A 孤儿关引号 | 韩先生讲解+男孩反应 |
| ch132 | L26-34 | A 孤儿关引号 | 丁老兵-小周对话全碎 |
| ch136 | L44-48 | A/B混合 | 顾明远+伤员孤儿引号 |
| ch138 | L73-80 | A/B混合 | 阿来-阿禾对话全碎 |

### 阶段2c：多角色对话合并扫描（必做）

```bash
python3 scripts/scan_multi_speaker.py <目录> --start N --end M [-v]
```

详见 `semantic-segmentation` 技能 `references/multi-speaker-detection.md`。

## 阶段3：分批扩充

### 扩充铁律（模板污染预防）

每段扩充必须：
1. 绑定该章专有人物/物件
2. 至少一处感官细节（声音/触感/气味/温度）
3. 与前后段落有明确因果或时间衔接

**禁止泛化收束模板。跨章复用同一段落 = 红线。**

### 扩充注入技术（进化过程）

**✅ 首选：纯ASCII字符串 `+` 拼接**（避免sandbox SyntaxError）
```python
E[179] = ("第一句话。" +
    "第二句话。" +
    "第三句话。")
```

**⚠️ 备用：不含中文弯引号的单行字符串**
```python
E[179] = "第一句话。第二句话。第三句话。"
```

**❌ 已弃用：三引号含中文弯引号** — sandbox中易 SyntaxError: unterminated string literal

## 阶段4：ASCII引号修复

**✅ 首选：状态机逐字替换（80章全验证，最可靠）**
```python
chars = list(text); flip = True
for i, c in enumerate(chars):
    if c == '"': chars[i] = '\u201c' if flip else '\u201d'; flip = not flip
text = ''.join(chars)
```

**❌ 已弃用：`re.sub(r'"([^"]*)"', r'\u201c\1\u201d', text)`** — sandbox中 `bad escape \u`

## 五维审计汇报格式（USER-REQUIRED）

### 汇报铁律：修复必须输出行号

**USER-REQUIRED (2026-05-22)**：当修复孤儿引号或多角色对话合并时，必须输出**文件行号**。格式：`chXXX L行号`。例如：`ch074 L36, L42, L50, L65-82`。用户明确要求"修复的时候输出问题的行数"。

---

**每批完成后必须按此格式汇报，不可跳过。用户明确要求"之后的汇报全部按照这个来"。**

```markdown
## 🔍 XXX-XXX批 五维审计报告

### ① 技术审计 ✅/❌
| 章 | CJK | 段数 | —— | 引号 |
|---|------|------|-----|------|
| ... | ... | ... | 0 | 平衡 |
> 总计: CJK=XX / 章均=XX / 零破折号 / 零ASCII

### ② 大纲对位 ✅/⚠️
逐章标题核对

### ③ 逻辑链 ✅
因果链图示

### ④ 故事性 ✅
主题/物码/节奏/视角

### ⑤ 衔接点 ✅
逐章衔接人物/物码/情节

---

### 📊 N批汇总
| 批次 | CJK | 章均 |
|------|-----|------|
| ... | ... | ... |
| **合计** | **XXX** | **XXX** |
```

## 已验证批次数据（80章）

| 批次 | 章数 | CJK | 章均 | 污染章 | 扩充轮次 |
|------|------|-----|------|--------|---------|
| 139-148 | 10 | 20,886 | 2,089 | 4 | 2 |
| 149-158 | 10 | 22,451 | 2,245 | 6 | 3 |
| 159-168 | 10 | 21,716 | 2,172 | 7 | 3-5 |
| 169-178 | 10 | 21,864 | 2,186 | 6 | 3-4 |
| 179-188 | 10 | 21,824 | 2,182 | 7 | 4 |
| 189-198 | 10 | 20,958 | 2,095 | 6 | 4 |
| 199-208 | 10 | 21,527 | 2,152 | 1 | 1 |
| 209-218 | 10 | 23,080 | 2,308 | 0 | 0 |
| **合计** | **80** | **174,306** | **2,179** | **37** | — |

严重污染章（模板占比>50%）约37/80=46%，消耗了约70%的扩充轮次。

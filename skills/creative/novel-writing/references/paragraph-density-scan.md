# 段落密度扫描 (Paragraph Density Scan)

批量检测哪些章节段落数偏低，需要语义重新分段。

## 基准

- 第001章：65段 / 2,074 CJK ≈ 32 CJK/段
- 合格线：≥25段/章（对标001章的40%密度）
- 优良线：≥50段/章

## 扫描脚本

```python
import os, re

base = "/path/to/volume/dir"
files = sorted([f for f in os.listdir(base) if f.endswith('.txt')])

for f in files:
    path = os.path.join(base, f)
    with open(path, 'r', encoding='utf-8') as fh:
        text = fh.read()
    
    body = [l.strip() for l in text.split('\n') if l.strip() 
            and not l.strip().startswith('*第') 
            and not l.strip().startswith('第0')]
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    if len(body) < 25:
        flag = "⚠️ 需分段"
    elif len(body) < 40:
        flag = "⚡ 偏少"
    else:
        flag = "✅"
    
    if len(body) < 40:
        print(f"{f[:30]:30s} {len(body):4d} {cjk:5d} {flag}")
```

## 第一卷实测数据（2026-05-20）

| 范围 | 段数范围 | 评价 |
|------|---------|------|
| 001-029 | 32-88段 | ✅ 基准以上（019章32段为最低） |
| 030-058 | 17-93段 | ⚠️ 被错误"修复"过，段数虚高但对话拆碎 |
| 059-120 | 12-42段 | ⚠️ 严重欠分段（059起骤降至27段以下） |

第二至五卷待扫描。

## 后续处理优先级

1. **去重**：扫描相邻段前60字符是否重复 → 去重
2. **裂引号修复**：`scripts/fix-dialogue-splits.py`
3. **段落内逗号流**：`scripts/fix-internal-periods.py`
4. **语义重新分段**：按口诀（时间/地点/事件阶段/内容/感情变→分段）逐章精读判断

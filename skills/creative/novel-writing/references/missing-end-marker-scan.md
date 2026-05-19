# 批量操作后结束标记扫描

## 触发条件
在任何批量编辑操作后运行——分段拆分、破折号替换、元叙事清除、引号替换等涉及多文件 `execute_code` 重写的操作。

## 扫描脚本

```python
import re, os

base = "/mnt/d/sideline/ai/novel/{书名}/{卷名}/"

missing = []
for fname in sorted(os.listdir(base)):
    if not fname.endswith('.txt'):
        continue
    fpath = os.path.join(base, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Check for end marker
    if not re.search(r'\*第.*章·完', text):
        missing.append(fname)

if missing:
    print(f"❌ {len(missing)}章缺结束标记:")
    for m in missing:
        print(f"  {m}")
    
    # Fix: append end marker
    for fname in missing:
        ch_num = int(fname[1:4])
        fpath = os.path.join(base, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            text = f.read()
        text = text.rstrip() + f"\n\n*第{ch_num}章·完*\n"
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  ✅ {fname} 已补")
else:
    print("✅ 所有章节结束标记完整")
```

## 注意事项
- 弧线终章使用双格式标记（`*第X章·完 | 第X阶段「弧线名」终*`），但扫描时 `\*第.*章·完` 能匹配两种格式
- 补入时使用简单格式 `*第N章·完*`，弧线终章的完整标记在弧线收束章节中单独处理
- **不要**在补入标记后加多余空行——标记后一个 `\n` 即可

## 本会话记录
- 2026-05-19: 第二卷056/058/059/060/063/065章缺结束标记，批次分段拆分后遗漏

# WSL环境下字数统计的可靠模式

## 问题

在WSL环境下（特别是小说文件位于`/mnt/d/` Windows挂载路径时），`terminal`工具执行`wc -c`或Python脚本可能超时。这是WSL跨文件系统通信延迟导致的，不是文件损坏。

## 解决方案

使用`execute_code`工具运行Python，通过`hermes_tools`内部API读取文件：

```python
from hermes_tools import read_file
import re

# 读取章节文件
data = read_file('/mnt/d/sideline/ai/novel/中土纪元/第一卷/第059章_向南的调令.txt')
text = data['content']

# 方法A: 仅中文字符（会排除标点，用于快速筛查）
cn_only = len(re.findall(r'[\u4e00-\u9fff]', text))

# 方法B: 含标点总字符（更准确，减掉标题行约30字符）
total = len(re.sub(r'\s', '', text)) - 30

print(f'中文字数(仅汉字): {cn_only}')
print(f'含标点有效字数: {total}')
```

## 批量检查模式

检查整个弧线的章节字数：

```python
from hermes_tools import read_file
import re
import glob

for ch in range(start, end+1):
    files = glob.glob(f'/path/to/第{ch:03d}章_*.txt')
    if files:
        with open(files[0]) as f:
            text = f.read()
        cn = len(re.findall(r'[\u4e00-\u9fff]', text))
        status = 'OK' if cn >= 2000 else 'SHORT'
        print(f'第{ch:03d}章: {cn}字 [{status}]')
```

## 已废弃的方法

- `terminal` + `wc -c` — 在WSL /mnt/路径下经常超时，不可靠
- `terminal` + Python脚本 — 同样超时风险
- `execute_code` + `hermes_tools.read_file` — ✅ 当前唯一可靠方法

## 注意事项

- `hermes_tools.read_file` 返回的是dict，用`data['content']`取文本
- 路径必须是WSL格式：`/mnt/d/sideline/...` 而不是 `D:\sideline\...`
- 批量检查时用`glob.glob`比手动列文件名更可靠

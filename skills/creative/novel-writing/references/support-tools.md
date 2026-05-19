# 辅助工具栈 (Support Tools)

本小说项目配备的工具栈，覆盖 审计→导出→进度→追踪 完整链路。

## 工具清单

| 工具 | 文件 | 功能 | 用法示例 |
|:--|:--|:--|:--|
| 一键审计 | `scripts/audit.py` | 四维审计：CJK+格式+引号+元叙事+情感 | `python3 scripts/audit.py 211-250 --full` |
| HTML审计 | `tools/audit_html.py` | 生成可视化HTML审计报告（Chart.js趋势图+表格） | `python3 tools/audit_html.py 211-250` |
| 校对稿导出 | `tools/export_docx.py` | pandoc一键导出章节为.docx | `python3 tools/export_docx.py 211-220 --merge` |
| 进度看板 | `tools/progress.py` | 三种模式：终端/图表PNG/HTML看板 | `python3 tools/progress.py --html` |
| 物码追踪 | `tools/motifs.py` | 全书物码/人物/地点/阵营频率追踪+CSV导出 | `python3 tools/motifs.py --tag 三角标记` |
| 提交前检查 | `tools/pre-commit-check.sh` | git提交前自动扫描格式问题 | 自动运行（已安装git hook） |

## 工具详细说明

### audit_html.py — 增强HTML审计报告

生成包含交互式Chart.js趋势图的暗色主题HTML报告。每章显示CJK字数、破折号、ASCII直引号、引号平衡、角括号标记、元叙事检测。自动标注不达标章节（红色警告）。

```
python3 tools/audit_html.py 211-250                    # 默认输出到 tools/audit_211_250.html
python3 tools/audit_html.py 121-150 --output arc6       # 自定义输出名
python3 tools/audit_html.py 001-050 --volume 卷一       # 指定卷目录
```

### export_docx.py — 校对稿导出

使用pandoc将章节txt转换为Word文档，支持合并导出和单文件导出。输出到 `exports/` 目录。

```
python3 tools/export_docx.py 211-220                   # 逐章导出
python3 tools/export_docx.py 211-250 --merge            # 合并为一个docx
python3 tools/export_docx.py 001-050 --volume 卷一      # 指定卷
```

依赖：`pandoc`（命令行工具）、`python-docx`（合并功能需要）

### progress.py — 进度看板

全书进度全景视图，三种输出模式：

```
python3 tools/progress.py              # 终端彩色进度条
python3 tools/progress.py --chart      # PNG图表（matplotlib暗色主题）
python3 tools/progress.py --html       # HTML交互看板
```

依赖：`matplotlib`（--chart模式需要）

### motifs.py — 物码追踪器

追踪全书物码/人物/地点/阵营的出现频率和分布。预定义30+关键物码模式（三角标记、竹雷、灰瓷罐、桅灯、识字课、白马集等），分为物码/意象/人物/地点/阵营/食物六大类。

```
python3 tools/motifs.py                       # 全书TOP 15
python3 tools/motifs.py 211-250               # 指定范围
python3 tools/motifs.py --tag 三角标记        # 追踪单个标记
python3 tools/motifs.py --top 20              # 自定义TOP数量
python3 tools/motifs.py --export motifs.csv   # 导出CSV
```

依赖：无外部依赖（纯Python标准库，jieba可选增强）

## 注意事项

- 所有工具需从小说根目录运行，或使用绝对路径
- WSL环境下中文路径可能导致`terminal`工具block，使用 `cd 'path' && python3 tools/xxx.py` 模式
- HTML报告在浏览器中打开查看，Chart.js通过CDN加载
- 物码追踪器的关键词模式可根据项目具体物码体系扩展 `MOTIF_PATTERNS` 字典

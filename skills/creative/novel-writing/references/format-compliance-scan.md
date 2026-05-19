# Format Compliance Scan (格式合规扫描)

Run after every major editing session on the novel. This catches `|` artifacts, `\\和\\` patterns, extra backslashes, and meta-narrative `第X章` references.

## Final Verification (After All Fixes)

The user expects a zero-result scan. Run this comprehensive check:

```bash
cd /mnt/d/sideline/ai/novel/{书名}/{卷}/

echo "=== 1. Meta-narrative '第X章' in content ==="
count=0
for f in 第*.txt; do
  result=$(grep -n '第[0-9]\+章' "$f" | grep -v '^3:' | grep -v '^1:')
  if [ -n "$result" ]; then
    echo "❌ $f: $result"
    count=$((count+1))
  fi
done
echo "Files with '第X章' in content: $count"

echo "=== 2. | line numbers ==="
grep -rlc '^\s*[0-9]\+|' *.txt | head -5
echo "Files: $(grep -rlc '^\s*[0-9]\+|' *.txt | wc -l)"

echo "=== 3. \\和\\ pattern ==="
grep -rl '\\和\\' *.txt | wc -l && echo "files"

echo "=== 4. Duplicate phrases (from bad replacements) ==="
grep -nE '(最初在东海郡最初|云泽那段日子云泽|今天今天|明天明天|北岭.*北岭|老铁匠.*老铁匠)' *.txt

echo "=== 5. Word count gate ==="
python3 -c "
import re, os, glob
for f in sorted(glob.glob('第*.txt')):
    t = open(f).read()
    cn = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]', t))
    ok = '✅' if cn >= 2000 else f'❌ {cn}'
    print(f'{f}: {cn}字 {ok}')
"
```

## Quick Scan (bash)

```bash
cd /mnt/d/sideline/ai/novel/{书名}/{卷}/

# 1. Check for | line numbers
grep -rlc '^\s*[0-9]\+|' *.txt | wc -l && echo "files with | artifacts"

# 2. Check for \\和\\
grep -rl '\\和\\' *.txt | wc -l && echo "files with \\和\\"

# 3. Word count gate
for f in *.txt; do
  chars=$(python3 -c "import re;t=open('$f').read();c=len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf]',t));print(c)")
  [ "$chars" -lt 2000 ] && echo "❌ $f: $chars字" || echo "✅ $f: $chars字"
done
```

## Fix | Line Numbers (Python)

```python
import re, os

base = "/path/to/novel/卷"
for fname in os.listdir(base):
    if not fname.endswith('.txt'): continue
    path = os.path.join(base, fname)
    with open(path) as f: text = f.read()
    
    # Strip leading spaces+digits+| pattern
    lines = text.split('\n')
    cleaned = [re.sub(r'^\s+\d+\|\s*', '', line) for line in lines]
    
    with open(path, 'w') as f:
        f.write('\n'.join(cleaned))
    
    # Verify
    with open(path) as f:
        remaining = len(re.findall(r'^\s+\d+\|', f.read(), re.MULTILINE))
    print(f"{fname}: {'✅' if remaining == 0 else f'❌ {remaining} lines'}")
```

## Content Compliance Quick Check

After fixing format, verify content:
1. No system/superpower/cheat references (系统/空间/异能/金手指) — except "情报系统", "通讯系统", etc.
2. No internet slang (牛逼, 卧槽, 666, etc.)
3. Metaphor faction names are consistent (瀛烬/天衡盟/赤炬/玄朔/星火盟)
4. 无现代网络烂梗
5. "最开始设定" compliance: 无系统/超能力/金手指, 单人穿越, 灵械术, 灵晶等级

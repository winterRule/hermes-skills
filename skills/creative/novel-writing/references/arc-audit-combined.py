# Arc audit: combined CJK word count + outline keyword alignment
# Usage: modify 'base', 'chapters' dict, and 'keywords' dict per arc, then run with execute_code
import re, os

base = "/mnt/d/sideline/ai/novel/中土纪元/第二卷/"

# Map chapter number to expected title and outline keywords
chapters = {
    "061": {"title": "上江陷落", "keywords": ["上江城", "刘铁山", "机甲", "码头"]},
    "062": {"title": "暴行", "keywords": ["处决", "劳役", "碎瓦", "良民证"]},
    # Add all 10 chapters for the arc
}

total_cjk = 0
pass_count = 0
alignment_ok = 0

for ch_num, info in chapters.items():
    # Find file
    for f in os.listdir(base):
        if f.startswith(f"第{ch_num}章"):
            fpath = os.path.join(base, f)
            with open(fpath, 'r', encoding='utf-8') as fh:
                text = fh.read()
            break
    else:
        print(f"第{ch_num}章: ❌ 文件未找到")
        continue
    
    cjk = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_cjk += cjk
    word_ok = cjk >= 2000
    
    # Check keywords (fuzzy match)
    found = [kw for kw in info["keywords"] if kw in text]
    missing = [kw for kw in info["keywords"] if kw not in found]
    kw_ok = len(found) >= 3  # At least 3/4 keywords present
    
    if word_ok and kw_ok:
        pass_count += 1
    
    wflag = "✅" if word_ok else f"❌{cjk}"
    kflag = f"大纲:{len(found)}/{len(info['keywords'])}" + ("" if kw_ok else f" 缺:{','.join(missing)}")
    print(f"第{ch_num}章 {info['title']}: {cjk:>5}字 {wflag} | {kflag}")

print(f"\n{'='*50}")
print(f"通过: {pass_count}/{len(chapters)} | 总字数: {total_cjk:,} | 章均: {total_cjk//len(chapters):,}")
print(f"{'✅ 完成' if pass_count == len(chapters) else '❌ 待补'}")
print(f"\nKeyword matching is fuzzy: '舰队' = '战舰' in intent. 3/4 match = pass.")

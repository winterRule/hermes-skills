#!/usr/bin/env python3
"""
Semantic paragraph segmentation for Chinese novels.
Pipeline: pre-clean → sentence split → dialogue rules → semantic grouping → comma flow → mechanical split
"""

import re, sys, argparse, os
from collections import Counter

try:
    import jieba
    JIEBA_OK = True
except ImportError:
    JIEBA_OK = False

TEMPLATES = [
    (r'水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。暗河的水在远处无声地流着[，。]*', ''),
    (r'水伯的竹篙在渡口的石阶上又刻下了一道新的水位线。\n', ''),
    (r'水伯的竹篙上又多了一道湿痕。', ''),
    (r'暗河的水在远处无声地流着。从北岭发源.*?水位的变化在篙身上留着。', ''),
    (r'科目002运行到第.*?没有人把情报变成可用的分析。', ''),
    (r'这件事后来被陆辰记录在科目002.*?没有人把情报变成可用的分析。', ''),
    (r'苏大姐在磨盘前看到了这个符号.*?丁仓管无名，符号有主。', ''),
    (r'沦陷后的一周里.*?还活着的原因。', ''),
]

def pre_clean(text):
    for pattern, repl in TEMPLATES:
        text = re.sub(pattern, repl, text, flags=re.DOTALL)
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        s = line.strip()
        if not s: cleaned.append(line); continue
        sents = re.split(r'(?<=[。])', s)
        if len(sents) > 5:
            seen, unique, dup = {}, [], 0
            for sent in sents:
                sc = sent.strip()
                if not sc: continue
                sig = sc[:20]
                if sig not in seen: seen[sig]=1; unique.append(sent)
                else: dup += 1
            if dup >= 3: cleaned.append(''.join(unique)); continue
        cleaned.append(line)
    return '\n'.join(cleaned)

def split_sentences(text):
    sents = re.split(r'(?<=[。！？])', text)
    return [s.strip() for s in sents if s.strip()]

def apply_dialogue_rules(sentences):
    paragraphs = []
    i = 0
    while i < len(sentences):
        s = sentences[i]
        has_open = '\u201c' in s
        has_close = '\u201d' in s
        if has_open and has_close:
            paragraphs.append(s); i += 1
        elif has_open and not has_close:
            buf = [s]; i += 1
            while i < len(sentences):
                buf.append(sentences[i])
                if '\u201d' in sentences[i]: i += 1; break
                i += 1
            paragraphs.append(''.join(buf))
        else:
            paragraphs.append(s); i += 1
    return paragraphs

def jieba_keywords(text, topk=8):
    if not JIEBA_OK:
        chars = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        return set([w for w, _ in Counter(chars).most_common(topk)])
    words = jieba.lcut(text)
    words = [w for w in words if len(w) >= 2 and not w.isspace()]
    return set(w for w, _ in Counter(words).most_common(topk))

def semantic_group(sentences, target_paras=50):
    if len(sentences) <= target_paras:
        return sentences
    win = 4
    sims = []
    for i in range(len(sentences) - win):
        prev = ' '.join(sentences[i:i+win])
        nxt = ' '.join(sentences[i+1:i+1+win])
        kp = jieba_keywords(prev, 8)
        kn = jieba_keywords(nxt, 8)
        sim = len(kp & kn) / max(len(kp), len(kn)) if (kp and kn) else 0
        sims.append(sim)
    if not sims: return sentences
    deltas = [(i+win, sims[i-1]-sims[i]) for i in range(1, len(sims))]
    deltas.sort(key=lambda x: -x[1])
    n_splits = min(target_paras - 1, len(deltas), len(sentences) - 1)
    split_points = sorted(set(d[0] for d in deltas[:n_splits]))
    paragraphs = []; start = 0
    for b in split_points:
        if b > start and b < len(sentences):
            para = ''.join(sentences[start:b])
            if para.strip(): paragraphs.append(para)
            start = b
    para = ''.join(sentences[start:])
    if para.strip(): paragraphs.append(para)
    return paragraphs

def comma_flow_cleanup(paragraphs):
    cleaned = []
    for p in paragraphs:
        p = p.strip()
        if not p: continue
        last_punct = max(p.rfind('。'), p.rfind('！'), p.rfind('？'))
        if last_punct > 0:
            before = p[:last_punct]
            after = p[last_punct:]
            before = before.replace('。', '，')
            before = re.sub(r'，{2,}', '，', before)
            before = re.sub(r'，$', '', before)
            p = before + after
        cleaned.append(p)
    return cleaned

def split_long_paragraphs(paragraphs, max_cjk=80, target_paras=50):
    cjk_pat = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
    result = []
    for p in paragraphs:
        cjk_count = len(cjk_pat.findall(p))
        if cjk_count <= max_cjk:
            result.append(p); continue
        commas = [m.start() for m in re.finditer('，', p)]
        if len(commas) < 2:
            result.append(p); continue
        n_chunks = max(2, cjk_count // max_cjk + 1)
        chunk_size = max(1, len(commas) // n_chunks)
        start = 0
        for i in range(n_chunks):
            if i == n_chunks - 1:
                chunk = p[start:]
            else:
                end_idx = min((i+1)*chunk_size, len(commas)-1)
                end_pos = commas[end_idx]
                chunk = p[start:end_pos+1]
                start = end_pos + 1
            chunk = chunk.strip().rstrip('，')
            if chunk:
                if not chunk.endswith('。') and not chunk.endswith('！') and not chunk.endswith('？'):
                    chunk += '。'
                result.append(chunk)
    return result

def fix_quotes(text):
    """Robust quote fix: normalize all curly→ASCII, then state-machine back.
    Handles ASCII quotes AND pre-existing imbalanced curly quotes.
    Also patches unmatched opening quotes at end-of-file."""
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    chars = list(text); flip = True
    for i, c in enumerate(chars):
        if c == '"':
            chars[i] = '\u201c' if flip else '\u201d'
            flip = not flip
    text = ''.join(chars)
    # Handle unmatched opening quote at end-of-file
    left = text.count('\u201c')
    right = text.count('\u201d')
    if left > right:
        balance = 0; last_open = -1
        for i, c in enumerate(text):
            if c == '\u201c':
                if balance == 0: last_open = i
                balance += 1
            elif c == '\u201d':
                balance -= 1
        if last_open >= 0 and balance > 0:
            end_m = re.search(r'\n(\*第.*章·完)', text)
            if end_m:
                text = text[:end_m.start()].rstrip() + '\u201d\n\n' + text[end_m.start():]
            else:
                text = text.rstrip() + '\u201d\n'
    return text

def fix_dashes(text):
    return text.replace('\u2014\u2014', '，')

def semantic_segment(text, target_paras=50, max_cjk=80, title_line=None):
    text = pre_clean(text)
    text = fix_dashes(text)
    lines = text.split('\n')
    title = title_line or ''
    end_marker = ''
    content_lines = []
    if not title:
        for l in lines:
            s = l.strip()
            if s.startswith('第') and '章' in s[:8]: title = s; break
    for l in lines:
        s = l.strip()
        if not s: continue
        if s.startswith('*第') and '章·完' in s: end_marker = s; continue
        if s == title: continue
        content_lines.append(s)
    content = ' '.join(content_lines)
    sents = split_sentences(content)
    paras = apply_dialogue_rules(sents)
    paras = semantic_group(paras, target_paras)
    paras = comma_flow_cleanup(paras)
    paras = split_long_paragraphs(paras, max_cjk=max_cjk, target_paras=target_paras)
    paras = comma_flow_cleanup(paras)
    paras = [fix_quotes(p) for p in paras]
    output_lines = [title, '']
    for p in paras: output_lines.append(p); output_lines.append('')
    output_lines.append(end_marker); output_lines.append('')
    full_text = '\n'.join(output_lines)
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', full_text))
    stats = {
        'paragraphs': len(paras), 'cjk': cjk,
        'dashes': full_text.count('\u2014\u2014'),
        'ascii_quotes': full_text.count('"'),
        'quote_balance': full_text.count('\u201c') == full_text.count('\u201d'),
    }
    return full_text, stats

def main():
    p = argparse.ArgumentParser()
    p.add_argument('file'); p.add_argument('--target-paras', type=int, default=50)
    p.add_argument('--in-place', '-i', action='store_true'); p.add_argument('--verbose', '-v', action='store_true')
    p.add_argument('--max-cjk', type=int, default=80, help='Max CJK per paragraph before mechanical split (default: 80)')
    args = p.parse_args()
    with open(args.file, 'r') as f: text = f.read()
    result, stats = semantic_segment(text, target_paras=args.target_paras, max_cjk=args.max_cjk)
    if args.verbose:
        print("File:", args.file); print("Paragraphs:", stats['paragraphs'])
        print("CJK:", stats['cjk']); print("Dashes:", stats['dashes'])
        print("ASCII quotes:", stats['ascii_quotes'])
        print("Quote balance:", 'OK' if stats['quote_balance'] else 'FAIL')
    if args.in_place:
        with open(args.file, 'w') as f: f.write(result)
        print("OK: %s (%d paras, %d CJK)" % (os.path.basename(args.file), stats['paragraphs'], stats['cjk']))
    else:
        print(result)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Quick post-write verification + auto-fix for a single novel chapter.
Run immediately after every write_file or patch call.

Usage:
  python3 scripts/quick-verify.py <chapter_file>

Checks: CJK count, em-dashes, ASCII quotes, half-width punctuation, curly-quote balance, bytes
Auto-fixes: em-dashes → 逗号, ASCII quotes → state-machine Chinese curly quotes, half-width punctuation → full-width
Reports: PASS or FAIL with specific issues

Exit code: 0 if all checks pass, 1 if issues remain after auto-fix
"""
import re, sys

def quick_verify(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    original = text
    issues = []
    
    # 1. CJK count
    cjk = len(re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]', text))
    
    # 2. Em-dashes — auto-fix
    dashes = text.count('——')
    if dashes > 0:
        text = text.replace('——', '，')
        issues.append(f'dashes:{dashes}→0 (auto-fixed)')
    
    # 3. ASCII quotes (including escaped from patch tool) — auto-fix with state machine
    # First handle escaped quotes: \\" → remove backslash + convert quote
    esc_q = text.count('\\"')
    if esc_q > 0:
        text = text.replace('\\"', '"')
        issues.append(f'escaped_quotes:{esc_q}→0 (auto-fixed)')
    
    ascii_q = text.count('"')
    if ascii_q > 0:
        flip = True
        chars = list(text)
        for i, c in enumerate(chars):
            if c == '"':
                chars[i] = '\u201c' if flip else '\u201d'
                flip = not flip
        text = ''.join(chars)
        issues.append(f'ascii_quotes:{ascii_q}→0 (auto-fixed)')
    
    # 4. Half-width → full-width Chinese punctuation (ARC 15 validated)
    hw_fixes = 0
    # ASCII comma+space after CJK → ，
    new_text, n = re.subn(r'(?<=[\u4e00-\u9fff]), ', '\uff0c', text)
    hw_fixes += n; text = new_text
    # Remaining ASCII comma+space (after non-CJK too) → ，
    new_text, n = re.subn(r', ', '\uff0c', text)
    hw_fixes += n; text = new_text
    # ASCII colon+space after CJK → ：
    new_text, n = re.subn(r'(?<=[\u4e00-\u9fff]): ', '\uff1a', text)
    hw_fixes += n; text = new_text
    # ASCII semicolon after CJK → ；
    new_text, n = re.subn(r'(?<=[\u4e00-\u9fff]); ', '\uff1b', text)
    hw_fixes += n; text = new_text
    # Clean double punctuation from replacements
    text = re.sub(r'\uff0c\uff0c+', '\uff0c', text)
    text = re.sub(r'\u3002\u3002+', '\u3002', text)
    if hw_fixes > 0:
        issues.append(f'half_width_punct:{hw_fixes}→0 (auto-fixed)')
    
    # 5. Curly quote balance
    lq = text.count('\u201c')
    rq = text.count('\u201d')
    q_ok = lq == rq
    if not q_ok:
        issues.append(f'quote_balance: L={lq} R={rq}')
    
    # 6. Byte count
    byte_count = len(text.encode('utf-8'))
    
    # Write back if fixes were applied
    if text != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
    
    # Report
    ch_name = filepath.split('/')[-1].replace('.txt', '')
    cjk_ok = cjk >= 2000
    dash_ok = text.count('——') == 0
    ascii_ok = text.count('"') == 0
    
    all_ok = cjk_ok and dash_ok and ascii_ok and q_ok
    
    print(f"{ch_name}: CJK={cjk} | bytes={byte_count} | dashes={text.count('——')} | quotes({lq}/{rq})")
    if issues:
        print(f"  Fixed: {' | '.join(issues)}")
    
    if not cjk_ok:
        print(f"  ⚠️  CJK={cjk} < 2000 — EXPAND NEEDED (byte={byte_count})")
    if not q_ok:
        print(f"  ⚠️  Unbalanced quotes — manual fix needed")
    
    status = "✅ PASS" if all_ok else "❌ FAIL"
    print(f"  {status}")
    
    return all_ok

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/quick-verify.py <chapter_file>")
        sys.exit(1)
    ok = quick_verify(sys.argv[1])
    sys.exit(0 if ok else 1)

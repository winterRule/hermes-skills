#!/usr/bin/env python3
"""
Detect multi-speaker dialogue merged in single paragraph.
Algorithm:
  1. Find all "..." quote pairs in a paragraph
  2. Between a closing quote and the next opening quote, check for:
     a. A DIFFERENT speaker indicator (name + 说/问/道/写 etc.)
     b. Distance < 50 chars (close proximity = merge, not separate narration)
  3. Report: chapter, paragraph#, context, speakers involved
"""

import re, os, sys, argparse
from collections import defaultdict

# Speaker verbs
VERBS = r'(?:说道|回答|答道|喊道|叫道|骂道|吼道|念道|讲道|写道|问|说|喊|叫|骂|讲|念|写|答)'

# Pattern: a potential speaker before a verb
# Chinese name: 1-3 chars + verb
SPEAKER_RE = re.compile(r'([\u4e00-\u9fff]{1,3})\s*(' + VERBS + r')')

def find_multi_speaker_merges(text, max_distance=80):
    """
    Find paragraphs where different speakers' dialogue is merged.
    
    Returns list of (para_index, context, speakers, distance)
    """
    # Split into paragraphs
    raw_lines = text.split('\n')
    paragraphs = []
    for l in raw_lines:
        s = l.strip()
        if not s: continue
        if re.match(r'第[\u4e00-\u9fff\d]+章', s): continue
        if re.match(r'\*第.*章·完', s): continue
        paragraphs.append(s)
    
    issues = []
    
    for pi, p in enumerate(paragraphs):
        # Find all quote positions
        close_pos = [j for j, c in enumerate(p) if c == '\u201d']
        open_pos = [j for j, c in enumerate(p) if c == '\u201c']
        
        if len(close_pos) < 2:
            continue
        
        # For each pair of consecutive closing quotes
        for ci in range(len(close_pos) - 1):
            c1 = close_pos[ci]
            c2 = close_pos[ci + 1]
            between = p[c1:c2]
            distance = len(between)
            
            # Must have an opening quote between two closing quotes
            if '\u201c' not in between:
                continue
            
            # Skip if distance is too large (separate narrations)
            if distance > max_distance:
                continue
            
            # Find speaker indicators in the between text
            speakers = SPEAKER_RE.findall(between)
            if not speakers:
                continue
            
            # Filter: ignore if the "speaker" is just a term reference
            # e.g. "XX说" that refers to previously mentioned speech, not new dialogue
            # Check if there's an opening quote shortly before the speaker verb
            speaker_names = []
            for name, verb in speakers:
                # Get position of this speaker
                sp_match = re.search(re.escape(name) + r'\s*' + re.escape(verb), between)
                if sp_match:
                    sp_pos = sp_match.start()
                    # Check: is there an opening quote within 10 chars before this speaker?
                    before_speaker = between[max(0, sp_pos-10):sp_pos]
                    if '\u201c' in before_speaker:
                        speaker_names.append(f"{name}{verb}")
            
            if not speaker_names:
                continue
            
            # Extract context
            start = max(0, c1 - 20)
            end = min(len(p), c2 + 20)
            ctx = p[start:end]
            
            issues.append({
                'para': pi,
                'context': ctx,
                'speakers': speaker_names,
                'distance': distance
            })
    
    return issues, paragraphs


def scan_file(filepath, max_distance=80):
    """Scan a single file for multi-speaker merges."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    issues, paragraphs = find_multi_speaker_merges(text, max_distance)
    return issues


def scan_directory(directory, start_ch=121, end_ch=220, max_distance=80):
    """Scan a range of chapters in a directory."""
    all_issues = {}
    
    for ch in range(start_ch, end_ch + 1):
        found = False
        for f in os.listdir(directory):
            if f.startswith(f'第{ch}章_') and f.endswith('.txt'):
                filepath = os.path.join(directory, f)
                found = True
                break
        
        if not found:
            continue
        
        issues = scan_file(filepath, max_distance)
        if issues:
            all_issues[ch] = issues
    
    return all_issues


def main():
    parser = argparse.ArgumentParser(description='Detect multi-speaker dialogue merges')
    parser.add_argument('directory', help='Directory containing chapter files')
    parser.add_argument('--start', type=int, default=121, help='Start chapter')
    parser.add_argument('--end', type=int, default=220, help='End chapter')
    parser.add_argument('--max-distance', type=int, default=80, 
                        help='Max chars between closing and opening quote (default: 80)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all issues with context')
    
    args = parser.parse_args()
    
    issues = scan_directory(args.directory, args.start, args.end, args.max_distance)
    
    if not issues:
        print("✅ No multi-speaker dialogue merges found!")
        return 0
    
    total = sum(len(v) for v in issues.values())
    print(f"📊 Found {total} issue(s) in {len(issues)} chapter(s):\n")
    
    for ch in sorted(issues.keys()):
        ch_issues = issues[ch]
        print(f"第{ch}章 ({len(ch_issues)}处):")
        for i, iss in enumerate(ch_issues):
            if args.verbose or len(ch_issues) <= 3:
                ctx = iss['context'].replace('\n', ' ')
                if len(ctx) > 120:
                    ctx = ctx[:60] + '...' + ctx[-60:]
                sp = '+'.join(iss['speakers'])
                print(f"  段{iss['para']} 距离={iss['distance']}字 [{sp}]")
                print(f"    {ctx}")
        print()
    
    return len(issues)


if __name__ == '__main__':
    sys.exit(main())

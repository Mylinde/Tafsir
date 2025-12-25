#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script: Determines why verses are not detected
"""

import re
from pathlib import Path

def analyze_verse_patterns(txt_dir:  str, sura_num: int = 20):
    """Analyze verse patterns for a specific sura"""
    txt_path = Path(txt_dir)
    
    print("=" * 70)
    print(f"🔍 Analyzing verse patterns for Sura {sura_num}")
    print("=" * 70)
    
    # Load all files
    all_lines = []
    for txt_file in sorted(txt_path.glob("*. txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                all_lines.append((txt_file. name, line_num, line))
    
    # Find sura start
    in_sura = False
    verse_count = 0
    verse_examples = []
    
    for file_name, line_num, line in all_lines:
        # Check if we're in the sura
        if f"({sura_num})" in line and "Sura" in line: 
            in_sura = True
            print(f"\n✓ Sura {sura_num} found in {file_name}:{line_num}")
            continue
        
        # Check if we've reached the next sura
        if in_sura and re.match(r'^\((\d+)\)\s+Sura', line. strip()):
            next_sura = int(re.match(r'^\((\d+)\)', line.strip()).group(1))
            if next_sura != sura_num:
                print(f"\n→ Next sura {next_sura} reached")
                break
        
        # Search for verses
        if in_sura: 
            # Test different verse patterns
            patterns = [
                (r'^(\d+):(\d+)\s*-\s*', "Standard:  11:1 - "),
                (r'^(\d+):(\d+)\s+-\s+', "With spaces: 11:1 - "),
                (r'^(\d+):(\d+)\s*-', "Without trailing space: 11:1 -"),
                (r'^(\d+):(\d+)', "Number only: 11:1"),
                (r'(\d+):(\d+)\s*-', "Anywhere: 11:1 -"),
            ]
            
            for pattern, desc in patterns:
                match = re.search(pattern, line. strip())
                if match: 
                    v_sura = int(match.group(1))
                    v_num = int(match.group(2))
                    
                    if v_sura == sura_num and verse_count < 10:
                        verse_count += 1
                        verse_examples.append({
                            'file': file_name,
                            'line_num': line_num,
                            'verse':  f"{v_sura}:{v_num}",
                            'pattern': desc,
                            'text': line. strip()[:80] + "..."
                        })
                    break
    
    # Output
    print(f"\n📊 Found verses:   {verse_count}")
    print("\n📄 Examples:")
    print("-" * 70)
    
    for ex in verse_examples:
        print(f"\nVerse {ex['verse']}")
        print(f"  Pattern: {ex['pattern']}")
        print(f"  File:    {ex['file']}:{ex['line_num']}")
        print(f"  Text:    {ex['text']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python debug_verse_patterns.py <txt_dir> [sura_num]")
        print("Example:   python debug_verse_patterns. py . / tafsir-txt/ 11")
        sys.exit(1)
    
    txt_dir = sys.argv[1]
    sura_num = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    
    analyze_verse_patterns(txt_dir, sura_num)
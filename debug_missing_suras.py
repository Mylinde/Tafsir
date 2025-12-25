#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script: Determines why certain suras are not detected
"""

import re
from pathlib import Path

# Missing suras
MISSING_SURAS = [2, 3]

def find_sura_headers(txt_dir:  str):
    """Search for sura headers in the text files"""
    txt_path = Path(txt_dir)
    
    # Load all text files
    all_lines = []
    for txt_file in sorted(txt_path.glob("*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                all_lines.append((txt_file. name, line_num, line. strip()))
    
    print("=" * 70)
    print("🔍 Searching for sura headers for missing suras")
    print("=" * 70)
    
    # Test different regex patterns
    patterns = [
        (r'\((\d+)\)\s+Sura\s+([\w\s-]+? )\s+\((.*?)\)', "Standard pattern"),
        (r'\((\d+)\)\s*Sura\s+(.*?)\s+\((.*?)\)', "Flexible pattern"),
        (r'\((\d+)\).*?Sura', "Number + Sura only"),
        (r'^\((\d+)\)', "Number at start only"),
    ]
    
    for sura_num in MISSING_SURAS:
        print(f"\n📖 Sura {sura_num}:")
        print("-" * 70)
        
        found = False
        
        # Search in all lines
        for file_name, line_num, line in all_lines:
            # Simple search for the number
            if f"({sura_num})" in line and "Sura" in line: 
                print(f"   ✓ Found in:  {file_name}:{line_num}")
                print(f"   📄 Line: {line[: 100]}...")
                
                # Test all patterns
                for pattern, name in patterns:
                    match = re.search(pattern, line)
                    if match:
                        print(f"   ✅ Match with '{name}': {match.groups()}")
                    else:
                        print(f"   ❌ No match with '{name}'")
                
                found = True
                break
        
        if not found:
            print(f"   ❌ Not found!")

if __name__ == "__main__": 
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python debug_missing_suras.py <txt_dir>")
        print("Example: python debug_missing_suras.py ./tafsir-txt/")
        sys.exit(1)
    
    find_sura_headers(sys. argv[1])
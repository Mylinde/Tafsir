#!/usr/bin/env python3
"""
Test parse_verse_reference with a real line
"""

import re

def parse_verse_reference(line:  str):
    """Extract verse reference(s)."""
    # Pattern 1: verse range (e.g., 114:1-6 -)
    range_pattern = r'^(\d+):(\d+)-(\d+)\s*-\s*(. *)$'
    range_match = re.match(range_pattern, line. strip())
    
    if range_match:
        sura_num = int(range_match.group(1))
        verse_start = int(range_match.group(2))
        verse_end = int(range_match.group(3))
        remaining = range_match.group(4)
        
        verse_nums = list(range(verse_start, verse_end + 1))
        return (sura_num, verse_nums, remaining)
    
    # Pattern 2: single verse (e.g., 2:1 -)
    single_pattern = r'^(\d+):(\d+)\s*-\s*(.*)$'
    single_match = re.match(single_pattern, line.strip())
    
    if single_match:
        sura_num = int(single_match.group(1))
        verse_num = int(single_match.group(2))
        remaining = single_match.group(3)
        return (sura_num, [verse_num], remaining)
    
    return None

# Test with the real line from Sura 114
test_line = "114:1-6 - This last Sura of the Qur'an, one of the two so-called protective suras"

result = parse_verse_reference(test_line)

if result:
    sura_num, verse_nums, remaining = result
    print(f"✓ Successfully parsed:")
    print(f"  Sura: {sura_num}")
    print(f"  Verses: {verse_nums}")
    print(f"  Number of verses: {len(verse_nums)}")
    print(f"  Remaining: {remaining[:60]}...")
else:
    print("❌ Could not be parsed")
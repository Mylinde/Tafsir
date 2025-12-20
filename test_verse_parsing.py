#!/usr/bin/env python3
"""
Teste parse_verse_reference mit der echten Zeile
"""

import re

def parse_verse_reference(line:  str):
    """Extrahiere Vers-Referenz(en)."""
    # Pattern 1: Vers-Bereich (z.B. 114:1-6 -)
    range_pattern = r'^(\d+):(\d+)-(\d+)\s*-\s*(. *)$'
    range_match = re.match(range_pattern, line. strip())
    
    if range_match:
        sura_num = int(range_match.group(1))
        verse_start = int(range_match.group(2))
        verse_end = int(range_match.group(3))
        remaining = range_match.group(4)
        
        verse_nums = list(range(verse_start, verse_end + 1))
        return (sura_num, verse_nums, remaining)
    
    # Pattern 2: Einzelvers (z.B. 2: 1 -)
    single_pattern = r'^(\d+):(\d+)\s*-\s*(.*)$'
    single_match = re.match(single_pattern, line.strip())
    
    if single_match:
        sura_num = int(single_match.group(1))
        verse_num = int(single_match.group(2))
        remaining = single_match.group(3)
        return (sura_num, [verse_num], remaining)
    
    return None

# Teste mit der echten Zeile aus Sura 114
test_line = "114:1-6 - Diese letzte Sura des Qur'ān, eine der beiden sogenannten Schutz-Suren"

result = parse_verse_reference(test_line)

if result:
    sura_num, verse_nums, remaining = result
    print(f"✓ Erfolgreich geparst:")
    print(f"  Sura: {sura_num}")
    print(f"  Verse: {verse_nums}")
    print(f"  Anzahl Verse: {len(verse_nums)}")
    print(f"  Remaining: {remaining[: 60]}...")
else:
    print("❌ Konnte nicht geparst werden")

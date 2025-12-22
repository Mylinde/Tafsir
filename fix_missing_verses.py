#!/usr/bin/env python3
"""
Finds missing verses and adds them with tafsir
"""

import json
import re
from pathlib import Path

def find_verse_in_text(txt_dir, sura, verse):
    """Search for a verse in text files"""
    pattern = f"\\({sura}:{verse}\\)"
    
    for txt_file in sorted(Path(txt_dir).glob("*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                # Find corresponding tafsir
                # Search for a line that starts with SURA:VERSE-
                for j in range(i, min(i+20, len(lines))):
                    tafsir_match = re.match(f'^{sura}:{verse}[\\s-]', lines[j].strip())
                    if tafsir_match:
                        # Collect tafsir
                        tafsir_lines = []
                        for k in range(j, len(lines)):
                            if re.match(r'^\d+:\d+', lines[k].strip()):
                                break
                            tafsir_lines.append(lines[k])
                        
                        return '\n'.join(tafsir_lines).strip()
                
                # No specific tafsir - use generic
                return f"[Tafsir for verse {sura}:{verse} - see Qur'an text]"
    
    return None

# Test with Sura 67:12
txt_dir = "./tafsir-txt/"
result = find_verse_in_text(txt_dir, 67, 12)

if result:
    print(f"✓ Tafsir for 67:12 found:")
    print(result[:200])
else:
    print("❌ Not found")
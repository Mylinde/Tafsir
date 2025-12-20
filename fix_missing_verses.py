#!/usr/bin/env python3
"""
Findet fehlende Verse und fügt sie mit Tafsir hinzu
"""

import json
import re
from pathlib import Path

def find_verse_in_text(txt_dir, sura, verse):
    """Suche Vers in Textdateien"""
    pattern = f"\\({sura}:{verse}\\)"
    
    for txt_file in sorted(Path(txt_dir).glob("*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                # Finde zugehörigen Tafsir
                # Suche nach Zeile die mit SURA:VERS- beginnt
                for j in range(i, min(i+20, len(lines))):
                    tafsir_match = re.match(f'^{sura}:{verse}[\\s-]', lines[j]. strip())
                    if tafsir_match:
                        # Sammle Tafsir
                        tafsir_lines = []
                        for k in range(j, len(lines)):
                            if re.match(r'^\d+:\d+', lines[k]. strip()):
                                break
                            tafsir_lines.append(lines[k])
                        
                        return '\n'.join(tafsir_lines).strip()
                
                # Kein spezifischer Tafsir - verwende generischen
                return f"[Tafsir für Vers {sura}:{verse} - siehe Qur'an-Text]"
    
    return None

# Teste mit Sura 67:12
txt_dir = "./tafsir-txt/"
result = find_verse_in_text(txt_dir, 67, 12)

if result:
    print(f"✓ Tafsir für 67:12 gefunden:")
    print(result[: 200])
else:
    print("❌ Nicht gefunden")
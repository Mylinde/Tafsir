#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug-Script:  Findet heraus warum bestimmte Suren nicht erkannt werden
"""

import re
from pathlib import Path

# Fehlende Suren
MISSING_SURAS = [11, 12, 15, 20, 31, 34, 36, 38, 47, 50, 75, 86, 97, 99, 100, 
                 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]

def find_sura_headers(txt_dir:  str):
    """Suche nach Sura-Headern in den Textdateien"""
    txt_path = Path(txt_dir)
    
    # Lade alle Textdateien
    all_lines = []
    for txt_file in sorted(txt_path.glob("*.txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                all_lines.append((txt_file. name, line_num, line. strip()))
    
    print("=" * 70)
    print("🔍 Suche nach Sura-Headern für fehlende Suren")
    print("=" * 70)
    
    # Verschiedene Regex-Patterns testen
    patterns = [
        (r'\((\d+)\)\s+Sura\s+([\w\s-]+? )\s+\((.*?)\)', "Standard Pattern"),
        (r'\((\d+)\)\s*Sura\s+(.*?)\s+\((.*?)\)', "Flexibles Pattern"),
        (r'\((\d+)\).*?Sura', "Nur Nummer + Sura"),
        (r'^\((\d+)\)', "Nur Nummer am Anfang"),
    ]
    
    for sura_num in MISSING_SURAS:
        print(f"\n📖 Sura {sura_num}:")
        print("-" * 70)
        
        found = False
        
        # Suche in allen Zeilen
        for file_name, line_num, line in all_lines:
            # Einfache Suche nach der Nummer
            if f"({sura_num})" in line and "Sura" in line: 
                print(f"   ✓ Gefunden in:  {file_name}:{line_num}")
                print(f"   📄 Zeile: {line[: 100]}...")
                
                # Teste alle Patterns
                for pattern, name in patterns:
                    match = re.search(pattern, line)
                    if match:
                        print(f"   ✅ Match mit '{name}': {match.groups()}")
                    else:
                        print(f"   ❌ Kein Match mit '{name}'")
                
                found = True
                break
        
        if not found:
            print(f"   ❌ Nicht gefunden!")

if __name__ == "__main__": 
    import sys
    
    if len(sys.argv) < 2:
        print("Verwendung: python debug_missing_suras.py <txt_dir>")
        print("Beispiel: python debug_missing_suras.py ./tafsir-txt/")
        sys.exit(1)
    
    find_sura_headers(sys. argv[1])
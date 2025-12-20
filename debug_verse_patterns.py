#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug:  Findet heraus warum Verse nicht erkannt werden
"""

import re
from pathlib import Path

def analyze_verse_patterns(txt_dir:  str, sura_num: int = 11):
    """Analysiere Vers-Muster für eine bestimmte Sura"""
    txt_path = Path(txt_dir)
    
    print("=" * 70)
    print(f"🔍 Analyse der Vers-Muster für Sura {sura_num}")
    print("=" * 70)
    
    # Lade alle Dateien
    all_lines = []
    for txt_file in sorted(txt_path.glob("*. txt")):
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                all_lines.append((txt_file. name, line_num, line))
    
    # Finde Sura-Start
    in_sura = False
    verse_count = 0
    verse_examples = []
    
    for file_name, line_num, line in all_lines:
        # Prüfe ob wir in der Sura sind
        if f"({sura_num})" in line and "Sura" in line: 
            in_sura = True
            print(f"\n✓ Sura {sura_num} gefunden in {file_name}:{line_num}")
            continue
        
        # Prüfe ob wir die nächste Sura erreicht haben
        if in_sura and re.match(r'^\((\d+)\)\s+Sura', line. strip()):
            next_sura = int(re.match(r'^\((\d+)\)', line.strip()).group(1))
            if next_sura != sura_num:
                print(f"\n→ Nächste Sura {next_sura} erreicht")
                break
        
        # Suche nach Versen
        if in_sura: 
            # Verschiedene Vers-Patterns testen
            patterns = [
                (r'^(\d+):(\d+)\s*-\s*', "Standard:  11:1 - "),
                (r'^(\d+):(\d+)\s+-\s+', "Mit Leerzeichen: 11:1 - "),
                (r'^(\d+):(\d+)\s*-', "Ohne Trailing Space: 11:1 -"),
                (r'^(\d+):(\d+)', "Nur Nummer: 11:1"),
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
    
    # Ausgabe
    print(f"\n📊 Gefundene Verse:   {verse_count}")
    print("\n📄 Beispiele:")
    print("-" * 70)
    
    for ex in verse_examples:
        print(f"\nVers {ex['verse']}")
        print(f"  Pattern: {ex['pattern']}")
        print(f"  Datei:    {ex['file']}:{ex['line_num']}")
        print(f"  Text:    {ex['text']}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Verwendung: python debug_verse_patterns.py <txt_dir> [sura_num]")
        print("Beispiel:   python debug_verse_patterns. py . / tafsir-txt/ 11")
        sys.exit(1)
    
    txt_dir = sys.argv[1]
    sura_num = int(sys.argv[2]) if len(sys.argv) > 2 else 11
    
    analyze_verse_patterns(txt_dir, sura_num)
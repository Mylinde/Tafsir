#!/usr/bin/env python3
"""
Findet Sura 114 und zeigt ALLES
"""

from pathlib import Path
import re

txt_dir = Path("./tafsir-txt/")

print("=" * 70)
print("🔍 Suche nach Sura 114")
print("=" * 70)

# Suche nach (114)
for txt_file in sorted(txt_dir.glob("*.txt")):
    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "(114)" in line:
            print(f"\n✓ Gefunden in {txt_file.name}: Zeile {i+1}")
            print(f"  Zeile: '{line.strip()}'")
            
            # Zeige 20 Zeilen nach dieser Zeile
            print(f"\n  → Nächste 20 Zeilen:")
            for j in range(i+1, min(i+21, len(lines))):
                print(f"    {j+1:4d}: {lines[j].rstrip()}")
            
            # Suche nach Vers-Pattern in den nächsten 30 Zeilen
            print(f"\n  → Suche nach Vers-Referenzen:")
            for j in range(i+1, min(i+31, len(lines))):
                line_text = lines[j].strip()
                
                # Teste verschiedene Patterns
                if re.match(r'^\d+:\d+', line_text):
                    print(f"    ✓ Zeile {j+1}: {line_text[: 80]}")
            
            print("\n" + "=" * 70)
            break

#!/usr/bin/env python3
"""
Prüft was in tafsir-txt ist
"""

from pathlib import Path

txt_dir = Path("./tafsir-txt/")

print("=" * 70)
print("📂 Inhalt von ./tafsir-txt/")
print("=" * 70)

# Liste alle . txt Dateien
txt_files = sorted(txt_dir.glob("*.txt"))
print(f"\n✓ {len(txt_files)} .txt Dateien gefunden\n")

if len(txt_files) > 0:
    print("Erste 10 Dateien:")
    for f in txt_files[:10]: 
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:50s} ({size_kb: 6.1f} KB)")
    
    print("\nLetzte 10 Dateien:")
    for f in txt_files[-10:]:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:50s} ({size_kb:6.1f} KB)")
    
    # Suche in letzter Datei nach 114
    print(f"\n" + "=" * 70)
    print(f"🔍 Suche nach '114' in letzter Datei:  {txt_files[-1].name}")
    print("=" * 70)
    
    with open(txt_files[-1], 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"Datei hat {len(lines)} Zeilen\n")
        
        for i, line in enumerate(lines, 1):
            if "114" in line:
                print(f"Zeile {i}: {line.strip()}")
                
                # Zeige Kontext
                if i > 1:
                    print(f"  Vorher: {lines[i-2].strip()}")
                print(f"  DIESE:   {line.strip()}")
                if i < len(lines):
                    print(f"  Danach: {lines[i].strip()}")
                print()
else:
    print("❌ Keine .txt Dateien gefunden!")
    print(f"   Verzeichnis: {txt_dir. absolute()}")

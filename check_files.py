#!/usr/bin/env python3
"""
Checks what's in tafsir-txt
"""

from pathlib import Path

txt_dir = Path("./tafsir-txt/")

print("=" * 70)
print("📂 Contents of ./tafsir-txt/")
print("=" * 70)

# List all .txt files
txt_files = sorted(txt_dir.glob("*.txt"))
print(f"\n✓ {len(txt_files)} .txt files found\n")

if len(txt_files) > 0:
    print("First 10 files:")
    for f in txt_files[:10]: 
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:50s} ({size_kb: 6.1f} KB)")
    
    print("\nLast 10 files:")
    for f in txt_files[-10:]:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name:50s} ({size_kb:6.1f} KB)")
    
    # Search for '114' in last file
    print(f"\n" + "=" * 70)
    print(f"🔍 Searching for '114' in last file:  {txt_files[-1].name}")
    print("=" * 70)
    
    with open(txt_files[-1], 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"File has {len(lines)} lines\n")
        
        for i, line in enumerate(lines, 1):
            if "114" in line:
                print(f"Line {i}: {line.strip()}")
                
                # Show context
                if i > 1:
                    print(f"  Previous: {lines[i-2].strip()}")
                print(f"  CURRENT:   {line.strip()}")
                if i < len(lines):
                    print(f"  Next: {lines[i].strip()}")
                print()
else:
    print("❌ No .txt files found!")
    print(f"   Directory: {txt_dir. absolute()}")
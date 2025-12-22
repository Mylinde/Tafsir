#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tafsir JSON validation and repair
Checks and repairs the generated JSON files
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Expected verse count per sura (1-114)
VERSE_COUNTS = {
    1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109,
    11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135,
    21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60,
    31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85,
    41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45,
    51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13,
    61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44,
    71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42,
    81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20,
    91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11,
    101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3,
    111: 5, 112: 4, 113: 5, 114: 6
}

class TafsirValidator:
    def __init__(self, json_dir: str, txt_dir: str):
        self.json_dir = Path(json_dir)
        self.txt_dir = Path(txt_dir)
        
        self.missing_suras: List[int] = []
        self.missing_verses: Dict[int, List[int]] = defaultdict(list)
        self.suras_without_intro: List[int] = []
        self.issues: List[str] = []
        
    def validate_all(self):
        """Main validation function"""
        print("=" * 70)
        print("🔍 Tafsir JSON Validation")
        print("=" * 70)
        
        # 1. Check for missing suras
        print("\n1️⃣  Checking for missing suras...")
        self._check_missing_suras()
        
        # 2. Check for missing verses in existing suras
        print("\n2️⃣  Checking for missing verses in existing suras...")
        self._check_missing_verses()
        
        # 3. Check sura introductions in the first verse
        print("\n3️⃣  Checking sura introductions in the first verse...")
        self._check_sura_introductions()
        
        # 4. Show summary
        self._print_summary()
        
        return len(self.missing_suras) == 0 and len(self.missing_verses) == 0
    
    def _check_missing_suras(self):
        """Check which suras are missing"""
        existing_suras = set()
        
        for sura_num in range(1, 115):
            json_file = self.json_dir / f"de_tafsir_surah_{sura_num}.json"
            if json_file.exists():
                existing_suras.add(sura_num)
            else:
                self.missing_suras.append(sura_num)
        
        if self.missing_suras:
            print(f"   ❌ {len(self.missing_suras)} suras missing:")
            print(f"      {', '.join(map(str, self.missing_suras))}")
        else:
            print(f"   ✅ All 114 suras present!")
    
    def _check_missing_verses(self):
        """Check for missing verses in each sura"""
        total_missing = 0
        
        for sura_num in range(1, 115):
            json_file = self.json_dir / f"de_tafsir_surah_{sura_num}.json"
            
            if not json_file.exists():
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract existing verse numbers
                existing_verses = set()
                for entry in data: 
                    verse_key = entry.get('verse_key', '')
                    match = re.match(r'(\d+):(\d+)', verse_key)
                    if match:
                        existing_verses.add(int(match.group(2)))
                
                # Check which verses are missing
                expected_count = VERSE_COUNTS[sura_num]
                expected_verses = set(range(1, expected_count + 1))
                missing = sorted(expected_verses - existing_verses)
                
                if missing: 
                    self.missing_verses[sura_num] = missing
                    total_missing += len(missing)
                    print(f"   ⚠️  Sura {sura_num}:  {len(missing)} verses missing:  {missing[: 10]}{'...' if len(missing) > 10 else ''}")
                    
            except Exception as e:
                self.issues.append(f"Sura {sura_num}:  Error reading - {e}")
                print(f"   ❌ Sura {sura_num}: Error reading - {e}")
        
        if total_missing == 0 and not self.missing_suras:
            print(f"   ✅ All verses in all suras present!")
        else:
            print(f"\n   📊 Total:   {total_missing} missing verses in {len(self.missing_verses)} suras")
    
    def _check_sura_introductions(self):
        """Check if the first verse contains the sura introduction"""
        for sura_num in range(1, 115):
            json_file = self.json_dir / f"de_tafsir_surah_{sura_num}.json"
            
            if not json_file.exists():
                continue
            
            try: 
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not data: 
                    continue
                
                # Check first verse
                first_verse = data[0]
                text = first_verse.get('text', '')
                
                # Check if sura title is present
                if '<h2>Sura ' not in text:
                    self.suras_without_intro.append(sura_num)
                    print(f"   ⚠️  Sura {sura_num}: No sura introduction in the first verse")
                    
            except Exception as e:
                self.issues.append(f"Sura {sura_num}: Error checking introduction - {e}")
        
        if not self.suras_without_intro:
            print(f"   ✅ All suras have an introduction in the first verse!")
    
    def _print_summary(self):
        """Print summary"""
        print("\n" + "=" * 70)
        print("📋 SUMMARY")
        print("=" * 70)
        
        print(f"\n✅ Suras present: {114 - len(self.missing_suras)}/114")
        print(f"❌ Suras missing:   {len(self.missing_suras)}/114")
        
        total_expected = sum(VERSE_COUNTS.values())
        total_missing_verses = sum(len(v) for v in self.missing_verses.values())
        print(f"\n✅ Verses present: {total_expected - total_missing_verses}/{total_expected}")
        print(f"❌ Verses missing:  {total_missing_verses}/{total_expected}")
        
        print(f"\n⚠️  Suras without introduction: {len(self.suras_without_intro)}")
        
        if self.issues:
            print(f"\n❗ Other issues:  {len(self.issues)}")
            for issue in self.issues[: 5]: 
                print(f"   - {issue}")
    
    def generate_fix_report(self, output_file: str = "tafsir_fix_report.txt"):
        """Generate detailed repair report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("TAFSIR JSON VALIDATION REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Date: {Path(output_file).stat().st_mtime}\n\n")
            
            if self.missing_suras:
                f.write(f"MISSING SURAS ({len(self.missing_suras)}):\n")
                f.write("-" * 70 + "\n")
                for sura in self.missing_suras:
                    expected = VERSE_COUNTS[sura]
                    f.write(f"  Sura {sura: 3d}: {expected:3d} verses expected\n")
                f.write("\n")
            
            if self.missing_verses:
                f.write(f"MISSING VERSES ({len(self.missing_verses)} suras affected):\n")
                f.write("-" * 70 + "\n")
                for sura, verses in sorted(self.missing_verses.items()):
                    f.write(f"  Sura {sura:3d}: {len(verses):3d} verses missing\n")
                    f.write(f"           Verses:  {', '.join(map(str, verses))}\n")
                f.write("\n")
            
            if self.suras_without_intro:
                f.write(f"SURAS WITHOUT INTRODUCTION ({len(self.suras_without_intro)}):\n")
                f.write("-" * 70 + "\n")
                for sura in self.suras_without_intro:
                    f.write(f"  Sura {sura}\n")
                f.write("\n")
            
            if self.issues:
                f.write(f"OTHER ISSUES ({len(self.issues)}):\n")
                f.write("-" * 70 + "\n")
                for issue in self.issues:
                    f.write(f"  {issue}\n")
        
        print(f"\n💾 Detailed report saved:  {output_file}")


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python validate_and_fix_tafsir.py <json_dir> <txt_dir>")
        print("\nExample:")
        print("  python validate_and_fix_tafsir.py ./tafsir_json_output .  ")
        sys.exit(1)
    
    json_dir = sys.argv[1]
    txt_dir = sys.argv[2]
    
    validator = TafsirValidator(json_dir, txt_dir)
    is_valid = validator.validate_all()
    
    # Generate report
    validator.generate_fix_report()
    
    if is_valid: 
        print("\n✅ All checks passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Issues found.  See report for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
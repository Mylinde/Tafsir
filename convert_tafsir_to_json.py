#!/usr/bin/env python3
"""
Tafsir Al-Quran to JSON Converter - Version 2.0

Converts German Tafsir text files to JSON format for the QuranApp.
Uses a two-pass approach: 
  Pass 1: Collect explicit Tafsir blocks (verse references at line start)
  Pass 2: Collect inline verses (only if not already found in Pass 1)
Copyright (c) 2025 Mario Herrmann
Licensed under the MIT License (see LICENSE for details)
"""

import os
import sys
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TafsirConverter: 
    """Converts Tafsir text files to JSON format."""
    
    # Arabic diacritical marks and characters for text formatting
    ARABIC_DIACRITICS = "āīūḥṣḍṭẓ'ʿḤṢḌṬẒĀĪŪǧǦ"
    ARABIC_CHAR_CLASS = r'[A-ZĀĪŪḤṢḌṬẒǦa-zāīūḥṣḍṭẓǧ''ʿ-]+'
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copyright information
        self.copyright_info = {
            "author": "Muhammad Ibn Ahmad Ibn Rassoul",
            "publisher":  "IB Verlag Islamische Bibliothek",
            "edition": "41. Auflage",
            "title": "Tafsīr Al-Qur'ān Al-Karīm"
        }
        
    def find_text_files(self) -> List[Path]:
        """Find all tafsir_al_quran.txt_*. txt files."""
        files = sorted(self.input_dir.glob("*.txt"),
                      key=lambda x: int(x.stem.split('_')[-1]))
        print(f"Found {len(files)} text files")
        return files
    
    def read_all_content(self) -> str:
        """Read and combine all text files."""
        files = self.find_text_files()
        all_content = []
        
        for file_path in files:
            try: 
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    all_content.append(content)
            except Exception as e:
                print(f"Error reading {file_path}:  {e}")
        
        return '\n'.join(all_content)
    
    def format_text_to_html(self, text: str) -> str:
        """
        Convert text to HTML with proper formatting.
        - Qur'an quotes in quotation marks become <strong>
        - Arabic terms (with diacritics) become <em>
        - Paragraphs become <p>
        """
        # Split into paragraphs
        paragraphs = []
        lines = text.strip().split('\n')
        current_para = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and page numbers
            if not line or re.match(r'^\d+$', line):
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
            # Skip header lines
            elif line.startswith("Tafsīr Al-Qur'ān Al-Karīm"):
                continue
            else:
                current_para.append(line)
        
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        # Format each paragraph
        html_parts = []
        for para in paragraphs:
            # Format quoted text as <strong>
            para = re.sub(r'"([^"]+)"', r'<strong>"\1"</strong>', para)
            
            # Format Arabic terms with diacritics as <em>
            def replace_arabic(match):
                word = match.group(0)
                if any(c in word for c in self.ARABIC_DIACRITICS):
                    return f'<em>{word}</em>'
                return word
            
            para = re.sub(r'\b' + self.ARABIC_CHAR_CLASS + r'\b', replace_arabic, para)
            
            html_parts.append(f'<p>{para}</p>')
        
        return '\n'.join(html_parts)
    
    def parse_verse_reference(self, line: str) -> Optional[Tuple[int, List[int], str]]:
        """
        Extract verse reference at line start. 
        Only matches explicit Tafsir blocks, not references.
        
        Supports:
        - Single verses: 2:1 - Text
        - Verse ranges: 114:1-6 - Text
        - Verses with colon separator: 9:117:  Text
        - Verses in parentheses: (67:12) Text
        
        Returns:  (sura_num, [verse_nums], remaining_text) or None
        """
        line_stripped = line.strip()
        
        # Pattern 1: Verse range with dash separator
        # e.g.  "114:1-6 - Text"
        range_pattern = r'^(\d+):(\d+)-(\d+)\s*[-–]\s*(.+)$'
        range_match = re.match(range_pattern, line_stripped)
        
        if range_match: 
            sura_num = int(range_match.group(1))
            verse_start = int(range_match.group(2))
            verse_end = int(range_match.group(3))
            remaining = range_match.group(4)
            verse_nums = list(range(verse_start, verse_end + 1))
            return (sura_num, verse_nums, remaining)
        
        # Pattern 2: Single verse with dash separator
        # e.g.  "2:1 - Text" (flexible whitespace)
        single_with_dash = r'^(\d+):(\d+)\s*[-–]\s*(.+)$'
        single_match = re.match(single_with_dash, line_stripped)
        
        if single_match:
            sura_num = int(single_match. group(1))
            verse_num = int(single_match. group(2))
            remaining = single_match.group(3)
            return (sura_num, [verse_num], remaining)
        
        # Pattern 3: Single verse with colon separator
        # e.g. "9:117: vgl. unten die Geschichte"
        single_with_colon = r'^(\d+):(\d+):\s+(.+)$'
        colon_match = re.match(single_with_colon, line_stripped)
        
        if colon_match:
            sura_num = int(colon_match.group(1))
            verse_num = int(colon_match.group(2))
            remaining = colon_match.group(3)
            # Only if text is substantial (not just a reference)
            if len(remaining) > 20: 
                return (sura_num, [verse_num], remaining)
        
        # Pattern 4: Single verse in parentheses at line start
        # e.g.  "(67:12) Text"
        parenthesis_pattern = r'^\((\d+):(\d+)\)\s*(.*)$'
        paren_match = re.match(parenthesis_pattern, line_stripped)
        
        if paren_match:
            sura_num = int(paren_match.group(1))
            verse_num = int(paren_match.group(2))
            remaining = paren_match. group(3)
            return (sura_num, [verse_num], remaining)
        
        return None
    
    def extract_inline_verses(self, line:  str, current_sura_num: int) -> List[int]:
        """
        Extract ALL verse numbers in format (SURA: VERS) from a line.
        Only for the current Sura. 
        
        Returns: List of verse numbers
        """
        pattern = r'\((\d+):(\d+)\)'
        matches = re.findall(pattern, line)
        
        verses = []
        for sura_str, verse_str in matches:
            sura_num = int(sura_str)
            verse_num = int(verse_str)
            
            if sura_num == current_sura_num:
                verses. append(verse_num)
        
        return verses
    
    def process_content(self) -> Dict[int, Dict]: 
        """Process all content and extract Sura and verse data using two-pass approach."""
        content = self.read_all_content()
        lines = content.split('\n')
        
        print("\n" + "="*70)
        print("PASS 1: Extracting Sura metadata and explicit Tafsir blocks")
        print("="*70 + "\n")
        
        # Patterns for Sura headers
        sura_pattern_with_trans = r'^\((\d+)\)\s+Sura\s+(. +? )\s+\(([^\)]+)\)\.* $'
        sura_pattern_no_trans_dots = r'^\((\d+)\)\s+Sura\s+([^\.  ]+)\.{3}'
        sura_pattern_no_trans = r'^\((\d+)\)\s+Sura\s+([^\n\(]+)'
        
        location_pattern = r'^\(offenbart zu (Makka|Al-Madīna)\)'
        verses_pattern = r'^(\d+)\s+[AĀ].*?y.*?[aā].*?t'
        
        suras = {}
        current_sura = None
        
        # PASS 1: Collect Suras and explicit Tafsir blocks
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for Sura header
            sura_match = None
            has_translation = False
            
            sura_match = re.match(sura_pattern_with_trans, line)
            if sura_match:
                has_translation = True
            else:
                sura_match = re.match(sura_pattern_no_trans_dots, line)
                if not sura_match:
                    sura_match = re.match(sura_pattern_no_trans, line)
            
            if sura_match:
                sura_num = int(sura_match.group(1))
                
                if sura_num not in suras:
                    sura_name = sura_match.group(2).strip().rstrip('. ')
                    
                    if has_translation and len(sura_match.groups()) >= 3:
                        translation = sura_match.group(3).strip()
                    else:
                        translation = ""
                    
                    # Look ahead for location and verse count
                    location = "Unknown"
                    verse_count = 0
                    intro_start = i + 1
                    
                    for j in range(i + 1, min(i + 10, len(lines))):
                        loc_match = re.match(location_pattern, lines[j].strip())
                        if loc_match:
                            location = loc_match.group(1)
                        
                        vc_match = re.match(verses_pattern, lines[j].strip())
                        if vc_match:
                            verse_count = int(vc_match. group(1))
                            intro_start = j + 1
                            break
                    
                    # Collect introduction (text until first verse reference)
                    intro_lines = []
                    for j in range(intro_start, len(lines)):
                        if self.parse_verse_reference(lines[j].strip()):
                            break
                        intro_lines.append(lines[j])
                    
                    current_sura = {
                        'number': sura_num,
                        'name': sura_name,
                        'translation': translation,
                        'location': location,
                        'verse_count': verse_count,
                        'introduction': '\n'.join(intro_lines).strip(),
                        'verses': {}
                    }
                    suras[sura_num] = current_sura
                    
                    if translation:
                        print(f"Found Sura {sura_num}:  {sura_name} ({translation})")
                    else: 
                        print(f"Found Sura {sura_num}:  {sura_name}")
            
            # Check for explicit verse reference at line start
            verse_ref = self.parse_verse_reference(line)
            if verse_ref and current_sura:
                sura_n, verse_nums, remaining = verse_ref
                
                if sura_n == current_sura['number']: 
                    # Collect content until next verse or Sura
                    verse_content = [remaining] if remaining else []
                    
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        
                        # Stop at next verse
                        if self.parse_verse_reference(next_line):
                            break
                        
                        # Stop at new Sura
                        if re.match(sura_pattern_with_trans, next_line) or \
                           re.match(sura_pattern_no_trans_dots, next_line) or \
                           re.match(sura_pattern_no_trans, next_line):
                            break
                        
                        if next_line: 
                            verse_content.append(next_line)
                        
                        j += 1
                    
                    # Store for ALL verses in range
                    verse_text = '\n'.join(verse_content).strip()
                    for v_num in verse_nums:
                        verse_key = f"{current_sura['number']}:{v_num}"
                        current_sura['verses'][verse_key] = verse_text
                        print(f"  → Verse {verse_key} stored (explicit Tafsir)")
                else:
                    # Switch to new Sura
                    if sura_n in suras:
                        current_sura = suras[sura_n]
            
            i += 1
        
        # PASS 2: Collect inline verses (only if not already found)
        print("\n" + "="*70)
        print("PASS 2: Collecting inline verses")
        print("="*70 + "\n")
        
        current_sura = None
        i = 0
        
        while i < len(lines):
            line = lines[i]. strip()
            
            # Track current Sura
            sura_match = re.match(sura_pattern_with_trans, line) or \
                        re.match(sura_pattern_no_trans_dots, line) or \
                        re. match(sura_pattern_no_trans, line)
            
            if sura_match: 
                sura_num = int(sura_match.group(1))
                if sura_num in suras:
                    current_sura = suras[sura_num]
            
            # Check for inline verses
            if current_sura: 
                inline_verses = self.extract_inline_verses(line, current_sura['number'])
                
                if inline_verses:
                    # Search for Tafsir block in next lines
                    tafsir_found = False
                    
                    for j in range(i, min(i + 30, len(lines))):
                        next_line = lines[j].strip()
                        
                        # Search for Tafsir pattern:  SURA:VERS-VERS or SURA:VERS
                        for verse_num in inline_verses:
                            tafsir_patterns = [
                                rf'^{current_sura["number"]}:{verse_num}-\d+\s*-',
                                rf'^{current_sura["number"]}:{verse_num}\s*-',
                            ]
                            
                            for tafsir_pattern in tafsir_patterns:
                                if re.match(tafsir_pattern, next_line):
                                    # Found Tafsir!  Collect until next verse
                                    tafsir_content = []
                                    for k in range(j, len(lines)):
                                        # Stop at next verse block
                                        if k > j and re.match(r'^\d+:\d+', lines[k]. strip()):
                                            break
                                        tafsir_content.append(lines[k])
                                    
                                    tafsir_text = '\n'.join(tafsir_content).strip()
                                    
                                    # Store for ALL inline verses (only if not already present)
                                    for v_num in inline_verses:
                                        verse_key = f"{current_sura['number']}:{v_num}"
                                        if verse_key not in current_sura['verses']:
                                            current_sura['verses'][verse_key] = tafsir_text
                                            print(f"  → Inline verse {verse_key} stored (with Tafsir)")
                                    
                                    tafsir_found = True
                                    break
                            
                            if tafsir_found:
                                break
                        
                        if tafsir_found: 
                            break
                    
                    # No specific Tafsir found - use context
                    if not tafsir_found:
                        context_lines = []
                        for j in range(max(0, i-1), min(i+5, len(lines))):
                            if lines[j].strip():
                                context_lines.append(lines[j])
                        
                        context_text = '\n'.join(context_lines).strip()
                        
                        for v_num in inline_verses: 
                            verse_key = f"{current_sura['number']}:{v_num}"
                            if verse_key not in current_sura['verses']:
                                current_sura['verses'][verse_key] = context_text
                                print(f"  → Inline verse {verse_key} stored (with context)")
            
            i += 1
        
        return suras
    
    def generate_json_output(self, suras:  Dict[int, Dict]):
        """Generate JSON output files."""
        all_verses = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for sura_num in sorted(suras.keys()):
            sura = suras[sura_num]
            sura_verses = []
            
            verse_keys = sorted(sura['verses'].keys(),
                              key=lambda x:  int(x.split(':')[1]))
            
            print(f"\n→ Sura {sura_num}:  {len(verse_keys)} verses found")
            
            for idx, verse_key in enumerate(verse_keys):
                verse_text = sura['verses'][verse_key]
                
                # For first verse, include Sura introduction
                if idx == 0:
                    if sura['translation']:
                        header = f"<h2>Sura {sura['name']} ({sura['translation']})</h2>"
                    else:
                        header = f"<h2>Sura {sura['name']}</h2>"
                    
                    location = f"<p><em>(offenbart zu {sura['location']})</em></p>"
                    vc = f"<p><em>{sura['verse_count']} Āyāt</em></p>"
                    intro_html = self.format_text_to_html(sura['introduction'])
                    verse_html = self.format_text_to_html(verse_text)
                    #full_text = f"{header}\n{location}\n{vc}\n{intro_html}\n{verse_html}"
                    full_text = f"{header}\n{location}\n{vc}\n{verse_html}"
                else: 
                    full_text = self.format_text_to_html(verse_text)
                
                verse_entry = {
                    "key": "de_tafsir-al-quran-al-karim",
                    "verse_key": verse_key,
                    "verses": [verse_key],
                    "text": full_text,
                    "timestamp": timestamp,
                    "version": "1.0",
                    "copyright": self.copyright_info
                }
                
                sura_verses.append(verse_entry)
                all_verses.append(verse_entry)
            
            # Write individual Sura file
            if sura_verses:
                sura_file = self.output_dir / f"de_tafsir_surah_{sura_num}.json"
                with open(sura_file, 'w', encoding='utf-8') as f:
                    json.dump(sura_verses, f, ensure_ascii=False, indent=2)
                
                print(f"Created {sura_file. name} with {len(sura_verses)} verses")
        
        # Write complete file with metadata
        complete_data = {
            "metadata": {
                "key": "de_tafsir-al-quran",
                "name": "Tafsīr Al-Qur'ān Al-Karīm (German)",
                "author": self.copyright_info['author'],
                "publisher": self.copyright_info['publisher'],
                "version": "1.0",
                "timestamp": timestamp,
                "total_verses": len(all_verses),
                "total_suras": len(suras)
            },
            "verses": all_verses
        }
        
        complete_file = self.output_dir / "de_tafsir_complete.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nCreated {complete_file.name} with {len(all_verses)} total verses")
        print(f"Processed {len(suras)} Suras")


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python3 convert_tafsir_to_json.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    
    print(f"Starting Tafsir conversion...")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print()
    
    converter = TafsirConverter(input_dir, output_dir)
    suras = converter.process_content()
    converter.generate_json_output(suras)
    
    print("\n" + "="*70)
    print("Conversion completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
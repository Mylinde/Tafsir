#!/usr/bin/env python3
"""
Tafsir Al-Quran to JSON Converter

Converts German Tafsir text files to JSON format for the QuranApp. 
Supports both single verses (2:1) and verse ranges (114:1-6).

Author: Muhammad Ibn Ahmad Ibn Rassoul
Publisher: IB Verlag Islamische Bibliothek
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
            "publisher": "IB Verlag Islamische Bibliothek",
            "edition": "41.  Auflage",
            "title": "Tafsīr Al-Qur'ān Al-Karīm"
        }
        
    def find_text_files(self) -> List[Path]:
        """Find all tafsir_al_quran.txt_*. txt files."""
        files = sorted(self.input_dir.glob("tafsir_al_quran.txt_*.txt"), 
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
            # Match words containing Arabic diacritical marks
            def replace_arabic(match):
                word = match.group(0)
                if any(c in word for c in self.ARABIC_DIACRITICS):
                    return f'<em>{word}</em>'
                return word
            
            para = re.sub(r'\b' + self.ARABIC_CHAR_CLASS + r'\b', replace_arabic, para)
            
            html_parts.append(f'<p>{para}</p>')
        
        return '\n'. join(html_parts)
    
    def parse_verse_reference(self, line: str) -> Optional[Tuple[int, List[int], str]]:
        """
        Extrahiere Vers-Referenz(en).
        Unterstützt: 
        - Einzelverse:  2:1 -
        - Bereiche: 114:1-6 -
        
        Returns:  (sura_num, [verse_nums], remaining_text) oder None
        """
        # Pattern 1: Vers-Bereich (z.B. 114:1-6 -)
        range_pattern = r'^(\d+):(\d+)-(\d+)\s*-\s*(. *)$'
        range_match = re.match(range_pattern, line.strip())
        
        if range_match:
            sura_num = int(range_match.group(1))
            verse_start = int(range_match.group(2))
            verse_end = int(range_match.group(3))
            remaining = range_match.group(4)
            
            # Expandiere den Bereich
            verse_nums = list(range(verse_start, verse_end + 1))
            return (sura_num, verse_nums, remaining)
        
        # Pattern 2: Einzelvers (z.B. 2:1 -)
        single_pattern = r'^(\d+):(\d+)\s*-\s*(.*)$'
        single_match = re.match(single_pattern, line.strip())
        
        if single_match: 
            sura_num = int(single_match.group(1))
            verse_num = int(single_match.group(2))
            remaining = single_match. group(3)
            return (sura_num, [verse_num], remaining)
        
        return None
    
    def process_content(self) -> Dict[int, Dict]:
        """Process all content and extract Sura and verse data."""
        content = self.read_all_content()
        lines = content.split('\n')
        
        # Patterns für Sura-Header - OPTIMIERT
        # Pattern 1: Mit deutscher Übersetzung:  (75) Sura Al-Qiyāma (Die Auferstehung)...
        sura_pattern_with_trans = r'^\((\d+)\)\s+Sura\s+(. +? )\s+\(([^\)]+)\)\. {3}'
        # Pattern 2: Ohne Übersetzung mit .. .: (11) Sura Hūd... 
        sura_pattern_no_trans_dots = r'^\((\d+)\)\s+Sura\s+([^\.]+)\.{3}'
        # Pattern 3: Fallback ohne .. .: (11) Sura Hūd
        sura_pattern_no_trans = r'^\((\d+)\)\s+Sura\s+([^\n\(]+)'
        
        location_pattern = r'^\(offenbart zu (Makka|Al-Madīna)\)'
        verses_pattern = r'^(\d+)\s+Āyāt'
        
        suras = {}
        current_sura = None
        current_verses = None  # Liste von Vers-Nummern für aktuellen Eintrag
        verse_content = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for Sura header
            sura_match = None
            has_translation = False
            
            # Versuch 1: Mit Übersetzung und ... 
            sura_match = re.match(sura_pattern_with_trans, line)
            if sura_match:
                has_translation = True
            else:
                # Versuch 2: Ohne Übersetzung mit ... 
                sura_match = re.match(sura_pattern_no_trans_dots, line)
                if not sura_match:
                    # Versuch 3: Ohne Übersetzung ohne ...
                    sura_match = re.match(sura_pattern_no_trans, line)
            
            if sura_match: 
                sura_num = int(sura_match.group(1))
                
                # Only process if we haven't seen this Sura before
                if sura_num not in suras: 
                    sura_name = sura_match.group(2).strip()
                    # Entferne "..." und Leerzeichen am Ende
                    sura_name = sura_name.rstrip('. ')
                    
                    # Deutsche Übersetzung nur wenn vorhanden
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
                        if self.parse_verse_reference(lines[j]. strip()):
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
                    
                    # Ausgabe
                    if translation:
                        print(f"Found Sura {sura_num}:  {sura_name} ({translation})")
                    else: 
                        print(f"Found Sura {sura_num}: {sura_name}")
            
            # Check for verse reference (Einzelvers oder Bereich)
            verse_ref = self.parse_verse_reference(line)
            if verse_ref and current_sura:
                sura_n, verse_nums, remaining = verse_ref
                
                # Only process if it belongs to current Sura
                if sura_n == current_sura['number']:
                    # Save previous verse(s) if exists
                    if current_verses and verse_content:
                        verse_text = '\n'.join(verse_content).strip()
                        # Speichere für jeden Vers im Bereich
                        for v_num in current_verses:
                            verse_key = f"{current_sura['number']}:{v_num}"
                            current_sura['verses'][verse_key] = verse_text
                    
                    # Start new verse(s)
                    current_verses = verse_nums
                    verse_content = [remaining] if remaining else []
                else:
                    # We've moved to a new Sura
                    if sura_n in suras:
                        # Save previous verse(s) first
                        if current_verses and verse_content and current_sura: 
                            verse_text = '\n'.join(verse_content).strip()
                            for v_num in current_verses:
                                verse_key = f"{current_sura['number']}:{v_num}"
                                current_sura['verses'][verse_key] = verse_text
                        
                        current_sura = suras[sura_n]
                        current_verses = verse_nums
                        verse_content = [remaining] if remaining else []
            elif current_verses and line:
                # Continue collecting verse content
                verse_content.append(line)
            
            i += 1
        
        # Save last verse(s)
        if current_verses and verse_content and current_sura: 
            verse_text = '\n'.join(verse_content).strip()
            for v_num in current_verses:
                verse_key = f"{current_sura['number']}:{v_num}"
                current_sura['verses'][verse_key] = verse_text
        
        return suras
    
    def generate_json_output(self, suras: Dict[int, Dict]):
        """Generate JSON output files."""
        all_verses = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for sura_num in sorted(suras.keys()):
            sura = suras[sura_num]
            sura_verses = []
            
            verse_keys = sorted(sura['verses']. keys(), 
                              key=lambda x:  int(x.split(':')[1]))
            
            for idx, verse_key in enumerate(verse_keys):
                verse_text = sura['verses'][verse_key]
                
                # For first verse, include Sura introduction
                if idx == 0:
                    # Header mit oder ohne deutsche Übersetzung
                    if sura['translation']:
                        header = f"<h2>Sura {sura['name']} ({sura['translation']})</h2>"
                    else:
                        header = f"<h2>Sura {sura['name']}</h2>"
                    
                    location = f"<p><em>(offenbart zu {sura['location']})</em></p>"
                    vc = f"<p><em>{sura['verse_count']} Āyāt</em></p>"
                    intro_html = self.format_text_to_html(sura['introduction'])
                    verse_html = self.format_text_to_html(verse_text)
                    full_text = f"{header}\n{location}\n{vc}\n{intro_html}\n{verse_html}"
                else:
                    full_text = self.format_text_to_html(verse_text)
                
                verse_entry = {
                    "key": "de_tafsir-al-azhar",
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
                "key": "de_tafsir-al-azhar",
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
        print("Example: python3 convert_tafsir_to_json. py .  tafsir_json_output")
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
    
    print("\nConversion completed successfully!")


if __name__ == "__main__":
    main()
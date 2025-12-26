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
        files = sorted(self.input_dir.glob("pg_*.txt"),
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
        """Minimal HTML conversion (paragraph splitting). Removes 'Ende der Sura XXX' and page numbers."""
        import re
        # Remove lines like 'Ende der Sura XXX'
        text = re.sub(r'^Ende der Sura\s+\d+\s*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # Remove lines that are only page numbers (e.g. '123', '12', etc.)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        paras = []
        buf = []
        for l in lines:
            if not l:
                if buf:
                    paras.append(" ".join(buf).strip())
                    buf = []
            else:
                buf.append(l)
        if buf:
            paras.append(" ".join(buf).strip())
        html = "\n".join(f"<p>{p}</p>" for p in paras)
        return html
    
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

        # Pattern 1b: Verse range without dash separator (e.g. "114:1-6 Text")
        range_pattern_nodash = r'^(\d+):(\d+)-(\d+)\s+(.+)$'
        range_match_nodash = re.match(range_pattern_nodash, line_stripped)

        if range_match_nodash:
            sura_num = int(range_match_nodash.group(1))
            verse_start = int(range_match_nodash.group(2))
            verse_end = int(range_match_nodash.group(3))
            remaining = range_match_nodash.group(4)
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
        """Parse combined text and build sura -> verses mapping."""
        import re
        text = self.read_all_content()
        lines = text.splitlines()

        # Robustes Pattern für Sura-Header mit optionaler Übersetzung
        sura_header_regex = re.compile(
            r'^\((\d{1,3})\)\s*(?:Sura\s*)?([^\(]+?)(?:\s*\(([^)]+)\))?\s*$', re.IGNORECASE
        )
        sura_number_only = re.compile(r'^\((\d{1,3})\)\s*$')
        location_pattern = re.compile(r'^\(offenbart zu (Makka|Al-Madīna)\)', re.IGNORECASE)
        verses_pattern = re.compile(r'^(\d+)\s+[AĀa].*?y.*?[aā]')
        end_of_sura_pattern = re.compile(r'^Ende der Sura\s+\d+', re.IGNORECASE)
        explicit_verse_ref_pattern = re.compile(r'^\d{1,3}:\d{1,3}([\-–—]\d{1,3})?\b')

        suras: Dict[int, Dict] = {}
        current_sura_num: Optional[int] = None
        current_buffer: List[str] = []
        current_verse_list: List[int] = []

        def flush_current():
            nonlocal current_buffer, current_verse_list, current_sura_num
            if current_sura_num is None or not current_verse_list:
                current_buffer = []
                current_verse_list = []
                return
            text_blob = "\n".join(current_buffer).strip()
            if not text_blob:
                current_buffer = []
                current_verse_list = []
                return
            html = self.format_text_to_html(text_blob)
            sura_obj = suras.setdefault(current_sura_num, {
                "number": current_sura_num,
                "name": "",
                "translation": "",
                "location": "",
                "verse_count": 0,
                "introduction": "",
                "verses": {}
            })
            for v in current_verse_list:
                if v not in sura_obj["verses"]:
                    sura_obj["verses"][v] = html
            current_buffer = []
            current_verse_list = []

        i = 0
        while i < len(lines):
            raw = lines[i]
            line = raw.strip()

            # Sura-Header mit optionaler Übersetzung
            mh = sura_header_regex.match(line)
            if mh:
                flush_current()
                current_sura_num = int(mh.group(1))
                name = (mh.group(2) or "").strip().rstrip('.')
                trans = (mh.group(3) or "").strip()
                loc = "Unknown"
                vc = 0
                intro_start = i + 1
                for j in range(i + 1, min(i + 12, len(lines))):
                    lm = location_pattern.match(lines[j].strip())
                    if lm:
                        loc = lm.group(1)
                    vm = verses_pattern.match(lines[j].strip())
                    if vm:
                        try:
                            vc = int(vm.group(1))
                        except Exception:
                            vc = 0
                        intro_start = j + 1
                        break
                suras.setdefault(current_sura_num, {
                    "number": current_sura_num,
                    "name": name,
                    "translation": trans,
                    "location": loc,
                    "verse_count": vc,
                    "introduction": "",
                    "verses": {}
                })
                intro_lines = []
                for j in range(intro_start, len(lines)):
                    if self.parse_verse_reference(lines[j].strip()):
                        break
                    intro_lines.append(lines[j])
                suras[current_sura_num]["introduction"] = "\n".join(l.strip() for l in intro_lines).strip()
                i = max(i, intro_start - 1)
                i += 1
                continue

            # Nur Sura-Nummer
            mn = sura_number_only.match(line)
            if mn:
                flush_current()
                current_sura_num = int(mn.group(1))
                name = ""
                trans = ""
                intro_start = i + 1
                for j in range(i + 1, min(i + 8, len(lines))):
                    nline = lines[j].strip()
                    m2 = sura_header_regex.match(nline)
                    if m2:
                        name = (m2.group(2) or "").strip().rstrip('.')
                        trans = (m2.group(3) or "").strip()
                        intro_start = j + 1
                        break
                    m3 = re.match(r'^[Ss]ura\s+(.+?)(?:\s*\(([^)]+)\))?\s*$', nline)
                    if m3:
                        name = m3.group(1).strip().rstrip('.')
                        trans = (m3.group(2) or "").strip()
                        intro_start = j + 1
                        break
                loc = "Unknown"
                vc = 0
                for j in range(intro_start, min(i + 14, len(lines))):
                    lm = location_pattern.match(lines[j].strip())
                    if lm:
                        loc = lm.group(1)
                    vm = verses_pattern.match(lines[j].strip())
                    if vm:
                        try:
                            vc = int(vm.group(1))
                        except Exception:
                            vc = 0
                        intro_start = j + 1
                        break
                suras.setdefault(current_sura_num, {
                    "number": current_sura_num,
                    "name": name,
                    "translation": trans,
                    "location": loc,
                    "verse_count": vc,
                    "introduction": "",
                    "verses": {}
                })
                intro_lines = []
                for j in range(intro_start, len(lines)):
                    if self.parse_verse_reference(lines[j].strip()):
                        break
                    intro_lines.append(lines[j])
                suras[current_sura_num]["introduction"] = "\n".join(l.strip() for l in intro_lines).strip()
                i = max(i, intro_start - 1)
                i += 1
                continue

            # Ende der Sura
            if end_of_sura_pattern.match(line):
                flush_current()
                current_verse_list = []
                current_buffer = []
                i += 1
                continue

            # Explizite Versreferenz am Zeilenanfang
            if explicit_verse_ref_pattern.match(line):
                flush_current()
                pv = self.parse_verse_reference(line)
                if pv:
                    sura_num, verses, trailing = pv
                    if current_sura_num is None:
                        current_sura_num = sura_num
                    current_verse_list = verses
                    current_buffer = []
                    if trailing:
                        current_buffer.append(trailing)
                    k = i + 1
                    while k < len(lines):
                        next_line = lines[k].strip()
                        if self.parse_verse_reference(next_line):
                            break
                        if sura_header_regex.match(next_line):
                            break
                        if end_of_sura_pattern.match(next_line):
                            break
                        current_buffer.append(lines[k])
                        k += 1
                    flush_current()
                    i = k
                    continue

            # Sonst: Text ggf. zum aktuellen Vers sammeln
            if current_verse_list:
                current_buffer.append(raw)
            i += 1

        flush_current()
        return suras
    
    def generate_json_output(self, suras:  Dict[int, Dict]):
        """Generate JSON output files."""
        all_verses = []
        timestamp = datetime.now(timezone.utc).isoformat()
        
        for sura_num in sorted(suras.keys()):
            sura = suras[sura_num]
            sura_verses = []
            
            def verse_key_sorter(x):
                if isinstance(x, int):
                    return x
                if isinstance(x, str) and ':' in x:
                    return int(x.split(':')[1])
                try:
                    return int(x)
                except Exception:
                    return 0

            verse_keys = sorted(sura['verses'].keys(), key=verse_key_sorter)
            
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
                    full_text = f"{header}\n{location}\n{vc}\n{intro_html}\n{verse_html}"
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
    
    print("\n" + "="*70)
    print("Conversion completed successfully!")
    print("="*70)


if __name__ == "__main__":
    main()
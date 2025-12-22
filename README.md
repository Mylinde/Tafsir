# Tafsīr Al-Qur'ān Al-Karīm - JSON Converter

This repository contains an automated conversion system that transforms the German tafsir text files (Qur'an commentaries) into JSON format for Qur'an applications.

## About the Work

**Title:** Tafsīr Al-Qur'ān Al-Karīm  
**Author:** Abū-r-Riḍā' Muhammad Ibn Ahmad Ibn Rassoul  
**Publisher:** IB Verlag Islamische Bibliothek  
**Edition:** 41st revised and expanded edition

### Copyright & Source

Reproduction, reprinting, and translation of this work into a foreign language are permitted provided that this source is cited.

Source: IB Verlag Islamische Bibliothek

PDF source: [Tafsīr Al-Qur'ān PDF](https://islamicbulletin.org/de/ebooks/koran/tafsir_al_quran.pdf?vQE5lZNHW=Qry1o4CiDDubD)

## Automatic Conversion

### With GitHub Actions

The easiest way to generate the JSON files:

1. Go to **Actions** → **Convert Tafsir to JSON**
2. Click **Run workflow**
3. Optional: Enable **Create a GitHub Release** to publish a public release
4. The generated JSON files will be uploaded as artifacts (retained for 90 days)

### Local Usage

Requirements:
- Python 3.11 or later
- UTF-8 encoding support

Run:

```bash
python3 convert_tafsir_to_json.py <input_dir> <output_dir>
```

Example:

```bash
python3 convert_tafsir_to_json.py . tafsir_json_output
```

## Output Files

The conversion script creates the following JSON files:

### Individual Sura Files

- `de_tafsir_surah_1.json` through `de_tafsir_surah_114.json`
- Each file contains the tafsir comments for a single Sura
- Format: array of verse objects

### Complete File

- `de_tafsir_complete.json`
- Contains all Suras and verses
- Includes metadata (author, publisher, overall statistics)

## JSON Structure

Each verse has the following structure:

```json
{
  "key": "de_tafsir-al-quran-al-karim",
  "verse_key": "1:1",
  "verses": ["1:1"],
  "text": "<h2>Sura Al-Fātiḥa...</h2><p>...</p>",
  "timestamp": "2025-12-20T...",
  "version": "1.0",
  "copyright": {
    "author": "Muhammad Ibn Ahmad Ibn Rassoul",
    "publisher": "IB Verlag Islamische Bibliothek",
    "edition": "41. Auflage",
    "title": "Tafsīr Al-Qur'ān Al-Karīm"
  }
}
```

### HTML Formatting

The text is automatically converted to HTML:

- `<h2>` - Sura headings
- `<p>` - Paragraphs
- `<strong>` - Qur'an quotations (in quotation marks)
- `<em>` - Arabic terms with diacritical marks

## Features

- ✅ UTF-8 encoding for all files  
- ✅ Error handling for missing text files  
- ✅ Progress output during conversion  
- ✅ Copyright notices included in JSON files  
- ✅ Automatic HTML formatting  
- ✅ Metadata included in the complete JSON file  

## Technical Details

### Input Format

The script processes `tafsir_al_quran.txt_*.txt` files with the following structure:

- Sura header: `(Number) Sura Name (German translation)`
- Revelation place: `(revealed in Makka/Al-Madīna)`
- Verse count: `N Āyāt`
- Verse references: `N:N - commentary...`

### Conversion Process

1. Reads all text files sequentially  
2. Identifies Sura headers and metadata  
3. Extracts verse commentaries  
4. Converts text to HTML  
5. Generates JSON output files

## License

The original work is subject to the copyright of the author and publisher. Use is permitted according to the publisher's licensing terms.

## Contact

For questions about the original work:  
IB Verlag Islamische Bibliothek

For technical questions about this conversion script:  
See the GitHub Issues in this repository

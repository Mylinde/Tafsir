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

## Workflow

### Step 1: Extract Text from PDF

Before converting to JSON, extract text from the PDF file using the `pdf_extract_to_txt.sh` bash script.

Requirements:
- `pdftk` utility (for PDF manipulation)
- `pdftotext` utility (part of Poppler)
- Bash shell
- Standard Unix tools: `sed`, `grep`, `awk`

Install dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install pdftk poppler-utils

# macOS
brew install pdftk poppler

# CentOS/RHEL
sudo yum install pdftk poppler-utils
```

Run the extraction script:

```bash
bash pdf_extract_to_txt.sh
```

This will create individual text files (`pg_XXXX.txt`) in the current directory, one for each page of the PDF (pages 35-1009).

### Step 2: Convert Text to JSON

After extracting the text files, convert them to JSON format using the `convert_tafsir_to_json.py` Python script.

## Automatic Conversion with GitHub Actions

The easiest way to generate the JSON files:

1. Go to **Actions** → **Convert Tafsir to JSON**
2. Click **Run workflow**
3. Optional: Enable **Create a GitHub Release** to publish a public release
4. The generated JSON files will be uploaded as artifacts (retained for 90 days)

## Local Usage

### Requirements

- Python 3.11 or later
- Bash shell
- `pdftotext` utility (for PDF extraction)
- UTF-8 encoding support

### Extract Text from PDF

```bash
bash pdf_extract_to_txt.sh <input_pdf> <output_dir>
```

Example:

```bash
bash pdf_extract_to_txt.sh tafsir_al_quran.pdf tafsir-txt
```

### Convert Text to JSON

```bash
python3 convert_tafsir_to_json.py <input_dir> <output_dir>
```

Example:

```bash
python3 convert_tafsir_to_json.py tafsir-txt tafsir-json
```

### Complete Workflow Example

```bash
# Step 1: Extract text from PDF
bash pdf_extract_to_txt.sh tafsir_al_quran.pdf tafsir-txt

# Step 2: Convert text to JSON
Before converting some sura/verse references need to be corrected to the format [sura:verse -] or [sura:verse-verse -]!

python3 convert_tafsir_to_json.py tafsir-txt tafsir-json
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

- ✅ Automatic PDF text extraction
- ✅ UTF-8 encoding for all files  
- ✅ Error handling for missing text files  
- ✅ Progress output during conversion  
- ✅ Copyright notices included in JSON files  
- ✅ Automatic HTML formatting  
- ✅ Metadata included in the complete JSON file  

## Technical Details

### PDF Extraction

The `pdf_extract_to_txt.sh` bash script:
- Uses `pdftotext` utility to extract text from PDF
- Converts each page to a separate text file
- Names files sequentially (`pg_XXXX.txt`)
- Preserves text encoding and formatting

### JSON Conversion

The `convert_tafsir_to_json.py` script processes text files with the following structure:

- Sura header: `(Number) Sura Name (German translation)`
- Revelation place: `(revealed in Makka/Al-Madīna)`
- Verse count: `N Āyāt`
- Verse references: `N:N - commentary...`

### Conversion Process

1. Extracts text from PDF pages using `pdftotext`
2. Reads all text files sequentially  
3. Identifies Sura headers and metadata  
4. Extracts verse commentaries  
5. Merges text for verse ranges (e.g., 2:142-145)
6. Converts text to HTML  
7. Generates JSON output files

## License

The original work is subject to the copyright of the author and publisher. Use is permitted according to the publisher's licensing terms.

## Contact

For questions about the original work:  
IB Verlag Islamische Bibliothek

For technical questions about this conversion script:  
See the GitHub Issues in this repository

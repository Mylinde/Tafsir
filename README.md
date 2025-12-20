# Tafsīr Al-Qur'ān Al-Karīm - JSON Converter

Dieses Repository enthält ein automatisches Konvertierungssystem, das die deutschen Tafsir-Textdateien (Qur'an-Kommentare) in das JSON-Format für Qur'an-Anwendungen umwandelt.

## Über das Werk

**Titel:** Tafsīr Al-Qur'ān Al-Karīm  
**Autor:** Abū-r-Riḍā' Muhammad Ibn Ahmad Ibn Rassoul  
**Verlag:** IB Verlag Islamische Bibliothek  
**Auflage:** 41., verbesserte und erweiterte Auflage  

### Copyright & Quelle

Die Vervielfältigung, der Nachdruck und die Übersetzung dieses Werkes in eine Fremdsprache sind erlaubt, wenn dabei auf diese Quelle hingewiesen wird.

Quelle: IB Verlag Islamische Bibliothek

## Automatische Konvertierung

### Mit GitHub Actions

Der einfachste Weg, die JSON-Dateien zu generieren:

1. Gehe zu **Actions** → **Convert Tafsir to JSON**
2. Klicke auf **Run workflow**
3. Optional: Aktiviere **Create a GitHub Release** für ein öffentliches Release
4. Die generierten JSON-Dateien werden als Artifacts (90 Tage Aufbewahrung) hochgeladen

### Lokale Verwendung

Voraussetzungen:
- Python 3.11 oder höher
- UTF-8 Encoding-Unterstützung

Ausführung:

```bash
python3 convert_tafsir_to_json.py <input_dir> <output_dir>
```

Beispiel:

```bash
python3 convert_tafsir_to_json.py . tafsir_json_output
```

## Ausgabe-Dateien

Das Konvertierungsskript erstellt folgende JSON-Dateien:

### Einzelne Sura-Dateien

- `de_tafsir_surah_1.json` bis `de_tafsir_surah_114.json`
- Jede Datei enthält die Tafsir-Kommentare für eine einzelne Sura
- Format: Array von Vers-Objekten

### Vollständige Datei

- `de_tafsir_complete.json`
- Enthält alle Suras und Verse
- Enthält Metadaten (Autor, Verlag, Gesamtstatistiken)

## JSON-Struktur

Jeder Vers hat folgende Struktur:

```json
{
  "key": "de_tafsir-al-azhar",
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

### HTML-Formatierung

Der Text wird automatisch in HTML konvertiert:

- **`<h2>`** - Sura-Überschriften
- **`<p>`** - Absätze
- **`<strong>`** - Qur'an-Zitate in Anführungszeichen
- **`<em>`** - Arabische Begriffe mit diakritischen Zeichen

## Funktionen

✅ UTF-8 Encoding für alle Dateien  
✅ Fehlerbehandlung bei fehlenden Textdateien  
✅ Progress-Ausgabe während der Konvertierung  
✅ Copyright-Hinweise in JSON-Dateien  
✅ Automatische HTML-Formatierung  
✅ Metadaten in vollständiger JSON-Datei  

## Technische Details

### Eingabeformat

Das Skript verarbeitet `tafsir_al_quran.txt_*.txt` Dateien mit folgendem Format:

- Sura-Header: `(Nummer) Sura Name (Deutsche Übersetzung)`
- Offenbarungsort: `(offenbart zu Makka/Al-Madīna)`
- Versanzahl: `N Āyāt`
- Vers-Referenzen: `N:N - Kommentar...`

### Konvertierungsprozess

1. Liest alle Textdateien sequenziell
2. Identifiziert Sura-Header und Metadaten
3. Extrahiert Vers-Kommentare
4. Konvertiert Text in HTML
5. Generiert JSON-Ausgabedateien

## Lizenz

Das ursprüngliche Werk unterliegt dem Copyright des Autors und Verlags. Die Nutzung ist gemäß den Lizenzbedingungen des Verlags erlaubt.

## Kontakt

Für Fragen zum ursprünglichen Werk:  
IB Verlag Islamische Bibliothek

Für technische Fragen zu diesem Konvertierungsskript:  
Siehe GitHub Issues in diesem Repository

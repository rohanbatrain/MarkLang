# MarkLang

![2](https://github.com/user-attachments/assets/50f79810-815f-4263-a4e0-a41f0b8017d5)


MarkLang is a robust, production-ready CLI tool for translating Markdown blog posts (including frontmatter, tags, and categories) from one language to another. It supports custom per-language dictionaries, Google Translate, and offline transliteration for technical terms and proper nouns.

## Features
- **CLI-based**: Translate files with a single command.
- **Frontmatter Support**: Translates title, description, tags, categories, and more.
- **Custom Dictionary**: Per-language CSV files for preferred translations of tags/categories.
- **Google Translate Fallback**: Uses Google Translate for tags/categories if not found in the dictionary.
- **Offline Transliteration**: For technical terms, falls back to script transliteration (e.g., Devanagari for Hindi).
- **Robust Logging**: Detailed logs for every step, including dictionary usage and translation fallbacks.
- **Production-Ready**: Modular, type-annotated, and well-documented code.

## How It Works
1. **Input**: You provide a Markdown file with YAML frontmatter (e.g., `en/blog/example.md`).
2. **Translation**: The script translates the title, description, tags, categories, and content to the target language.
3. **Custom Dictionary**: For tags/categories, it first checks a per-language CSV (e.g., `translations_hi.csv`).
4. **Fallbacks**: If not found, it uses Google Translate; if that fails, it uses offline transliteration.
5. **Output**: The translated file is written to the corresponding target language directory (e.g., `hi/blog/example.md`).

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/rohanbatrain/MarkLang
   cd MarkLang
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   For Hindi/Thai transliteration, also install:
   ```sh
   pip install indic-transliteration aksharamukha
   ```

## Usage

```sh
python main.py <input_file> <target_lang> [--source_lang en] [--model llama3.2:3b]
```

- `<input_file>`: Path to the input Markdown file (with frontmatter)
- `<target_lang>`: Target language code (e.g., `hi`, `fr`, `de`)
- `--source_lang`: Source language code (default: `en`)
- `--model`: Translation model to use (default: `llama3.2:3b`)

**Example:**
```sh
python main.py en/blog/example.md hi
```
This will create `hi/blog/example.md` with all content translated to Hindi.

## Custom Dictionary
- Place per-language CSVs in the `translations/` directory, e.g., `translations_hi.csv`, `translations_fr.csv`.
- Each CSV should have columns: `word,translation`
- Example (`translations_hi.csv`):
  ```csv
  word,translation
  Automation,ऑटोमेशन
  Linux,लिनक्स
  SSH,एसएसएच
  ```
- The script will always check the dictionary first for tags/categories.

## How It Was Made
- **Initial Version**: Focused on translating titles/descriptions using a translation API.
- **Enhancements**:
  - Added support for arrays (tags/categories) and batch translation.
  - Implemented robust error handling and logging.
  - Added custom dictionary support and offline transliteration.
  - Refactored for CLI usage and production-readiness.
- **Fallback Logic**: Always tries dictionary → Google Translate → offline transliteration.
- **Validation**: Ensures frontmatter is valid and all keys have values.
- **Extensible**: Easy to add new languages or extend dictionary files.

## Supported Languages
- English (`en`)
- Hindi (`hi`)
- French (`fr`)
- German (`de`)
- Italian (`it`)
- Portuguese (`pt`)
- Spanish (`es`)
- Thai (`th`)

## Logging & Troubleshooting
- All major steps are logged to the console.
- Errors in translation, dictionary loading, or file writing are clearly reported.
- If a translation fails, the script falls back gracefully and logs the fallback used.

## Contributing
- PRs are welcome! Please add tests for new features.
- For new languages, add a `translations_<lang>.csv` file in the `translations/` directory.

## License
MIT License

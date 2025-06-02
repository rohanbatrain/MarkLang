import frontmatter
import requests
import os
from googletrans import Translator # type: ignore
import asyncio
import argparse
import csv
import logging



# Translation model and API settings
TRANSLATION_MODEL = "llama3.2"
TRANSLATION_API_URL = "http://localhost:1024/api/generate"

# Update prompts to include full language names with codes
TITLE_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following blog post title from {source_lang_full} ({source_lang_code}) to {target_lang_full} ({target_lang_code}), ensuring it sounds natural, engaging, and idiomatic in {target_lang_full}. "
    "Maintain the tone and intent of the original title, whether it is informative, persuasive, or creative. "
    "The translation should be concise, culturally appropriate, and appealing to native speakers. "
    "\n\nTitle: \"{text}\"\n\n"
    "Return only the translated title in {target_lang_full}, with no explanation or additional text. without single quotes and in a single line."
)

DESCRIPTION_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following blog post description from {source_lang_full} ({source_lang_code}) to {target_lang_full} ({target_lang_code}), ensuring it sounds natural, engaging, and idiomatic in {target_lang_full}. "
    "Maintain the tone and intent of the original description, whether it is informative, persuasive, or creative. "
    "The translation should be concise, culturally appropriate, and appealing to native speakers. "
    "\n\nDescription: \"{text}\"\n\n"
    "Return only the translated description in {target_lang_full}, with no explanation or additional text. without single quotes and in a single line."
)

CONTENT_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following Markdown document into {target_lang_full} ({target_lang_code}).\n\n"
    "Keep all code blocks, inline code, file paths, URLs, and any technical content (like JSON, HTML, YAML, shell commands, etc.) unchanged.\n\n"
    "Only translate human-readable text such as headings, paragraphs, and comments.\n\n"
    "Preserve the original Markdown formatting and structure exactly as is.\n\n"
    "Do not alter indentation, punctuation, or spacing.\n\n"
    "Do not explain anything—just return the translated Markdown document.\n\n"
    "Here is the Markdown content:\n\n\"{text}\"\n"
)

# Add toggles for rendering specific keys
RENDER_KEYS = {
    "title": True,
    "description": True,
    "tags": True,
    "categories": True,
    "date": True,
    "draft": True,
    "author": True, 
}

# Initialize the Google Translator
translator = Translator()

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "pt": "Portuguese",
    "es": "Spanish",
    "th": "Thai"
}

# AI notification message template (global)
AI_NOTIFICATION_MSG = (
    "> This content was automatically translated from {source_lang} to {target_lang} and rewritten by AI."
)

def replace_double_with_single_quotes(text: str) -> str:
    return text.replace('"', "'")

def replace_mixed_quotes(text: str) -> str:
    return text.replace("'", "\"").replace("'", "\"")

def clean_frontmatter_value(value: str) -> str:
    """Replace "' or '" with just " in frontmatter values."""
    value = value.replace("\"'", "\"").replace("'\"", "\"")
    return value

# Utility functions for cleaning up special characters

def replace_dot_quote(text: str) -> str:
    return text.replace('."', '.')

def replace_arrow_quote(text: str) -> str:
    return text.replace('">', '>')

def replace_hash_quote(text: str) -> str:
    return text.replace('"#', '#')

def clean_special_quotes(text: str) -> str:
    text = replace_dot_quote(text)
    text = replace_arrow_quote(text)
    text = replace_hash_quote(text)
    return text

def translate_title(
    title: str,
    source_lang: str,
    target_lang: str,
    model: str,
    api_url: str = TRANSLATION_API_URL
) -> str:
    print(f"[LOG] Translating title: '{title}' from {source_lang} to {target_lang}")
    prompt = TITLE_TRANSLATION_PROMPT.format(
        source_lang_full=LANGUAGE_NAMES[source_lang],
        source_lang_code=source_lang,
        target_lang_full=LANGUAGE_NAMES[target_lang],
        target_lang_code=target_lang,
        text=title
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    print(f"[LOG] Sending title translation request to API: {api_url}")
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("response", "").strip("")
        print(f"[LOG] Title translation result: {translated_text}")
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        print(f"[ERROR] Title translation failed: {e}")
        return f"[Error] {e}"

def validate_frontmatter(file_path: str) -> bool:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if frontmatter starts with '---' and contains a closing '---' (not necessarily at the end)
        if not content.startswith("---\n"):
            return False
        if "\n---\n" not in content:
            return False

        # Parse frontmatter content
        frontmatter_data = frontmatter.loads(content)

        # Check if all keys have values
        for key, value in frontmatter_data.metadata.items():
            if value is None or value == "":
                print(f"[Error] Missing value for key: {key}")
                return False

        return True
    except Exception as e:
        print(f"[Error] Validation failed: {e}")
        return False

def translate_description(
    description: str,
    source_lang: str,
    target_lang: str,
    model: str,
    api_url: str = TRANSLATION_API_URL
) -> str:
    print(f"[LOG] Translating description: '{description}' from {source_lang} to {target_lang}")
    prompt = DESCRIPTION_TRANSLATION_PROMPT.format(
        source_lang_full=LANGUAGE_NAMES[source_lang],
        source_lang_code=source_lang,
        target_lang_full=LANGUAGE_NAMES[target_lang],
        target_lang_code=target_lang,
        text=description
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    print(f"[LOG] Sending description translation request to API: {api_url}")
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("response", "").strip("")
        print(f"[LOG] Description translation result: {translated_text}")
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        print(f"[ERROR] Description translation failed: {e}")
        return f"[Error] {e}"

def translate_content(
    content: str,
    source_lang: str,
    target_lang: str,
    model: str,
    api_url: str = TRANSLATION_API_URL
) -> str:
    print(f"[LOG] Translating content from {source_lang} to {target_lang}")
    prompt = CONTENT_TRANSLATION_PROMPT.format(
        source_lang_full=LANGUAGE_NAMES[source_lang],
        source_lang_code=source_lang,
        target_lang_full=LANGUAGE_NAMES[target_lang],
        target_lang_code=target_lang,
        text=content
    )
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    print(f"[LOG] Sending content translation request to API: {api_url}")
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("response", "").strip("")
        print(f"[LOG] Content translation result: {translated_text[:100]}... (truncated)")
        return translated_text
    except requests.RequestException as e:
        print(f"[ERROR] Content translation failed: {e}")
        return f"[Error] {e}"

def transliterate_to_script(text: str, lang_code: str) -> str:
    """
    Transliterate English text into the script of the target language, preserving pronunciation.
    Supports Hindi (hi, Devanagari) and Thai (th, Thai script). Returns original for Latin-alphabet languages.
    """
    latin_langs = {"de", "fr", "it", "pt", "es"}
    if lang_code in latin_langs:
        return text
    if lang_code == "hi":
        try:
            from indic_transliteration.sanscript import transliterate
            return transliterate(text, 'iast', 'devanagari')
        except ImportError:
            print("[ERROR] Please install indic-transliteration for Hindi transliteration: pip install indic-transliteration")
            return text
    if lang_code == "th":
        try:
            from aksharamukha.transliterate import process
            return process('IAST', 'Thai', text)
        except ImportError:
            print("[ERROR] Please install aksharamukha for Thai transliteration: pip install aksharamukha")
            return text
    print(f"[WARN] Transliteration for language code '{lang_code}' is not supported. Returning original text.")
    return text

# Load custom dictionary from CSV
CUSTOM_DICT = {}
def load_custom_dictionary(lang_code: str, base_path: str = "translations") -> None:
    """Load a custom dictionary for the target language from a CSV file."""
    global CUSTOM_DICT
    CUSTOM_DICT = {}
    csv_path = os.path.join(base_path, f"translations_{lang_code}.csv")
    logging.info(f"Attempting to load custom dictionary: {csv_path}")
    if not os.path.exists(csv_path):
        logging.info(f"Custom dictionary CSV '{csv_path}' not found. Skipping.")
        return
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            word = row['word'].strip()
            translation = row['translation'].strip()
            CUSTOM_DICT[word.lower()] = translation
    logging.info(f"Loaded {len(CUSTOM_DICT)} custom dictionary entries from {csv_path}.")

async def translate_single_word(translator, word: str, target_lang: str) -> str:
    """Translate a single word using custom dictionary, Googletrans, or offline transliteration."""
    custom = CUSTOM_DICT.get(word.lower())
    if custom:
        logging.info(f"Using custom dictionary translation for '{word}' in '{target_lang}': {custom} (from translations_{target_lang}.csv)")
        return custom
    try:
        translation = await translator.translate(word, dest=target_lang)
        if translation.text.strip().lower() == word.strip().lower():
            logging.warning(f"Googletrans did not translate '{word}'. Using offline transliteration fallback.")
            return transliterate_to_script(word, target_lang)
        return translation.text
    except Exception as e:
        logging.warning(f"Googletrans failed for '{word}': {e}. Using offline transliteration fallback.")
        return transliterate_to_script(word, target_lang)

async def translate_array_with_googletrans(translator, array: list, target_lang: str) -> list:
    """Translate an array of words using translate_single_word."""
    tasks = [translate_single_word(translator, word, target_lang) for word in array]
    return await asyncio.gather(*tasks)

async def translate_author_with_transliteration(translator, author: str, target_lang: str) -> str:
    """Translates and transliterates the author field if needed."""
    if not author:
        return author
    # Try custom dictionary or Googletrans, then transliterate if needed
    translated = await translate_single_word(translator, author, target_lang)
    return transliterate_to_script(translated, target_lang)

def process_markdown(file_path: str, output_path: str = "output.md") -> None:
    """Process a markdown file: translate frontmatter and content, write to output."""
    logging.info(f"Starting processing of markdown file: {file_path}")
    try:
        post = frontmatter.load(file_path)
        logging.info("Successfully loaded markdown file.")
    except Exception as e:
        logging.error(f"Failed to load markdown file: {e}")
        return

    async def main():
        logging.info("Entered async main() for processing.")
        translated_title = ""
        if RENDER_KEYS["title"]:
            original_title = post.get("title")
            logging.info(f"Original title: {original_title}")
            if not original_title:
                logging.error("No title found in frontmatter.")
                return
            logging.info("Translating title...")
            translated_title = translate_title(original_title, SOURCE_LANG, TARGET_LANG, TRANSLATION_MODEL)
            logging.info(f"Title translated: {translated_title}")

        translated_description = ""
        if RENDER_KEYS["description"]:
            original_description = post.get("description")
            logging.info(f"Original description: {original_description}")
            if original_description:
                logging.info("Translating description...")
                translated_description = translate_description(original_description, SOURCE_LANG, TARGET_LANG, TRANSLATION_MODEL)
                logging.info(f"Description translated: {translated_description}")

        translated_tags = []
        if RENDER_KEYS["tags"]:
            original_tags = post.get("tags", [])
            logging.info(f"Original tags: {original_tags} (type: {type(original_tags)})")
            if isinstance(original_tags, str):
                original_tags = [tag.strip() for tag in original_tags.split(",") if tag.strip()]
            if original_tags:
                logging.info(f"Translating tags from {LANGUAGE_NAMES[SOURCE_LANG]} ({SOURCE_LANG}) to {LANGUAGE_NAMES[TARGET_LANG]} ({TARGET_LANG})...")
                translated_tags = await translate_array_with_googletrans(translator, original_tags, TARGET_LANG)
                translated_tags = [transliterate_to_script(tag, TARGET_LANG) for tag in translated_tags]
                logging.info(f"Tags translated: {translated_tags}")

        translated_categories = []
        if RENDER_KEYS["categories"]:
            original_categories = post.get("categories", [])
            logging.info(f"Original categories: {original_categories} (type: {type(original_categories)})")
            if isinstance(original_categories, str):
                original_categories = [cat.strip() for cat in original_categories.split(",") if cat.strip()]
            if original_categories:
                logging.info(f"Translating categories from {LANGUAGE_NAMES[SOURCE_LANG]} ({SOURCE_LANG}) to {LANGUAGE_NAMES[TARGET_LANG]} ({TARGET_LANG})...")
                translated_categories = await translate_array_with_googletrans(translator, original_categories, TARGET_LANG)
                translated_categories = [transliterate_to_script(cat, TARGET_LANG) for cat in translated_categories]
                logging.info(f"Categories translated: {translated_categories}")

        date = post.get("date", "")
        draft = post.get("draft", "")

        translated_author = ""
        if RENDER_KEYS.get("author"):
            original_author = post.get("author", "")
            logging.info(f"Original author: {original_author}")
            if original_author:
                logging.info("Transliterating author...")
                translated_author = await translate_author_with_transliteration(translator, original_author, TARGET_LANG)
                logging.info(f"Author transliterated: {translated_author}")

        logging.info("Creating new frontmatter...")
        new_metadata = {
            "title": f'"{translated_title}"' if RENDER_KEYS["title"] else None,
            "description": f'"{translated_description}"' if RENDER_KEYS["description"] else None,
            "tags": translated_tags if RENDER_KEYS["tags"] else None,
            "categories": translated_categories if RENDER_KEYS["categories"] else None,
            "date": date if RENDER_KEYS["date"] else None,
            "draft": draft if RENDER_KEYS["draft"] else None,
            "author": f'"{translated_author}"' if RENDER_KEYS.get("author") and translated_author else None
        }
        logging.info(f"New metadata for frontmatter: {new_metadata}")
        new_frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in new_metadata.items() if value or isinstance(value, bool)) + "\n---\n"
        new_frontmatter = clean_frontmatter_value(new_frontmatter)
        logging.info(f"New frontmatter generated:\n{new_frontmatter}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                logging.info(f"Writing frontmatter to {output_path}")
                f.write(new_frontmatter)
                ai_message_en = AI_NOTIFICATION_MSG.format(
                    source_lang=LANGUAGE_NAMES[SOURCE_LANG],
                    target_lang=LANGUAGE_NAMES[TARGET_LANG]
                )
                logging.info(f"Translating AI notification message: {ai_message_en}")
                ai_message_translated = translate_content(ai_message_en, SOURCE_LANG, TARGET_LANG, TRANSLATION_MODEL)
                ai_message_translated = clean_special_quotes(ai_message_translated)
                logging.info(f"Writing AI notification message: {ai_message_translated}")
                f.write(f"\n{ai_message_translated}\n")
                markdown_content = post.content
                logging.info(f"Translating markdown content (first 100 chars): {markdown_content[:100]}... (truncated)")
                translated_markdown = translate_content(markdown_content, SOURCE_LANG, TARGET_LANG, TRANSLATION_MODEL)
                translated_markdown = clean_special_quotes(translated_markdown)
                logging.info(f"Writing translated markdown content (first 100 chars): {translated_markdown[:100]}... (truncated)")
                f.write(f"\n{translated_markdown}\n")
            logging.info(f"Successfully wrote translated content to: {output_path}")
        except Exception as e:
            logging.error(f"Failed to write output file: {e}")
            return

        logging.info("Validating frontmatter...")
        if not validate_frontmatter(output_path):
            logging.error("Invalid frontmatter. Deleting output file and retrying.")
            os.remove(output_path)
            await main()
        else:
            logging.info("Frontmatter validation successful.")

    asyncio.run(main())

def validate_language_code(lang_code: str) -> bool:
    """Check if the language code is supported."""
    return lang_code in LANGUAGE_NAMES

def main_cli() -> None:
    """Main CLI entry point for MarkLang translation script."""
    parser = argparse.ArgumentParser(description="Translate a markdown file with frontmatter to a target language.")
    parser.add_argument("input_file", type=str, help="Path to the input markdown file (with frontmatter)")
    parser.add_argument("target_lang", type=str, help="Target language code (e.g., fr, de, hi, etc.)")
    parser.add_argument("--source_lang", type=str, default="en", help="Source language code (default: en)")
    parser.add_argument("--model", type=str, default="llama3.2:3b", help="Translation model to use (default: llama3.2:3b)")
    args = parser.parse_args()

    global SOURCE_LANG, TARGET_LANG, TRANSLATION_MODEL
    SOURCE_LANG = args.source_lang
    TARGET_LANG = args.target_lang
    TRANSLATION_MODEL = args.model

    # Language code validation
    if not validate_language_code(SOURCE_LANG):
        print(f"[ERROR] Unsupported source language code: {SOURCE_LANG}")
        print(f"Supported codes: {list(LANGUAGE_NAMES.keys())}")
        exit(1)
    if not validate_language_code(TARGET_LANG):
        print(f"[ERROR] Unsupported target language code: {TARGET_LANG}")
        print(f"Supported codes: {list(LANGUAGE_NAMES.keys())}")
        exit(1)

    input_file = args.input_file
    output_file = input_file.replace(f"{SOURCE_LANG}/", f"{TARGET_LANG}/")
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    load_custom_dictionary(TARGET_LANG)
    try:
        process_markdown(input_file, output_file)
    except KeyboardInterrupt:
        print("\n[INFO] Translation interrupted by user. Exiting gracefully.")
        exit(0)

if __name__ == "__main__":
    main_cli()

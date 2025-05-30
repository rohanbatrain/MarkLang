import frontmatter
import requests
import os
from googletrans import Translator # type: ignore
import asyncio

# Global language settings
SOURCE_LANG = "en"  # English
TARGET_LANG = "fr"  # Hindi

# Translation model and API settings
TRANSLATION_MODEL = "llama3.2:3b"
TRANSLATION_API_URL = "http://localhost:11434/api/generate"

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

def replace_double_with_single_quotes(text: str) -> str:
    return text.replace('"', "'")

def replace_mixed_quotes(text: str) -> str:
    return text.replace("'", "\"").replace("'", "\"")

def clean_frontmatter_value(value):
    # Replace "' or '" with just "
    value = value.replace("\"'", "\"").replace("'\"", "\"")
    return value

def translate_title(
    title: str,
    source_lang: str = SOURCE_LANG,
    target_lang: str = TARGET_LANG,
    model: str = TRANSLATION_MODEL,
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
        # Only replace quotes for title
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        print(f"[ERROR] Title translation failed: {e}")
        return f"[Error] {e}"

def validate_frontmatter(file_path):
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
    source_lang: str = SOURCE_LANG,
    target_lang: str = TARGET_LANG,
    model: str = TRANSLATION_MODEL,
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
        # Only replace quotes for description
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        print(f"[ERROR] Description translation failed: {e}")
        return f"[Error] {e}"

def translate_content(
    content: str,
    source_lang: str = SOURCE_LANG,
    target_lang: str = TARGET_LANG,
    model: str = TRANSLATION_MODEL,
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
        # Do NOT replace quotes for markdown content
        return translated_text
    except requests.RequestException as e:
        print(f"[ERROR] Content translation failed: {e}")
        return f"[Error] {e}"

async def translate_single_word(translator, word, target_lang):
    try:
        translation = await translator.translate(word, dest=target_lang)
        return translation.text
    except Exception as e:
        return f"[Error translating '{word}']: {e}"

async def translate_array_with_googletrans(translator, array: list, target_lang: str = TARGET_LANG) -> list:
    translated_array = []
    tasks = [translate_single_word(translator, word, target_lang) for word in array]
    results = await asyncio.gather(*tasks)
    translated_array.extend(results)
    return translated_array

def process_markdown(file_path, output_path="output.md"):
    print(f"[INFO] Starting processing of markdown file: {file_path}")

    # Load original markdown file
    try:
        post = frontmatter.load(file_path)
        print("[INFO] Successfully loaded markdown file.")
    except Exception as e:
        print(f"[ERROR] Failed to load markdown file: {e}")
        return

    async def main():
        print("[LOG] Entered async main() for processing.")
        translated_title = ""
        if RENDER_KEYS["title"]:
            original_title = post.get("title")
            print(f"[LOG] Original title: {original_title}")
            if not original_title:
                print("[ERROR] No title found in frontmatter.")
                return

            print("[INFO] Translating title...")
            translated_title = translate_title(original_title)
            print(f"[INFO] Title translated: {translated_title}")

        translated_description = ""
        if RENDER_KEYS["description"]:
            original_description = post.get("description")
            print(f"[LOG] Original description: {original_description}")
            if original_description:
                print("[INFO] Translating description...")
                translated_description = translate_description(original_description)
                print(f"[INFO] Description translated: {translated_description}")

        translated_tags = []
        if RENDER_KEYS["tags"]:
            original_tags = post.get("tags", [])
            print(f"[LOG] Original tags: {original_tags}")
            if original_tags:
                print(f"[INFO] Translating tags from {LANGUAGE_NAMES[SOURCE_LANG]} ({SOURCE_LANG}) to {LANGUAGE_NAMES[TARGET_LANG]} ({TARGET_LANG})...")
                translated_tags = await translate_array_with_googletrans(translator, original_tags)
                print(f"[INFO] Tags translated: {translated_tags}")

        translated_categories = []
        if RENDER_KEYS["categories"]:
            original_categories = post.get("categories", [])
            print(f"[LOG] Original categories: {original_categories}")
            if original_categories:
                print(f"[INFO] Translating categories from {LANGUAGE_NAMES[SOURCE_LANG]} ({SOURCE_LANG}) to {LANGUAGE_NAMES[TARGET_LANG]} ({TARGET_LANG})...")
                translated_categories = await translate_array_with_googletrans(translator, original_categories)
                print(f"[INFO] Categories translated: {translated_categories}")

        date = post.get("date", "")
        draft = post.get("draft", "")

        print("[INFO] Creating new frontmatter...")
        new_metadata = {
            "title": f'"{translated_title}"' if RENDER_KEYS["title"] else None,
            "description": f'"{translated_description}"' if RENDER_KEYS["description"] else None,
            "tags": translated_tags if RENDER_KEYS["tags"] else None,
            "categories": translated_categories if RENDER_KEYS["categories"] else None,
            "date": date if RENDER_KEYS["date"] else None,
            "draft": draft if RENDER_KEYS["draft"] else None
        }
        print(f"[LOG] New metadata for frontmatter: {new_metadata}")
        new_frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in new_metadata.items() if value or isinstance(value, bool)) + "\n---\n"
        new_frontmatter = clean_frontmatter_value(new_frontmatter)
        print(f"[LOG] New frontmatter generated:\n{new_frontmatter}")

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                print(f"[LOG] Writing frontmatter to {output_path}")
                f.write(new_frontmatter)
                # Translate the AI generated message
                ai_message_en = "> This content was automatically translated and rewritten in {lang} by AI.".format(lang=LANGUAGE_NAMES[TARGET_LANG])
                print(f"[LOG] Translating AI notification message: {ai_message_en}")
                ai_message_translated = translate_content(ai_message_en)
                print(f"[LOG] Writing AI notification message: {ai_message_translated}")
                f.write(f"\n{ai_message_translated}\n")
                # Get markdown content (without frontmatter)
                markdown_content = post.content
                print(f"[LOG] Translating markdown content (first 100 chars): {markdown_content[:100]}... (truncated)")
                translated_markdown = translate_content(markdown_content)
                print(f"[LOG] Writing translated markdown content (first 100 chars): {translated_markdown[:100]}... (truncated)")
                f.write(f"\n{translated_markdown}\n")
            print(f"[INFO] Successfully wrote translated content to: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to write output file: {e}")
            return

        print("[INFO] Validating frontmatter...")
        if not validate_frontmatter(output_path):
            print("[ERROR] Invalid frontmatter. Deleting output file and retrying.")
            os.remove(output_path)
            await main() # Call main again if validation fails
        else:
            print("[INFO] Frontmatter validation successful.")

    asyncio.run(main())
    
# Example usage
process_markdown("example.md")
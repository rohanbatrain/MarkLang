import frontmatter
import requests
import os

# Global language settings
SOURCE_LANG = "English"
TARGET_LANG = "Hindi"

# Global variables for title-specific translation
TRANSLATION_MODEL = "llama3.2:3b"
TRANSLATION_API_URL = "http://localhost:11434/api/generate"
TITLE_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following blog post title from {source_lang} to {target_lang}, ensuring it sounds natural, engaging, and idiomatic in {target_lang}. "
    "Maintain the tone and intent of the original title, whether it is informative, persuasive, or creative. "
    "The translation should be concise, culturally appropriate, and appealing to native speakers. "
    "\n\nTitle: \"{text}\"\n\n"
    "Return only the translated title in {target_lang}, with no explanation or additional text. without single quotes and in a single line."
)

DESCRIPTION_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following blog post description from {source_lang} to {target_lang}, ensuring it sounds natural, engaging, and idiomatic in {target_lang}. "
    "Maintain the tone and intent of the original description, whether it is informative, persuasive, or creative. "
    "The translation should be concise, culturally appropriate, and appealing to native speakers. "
    "\n\nDescription: \"{text}\"\n\n"
    "Return only the translated description in {target_lang}, with no explanation or additional text. without single quotes and in a single line."
)

# ARRAY_TRANSLATION_PROMPT = (
#     "You are a professional translator with expertise in content localization and digital media. "
#     "Translate the following single word from {source_lang} to {target_lang}. "
#     "The translation must be idiomatic, culturally appropriate, and naturally used by native {target_lang} speakers. "
#     "Preserve the original word’s intent and tone—whether informative, technical, persuasive, or creative. "
#     "Respond with only the translated word in {target_lang}. "
#     "Do not include transliterations, parentheses, quotes, romanized forms, or any explanations—just the translated word only."
#     "\n\nWord: {text}\n"
# )


# ARRAY_TRANSLATION_PROMPT = (
#     "You are a professional linguist with expertise in multilingual typography and digital media. "
#     "Render the following single word using the script or font of {target_lang}, without translating it. "
#     "Keep the original word unchanged in meaning, spelling, and tone. "
#     "Simply convert the appearance to match how native {target_lang} speakers would visually write this word in their own script or font. "
#     "Respond with only the rendered word in {target_lang} script. "
#     "Do not translate, transliterate, or explain. No parentheses, quotes, or romanized forms—just the visually converted word only."
#     "\n\nWord: {text}\n"
# )


# ARRAY_TRANSLATION_PROMPT = (
#     "You are a professional linguist with expertise in multilingual typography and digital media. "
#     "Render the following single word using the script or font of {target_lang}. "
#     "You are **not allowed** to translate, transliterate, explain, or modify the word in any way. "
#     "The word must remain exactly as provided, in terms of meaning, spelling, and tone. "
#     "Only the visual appearance of the word should be converted to match how native {target_lang} speakers would write it in their script or font. "
#     "Failure to follow these instructions will result in failure. "
#     "Your response should **only** be the rendered word in {target_lang} script—nothing else, no parentheses, no quotes, no explanation. "
#     "Any deviation from this will result in failure."
#     "\n\nWord: {text}\n"
# )



# Add toggles for rendering specific keys
RENDER_KEYS = {
    "title": False,
    "description": False,
    "tags": True,
    "categories": True,
    "date": False,
    "draft": False
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
    prompt = TITLE_TRANSLATION_PROMPT.format(source_lang=source_lang, target_lang=target_lang, text=title)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("response", "").strip("")
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        return f"[Error] {e}"

def validate_frontmatter(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if frontmatter starts and ends with '---'
        if not (content.startswith("---\n") and content.endswith("\n---\n")):
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
    prompt = DESCRIPTION_TRANSLATION_PROMPT.format(source_lang=source_lang, target_lang=target_lang, text=description)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        data = response.json()
        translated_text = data.get("response", "").strip("")
        return replace_double_with_single_quotes(translated_text)
    except requests.RequestException as e:
        return f"[Error] {e}"

def translate_array(
    array: list,
    source_lang: str = SOURCE_LANG,
    target_lang: str = TARGET_LANG,
    model: str = TRANSLATION_MODEL,
    api_url: str = TRANSLATION_API_URL
) -> list:
    translated_array = []
    for word in array:
        prompt = ARRAY_TRANSLATION_PROMPT.format(source_lang=source_lang, target_lang=target_lang, text=word)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            translated_word = data.get("response", "").strip()
            translated_array.append(replace_double_with_single_quotes(translated_word))
        except requests.RequestException as e:
            translated_array.append(f"[Error translating '{word}']: {e}")

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

    # Extract and translate title if enabled
    translated_title = ""
    if RENDER_KEYS["title"]:
        original_title = post.get("title")
        if not original_title:
            print("[ERROR] No title found in frontmatter.")
            return

        print("[INFO] Translating title...")
        translated_title = translate_title(original_title)
        print(f"[INFO] Title translated: {translated_title}")

    # Extract and translate description if enabled
    translated_description = ""
    if RENDER_KEYS["description"]:
        original_description = post.get("description")
        if original_description:
            print("[INFO] Translating description...")
            translated_description = translate_description(original_description)
            print(f"[INFO] Description translated: {translated_description}")

    # Extract and translate tags if enabled
    translated_tags = []
    if RENDER_KEYS["tags"]:
        original_tags = post.get("tags", [])
        if original_tags:
            print("[INFO] Translating tags...")
            translated_tags = translate_array(original_tags)
            print(f"[INFO] Tags translated: {translated_tags}")

    # Extract and translate categories if enabled
    translated_categories = []
    if RENDER_KEYS["categories"]:
        original_categories = post.get("categories", [])
        if original_categories:
            print("[INFO] Translating categories...")
            translated_categories = translate_array(original_categories)
            print(f"[INFO] Categories translated: {translated_categories}")

    # Copy date and draft from original frontmatter
    date = post.get("date", "")
    draft = post.get("draft", "")

    # Create new post with translated title, description, tags, categories, date, and draft in frontmatter
    print("[INFO] Creating new frontmatter...")
    new_metadata = {
        "title": f'"{translated_title}"' if RENDER_KEYS["title"] else None,
        "description": f'"{translated_description}"' if RENDER_KEYS["description"] else None,
        "tags": translated_tags if RENDER_KEYS["tags"] else None,
        "categories": translated_categories if RENDER_KEYS["categories"] else None,
        "date": date if RENDER_KEYS["date"] else None,
        "draft": draft if RENDER_KEYS["draft"] else None
    }
    new_frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in new_metadata.items() if value or isinstance(value, bool)) + "\n---\n"
    new_frontmatter = clean_frontmatter_value(new_frontmatter)

    # Write to output.md
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_frontmatter)
        print(f"[INFO] Successfully wrote translated content to: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to write output file: {e}")
        return

    # Validate the frontmatter
    print("[INFO] Validating frontmatter...")
    if not validate_frontmatter(output_path):
        print("[ERROR] Invalid frontmatter. Deleting output file and retrying.")
        os.remove(output_path)
        process_markdown(file_path, output_path)
    else:
        print("[INFO] Frontmatter validation successful.")

# Example usage
process_markdown("example.md")

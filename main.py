import frontmatter
import requests
import os

# Global language settings
SOURCE_LANG = "English"
TARGET_LANG = "Spanish"

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

def process_markdown(file_path, output_path="output.md"):
    # Load original markdown file
    post = frontmatter.load(file_path)

    # Extract and translate title
    original_title = post.get("title")
    if not original_title:
        print("[Error] No title found in frontmatter.")
        return

    translated_title = translate_title(original_title)

    # Extract and translate description
    original_description = post.get("description")
    translated_description = ""
    if original_description:
        translated_description = translate_description(original_description)

    # Copy date and draft from original frontmatter
    date = post.get("date", "")
    draft = post.get("draft", "")

    # Create new post with translated title, description, date, and draft in frontmatter
    new_metadata = {
        "title": f'"{translated_title}"',
        "description": f'"{translated_description}"',
        "date": date,
        "draft": draft
    }
    new_frontmatter = "---\n" + "\n".join(f"{key}: {value}" for key, value in new_metadata.items() if value or isinstance(value, bool)) + "\n---\n"
    new_frontmatter = clean_frontmatter_value(new_frontmatter)

    # Write to output.md
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_frontmatter)
    
    # Validate the frontmatter
    if not validate_frontmatter(output_path):
        print("[Error] Invalid frontmatter. Deleting output file and retrying.")
        os.remove(output_path)
        process_markdown(file_path, output_path)

# Example usage
process_markdown("example.md")

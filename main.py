import frontmatter
import requests

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
    "Return only the translated title in {target_lang}, with no explanation or additional text. without double quotes and in a single line."
)

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
        return data.get("response", "").strip("")
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

    # Create new post with only the translated title in frontmatter and no content
    new_metadata = {"title": translated_title}
    new_post = frontmatter.Post(content="", **new_metadata)

    # Write to output.md
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(new_post))

# Example usage
process_markdown("example.md")

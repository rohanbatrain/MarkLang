import requests

# Global variables for title-specific translation
TRANSLATION_MODEL = "llama3.2:3b"
TRANSLATION_API_URL = "http://localhost:11434/api/generate"
TITLE_TRANSLATION_PROMPT = (
    "You are an expert translator specializing in content localization and digital media. "
    "Translate the following blog post title from {source_lang} to {target_lang}, ensuring it sounds natural, engaging, and idiomatic in {target_lang}. "
    "Maintain the tone and intent of the original title, whether it is informative, persuasive, or creative. "
    "The translation should be concise, culturally appropriate, and appealing to native speakers. "
    "\n\nTitle: \"{text}\"\n\n"
    "Return only the translated title in {target_lang}, with no explanation or additional text."
)

def translate_title(
    title: str,
    source_lang: str,
    target_lang: str,
    model: str = TRANSLATION_MODEL,
    api_url: str = TRANSLATION_API_URL
) -> str:
    """
    Translate `title` from `source_lang` to `target_lang` using Ollama + LLaMA 3.2.

    Args:
        title: The string to translate (title of a blog post or article).
        source_lang: Language code or name of the source text (e.g. "English").
        target_lang: Language code or name to translate into (e.g. "Spanish").
        model: Ollama model identifier (default "llama3.2:3b").
        api_url: URL of the Ollama generate endpoint.

    Returns:
        The translated string, or an error message on failure.
    """
    # Build a clear title-specific translation prompt
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
        # Ollama returns its reply under the "response" key
        return data.get("response", "").strip()
    except requests.RequestException as e:
        return f"[Error] {e}"


###########_______TESTING_______############
# Test the translation function
def test_title_translation():
    # Example CLI usage
    src = "english"
    tgt = "french"
    txt = input("Title to translate: ").strip()

    translated = translate_title(txt, src, tgt)
    print(translated)


# Running text
test_title_translation()
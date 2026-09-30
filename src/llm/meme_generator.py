import os
from groq import Groq


KEY_PATH = "/home/mglocadmin/Downloads/grok_api.txt"


def _get_client():
    """Read the API key from Streamlit secrets, env var, or file."""
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key:
            return Groq(api_key=api_key)
    except Exception:
        pass

    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)

    with open(KEY_PATH, "r") as f:
        api_key = f.read().strip()
    return Groq(api_key=api_key)


PROMPT_TEMPLATE = """You are a meme writer for social media (Instagram, Reddit).

Given this trending topic: "{topic}"

Write ONE short, funny meme caption.
Under 15 words. No hashtags. No explanations. Just the caption.

Also pick ONE emoji that best captures the mood of this meme.

Style:
- Dry, relatable humor
- Everyday things: salary, traffic, family, government, cricket
- No political bias, no offensive content

Respond in EXACTLY this format:

EMOJI: <single emoji>
CAPTION: <your meme>"""


MODELS = ["qwen/qwen3.8-27b", "allam-2-7b"]


def generate_caption(topic: str) -> dict:
    """Generate a meme caption + emoji with model fallback."""
    client = _get_client()

    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
                temperature=0.9,
                max_tokens=150,
            )
            text = response.choices[0].message.content.strip()
            if not text:
                print(f"[{model}] empty response, trying next...")
                continue

            # Parse EMOJI and CAPTION
            emoji = "😂"
            caption = text
            for line in text.splitlines():
                if line.startswith("EMOJI:"):
                    emoji = line.replace("EMOJI:", "").strip()
                elif line.startswith("CAPTION:"):
                    caption = line.replace("CAPTION:", "").strip()

            return {"emoji": emoji, "caption": caption}

        except Exception as e:
            print(f"[{model}] failed: {e}")
            continue

    return {"emoji": "😐", "caption": "(no response)"}
if __name__ == "__main__":
    result = generate_caption("Rupee hits new low against dollar")
    print(f"Emoji: {result['emoji']}")
    print(f"Caption: {result['caption']}")
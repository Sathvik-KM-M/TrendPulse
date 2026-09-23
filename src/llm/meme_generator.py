from groq import Groq

KEY_PATH = "/home/mglocadmin/Downloads/grok_api.txt"


def _get_client():
    with open(KEY_PATH, "r") as f:
        api_key = f.read().strip()
    return Groq(api_key=api_key)


PROMPT_TEMPLATE = """You are a meme writer for social media (Instagram, Reddit).

Given this trending topic: "{topic}"

Write ONE short, funny meme caption.
Under 15 words. No hashtags. No explanations. Just the caption.

Style:
- Dry, relatable humor
- Everyday things: salary, traffic, family, government, cricket
- No political bias, no offensive content

Caption:"""


def generate_caption(topic: str) -> str:
    """Generate a meme caption from a trending topic using Groq."""
    client = _get_client()
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
        temperature=0.9,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    test_topics = [
        "Rupee hits new low against dollar",
        "BESCOM power cut in Bangalore",
        "Supreme Court on Vande Mataram",
    ]
    for t in test_topics:
        print(f"Topic: {t}")
        print(f"Meme : {generate_caption(t)}")
        print("-" * 60)

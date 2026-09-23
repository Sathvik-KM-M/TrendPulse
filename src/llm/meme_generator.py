import random

# Simple templates — will be replaced by LLM later
TEMPLATES = [
    "When {topic} hits different",
    "Nobody:\nAbsolutely nobody:\n{topic}",
    "{topic}\n\nIndia's economy rn: 📉",
    "POV: You just read about {topic}",
    "Me pretending I understand {topic}",
    "Government: We are fixing {topic}\nCitizens: 😐",
]


def generate_caption(topic: str) -> str:
    """Generate a meme caption from a topic title."""
    template = random.choice(TEMPLATES)
    return template.format(topic=topic[:60])  # trim long titles


if __name__ == "__main__":
    test_topics = [
        "Rupee hits new low against dollar",
        "Ask India Thread",
        "Supreme Court on Vande Mataram",
    ]
    for t in test_topics:
        print(f"Topic: {t}")
        print(f"Meme : {generate_caption(t)}")
        print("-" * 50)

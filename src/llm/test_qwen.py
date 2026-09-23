from groq import Groq

with open("/home/mglocadmin/Downloads/grok_api.txt") as f:
    api_key = f.read().strip()

client = Groq(api_key=api_key)

prompt = """ನೀವು ಕನ್ನಡ ಸೋಶಿಯಲ್ ಮೀಡಿಯಾ ಮೀಮ್ ರೈಟರ್.

ವಿಷಯ: "ರೂಪಾಯಿ ಡಾಲರ್ ಎದುರು ಕುಸಿತ"

ಒಂದು ಚಿಕ್ಕ, ತಮಾಷೆಯ ಮೀಮ್ ಕ್ಯಾಪ್ಷನ್ ಬರೆಯಿರಿ (15 ಪದಗಳಿಗಿಂತ ಕಡಿಮೆ).
ಬರೀ ಕ್ಯಾಪ್ಷನ್ ಬರೆಯಿರಿ, ಬೇರೆ ಏನೂ ಇಲ್ಲ.

ಉದಾಹರಣೆ:
- "ಬೆಸ್ಕಾಂ ಪವರ್ ಕಟ್, ನನ್ನ ಲೈಫ್ ಕಟ್"
- "ಮೆಟ್ರೋ ದರ ಏರಿಸಿದ್ರು, ಜೇಬು ಖಾಲಿ"

ಕ್ಯಾಪ್ಷನ್:"""

response = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.9,
    max_tokens=300,
)

print(repr(response.choices[0].message.content))

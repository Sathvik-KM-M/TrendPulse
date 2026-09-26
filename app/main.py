import sys
import os

# Allow imports from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import random
from src.ingestion.reddit_ingester import get_trending_topics
from src.llm.meme_generator import generate_caption

# MUST be the first Streamlit command
st.set_page_config(page_title="TrendPulse", page_icon="🎭")

# Signature
st.markdown(
    "<p style='text-align: left; font-size: 14px; color: #888; margin-bottom: -10px;'>SKM</p>",
    unsafe_allow_html=True
)

# Fun fact (now after set_page_config)
FUN_FACTS = [
    "The word 'meme' was coined by biologist Richard Dawkins in 1976 — long before the internet existed.",
    "The first viral internet meme was a dancing baby animation in 1996.",
    "'Meme' comes from the Greek word 'mimema', meaning 'something imitated'.",
    "Dawkins later said internet memes were 'hijacking' his original idea.",
    "The 'Doge' meme's Shiba Inu was named Kabosu and lived until 2024.",
]
st.info(f"🧬 {random.choice(FUN_FACTS)}")

# Main content
st.title("🎭 TrendPulse")
st.caption("Live trends → AI-generated memes")

subreddit = st.selectbox("Pick a subreddit", ["india", "worldnews", "bengaluru", "cricket"])
limit = st.slider("How many memes?", 3, 10, 5)

if st.button("Generate Memes 🦁"):
    with st.spinner("Fetching trends and cooking memes..."):
        topics = get_trending_topics(subreddit=subreddit, limit=limit)

    for i, topic in enumerate(topics, 1):
        st.markdown(f"### {i}. {topic['title']}")
        meme = generate_caption(topic["title"])
        st.success(f"**Meme:** {meme}")
        st.markdown(f"[Read original]({topic['link']})")
        st.divider()

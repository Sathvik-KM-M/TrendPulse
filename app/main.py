import sys
import os

# Allow imports from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src.ingestion.reddit_ingester import get_trending_topics
from src.llm.meme_generator import generate_caption


st.set_page_config(page_title="TrendPulse", page_icon="🎭")

st.title("🎭 TrendPulse")
st.caption("Live trends → AI-generated memes")

subreddit = st.selectbox("Pick a subreddit", ["india", "worldnews", "bangalore", "cricket"])
limit = st.slider("How many memes?", 3, 10, 5)

if st.button("Generate Memes 🦁"):
    with st.spinner("Fetching trends and cooking memes..."):
        topics = get_trending_topics(subreddit=subreddit, limit=limit)

    for i, topic in enumerate(topics, 1):
        st.markdown(f"### {i}. {topic['title']}")
        meme = generate_caption(topic["title"])
        st.success(meme)
        st.markdown(f"[Read original]({topic['link']})")
        st.divider()

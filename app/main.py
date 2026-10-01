import sys
import os
import json
import random
from datetime import datetime

# Allow imports from src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(page_title="TrendPulse", page_icon="🎭")

# Bounce animation CSS
st.markdown("""
<style>
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}
.bouncing-emoji {
    display: inline-block;
    animation: bounce 1s infinite ease-in-out;
    font-size: 1.2em;
}
</style>
""", unsafe_allow_html=True)

# Signature
col1, col2 = st.columns([1, 11])
with col1:
    st.markdown(
        "<p style='font-size: 14px; color: #888; margin: 0;'>SKM</p>",
        unsafe_allow_html=True
    )

# Fun fact
FUN_FACTS = [
    "The word 'meme' was coined by biologist Richard Dawkins in 1976 — long before the internet existed.",
    "The first viral internet meme was a dancing baby animation in 1996.",
    "'Meme' comes from the Greek word 'mimema', meaning 'something imitated'.",
    "Dawkins later said internet memes were 'hijacking' his original idea.",
    "The 'Doge' meme's Shiba Inu was named Kabosu and lived until 2024.",
]
st.info(f"🧬 {random.choice(FUN_FACTS)}")

# Title with bouncing emoji
st.markdown(
    "<h1><span class='bouncing-emoji'>🎭</span> TrendPulse</h1>",
    unsafe_allow_html=True
)
st.caption("Live trends → AI-generated memes (streamed via Kafka)")

# Load memes
MEMES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "memes.jsonl")


def load_memes():
    """Read all memes from the JSONL file."""
    if not os.path.exists(MEMES_FILE):
        return []
    memes = []
    try:
        with open(MEMES_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        memes.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return []
    return memes


def get_last_updated(memes):
    """Return the timestamp of the most recent meme."""
    if not memes:
        return None
    timestamps = [m.get("processed_at", 0) for m in memes if m.get("processed_at")]
    if not timestamps:
        return None
    latest = max(timestamps)
    return datetime.fromtimestamp(latest).strftime("%b %d, %Y %H:%M")


all_memes = load_memes()

# ---------- Stats row ----------
if all_memes:
    last_updated = get_last_updated(all_memes)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total memes", len(all_memes))
    with col2:
        sources_count = len(set(m.get("source", "unknown") for m in all_memes))
        st.metric("Sources", sources_count)
    with col3:
        st.metric("Last updated", last_updated or "—")
else:
    st.warning("No memes yet. Run the Kafka producer and consumer to start streaming.")
    st.code(
        "# In two terminals:\n"
        "python -m src.ingestion.kafka_producer\n"
        "python -m src.processing.kafka_consumer",
        language="bash"
    )

# ---------- Source emojis ----------
SOURCE_EMOJI = {
    "india": "🇮🇳",
    "worldnews": "🌍",
    "bengaluru": "🏙️",
    "cricket": "🏏",
}

# ---------- Filters ----------
if all_memes:
    col_filter, col_search = st.columns([1, 2])

    with col_filter:
        found_sources = set(m.get("source", "unknown") for m in all_memes)
        all_sources = ["india", "worldnews", "bengaluru", "cricket"]
        sources = sorted(set(all_sources) | found_sources)

        display_options = ["🌐 all"] + [
            f"{SOURCE_EMOJI.get(s, '📌')} {s}" for s in sources
        ]
        selected_label = st.selectbox("Filter by source", display_options)
        selected = selected_label.split(" ", 1)[1]

    with col_search:
        query = st.text_input("Search memes", placeholder="e.g. cricket, salary...")

    # Apply filters
    if selected != "all":
        filtered = [m for m in all_memes if m.get("source") == selected]
    else:
        filtered = all_memes

    if query:
        q = query.lower()
        filtered = [
            m for m in filtered
            if q in m.get("meme", "").lower() or q in m.get("topic", "").lower()
        ]

    filtered = list(reversed(filtered))

    # Slider
    if len(filtered) == 0:
        st.info("No memes match your filters. Try a different search or source.")
    else:
        limit = st.slider(
            "How many to show?",
            3,
            min(50, len(filtered)),
            min(10, len(filtered))
        )

        # ---------- Meme list ----------
        for m in filtered[:limit]:
            st.markdown(f"**{m['topic']}**")
            emoji = m.get("emoji", "😂")
            st.markdown(
                f"""
                <div style='background-color: #d4edda; border-left: 4px solid #28a745;
                            padding: 10px; border-radius: 4px; color: #155724; margin: 8px 0;'>
                    <strong>Meme:</strong>
                    <span class='bouncing-emoji'>{emoji}</span> {m['meme']}
                </div>
                """,
                unsafe_allow_html=True
            )
            st.caption(f"[Read original]({m['link']}) · {m.get('source', 'unknown')}")
            st.divider()

# Refresh button
if st.button("🔄 Refresh"):
    st.rerun()
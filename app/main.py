import sys
import os
import random
from datetime import datetime

import json
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from deltalake import DeltaTable

# MUST be the first Streamlit command
st.set_page_config(page_title="TrendPulse", page_icon="🎭")

# ---------- Bounce animation ----------
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

# ---------- Paths ----------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SILVER_PATH = os.path.join(BASE_DIR, "delta", "silver", "memes")
GOLD_SOURCE_PATH = os.path.join(BASE_DIR, "delta", "gold", "source_stats")
GOLD_DAILY_PATH = os.path.join(BASE_DIR, "delta", "gold", "daily_stats")


# # ---------- Data loaders (no Spark) ----------
# @st.cache_data(ttl=30)
# def load_silver():
#     try:
#         return DeltaTable(SILVER_PATH).to_pandas()
#     except Exception as e:
#         print(f"[load_silver] failed: {e}")
#         return None


# @st.cache_data(ttl=30)
# def load_source_stats():
#     try:
#         return DeltaTable(GOLD_SOURCE_PATH).to_pandas()
#     except Exception as e:
#         print(f"[load_source_stats] failed: {e}")
#         return None


# @st.cache_data(ttl=30)
# def load_daily_stats():
#     try:
#         return DeltaTable(GOLD_DAILY_PATH).to_pandas()
#     except Exception as e:
#         print(f"[load_daily_stats] failed: {e}")
#         return None


@st.cache_data(ttl=30)
def load_silver():
    try:
        return DeltaTable(SILVER_PATH).to_pandas()
    except Exception:
        json_path = os.path.join(BASE_DIR, "data", "silver_sample.json")
        if os.path.exists(json_path):
            return pd.read_json(json_path)
        return None


@st.cache_data(ttl=30)
def load_source_stats():
    try:
        return DeltaTable(GOLD_SOURCE_PATH).to_pandas()
    except Exception:
        json_path = os.path.join(BASE_DIR, "data", "source_stats_sample.json")
        if os.path.exists(json_path):
            return pd.read_json(json_path)
        return None


@st.cache_data(ttl=30)
def load_daily_stats():
    try:
        return DeltaTable(GOLD_DAILY_PATH).to_pandas()
    except Exception:
        json_path = os.path.join(BASE_DIR, "data", "daily_stats_sample.json")
        if os.path.exists(json_path):
            return pd.read_json(json_path)
        return None
# ---------- Signature ----------
col1, col2 = st.columns([1, 11])
with col1:
    st.markdown(
        "<p style='font-size: 14px; color: #888; margin: 0;'>SKM</p>",
        unsafe_allow_html=True
    )

# ---------- Fun fact ----------
FUN_FACTS = [
    "The word 'meme' was coined by biologist Richard Dawkins in 1976.",
    "The first viral internet meme was a dancing baby animation in 1996.",
    "'Meme' comes from the Greek word 'mimema', meaning 'something imitated'.",
    "Dawkins later said internet memes were 'hijacking' his original idea.",
    "The 'Doge' meme's Shiba Inu was named Kabosu and lived until 2024.",
]
st.info(f"🧬 {random.choice(FUN_FACTS)}")

# ---------- Title ----------
st.markdown(
    "<h1><span class='bouncing-emoji'>🎭</span> TrendPulse</h1>",
    unsafe_allow_html=True
)
st.caption("Live trends → AI-generated memes (streamed via Kafka + PySpark + Delta Lake)")

# ---------- Load all data ----------
silver = load_silver()
source_stats = load_source_stats()
daily_stats = load_daily_stats()

# ---------- Section 1: Today's stats ----------
if daily_stats is not None and len(daily_stats) > 0:
    st.subheader("📊 Latest Stats")
    latest_day = daily_stats.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Memes today", int(latest_day["total_memes"]))
    col2.metric("Active sources", int(latest_day["sources_active"]))
    col3.metric("Top source", str(latest_day["top_source"]).title())
else:
    st.info("📊 Stats will appear once the pipeline processes data.")
    with st.expander("⚙️ Developer: build gold layer"):
        st.code("python -m src.processing.gold_worker", language="bash")

# ---------- Section 2: Source breakdown ----------
if source_stats is not None and len(source_stats) > 0:
    st.subheader("📈 Source Breakdown")
    for _, row in source_stats.iterrows():
        source = str(row["source"])
        emoji_map = {"india": "🇮🇳", "worldnews": "🌍", "bengaluru": "🏙️", "cricket": "🏏"}
        icon = emoji_map.get(source, "📌")
        with st.expander(f"{icon} {source.title()} — {int(row['total_memes'])} memes"):
            st.markdown(f"**Latest meme:** {row['latest_emoji']} {row['latest_meme']}")

# ---------- Section 3: Latest memes ----------
if silver is not None and len(silver) > 0:
    st.subheader("🎭 Latest Memes")

    source_filter = st.selectbox(
        "Filter by source",
        ["all"] + sorted(silver["source"].unique().tolist())
    )

    limit = st.slider("How many to show?", 3, min(50, len(silver)), 10)

    filtered = silver if source_filter == "all" else silver[silver["source"] == source_filter]
    filtered = filtered.sort_values("processed_at", ascending=False).head(limit)

    for _, row in filtered.iterrows():
        st.markdown(f"**{row['topic']}**")
        st.markdown(
            f"""
            <div style='background-color: #d4edda; border-left: 4px solid #28a745;
                        padding: 10px; border-radius: 4px; color: #155724; margin: 8px 0;'>
                <strong>Meme:</strong>
                <span class='bouncing-emoji'>{row['emoji']}</span> {row['meme']}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption(f"[Read original]({row['link']}) · {row['source']}")
        st.divider()
else:
    st.info("🎭 No memes yet — the pipeline is warming up.")
    st.caption("Memes will appear here as soon as new trends are processed.")
    with st.expander("⚙️ Developer: how to start the pipeline"):
        st.code(
            "python -m src.ingestion.kafka_producer\n"
            "python -m src.processing.spark_consumer\n"
            "python -m src.processing.silver_worker\n"
            "python -m src.processing.gold_worker",
            language="bash"
        )

if st.button("🔄 Refresh"):
    st.cache_data.clear()
    st.rerun()
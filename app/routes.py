import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.audio_downloader import process_video_url
from core.accent_analyzer import AccentAnalyzer


def analyze_accent_from_url(video_url: str):
    """
    Orchestrates the full analysis pipeline from video URL.

    Args:
        video_url (str): Direct MP4 or Loom link.

    Returns:
        dict: Analysis result with accent, confidence, etc.
    """
    st.info("Downloading and processing video...")

    try:
        # 1. Extract audio from video
        audio_path = process_video_url(video_url)

        # 2. Analyze accent
        analyzer = AccentAnalyzer()
        result = analyzer.analyze(audio_path)

        return result

    except Exception as e:
        st.error(f"❌ Error: {e}")
        print(f"🔴 Exception raised: {e}")

        return None

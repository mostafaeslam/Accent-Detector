import sys
import os
import streamlit as st
from PIL import Image
from routes import analyze_accent_from_url
import pandas as pd
import plotly.express as px
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Page Config ---
st.set_page_config(page_title="REMWaste Accent Detector", page_icon="♻️", layout="wide")

# --- Custom CSS for creativity and fit ---
st.markdown(
    """
    <style>
        body, .stApp {
            background: linear-gradient(120deg, #23272f 0%, #181c22 100%) !important;
        }
        section[data-testid="stSidebar"], .css-1d391kg, .css-1lcbmhc {
            background: linear-gradient(120deg, #23272f 0%, #181c22 100%) !important;
        }
        .rem-card {
            background: #23272f;
            border-radius: 18px;
            box-shadow: 0 4px 24px rgba(30, 40, 60, 0.18);
            padding: 2.5rem 2rem 2rem 2rem;
            margin-top: 1.5rem;
        }
        .rem-header {
            font-size: 2.7rem;
            color: #7CFC00;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        .rem-sub {
            font-size: 1.2rem;
            color: #b2ff59;
            margin-bottom: 1.5rem;
        }
        .rem-footer {
            color: #bbb;
            font-size: 1rem;
            margin-top: 2em;
        }
        .rem-badge {
            display: inline-block;
            padding: 0.3em 0.8em;
            border-radius: 12px;
            background: #1b5e20;
            color: #b2ff59;
            font-weight: 600;
            margin-left: 0.5em;
        }
        .rem-watermark {
            position: fixed;
            bottom: 2em;
            right: 2em;
            opacity: 0.08;
            z-index: 0;
        }
        /* Info box override for summary */
        .stAlert {
            background-color: #23272f !important;
            color: #b2ff59 !important;
            border-left: 6px solid #7CFC00 !important;
        }
        /* Download button style */
        .stDownloadButton button {
            background-color: #7CFC00 !important;
            color: #181c22 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            border: none !important;
            transition: background 0.2s;
        }
        .stDownloadButton button:hover {
            background-color: #b2ff59 !important;
            color: #181c22 !important;
        }
        /* Headings for transcript and summary */
        .rem-section-title {
            font-size: 1.4rem;
            color: #7CFC00;
            font-weight: 700;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            display: flex;
            align-items: center;
        }
        .rem-section-title .emoji {
            margin-right: 0.5em;
        }
        /* Chart background */
        .element-container .stPlotlyChart, .element-container .stAltairChart, .element-container .stVegaLiteChart, .element-container .stBarChart {
            background: #23272f !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar ---
with st.sidebar:
    logo_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../images/REMWaste.png")
    )
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    st.markdown(
        "<h3 style='color:#2E7D32;'>REMWaste English Accent Detection</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size: 1rem;'>Empowering communication in global waste management.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "Try a sample video: [British Accent](https://www.youtube.com/watch?v=swb7lMQHkVE)"
    )
    st.markdown("Contact: [info@remwaste.com](mailto:info@remwaste.com)")

# --- Header ---
st.markdown(
    "<div class='rem-header' style='text-align:center;'>🎙️ REMWaste Accent Detector</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='rem-sub' style='text-align:center;'>Upload a video URL and detect the speaker's English accent. Powered by AI for the waste management industry.</div>",
    unsafe_allow_html=True,
)

# --- Input & Output Columns ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.markdown("#### 📥 Enter Public Video URL")
    video_url = st.text_input(
        "",
        placeholder="https://example.com/video.mp4",
        help="Paste a public video URL (e.g., YouTube, Loom, MP4)",
    )
    if st.button("🚀 Analyze", use_container_width=True):
        st.session_state["analyze"] = True
        st.session_state["video_url"] = video_url
    if st.button("🎬 Try Demo", use_container_width=True):
        st.session_state["analyze"] = True
        st.session_state["video_url"] = "https://www.youtube.com/watch?v=swb7lMQHkVE"

with col2:
    if (
        st.session_state.get("analyze")
        and st.session_state.get("video_url", "").strip()
    ):
        with st.spinner("🚧 Analyzing the video..."):
            result = analyze_accent_from_url(st.session_state["video_url"])

        if result:
            st.markdown("<div class='rem-card'>", unsafe_allow_html=True)
            st.success("✅ Accent Analysis Complete")

            # Handle uncertain predictions
            if result["accent"] == "Uncertain":
                st.warning("⚠️ The accent could not be determined with high confidence")
                st.markdown(
                    "<h4>🤔 Result: <span class='rem-badge' style='background:#fff3e0;color:#e65100'>Uncertain</span></h4>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<h4>🗣️ Accent Detected: <span class='rem-badge'>{result['accent']}</span></h4>",
                    unsafe_allow_html=True,
                )

            # Show confidence with color coding
            confidence = result["confidence"]
            confidence_color = (
                "#4caf50"
                if confidence >= 70
                else "#fbc02d" if confidence >= 40 else "#f44336"
            )
            st.markdown(
                f"<p>🎯 <b>Confidence:</b> <span class='rem-badge' style='background:{confidence_color}20;color:{confidence_color}'>{confidence}%</span></p>",
                unsafe_allow_html=True,
            )

            # Language detection with improved styling
            st.markdown(
                f"<p>🌐 <b>Language Detected:</b> <span class='rem-badge' style='background:#e3f2fd;color:#1976d2'>{result['language']}</span> ({result['language_score']}% sure)</p>",
                unsafe_allow_html=True,
            )

            # Accent scores visualization
            st.markdown("### 📊 Accent Probability Distribution")

            # Define accent colors for consistency
            accent_colors = {
                "US": "#2196f3",
                "UK": "#4caf50",
                "Australia": "#ff9800",
                "Canada": "#e91e63",
                "India": "#9c27b0",
                "African": "#ff5722",
                "Others": "#607d8b",
            }

            scores_df = pd.DataFrame(
                result["all_scores"].items(), columns=["Accent", "Probability"]
            ).sort_values("Probability", ascending=False)

            # Create a more appealing chart with consistent colors
            fig = px.bar(
                scores_df,
                x="Accent",
                y="Probability",
                color="Accent",
                color_discrete_map=accent_colors,
                title="Accent Confidence Distribution",
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#b2ff59",
                showlegend=True,
                legend_title_text="Accents",
                xaxis_title="Accent Type",
                yaxis_title="Confidence (%)",
                title_x=0.5,
                bargap=0.2,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add accent description
            accent_descriptions = {
                "US": "American English accent, commonly found in the United States",
                "UK": "British English accent, typical of the United Kingdom",
                "Australia": "Australian English accent",
                "Canada": "Canadian English accent",
                "India": "Indian English accent, influenced by Indian languages",
                "African": "African English accent, varies by region",
                "Others": "Other English accents not in the main categories",
            }

            if result["accent"] != "Uncertain":
                st.markdown("#### 📚 About this Accent")
                st.info(
                    accent_descriptions.get(
                        result["accent"], "No description available"
                    )
                )

            # Transcript and summary sections
            st.markdown(
                "<div class='rem-section-title'><span class='emoji'>📝</span>Transcript</div>",
                unsafe_allow_html=True,
            )
            st.code(result["transcript"], language="text")

            st.markdown(
                "<div class='rem-section-title'><span class='emoji'>📄</span>Summary</div>",
                unsafe_allow_html=True,
            )
            st.info(result["summary"])

            # Enhanced report download
            report_content = f"""REMWaste Accent Analysis Report
            
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Video URL: {st.session_state["video_url"]}

RESULTS
-------
Detected Accent: {result['accent']}
Confidence: {result['confidence']}%
Language: {result['language']} ({result['language_score']}% confidence)

Accent Probability Distribution:
{scores_df.to_string()}

TRANSCRIPT
----------
{result["transcript"]}

SUMMARY
-------
{result["summary"]}
"""
            st.download_button(
                "📥 Download Detailed Report",
                report_content,
                file_name=f"accent_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            )
            st.markdown("</div>", unsafe_allow_html=True)
        st.session_state["analyze"] = False
    elif st.session_state.get("analyze"):
        st.warning("⚠️ Please enter a valid video URL.")
        st.session_state["analyze"] = False

# --- Watermark (optional) ---
if os.path.exists(logo_path):
    st.markdown(
        f"<img src='file://{logo_path}' class='rem-watermark' width='200'>",
        unsafe_allow_html=True,
    )

# --- Footer ---
st.markdown(
    """
    <hr style='margin-top:2em;'>
    <center><span class='rem-footer'>Made with ❤️ by REMWaste AI Team</span></center>
    """,
    unsafe_allow_html=True,
)

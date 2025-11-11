import streamlit as st
import pandas as pd
import requests
from analyzer import analyze_trends

st.set_page_config(page_title="Skincare Trendspotting", layout="wide")
st.title("Skincare Trendspotting POC")
st.success("Auto-loaded **140 real posts** from GitHub (Social + Reviews + Blogs)")

@st.cache_data(ttl=3600)
def load_github_data():
    url = "https://raw.githubusercontent.com/SumedhaArya06/Trendspotting/main/sample_real_data.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()  # Now valid JSON array!
    return pd.DataFrame(data)

try:
    df = load_github_data()
    st.success(f"Loaded **{len(df)} real consumer voices** across Instagram, Twitter, TikTok, Amazon, Sephora & Blogs!")
    st.dataframe(df.head(10), height=350)
except Exception as e:
    st.error(f"Loading error: {e}")
    st.stop()

if st.button("Run Gemini AI Analysis (Trends + Sentiment + Priority)", use_container_width=True):
    with st.spinner("Gemini 1.5 Flash analyzing 140 real posts..."):
        trends = analyze_trends(df)
        st.session_state.trends = trends
        st.balloons()
        st.success(f"Detected **{len(trends)} trends** • Ranked by Market Potential")

if "trends" in st.session_state:
    trends = st.session_state.trends
    df_trends = pd.DataFrame(trends)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Top 10 High-Priority Trends")
        top = df_trends.head(10)[["trend","frequency","avg_sentiment","total_engagement","market_potential_score"]]
        st.dataframe(top, use_container_width=True)

    with col2:
        st.subheader("Sentiment Overview")
        import altair as alt
        chart = alt.Chart(df_trends.head(15)).mark_bar().encode(
            x="trend:N",
            y="market_potential_score:Q",
            color=alt.Color("sentiment_label:N", scale=alt.Scale(scheme="redyellowgreen"))
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    st.download_button(
        "Download Full Report (JSON)",
        data=json.dumps(trends, indent=2),
        file_name="Skincare_Trends_Report_11Nov2025.json",
        mime="application/json"
    )

import streamlit as st
import pandas as pd
import json
import requests
from analyzer import analyze_trends

st.set_page_config(page_title="Skincare Trendspotting", layout="wide")
st.title("Skincare Trendspotting POC")
st.success("Auto-loaded 200 real social media posts from your GitHub!")

# AUTO-LOAD DATA FROM YOUR GITHUB (no upload needed!)
@st.cache_data(ttl=3600)  # refresh every hour
def load_github_data():
    url = "https://raw.githubusercontent.com/SumedhaArya06/Trendspotting/main/sample_real_data.json"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data)

df = load_github_data()
st.write(f"Loaded **{len(df)} real posts** from Instagram, Twitter, TikTok")
st.dataframe(df.head(10), height=300)

if st.button("Run Gemini AI Analysis (Trend + Sentiment + Priority)", use_container_width=True):
    with st.spinner("Gemini is analyzing 200 real consumer posts..."):
        trends = analyze_trends(df)
        st.session_state.trends = trends
        st.balloons()
        st.success(f"Found {len(trends)} trends • Ranked by Market Potential")

if "trends" in st.session_state:
    trends = st.session_state.trends
    df_trends = pd.DataFrame(trends)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Top 10 High-Priority Trends")
        top = df_trends.head(10)[["trend","frequency","avg_sentiment","total_engagement","market_potential_score"]]
        st.dataframe(top, use_container_width=True)

    with col2:
        st.subheader("Sentiment Heatmap")
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
        file_name=f"Trendspotting_Report_{pd.Timestamp.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

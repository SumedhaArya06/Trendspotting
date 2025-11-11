import streamlit as st
import pandas as pd
import json
from data_loader import load_data
from analyzer import analyze_trends

st.set_page_config(page_title="Skincare Trendspotting", layout="wide")
st.title(" Skincare Trendspotting POC")
st.markdown("Upload your **real** social-media JSON/CSV → get trends + sentiment + priority score")

# File upload
uploaded = st.file_uploader("Choose JSON or CSV", type=["json", "csv"])

if uploaded:
    df = load_data(uploaded)
    st.success(f"Loaded {len(df)} real posts")
    st.dataframe(df.head(10))

    if st.button(" Run Gemini Analysis"):
        with st.spinner("Gemini is reading consumer voice..."):
            trends = analyze_trends(df)
            st.session_state.trends = trends
            st.balloons()

if "trends" in st.session_state:
    trends = st.session_state.trends
    df_trends = pd.DataFrame(trends)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Top 10 Trends by Market Potential")
        st.dataframe(df_trends.head(10)[["trend","frequency","avg_sentiment","total_engagement","market_potential_score"]])

    with col2:
        st.subheader("Sentiment Distribution")
        import altair as alt
        chart = alt.Chart(df_trends).mark_bar().encode(
            x="trend:N",
            y="market_potential_score:Q",
            color=alt.Color("sentiment_label:N", scale=alt.Scale(scheme="set2"))
        )
        st.altair_chart(chart, use_container_width=True)

    st.download_button(
        " Download Full Report",
        data=json.dumps(trends, indent=2),
        file_name="skincare_trends_report.json",
        mime="application/json"
    )

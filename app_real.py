# app_real.py
import streamlit as st
import pandas as pd
import json
import altair as alt
from real_data_trend_analyzer import load_real_data, analyze_with_gemini

st.set_page_config(page_title="Skincare Trendspotting LIVE", layout="wide")
st.title("AI-Powered Skincare Trendspotting")
st.subheader("Real Social Media Data • Gemini 1.5 Flash • Live Sentiment & Engagement")

# Upload your real data
uploaded_file = st.file_uploader("Upload your real data (JSON or CSV)", type=['json', 'csv'])

if uploaded_file:
    df = load_real_data(uploaded_file)
    st.success(f"Loaded {len(df)} real posts from {df['platform'].nunique()} platforms")
    st.dataframe(df.head())

    if st.button("Run AI Trend + Sentiment Analysis"):
        with st.spinner("Gemini is analyzing real consumer voice..."):
            trends = analyze_with_gemini(df)
            st.session_state.trends = trends
            
            # Save
            with open("REAL_trends_report.json", "w") as f:
                json.dump(trends, f, indent=2)
            
            st.balloons()
            st.success(f"Found {len(trends)} trends • Ranked by Market Potential")

    if 'trends' in st.session_state:
        trends = st.session_state.trends
        df_trends = pd.DataFrame(trends)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Top 10 Trends by Market Potential")
            top = df_trends.head(10)
            st.dataframe(top[['trend', 'frequency', 'avg_sentiment', 'total_engagement', 'market_potential_score']], use_container_width=True)

        with col2:
            st.subheader("Sentiment Overview")
            chart = alt.Chart(df_trends).mark_bar().encode(
                x='trend:N',
                y='market_potential_score:Q',
                color=alt.Color('sentiment_label:N', scale=alt.Scale(domain=['Very Negative','Negative','Neutral','Positive','Very Positive'],
                range=['#e74c3c','#e67e22','#95a5a6','#27ae60','#2ecc71']))
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

        st.download_button(
            "Download Full Report",
            data=json.dumps(trends, indent=2),
            file_name=f"skincare_trends_{datetime.now().strftime('%Y%m%d')}.json"
        )

        st.write("### All Trends")
        st.dataframe(df_trends, use_container_width=True)

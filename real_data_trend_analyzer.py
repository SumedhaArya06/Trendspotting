# real_data_trend_analyzer.py
import pandas as pd
import json
import google.generativeai as genai
from datetime import datetime
import streamlit as st

# Configure Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # or use sidebar input
model = genai.GenerativeModel('gemini-1.5-flash')

def load_real_data(file_path_or_json):
    """Load your real JSON/CSV data"""
    if isinstance(file_path_or_json, str):
        if file_path_or_json.endswith('.json'):
            with open(file_path_or_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path_or_json.endswith('.csv'):
            df = pd.read_csv(file_path_or_json)
            data = df.to_dict(orient='records')
    else:
        data = file_path_or_json  # direct list of dicts
    return pd.DataFrame(data)

def analyze_with_gemini(df, batch_size=12):
    texts = []
    for _, row in df.iterrows():
        text = row['text']
        platform = row.get('platform', 'unknown')
        engagement = row.get('engagement', {})
        likes = engagement.get('likes', 0) + engagement.get('retweets', 0) + engagement.get('shares', 0)
        comments = engagement.get('comments', 0)
        total_engagement = likes + comments * 3  # weight comments higher
        
        texts.append({
            "id": row['id'],
            "text": text,
            "platform": platform,
            "date": row['date'],
            "engagement_score": total_engagement,
            "original": row
        })
    
    all_results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_str = "\n".join([f"{j+1}. [{b['platform']}] {b['text']}" for j, b in enumerate(batch)])
        
        prompt = f"""
You are a senior beauty trend analyst for a leading skincare brand.

Analyze these {len(batch)} real social media posts from Instagram, Twitter, TikTok.

For EACH post:
- Extract ALL skincare trends mentioned (e.g., slugging, ceramides, skin cycling, niacinamide)
- For each trend in a post, give:
  - sentiment_score: -1.0 to +1.0
  - sentiment_label: Very Negative | Negative | Neutral | Positive | Very Positive

Return STRICT JSON:
[
  {{
    "post_id": "SM001",
    "trends": [
      {{
        "trend": "slugging",
        "sentiment_score": 0.9,
        "sentiment_label": "Very Positive"
      }}
    ]
  }}
]
Posts:
{batch_str}
"""
        try:
            response = model.generate_content(prompt)
            cleaned = response.text.strip().strip("```json").strip("```")
            batch_result = json.loads(cleaned)
            all_results.extend(batch_result)
        except Exception as e:
            st.error(f"Gemini error: {e}")
            continue
    
    # Aggregate by trend
    trend_map = {}
    for item in all_results:
        post_id = item['post_id']
        post_data = next((x for x in texts if x['id'] == post_id), None)
        if not post_data: continue
        
        for t in item['trends']:
            trend = t['trend'].lower().strip()
            if trend not in trend_map:
                trend_map[trend] = {
                    "trend": t['trend'],
                    "mentions": [],
                    "total_engagement": 0
                }
            trend_map[trend]["mentions"].append({
                "post_id": post_id,
                "text": post_data['text'][:120] + "...",
                "platform": post_data['platform'],
                "sentiment_score": t['sentiment_score'],
                "sentiment_label": t['sentiment_label'],
                "engagement": post_data['engagement_score']
            })
            trend_map[trend]["total_engagement"] += post_data['engagement_score']
    
    # Final output
    final_trends = []
    for trend, data in trend_map.items():
        mentions = data['mentions']
        freq = len(mentions)
        avg_sentiment = sum(m['sentiment_score'] for m in mentions) / freq
        sentiment_label = (
            "Very Positive" if avg_sentiment >= 0.6 else
            "Positive" if avg_sentiment >= 0.2 else
            "Neutral" if avg_sentiment >= -0.2 else
            "Negative" if avg_sentiment >= -0.6 else
            "Very Negative"
        )
        market_potential = freq * avg_sentiment * (data['total_engagement'] / max(1, sum(t['total_engagement'] for t in trend_map.values())))
        
        final_trends.append({
            "trend": data['trend'],
            "frequency": freq,
            "avg_sentiment": round(avg_sentiment, 3),
            "sentiment_label": sentiment_label,
            "total_engagement": data['total_engagement'],
            "market_potential_score": round(market_potential, 2),
            "platforms": list(set(m['platform'] for m in mentions)),
            "sample_posts": [m['text'] for m in mentions[:3]]
        })
    
    final_trends.sort(key=lambda x: x['market_potential_score'], reverse=True)
    return final_trends

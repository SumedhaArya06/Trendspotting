import google.generativeai as genai
import json
import streamlit as st

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY") or st.text_input("Gemini API Key", type="password"))

model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_trends(df, batch_size=10):
    texts = []
    for _, row in df.iterrows():
        engagement = row.get("engagement", {})
        likes = sum(v for k,v in engagement.items() if "like" in k.lower() or k=="likes")
        comments = sum(v for k,v in engagement.items() if "comment" in k.lower())
        total = likes + comments*3
        texts.append({
            "id": row["id"],
            "text": row["text"],
            "platform": row.get("platform", "unknown"),
            "engagement": total
        })

    all_results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_str = "\n".join([f"{j+1}. [{b['platform']}] {b['text']}" for j, b in enumerate(batch)])

        prompt = f"""
Analyze these real skincare posts. Extract every trend mentioned.
For each trend in each post give sentiment_score (-1.0 to +1.0) and sentiment_label.
Return ONLY JSON array:
[
  {{"post_id": "SM001", "trends": [{{"trend": "slugging", "sentiment_score": 0.9, "sentiment_label": "Very Positive"}}]}}
]
Posts:
{batch_str}
"""
        try:
            resp = model.generate_content(prompt)
            cleaned = resp.text.strip("```json").strip("```")
            all_results.extend(json.loads(cleaned))
        except Exception as e:
            st.error(f"Gemini error: {e}")

    # Aggregate
    trend_dict = {}
    for item in all_results:
        post = next(p for p in texts if p["id"] == item["post_id"])
        for t in item["trends"]:
            name = t["trend"].lower()
            if name not in trend_dict:
                trend_dict[name] = {"trend": t["trend"], "mentions": [], "engagement": 0}
            trend_dict[name]["mentions"].append({
                "score": t["sentiment_score"],
                "label": t["sentiment_label"]
            })
            trend_dict[name]["engagement"] += post["engagement"]

    final = []
    for name, data in trend_dict.items():
        freq = len(data["mentions"])
        avg_sent = sum(m["score"] for m in data["mentions"]) / freq
        label = "Very Positive" if avg_sent >= 0.6 else "Positive" if avg_sent >= 0.2 else "Neutral" if avg_sent >= -0.2 else "Negative" if avg_sent >= -0.6 else "Very Negative"
        potential = freq * avg_sent * (data["engagement"] / 100)
        final.append({
            "trend": data["trend"],
            "frequency": freq,
            "avg_sentiment": round(avg_sent, 3),
            "sentiment_label": label,
            "total_engagement": data["engagement"],
            "market_potential_score": round(potential, 2)
        })

    final.sort(key=lambda x: x["market_potential_score"], reverse=True)
    return final

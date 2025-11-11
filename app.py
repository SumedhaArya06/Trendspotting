@st.cache_data(ttl=3600)
def load_github_data():
    url = "https://raw.githubusercontent.com/SumedhaArya06/Trendspotting/main/sample_real_data.json"
    response = requests.get(url)
    response.raise_for_status()
    raw_text = response.text.strip()
    
    # FIX ANY JSON FORMAT
    if raw_text.startswith('['):
        data = json.loads(raw_text)
    elif raw_text.startswith('{'):
        # If it's {"data": [...]} or single object
        parsed = json.loads(raw_text)
        if "data" in parsed:
            data = parsed["data"]
        else:
            data = [parsed]
    else:
        # Fallback: manual fix for broken multi-object JSON
        raw_text = raw_text.strip()
        if not raw_text.startswith('['):
            raw_text = '[' + raw_text.replace('}\n{', '},\n{') + ']'
        data = json.loads(raw_text)
    
    return pd.DataFrame(data)

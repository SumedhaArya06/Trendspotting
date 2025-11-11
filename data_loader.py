import pandas as pd
import json

def load_data(uploaded_file):
    if uploaded_file.name.endswith(".json"):
        data = json.load(uploaded_file)
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(uploaded_file)
    return df

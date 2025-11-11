import pandas as pd
import google.generativeai as genai
import json
import random
from datetime import datetime
import streamlit as st

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def load_real_data(file_path_or_Json):
  if isinstance(file_path_or_Json, str):
    if file_path_or_Json.endswith('.json'):
      with open(file_path_or_Json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    elif file_path_or_Json.endswith('.csv'):
      df = pd.read_csv(file_path_or_Json)
      data=df.to_dict(orient='records')    
    else:
      data = file_path_or_Json
    return pd.DataFrame(data)

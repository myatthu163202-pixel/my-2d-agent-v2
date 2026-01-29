import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", page_icon="💰", layout="wide")

sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

try:
    # Cache မငြိအောင် အချိန်ထည့်ပြီး ဖတ်ပါမည်
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# --- SIDEBAR (အကုန်ဖျက်ရန်) ---
st.sidebar.header("⚠️ စီမံခန့်ခွဲရန်")
all_del_pw = st.sidebar.text_input("Password ရိုက်ပါ", type="password")

if st.sidebar.button("🗑 စာရင်းအားလုံး ရှင်းလင်းမည်"):
    if all_del_pw == "1234": # Password က 1234 ပါ
        with st.spinner('ရှင်းလင်းနေပါသည်...'):
            requests.post(script_url, json={"action": "clear_all"})
            st.rerun()
    else:
        st.sidebar.error("Password မှားနေပါသည်။")

# --- MAIN UI ---
st.title("💰 2D Professional Agent")
st.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['Amount'].sum() if not df.empty else 0:,.0f} Ks")
st.dataframe(df.iloc[::-1], use_container_width=True)

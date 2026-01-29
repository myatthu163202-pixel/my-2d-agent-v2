import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", layout="wide")

sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# SIDEBAR
st.sidebar.header("⚙️ Admin Controls")
del_pw = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("🗑 အကုန်ဖျက်မည်"):
    if del_pw == "1632022":
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

# MAIN UI
st.title("💰 2D Agent Professional")
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်း")
    with st.form("entry", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                payload = {"action": "insert", "Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=payload)
                st.rerun()

with c2:
    st.subheader("🔍 စာရင်းကြည့်ရန်")
    if not df.empty:
        for i, r in df.iloc[::-1].iterrows():
            with st.expander(f"👤 {r['Customer']} | 🔢 {r['Number']} | 💵 {r['Amount']} Ks"):
                if st.button("🗑 ဖျက်ရန်", key=f"d_{i}"):
                    requests.post(script_url, json={"action": "delete", "Customer": r['Customer'], "Number": str(r['Number']), "Time": r['Time']})
                    st.rerun()
    else:
        st.info("စာရင်းမရှိသေးပါ။")

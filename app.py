import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Professional Agent", page_icon="💰", layout="wide")

# Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# Data Loading
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# SIDEBAR
st.sidebar.header("⚙️ Admin Controls")
win_num = st.sidebar.text_input("🏆 ပေါက်ဂဏန်း", max_chars=2)
comm = st.sidebar.slider("ကော်မရှင် (%)", 0, 20, 10)

if not df.empty:
    sales = df['Amount'].sum()
    net = sales * (1 - comm/100)
    st.sidebar.write(f"စုစုပေါင်း: {sales:,.0f} Ks")
    if win_num:
        payout = df[df['Number'] == win_num]['Amount'].sum() * 80
        st.sidebar.warning(f"အမြတ်/အရှုံး: {net - payout:,.0f} Ks")

st.sidebar.divider()
del_pw = st.sidebar.text_input("Admin Password", type="password")
if st.sidebar.button("🗑 အကုန်ဖျက်မည်"):
    if del_pw == "1632022": # Password ကို သေချာစစ်ပါ
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

# MAIN UI
st.title("💰 2D Agent Pro")
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်း")
    with st.form("entry", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                # action: "insert" ကို သေချာထည့်ထားပါတယ်
                payload = {"action": "insert", "Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=payload)
                st.rerun()

with c2:
    st.subheader("🔍 စာရင်းကြည့်ရန်")
    search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
    view_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
    for i, r in view_df.iloc[::-1].iterrows():
        with st.expander(f"👤 {r['Customer']} | 🔢 {r['Number']} | 💵 {r['Amount']} Ks"):
            if st.button("🗑 ဖျက်ရန်", key=f"d_{i}"):
                requests.post(script_url, json={"action": "delete", "Customer": r['Customer'], "Number": str(r['Number']), "Time": r['Time']})
                st.rerun()

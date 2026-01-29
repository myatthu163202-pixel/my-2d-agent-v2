import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Professional", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာ ဖတ်ယူခြင်း
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Sidebar - စာရင်းအားလုံး ရှင်းလင်းရန်
st.sidebar.header("⚙️ Admin Panel")
del_pw = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("🗑 စာရင်းအားလုံး ရှင်းလင်းမည်"):
    if del_pw == "1632022": # Password ကို သေချာမှတ်ထားပါ
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

st.title("💰 2D Agent Pro")
c1, c2 = st.columns([1, 2])

# စာရင်းသွင်းရန် အပိုင်း
with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းဆည်းမည်"):
            if name and num:
                payload = {
                    "action": "insert",
                    "Customer": name,
                    "Number": str(num).zfill(2),
                    "Amount": int(amt),
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                requests.post(script_url, json=payload)
                st.rerun()

# စာရင်းကြည့်ရန် နှင့် တစ်ခုချင်း ဖျက်ရန် အပိုင်း
with c2:
    st.subheader("🔍 စာရင်းကြည့်ရန်")
    if not df.empty:
        search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
        view_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        for i, r in view_df.iloc[::-1].iterrows():
            with st.expander(f"👤 {r['Customer']} | 🔢 {r['Number']} | 💵 {r['Amount']} Ks"):
                if st.button("🗑 ဤစာရင်းကိုဖျက်ရန်", key=f"del_{i}"):
                    requests.post(script_url, json={
                        "action": "delete",
                        "Customer": r['Customer'],
                        "Number": str(r['Number']),
                        "Time": r['Time']
                    })
                    st.rerun()
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")

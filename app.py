import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", page_icon="💰", layout="wide")

sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# SIDEBAR
st.sidebar.header("⚙️ Control Panel")
if st.sidebar.button("🗑 စာရင်းအားလုံးဖျက်မည်"):
    # Password ရိုက်တဲ့နေရာ ပေါ်လာပါမယ်
    st.sidebar.warning("သတိ - အကုန်ပျက်သွားပါလိမ့်မည်")

# Password ရိုက်သည့်နေရာ
pw = st.sidebar.text_input("Password ရိုက်ပါ", type="password")

if st.sidebar.button("အတည်ပြုသည်"):
    if pw == "1234": # Password က 1234 ပါ
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

# MAIN UI
st.title("💰 2D Agent Pro")
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("Customer Name")
        num = st.text_input("Number", max_chars=2)
        amt = st.number_input("Amount", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                new_data = {"action": "insert", "Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=new_data)
                st.rerun()

with col2:
    st.subheader("🔍 စာရင်းများ")
    st.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['Amount'].sum():,.0f} Ks")
    for index, row in df.iloc[::-1].iterrows():
        with st.expander(f"👤 {row['Customer']} | 🔢 {row['Number']} | 💵 {row['Amount']} Ks"):
            if st.button(f"🗑 ဖျက်ရန်", key=f"del_{index}"):
                del_payload = {"action": "delete", "Customer": row['Customer'], "Number": str(row['Number']), "Time": row['Time']}
                requests.post(script_url, json=del_payload)
                st.rerun()

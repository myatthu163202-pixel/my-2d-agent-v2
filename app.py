import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", page_icon="💰", layout="wide")

sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# Data Loading
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Main UI
st.title("💰 2D Agent Pro (With Delete Function)")

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
    search_query = st.text_input("🔎 ရှာရန်", placeholder="နာမည်ရိုက်ပါ...")
    
    display_df = df.copy()
    if search_query:
        display_df = display_df[display_df['Customer'].str.contains(search_query, case=False, na=False)]
    
    # စာရင်းတစ်ခုချင်းစီကို ဖျက်လို့ရအောင် Loop ပတ်ပြမယ်
    for index, row in display_df.iloc[::-1].iterrows():
        with st.expander(f"👤 {row['Customer']} | 🔢 {row['Number']} | 💵 {row['Amount']} Ks"):
            st.write(f"အချိန်: {row['Time']}")
            if st.button(f"🗑 ဖျက်ရန် ({row['Customer']})", key=f"del_{index}"):
                del_data = {
                    "action": "delete",
                    "Customer": row['Customer'],
                    "Number": str(row['Number']),
                    "Time": row['Time']
                }
                with st.spinner('ဖျက်နေပါသည်...'):
                    res = requests.post(script_url, json=del_data)
                    if res.text == "Deleted":
                        st.success("ဖျက်ပြီးပါပြီ!")
                        st.rerun()

st.sidebar.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['Amount'].sum():,.0f} Ks")

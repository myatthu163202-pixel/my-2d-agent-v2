import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", page_icon="💰", layout="wide")

# Secrets များယူခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာဖတ်ခြင်း
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2)
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

st.title("💰 2D Professional Agent")

# Sidebar - ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("🏆 ပေါက်ဂဏန်းတိုက်ရန်")
win_num = st.sidebar.text_input("ဂဏန်းရိုက်ပါ", max_chars=2)
if win_num:
    winners = df[df['Number'] == win_num]
    if not winners.empty:
        st.sidebar.success(f"ပေါက်သူ {len(winners)} ဦး!")
        st.sidebar.warning(f"လျော်ကြေး: {winners['Amount'].sum() * 80:,.0f} Ks")

# Main Form
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("Customer Name")
        num = st.text_input("Number", max_chars=2)
        amt = st.number_input("Amount", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                new_data = {"Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=new_data)
                st.rerun()

with col2:
    st.subheader("🔍 ရှာဖွေရန်")
    search = st.text_input("🔎 နာမည်ဖြင့် ရှာရန်")
    display_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
    st.metric("စုစုပေါင်း ရောင်းရငွေ", f"{display_df['Amount'].sum():,.0f} Ks")
    st.dataframe(display_df.iloc[::-1], use_container_width=True)

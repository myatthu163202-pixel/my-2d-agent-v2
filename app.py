import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro", page_icon="💰", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #FF4B4B; color: white; }
    h1 { color: #1E3A8A; text-align: center; }
    .highlight { background-color: #e8f4fd; padding: 10px; border-radius: 10px; border-left: 5px solid #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 2D Agent Pro (Search & Winner System)")

# Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# Data Loading
try:
    df = pd.read_csv(f"{csv_url}&cachebuster={datetime.now().timestamp()}")
    df['Number'] = df['Number'].astype(str).str.zfill(2) # ဂဏန်းတွေကို ၀၀ ပုံစံပြောင်းမယ်
except:
    df = pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# Sidebar - ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("🏆 Winner Checker")
win_num = st.sidebar.text_input("ပေါက်ဂဏန်း ရိုက်ပါ", max_chars=2, placeholder="ဥပမာ - 85")

if win_num:
    winners = df[df['Number'] == win_num]
    if not winners.empty:
        st.sidebar.success(f"ဂုဏ်ယူပါတယ်! {len(winners)} ဦး ပေါက်ပါသည်။")
        st.sidebar.dataframe(winners[['Customer', 'Amount']])
        total_payout = winners['Amount'].sum() * 80 # ၈၀ ဆနဲ့ တွက်ပြတာပါ
        st.sidebar.warning(f"စုစုပေါင်း လျော်ကြေး: {total_payout:,.0f} Ks")
    else:
        st.sidebar.error("ပေါက်သူမရှိပါ။")

# Main UI
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("👤 Customer Name")
        num = st.text_input("🔢 Number (2D)", max_chars=2)
        amt = st.number_input("💵 Amount", min_value=100, step=100)
        if st.form_submit_button("✅ သိမ်းမည်"):
            if name and num:
                new_data = {"Customer": name, "Number": str(num).zfill(2), "Amount": int(amt), "Time": datetime.now().strftime("%I:%M %p")}
                requests.post(script_url, json=new_data)
                st.rerun()

with col2:
    st.subheader("🔍 စာရင်းရှာရန်/ကြည့်ရန်")
    
    # နာမည်ဖြင့်ရှာရန် Search Bar
    search_query = st.text_input("🔎 နာမည်ဖြင့် ရှာရန်", placeholder="ရှာလိုသော နာမည်ရိုက်ပါ...")
    
    display_df = df.copy()
    if search_query:
        display_df = display_df[display_df['Customer'].str.contains(search_query, case=False, na=False)]
    
    # Dashboard
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("စုစုပေါင်း ရောင်းရငွေ", f"{df['Amount'].sum():,.0f} Ks")
    kpi2.metric("လက်မှတ်အရေအတွက်", len(df))
    
    st.dataframe(display_df.iloc[::-1], use_container_width=True, height=400)

import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="2D Agent Pro", layout="wide")

# Secrets Link စစ်ဆေးခြင်း
if "connections" not in st.secrets:
    st.error("Secrets မရှိသေးပါ။ Settings > Secrets မှာ Link တွေအရင်ထည့်ပါ")
    st.stop()

sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာကို အတင်းအကျပ် အသစ်ဆွဲယူသည့် Function
def load_data():
    try:
        # Cache လုံးဝမကျန်အောင် timestamp ဖြင့် အမြဲပြောင်းလဲပေးသည်
        fresh_url = f"{csv_url}&gid=0&cache={int(time.time())}"
        data = pd.read_csv(fresh_url)
        if not data.empty:
            data['Number'] = data['Number'].astype(str).str.zfill(2)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

# App စတိုင်း ဒေတာအသစ်ယူမည်
df = load_data()

st.title("💰 2D Agent Pro Dashboard")

# အရောင်းစုစုပေါင်း
total_amt = df['Amount'].sum() if not df.empty else 0
st.metric("💵 စုစုပေါင်းရောင်းရငွေ", f"{total_amt:,.0f} Ks")

col1, col2 = st.columns([1, 2])

with col1:
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
                res = requests.post(script_url, json=payload)
                if res.status_code == 200:
                    st.success("သိမ်းပြီးပါပြီ။")
                    time.sleep(2) # Google ဘက်က Update ဖြစ်အောင် ခဏစောင့်ပေးသည်
                    st.rerun()
            else:
                st.warning("အချက်အလက် ပြည့်စုံအောင် ဖြည့်ပါ")

with col2:
    st.subheader("📊 အရောင်းဇယား")
    # Manual Refresh ခလုတ်
    if st.button("🔄 စာရင်းအသစ်ပြန်ကြည့်မည်"):
        st.rerun()

    if not df.empty:
        # Search Feature
        search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
        filtered_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        # ဇယားပုံစံအစစ် (Selection ပါဝင်သည်)
        # ဇယားမပေါ်ရခြင်းမှာ column configuration လွဲနေနိုင်၍ အခြေခံအတိုင်း အရင်ပြမည်
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )
        
        # တစ်ခုချင်းစီဖျက်ရန် Expanders
        st.divider()

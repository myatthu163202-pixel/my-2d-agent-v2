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

# --- SIDEBAR ---
st.sidebar.header("⚙️ Control Panel")

# ပေါက်ဂဏန်းစစ်ခြင်း
win_num = st.sidebar.text_input("🏆 ပေါက်ဂဏန်းတိုက်ရန်", max_chars=2)
if win_num:
    winners = df[df['Number'] == win_num]
    if not winners.empty:
        st.sidebar.success(f"ပေါက်သူ {len(winners)} ဦး!")
        st.sidebar.warning(f"လျော်ကြေး: {winners['Amount'].sum() * 80:,.0f} Ks")

st.sidebar.divider()

# အကုန်ဖျက်သည့်ခလုတ်
if st.sidebar.button("🗑 စာရင်းအားလုံးဖျက်မည်"):
    pw = st.sidebar.text_input("Password ရိုက်ပါ", type="password", key="all_del_pw")
    if pw == "1234":
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

# --- MAIN UI ---
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
    st.subheader("🔍 စာရင်းဇယား နှင့် တစ်ခုချင်းဖျက်ရန်")
    search = st.text_input("🔎 နာမည်ဖြင့် ရှာရန်")
    
    display_df = df.copy()
    if search:
        display_df = display_df[display_df['Customer'].str.contains(search, case=False, na=False)]
    
    st.metric("စုစုပေါင်း ရောင်းရငွေ", f"{display_df['Amount'].sum():,.0f} Ks")

    # တစ်ခုချင်းဖျက်ရန် List ပုံစံပြခြင်း
    for index, row in display_df.iloc[::-1].iterrows():
        # Expander လေးနဲ့ ပြထားလို့ ကြည့်ရတာ ရှင်းပါတယ်
        with st.expander(f"👤 {row['Customer']} | 🔢 {row['Number']} | 💵 {row['Amount']} Ks"):
            st.write(f"⏰ အချိန်: {row['Time']}")
            # ခလုတ်ကို နာမည်နဲ့ Index တွဲပေးထားလို့ မှားမဖျက်နိုင်ပါဘူး
            if st.button(f"🗑 ဤစာရင်းကို ဖျက်ရန်", key=f"del_{index}"):
                del_payload = {
                    "action": "delete",
                    "Customer": row['Customer'],
                    "Number": str(row['Number']),
                    "Time": row['Time']
                }
                with st.spinner('ဖျက်နေပါသည်...'):
                    res = requests.post(script_url, json=del_payload)
                    st.success("ဖျက်ပြီးပါပြီ!")
                    st.rerun()

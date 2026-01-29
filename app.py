import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="2D Agent Pro Dashboard", layout="wide")

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

st.title("💰 2D Pro Agent Dashboard")

# Dashboard - စုစုပေါင်းစာရင်းများ
total_in = df['Amount'].sum()
st.info(f"💵 စုစုပေါင်းရောင်းရငွေ: {total_in:,.0f} Ks")

# Sidebar - Admin & ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("⚙️ Admin Control")
win_num = st.sidebar.text_input("🎰 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2)
za_rate = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

# အဓိက အပိုင်း ၂ ခုခွဲမည်
c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း (ဥပမာ- 05)", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        submit = st.form_submit_button("✅ သိမ်းဆည်းမည်")
        
        if submit:
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

with c2:
    st.subheader("📊 အရောင်းဇယား နှင့် စီမံရန်")
    if not df.empty:
        # နာမည်ဖြင့်ရှာရန်
        search = st.text_input("🔎 နာမည်ဖြင့်ရှာရန်")
        filtered_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        # ဇယားပုံစံ (Selectable Table)
        st.write("ဖျက်လိုသော စာရင်းများကို ရွေးချယ်ပါ-")
        event = st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={"Amount": st.column_config.NumberColumn("ငွေပမာဏ", format="%d Ks")},
            hide_index=True,
            on_select="rerun",
            selection_mode="multi_rows"
        )
        
        # Select မှတ်ပြီးဖျက်ခြင်း
        selected_rows = event.selection.rows
        if selected_rows:
            if st.button(f"🗑 ရွေးထားသော ({len(selected_rows)}) ခုကိုဖျက်မည်"):
                for idx in selected_rows:
                    target = filtered_df.iloc[idx]
                    # ဒီနေရာမှာ ကွင်းပိတ် (Bracket) တွေကို အသေအချာ စစ်ဆေးပြီးဖြစ်သည်
                    requests.post(script_url, json={
                        "action": "delete",
                        "Customer": target['Customer'],
                        "Number": str(target['Number']),
                        "Time": target['Time']
                    })
                st.rerun()

        # ပေါက်ဂဏန်းစစ်ခြင်း နှင့် အမြတ်/အရှုံး
        if win_num:
            winners = df[df['Number'] == win_num]
            total_out = winners['Amount'].sum() * za_rate
            balance = total_in - total_out
            
            st.divider()
            st.subheader("📈 ရလဒ်အကျဉ်းချုပ်")
            col1, col2 = st.columns(2)
            col1.metric("လျော်ကြေးစုစုပေါင်း", f"{total_out:,.0f} Ks")
            col2.metric("အသားတင် အမြတ်/အရှုံး", f"{balance:,.0f} Ks", delta=balance)
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")

# Admin Password ဖြင့် အကုန်ဖျက်ရန်
st.sidebar.divider()
del_pw = st.sidebar.text_input("Admin Password", type="password")
if st.sidebar.button("⚠️ စာရင်းအားလုံး အပြီးတိုင်ဖျက်မည်"):
    if del_pw == "1632022":
        requests.post(script_url, json={"action": "clear_all"})
        st.rerun()

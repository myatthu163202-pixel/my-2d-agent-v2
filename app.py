import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import time

st.set_page_config(page_title="2D Agent Pro Dashboard", layout="wide")

# Link များ ချိတ်ဆက်ခြင်း
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace('/edit', '/export?format=csv')

# ဒေတာကို အသစ်ရအောင် ဆွဲယူသည့် Function
def load_data():
    try:
        url = f"{csv_url}&cachebuster={int(time.time())}"
        data = pd.read_csv(url)
        if not data.empty:
            data['Number'] = data['Number'].astype(str).str.zfill(2)
            data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["Customer", "Number", "Amount", "Time"])

df = load_data()

st.title("💰 2D Agent Pro Dashboard")

# Sidebar - Admin & ပေါက်ဂဏန်းစစ်ရန်
st.sidebar.header("⚙️ Admin & Win Check")
win_num = st.sidebar.text_input("🎰 ပေါက်ဂဏန်းရိုက်ပါ", max_chars=2)
za_rate = st.sidebar.number_input("💰 ဇ (အဆ)", value=80)

# Dashboard - စုစုပေါင်းစာရင်းများ
total_in = df['Amount'].sum() if not df.empty else 0
st.info(f"💵 စုစုပေါင်းရောင်းရငွေ: {total_in:,.0f} Ks")

c1, c2 = st.columns([1, 2])

with c1:
    st.subheader("📝 စာရင်းသွင်းရန်")
    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("နာမည်")
        num = st.text_input("ဂဏန်း (00-99)", max_chars=2)
        amt = st.number_input("ငွေပမာဏ", min_value=100, step=100)
        submit = st.form_submit_button("✅ သိမ်းဆည်းမည်")
        
        if submit:
            if name and num:
                payload = {
                    "action": "insert", "Customer": name, 
                    "Number": str(num).zfill(2), "Amount": int(amt), 
                    "Time": datetime.now().strftime("%I:%M %p")
                }
                requests.post(script_url, json=payload)
                st.success("သိမ်းပြီးပါပြီ။")
                time.sleep(1)
                st.rerun()

with c2:
    st.subheader("📊 အရောင်းဇယား")
    # Refresh & Search
    col_a, col_b = st.columns([1, 2])
    if col_a.button("🔄 Refresh"):
        st.rerun()
    search = col_b.text_input("🔎 နာမည်ဖြင့်ရှာရန်", placeholder="နာမည်ရိုက်ပါ...")

    if not df.empty:
        view_df = df[df['Customer'].str.contains(search, case=False, na=False)] if search else df
        
        # ဇယားပုံစံ
        st.dataframe(
            view_df,
            use_container_width=True,
            column_config={"Amount": st.column_config.NumberColumn("ငွေပမာဏ", format="%d Ks")},
            hide_index=True
        )

        # ပေါက်ဂဏန်းစစ်ခြင်း နှင့် အမြတ်/အရှုံး
        if win_num:
            winners = df[df['Number'] == win_num]
            total_out = winners['Amount'].sum() * za_rate
            balance = total_in - total_out
            
            st.divider()
            st.subheader("📈 ရလဒ်အကျဉ်းချုပ်")
            k1, k2, k3 = st.columns(3)
            k1.metric("🏆 ပေါက်သူ", f"{len(winners)} ဦး")
            k2.metric("💸 လျော်ကြေး", f"{total_out:,.0f} Ks")
            k3.metric("💹 အမြတ်/အရှုံး", f"{balance:,.0f} Ks", delta=balance)
    else:
        st.info("လက်ရှိတွင် စာရင်းမရှိသေးပါ။")

# စာရင်းဖျက်ရန် အပိုင်း (တစ်ခုချင်းစီ)
if not df.empty:
    st.divider()
    st.subheader("🗑 စာရင်းဖျက်ရန်")
    with st.expander("တစ်ခုချင်းစီ ဖျက်ရန် နှိပ်ပါ"):
        for i, r in df.iloc[::-1].iterrows():
            col_x, col_y = st.columns([4, 1])
            col_x.write(f"👤 {r['Customer']} | 🔢 {r['Number']} | 💵 {r['Amount']} Ks")
            if col_y.button("ဖျက်", key=f"del_{i}"):
                requests.post(script_url, json={"action": "delete", "Customer": r['Customer'], "Number": str(r['Number']), "Time": r['Time']})
                st.rerun()

# စာရင်းအားလုံးဖျက်ရန်
st.sidebar.divider()
if st.sidebar.button("⚠️ စာရင်းအားလုံးဖျက်မည်"):
    requests.post(script_url, json={"action": "clear_all"})
    st.rerun()

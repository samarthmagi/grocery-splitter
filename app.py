import streamlit as stimport streamlit as st
import pandas as pd
from collections import defaultdict

# 1. Page Config - Modern & Focused
st.set_page_config(page_title="Smart Grocery Splitter", page_icon="🛒", layout="wide")

# 2. Elegant UI Styling (Custom CSS)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header { font-size: 42px; font-weight: 700; color: #1E1E1E; letter-spacing: -1px; }
    div[data-testid="stMetric"] {
        background-color: #f9f9f9;
        border: 1px solid #eeeeee;
        padding: 20px;
        border-radius: 12px;
    }
    .footer-text { color: #666666; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - Founder & Context
with st.sidebar:
    st.markdown("## 🛒 Project Info")
    st.info("**Founder:** Sam  \n**Status:** MVP v1.0")
    st.divider()
    st.markdown("### How it Works")
    st.write("1. Input expenses in the ledger.")
    st.write("2. Add/Remove rows as needed.")
    st.write("3. Review real-time settlement.")

# 4. App Header
st.markdown('<p class="main-header">Smart Grocery Splitter</p>', unsafe_allow_html=True)
st.markdown("A minimalist engine for household expense settlement.")
st.divider()

# 5. The Ledger (Clean & Simple)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"item": "Milk", "price": 50.0, "buyer": "Alice"},
        {"item": "Bread", "price": 30.0, "buyer": "Bob"},
        {"item": "Eggs", "price": 60.0, "buyer": "Alice"}
    ])

st.write("### 📝 Expense Ledger")
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "price": st.column_config.NumberColumn("Price (₹)", format="₹%d"),
        "buyer": st.column_config.TextColumn("Buyer Name")
    }
)

# 6. Calculation Logic
def calculate_balances(df):
    spent = defaultdict(float)
    for _, row in df.iterrows():
        if pd.notnull(row["price"]) and pd.notnull(row["buyer"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])

    people = list(spent.keys())
    if not people: return {}
    
    total = sum(spent.values())
    avg = total / len(people)
    return {p: spent[p] - avg for p in people}

balances = calculate_balances(edited_df)

# 7. Settlement Visualization
if balances:
    st.write("### 💰 Final Balances")
    cols = st.columns(len(balances))
    
    for i, (person, bal) in enumerate(balances.items()):
        with cols[i]:
            if bal >= 0:
                st.metric(label=f"Owed to {person}", value=f"₹{bal:.2f}")
            else:
                st.metric(label=f"{person} owes", value=f"₹{abs(bal):.2f}", delta_color="inverse")

# 8. Elegant Footer (Your Professional Links)
st.divider()
st.markdown('<p class="footer-text">Built by Sam for the YC Fellowship Application</p>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?style=flat-square&logo=github)](https://github.com/samarthmagi)")
with c2:
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/samarthmagi)")
with c3:
    st.markdown("[![Gmail](https://img.shields.io/badge/Gmail-Contact-red?style=flat-square&logo=gmail)](mailto:samarthmagi@gmail.com)")

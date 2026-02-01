import streamlit as st
import pandas as pd
from collections import defaultdict

# 1. Premium Page Config
st.set_page_config(page_title="Splitly Premium", page_icon="💎", layout="wide")

# 2. Billionaire Aesthetics (Custom CSS)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to right, #ffffff, #f0f2f5); }
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .main-title { font-size: 50px; font-weight: 800; color: #1E1E1E; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar - The "Vision"
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2489/2489756.png", width=100)
    st.markdown("# Splitly v2.0")
    st.info("Built by Samarth Magi")
    st.success("Target: YC Summer 2026")
    st.divider()
    st.write("### 💎 Premium Features")
    st.write("✔️ Real-time Delta Tracking")
    st.write("✔️ Multi-Party Clearinghouse")
    st.write("✔️ Zero-Friction UI")

# 4. Main UI Header
st.markdown('<p class="main-title">Splitly Premium</p>', unsafe_allow_html=True)
st.markdown("#### The Intelligent Way to Settle Household Debt.")

# 5. The Input Engine (User-First Design)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"item": "Shared Pizza", "price": 1200.0, "buyer": "Alice"},
        {"item": "Electricity Bill", "price": 3500.0, "buyer": "Bob"},
        {"item": "Internet", "price": 999.0, "buyer": "Sam"}
    ])

st.write("### 📝 Active Ledger")
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "price": st.column_config.NumberColumn("Amount (₹)", format="₹%d", min_value=0),
        "buyer": st.column_config.SelectboxColumn("Paid By", options=["Alice", "Bob", "Sam", "Guest"], required=True)
    }
)

# 6. The "Billionaire" Logic Engine
def solve_debts(df):
    spent = defaultdict(float)
    for _, row in df.iterrows():
        if pd.notnull(row["price"]) and pd.notnull(row["buyer"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])
    
    people = list(spent.keys())
    if not people: return {}, 0
    
    total = sum(spent.values())
    avg = total / len(people)
    balances = {p: spent[p] - avg for p in people}
    return balances, total

balances, total_volume = solve_debts(edited_df)

# 7. Analytics Dashboard
st.divider()
st.write("### 📊 Wealth Distribution & Settlement")

# High-level metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Volume", f"₹{total_volume:,.2f}")
m2.metric("Active Users", len(balances))
m3.metric("Avg. Per Person", f"₹{total_volume/len(balances):,.2f}" if balances else "₹0")

# 8. Visualizing the "Split"
if balances:
    st.write("#### Final Balance Sheets")
    # Using columns for the metrics
    cols = st.columns(len(balances))
    for i, (person, bal) in enumerate(balances.items()):
        with cols[i]:
            color = "normal" if bal >= 0 else "inverse"
            st.metric(label=person, value=f"₹{bal:,.2f}", delta="Owed to them" if bal >= 0 else "Owes Group", delta_color=color)

# 9. Smart Footer (Professional Links)
st.divider()
f1, f2, f3 = st.columns([2, 1, 1])
with f1:
    st.write("🚀 **Samarth Magi** | Product Lead @ SVMP Systems")
with f2:
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-black?logo=github)](https://github.com/samarthmagi)")
with f3:
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?logo=linkedin)](https://linkedin.com/in/samarthmagi)")

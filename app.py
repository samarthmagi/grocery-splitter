import streamlit as st
import pandas as pd
from collections import defaultdict

# 1. Page Configuration & Professional Styling
st.set_page_config(page_title="Smart Grocery Splitter", page_icon="🛒", layout="wide")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTable { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_base_case=True)

# 2. Sidebar for Project Context (Great for YC Reviewers)
with st.sidebar:
    st.title("Project Details")
    st.info("""
    **Founder:** Sam  
    **Goal:** Eliminate household debt friction.  
    **Tech:** Python 3.14 + Streamlit
    """)
    st.divider()
    st.write("### How to use:")
    st.write("1. Edit the names/prices in the table.")
    st.write("2. Add new rows at the bottom.")
    st.write("3. Watch balances update live!")

# 3. Main Header
st.title("🛒 Smart Grocery Splitter")
st.subheader("Interactive Expense Settlement Engine")
st.markdown("---")

# 4. Live-Editable Data Grid
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"item": "Milk", "price": 50.0, "buyer": "Alice"},
        {"item": "Bread", "price": 30.0, "buyer": "Bob"},
        {"item": "Eggs", "price": 60.0, "buyer": "Alice"}
    ])

st.write("### 📝 Step 1: Input Expenses")
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "price": st.column_config.NumberColumn("Price (₹)", format="₹%d"),
        "buyer": st.column_config.TextColumn("Buyer Name")
    }
)

# 5. Calculation Engine
def calculate_balances(df):
    spent = defaultdict(float)
    for _, row in df.iterrows():
        if pd.notnull(row["price"]) and pd.notnull(row["buyer"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])

    people = list(spent.keys())
    if not people: return {}
    
    total = sum(spent.values())
    fair_share = total / len(people)
    return {p: spent[p] - fair_share for p in people}

balances = calculate_balances(edited_df)

# 6. Result Visualization
if balances:
    st.write("### 💰 Step 2: Live Balances")
    cols = st.columns(len(balances) if len(balances) > 0 else 1)
    
    for i, (person, bal) in enumerate(balances.items()):
        with cols[i % len(cols)]:
            if bal >= 0:
                st.metric(label=f"Owed to {person}", value=f"₹{bal:.2f}", delta="Recipient")
            else:
                st.metric(label=f"{person} owes", value=f"₹{abs(bal):.2f}", delta="-Settlement", delta_color="inverse")

# 7. Professional Footer (Your Links)
st.markdown("---")
st.write("### 🔗 Connect with the Developer")
col_gh, col_li, col_em = st.columns(3)

with col_gh:
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?style=for-the-badge&logo=github)](https://github.com/samarthmagi)")
with col_li:
    # Replace the link below with your actual LinkedIn URL
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/YOUR_LINKEDIN_USERNAME)")
with col_em:
    # Replace with your actual Gmail
    st.markdown("[![Gmail](https://img.shields.io/badge/Gmail-Contact-red?style=for-the-badge&logo=gmail)](mailto:yourname@gmail.com)")

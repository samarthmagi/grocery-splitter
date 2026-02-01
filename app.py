# Smart Grocery Splitter MVP
# Python 3.10+ recommended
# Streamlit UI included

import streamlit as st
import pandas as pd
from collections import defaultdict
import json

# =========================
# 1. Sample data for demo
# =========================
sample_data = [
    {"item": "Milk", "price": 50, "buyer": "Alice"},
    {"item": "Bread", "price": 30, "buyer": "Bob"},
    {"item": "Eggs", "price": 60, "buyer": "Alice"}
]

# =========================
# 2. Core logic to calculate balances
# =========================
def calculate_balances(data):
    spent = defaultdict(int)
    # Sum total spent per person
    for d in data:
        spent[d["buyer"]] += d["price"]

    # Calculate fair share per person
    people = list(spent.keys())
    if not people:
        return {}
    
    total = sum(spent.values())
    fair_share = total / len(people)

    # Compute balances (positive = others owe them, negative = they owe)
    balances = {p: spent[p] - fair_share for p in people}
    return balances

# =========================
# 3. Streamlit UI
# =========================
st.set_page_config(page_title="Smart Grocery Splitter", page_icon="🛒")
st.title("🛒 Smart Grocery Splitter")
st.markdown("Automate your household expenses and resolve roommate disputes.")

# File uploader for custom data
uploaded_file = st.file_uploader("Upload a JSON or CSV file", type=["json", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('.json'):
        data = json.load(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
        data = df.to_dict(orient="records")
else:
    st.info("Currently showing results using sample data.")
    data = sample_data

# Run the calculation
balances = calculate_balances(data)

# Display results
if balances:
    st.subheader("Final Balances")
    
    # Create a nice table for the UI
    balance_df = pd.DataFrame([
        {"Person": name, "Balance (₹)": f"{'+' if bal > 0 else ''}{bal:.2f}"}
        for name, bal in balances.items()
    ])
    st.table(balance_df)

    st.subheader("Action Items")
    for person, balance in balances.items():
        if balance > 0:
            st.success(f"**{person}** is owed **₹{balance:.2f}**.")
        elif balance < 0:
            st.warning(f"**{person}** needs to pay **₹{abs(balance):.2f}**.")
else:
    st.write("No data found to calculate.")

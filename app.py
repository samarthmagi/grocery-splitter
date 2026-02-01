import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict
from datetime import datetime
import time

# 1. Page Config
st.set_page_config(page_title="Splitly", page_icon="⚡", layout="wide")

# 2. Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #050505 60%); }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #ffffff !important; letter-spacing: -0.5px; }
    p, label, .stMarkdown, .stCaption { color: #a0a0a0 !important; }
    .stTextInput input, .stNumberInput input { background-color: #111111 !important; color: white !important; border: 1px solid #333 !important; border-radius: 8px !important; }
    div[data-testid="stMetric"] { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(125, 86, 244, 0.2); padding: 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(125, 86, 244, 0.1); }
    div.stButton > button { background: linear-gradient(90deg, #7D56F4 0%, #4B0082 100%); color: white; border: none; border-radius: 8px; padding: 12px 24px; font-weight: 600; width: 100%; transition: transform 0.1s ease; }
    div.stButton > button:active { transform: scale(0.98); }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State
if 'history' not in st.session_state: st.session_state.history = []
if 'show_results' not in st.session_state: st.session_state.show_results = False

# Initialize Roster
if 'members_df' not in st.session_state: 
    st.session_state.members_df = pd.DataFrame([
        {"Name": "You", "Role": "Admin"},
        {"Name": "Roommate 1", "Role": "Member"},
        {"Name": "Roommate 2", "Role": "Member"},
        {"Name": "Guest", "Role": "Guest"}
    ])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ Splitly")
    st.divider()
    st.markdown("### 👥 Squad Roster")
    st.caption("Add or remove people below.")
    
    edited_members = st.data_editor(
        st.session_state.members_df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", required=True),
            "Role": st.column_config.SelectboxColumn("Role", options=["Admin", "Member", "Guest"])
        },
        key="member_editor"
    )
    st.session_state.members_df = edited_members
    current_group_list = [name for name in st.session_state.members_df["Name"].dropna().unique().tolist() if name.strip() != ""]

    if current_group_list:
        st.markdown("#### Active Members")
        chips_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for name in current_group_list:
            avatar_url = f"https://api.dicebear.com/9.x/notionists/svg?seed={name}&backgroundColor=b6e3f4,c0aede,d1d4f9"
            chips_html += f'<div style="display: flex; align-items: center; gap: 8px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 4px 12px 4px 4px; border-radius: 30px;"><img src="{avatar_url}" width="28" height="28" style="border-radius: 50%;"><span style="color: #e0e0e0; font-size: 13px; font-weight: 500;">{name}</span></div>'
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

# --- MAIN APP ---
st.markdown("# ⚡ Dashboard")
st.markdown("Real-time settlement engine active.")
st.divider()

if 'data' not in st.session_state:
    p1 = current_group_list[0] if len(current_group_list) > 0 else "User"
    p2 = current_group_list[1] if len(current_group_list) > 1 else "User"
    st.session_state.data = pd.DataFrame([
        {"item": "Groceries", "price": 1500.0, "buyer": p1},
        {"item": "WiFi Bill", "price": 999.0, "buyer": p2},
    ])

st.write("### 📝 Active Ledger")
edited_display = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True, 
    column_config={
        "price": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
        "buyer": st.column_config.SelectboxColumn("Paid By", options=current_group_list, required=True),
        "item": st.column_config.TextColumn("Item Name", width="large")
    }
)

if not edited_display.equals(st.session_state.data):
    st.session_state.data = edited_display
    st.session_state.show_results = False
    st.rerun()

st.divider()

col_btn, col_blank = st.columns([1, 4])
with col_btn:
    if st.button("🚀 Calculate Split", type="primary", use_container_width=True):
        st.session_state.show_results = True

# --- LOGIC & RESULTS ---
if st.session_state.show_results:
    
    # 1. Net Balances
    def calculate_net_balances(df, members):
        spent = defaultdict(float)
        valid_rows = df[df["buyer"].isin(members)]
        for _, row in valid_rows.iterrows():
            if pd.notnull(row["price"]):
                spent[str(row["buyer"]).strip()] += float(row["price"])
        if not members: return {}, 0, {}
        
        total = sum(spent.values())
        avg = total / len(members) if members else 0
        
        final_balances = {}
        for person in members:
            person = str(person).strip()
            final_balances[person] = spent[person] - avg
        return final_balances, total, spent

    # 2. Who Pays Whom (Greedy)
    def solve_payments(balances):
        debtors = []
        creditors = []
        for person, amount in balances.items():
            if amount < -0.01: debtors.append([person, amount])
            elif amount > 0.01: creditors.append([person, amount])
        
        debtors.sort(key=lambda x: x[1])
        creditors.sort(key=lambda x: x[1], reverse=True)
        
        transfers = []
        i = 0; j = 0
        while i < len(debtors) and j < len(creditors):
            debtor = debtors[i]; creditor = creditors[j]
            amount = min(abs(debtor[1]), creditor[1])
            transfers.append(f"**{debtor[0]}** pays **{creditor[0]}** ₹{amount:.0f}")
            debtor[1] += amount; creditor[1] -= amount
            if abs(debtor[1]) < 0.01: i += 1
            if creditor[1] < 0.01: j += 1
        return transfers

    balances, total_volume, spent_dict = calculate_net_balances(st.session_state.data, current_group_list)
    transfer_instructions = solve_payments(balances)
    
    # --- VISUALIZATION ---
    c_viz, c_receipt = st.columns([1, 1])
    
    with c_viz:
        st.write("### 📊 Analytics")
        if total_volume > 0:
            chart_data = pd.DataFrame(list(spent_dict.items()), columns=["Person", "Amount"])
            fig = px.pie(chart_data, values='Amount', names='Person', hole=0.6, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Total Volume", f"₹{total_volume:,.0f}")
        else:
            st.info("No expenses added yet.")

    with c_receipt:
        st.write("### 💸 Settlement")
        
        active_balances = {k: v for k, v in balances.items() if abs(v) > 1}
        if not active_balances:
            st.success("All settled up! ✅")
        else:
            for person, bal in active_balances.items():
                color = "#7D56F4" if bal >= 0 else "#FF4B4B"
                label = "GETS" if bal >= 0 else "OWES"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                    background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid {color};">
                    <span style="font-weight: 500; color: #eee;">{person}</span>
                    <span style="font-weight: bold; color: {color};">{label} ₹{abs(bal):,.0f}</span>
                </div>
                """, unsafe_allow_html=True)
        
        if transfer_instructions:
            st.divider()
            st.markdown("#### 🔄 Transfer Plan")
            st.info("  \n".join([f"👉 {t}" for t in transfer_instructions]))

            st.divider()
            st.write("#### 📱 WhatsApp")
            receipt_text = f"🧾 *Splitly Plan*\n"
            for t in transfer_instructions:
                clean_t = t.replace("**", "")
                receipt_text += f"➡️ {clean_t}\n"
            receipt_text += f"\n🔗 Total: ₹{total_volume:,.0f}"
            st.code(receipt_text, language="text")

else:
    st.info("👆 Add expenses above and click 'Calculate Split' to see the breakdown.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2,1,1])
with f1: st.caption("© 2026 Splitly Inc.")
with f2: st.markdown("[![GitHub](https://img.shields.io/badge/Code-black?logo=github)](https://github.com/samarthmagi)")
with f3: st.markdown("[![Connect](https://img.shields.io/badge/Connect-blue?logo=linkedin)](https://linkedin.com/in/samarthmagi)")

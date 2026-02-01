import streamlit as st
import pandas as pd
import plotly.express as px
from collections import defaultdict
from datetime import datetime
import time

# 1. Page Config
st.set_page_config(page_title="Splitly | Smart Expense Engine", page_icon="⚡", layout="wide")

# 2. Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #050505 60%);
    }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #ffffff !important; letter-spacing: -0.5px; }
    p, label, .stMarkdown, .stCaption { color: #a0a0a0 !important; }
    
    .stTextInput input, .stNumberInput input {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(125, 86, 244, 0.2);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(125, 86, 244, 0.1);
    }
    
    div.stButton > button {
        background: linear-gradient(90deg, #7D56F4 0%, #4B0082 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State Init
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []
if 'members_df' not in st.session_state: 
    st.session_state.members_df = pd.DataFrame([
        {"Name": "You", "Role": "Admin"},
        {"Name": "Roommate 1", "Role": "Member"},
        {"Name": "Roommate 2", "Role": "Member"},
        {"Name": "Guest", "Role": "Guest"}
    ])

# --- AUTHENTICATION ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("# ⚡ Splitly")
        st.markdown("### The Frictionless Way to Settle Debt.")
        
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        with tab1:
            email = st.text_input("Email Address", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Log In →"):
                st.session_state.logged_in = True
                st.session_state.user = email.split('@')[0].capitalize() if email else "User"
                st.rerun()
            if st.button("Continue with Google"):
                with st.spinner("Connecting to Google..."):
                    time.sleep(1.0)
                    st.session_state.logged_in = True
                    st.session_state.user = "Samarth"
                    st.rerun()
    st.stop()

# --- MAIN APP ---
with st.sidebar:
    st.markdown(f"### 👋 Hi, {st.session_state.user}")
    
    st.divider()
    st.markdown("### 👥 Squad Roster")
    st.caption("Edit names below to auto-generate avatars.")
    
    # EDITABLE ROSTER
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

    # NEW: AVATARS (DiceBear API)
    if current_group_list:
        st.markdown("#### Active Members")
        chips_html = '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
        for name in current_group_list:
            # Generate a unique avatar for each name
            avatar_url = f"https://api.dicebear.com/9.x/notionists/svg?seed={name}&backgroundColor=b6e3f4,c0aede,d1d4f9"
            chips_html += f'''
            <div style="
                display: flex; align-items: center; gap: 8px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 4px 12px 4px 4px;
                border-radius: 30px;
            ">
                <img src="{avatar_url}" width="28" height="28" style="border-radius: 50%;">
                <span style="color: #e0e0e0; font-size: 13px; font-weight: 500;">{name}</span>
            </div>
            '''
        chips_html += "</div>"
        st.markdown(chips_html, unsafe_allow_html=True)

    st.divider()
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.markdown("# ⚡ Dashboard")
st.markdown("Real-time settlement engine active.")
st.divider()

# Expense Data
if 'data' not in st.session_state:
    p1 = current_group_list[0] if len(current_group_list) > 0 else "User"
    p2 = current_group_list[1] if len(current_group_list) > 1 else "User"
    st.session_state.data = pd.DataFrame([
        {"item": "Groceries", "price": 1500.0, "buyer": p1},
        {"item": "WiFi Bill", "price": 999.0, "buyer": p2},
    ])

def calculate_balances(df, members):
    spent = defaultdict(float)
    valid_rows = df[df["buyer"].isin(members)]
    for _, row in valid_rows.iterrows():
        if pd.notnull(row["price"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])
    if not members: return {}, 0, {}
    
    total = sum(spent.values())
    group_size = len(members) 
    avg = total / group_size if group_size > 0 else 0
    
    final_balances = {}
    for person in members:
        person = str(person).strip()
        final_balances[person] = spent[person] - avg
        
    return final_balances, total, spent

balances, total_volume, spent_dict = calculate_balances(st.session_state.data, current_group_list)

# Layout: Ledger vs Analytics
c_main, c_viz = st.columns([2, 1])

with c_main:
    st.write("### 📝 Active Ledger")
    edited_df = st.data_editor(
        st.session_state.data, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "price": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "buyer": st.column_config.SelectboxColumn("Paid By", options=current_group_list, required=True)
        }
    )
    st.session_state.data = edited_df

with c_viz:
    st.write("### 📊 Analytics")
    
    # NEW: INTERACTIVE DONUT CHART
    if total_volume > 0:
        chart_data = pd.DataFrame(list(spent_dict.items()), columns=["Person", "Amount"])
        fig = px.pie(chart_data, values='Amount', names='Person', hole=0.6, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
        fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Add expenses to see the breakdown.")

    st.metric("Total Volume", f"₹{total_volume:,.0f}")
    
    if st.button("💾 Save to History"):
        if balances:
            summary_text = " | ".join([f"{k}: {v:+.0f}" for k,v in balances.items() if abs(v) > 1])
            st.session_state.history.append({"date": datetime.now().strftime("%d %b"), "total": total_volume, "summary": summary_text})
            st.success("Saved!")
            time.sleep(1)
            st.rerun()

# Settlement & Receipt
if balances:
    st.write("### 💸 Settlement Status")
    active_balances = {k: v for k, v in balances.items() if abs(v) > 1}
    
    if not active_balances:
        st.info("Everything is settled up! ✅")
    else:
        # Cards
        cols = st.columns(4)
        for i, (person, bal) in enumerate(active_balances.items()):
            with cols[i % 4]:
                color = "#7D56F4" if bal >= 0 else "#FF4B4B"
                label = "Receive" if bal >= 0 else "Pay"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
                    border: 1px solid {color}40; border-radius: 12px; padding: 15px; text-align: center;">
                    <div style="color: #888; font-size: 12px; text-transform: uppercase;">{person}</div>
                    <div style="color: white; font-size: 20px; font-weight: bold;">₹{abs(bal):,.0f}</div>
                    <div style="color: {color}; font-size: 14px; font-weight: 600;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

    # NEW: WHATSAPP RECEIPT GENERATOR
    st.divider()
    st.write("### 📱 Share Receipt")
    
    receipt_text = f"🧾 *Splitly Receipt*\n🗓 {datetime.now().strftime('%d %b %Y')}\n\n"
    for person, bal in active_balances.items():
        if bal < 0:
            receipt_text += f"🔴 {person} owes ₹{abs(bal):.0f}\n"
        else:
            receipt_text += f"🟢 {person} gets ₹{abs(bal):.0f}\n"
    receipt_text += f"\n💰 Total Spend: ₹{total_volume:,.0f}\n🔗 Settled via Splitly"
    
    st.code(receipt_text, language="text")
    st.caption("Copy the text above and paste it into your group chat.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2,1,1])
with f1: st.caption("© 2026 Splitly Inc.")
with f2: st.markdown("[![GitHub](https://img.shields.io/badge/Code-black?logo=github)](https://github.com/samarthmagi)")
with f3: st.markdown("[![Connect](https://img.shields.io/badge/Connect-blue?logo=linkedin)](https://linkedin.com/in/samarthmagi)")

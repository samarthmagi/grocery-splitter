import streamlit as stimport streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
import time

# 1. Page Config (Dark Mode & Wide Layout)
st.set_page_config(page_title="Splitly | Smart Expense Engine", page_icon="⚡", layout="wide")

# 2. "Awwwards" Level Custom CSS
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #050505 60%);
    }
    
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #ffffff !important; letter-spacing: -0.5px; }
    p, label, .stMarkdown, .stCaption { color: #a0a0a0 !important; }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(125, 86, 244, 0.2);
        padding: 20px;
        border-radius: 12px;
        transition: transform 0.2s;
        box-shadow: 0 4px 20px rgba(125, 86, 244, 0.1);
    }
    
    /* Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #7D56F4 0%, #4B0082 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: opacity 0.3s;
    }
    div.stButton > button:hover { opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State Management
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []
# NEW: Store the group members in session state
if 'group_members' not in st.session_state: 
    st.session_state.group_members = ["You", "Roommate 1", "Roommate 2"]

# --- AUTHENTICATION SCREEN ---
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
            
            if st.button("Log In →", use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.user = email.split('@')[0].capitalize() if email else "User"
                st.rerun()
                
            if st.button("Continue with Google", use_container_width=True):
                with st.spinner("Connecting to Google..."):
                    time.sleep(1.0)
                    st.session_state.logged_in = True
                    st.session_state.user = "Samarth"
                    st.rerun()
    st.stop()

# --- MAIN APP UI ---

# Sidebar: Manage Group & History
with st.sidebar:
    st.markdown(f"### 👋 Hi, {st.session_state.user}")
    
    # NEW: Manage Group Section
    st.divider()
    st.markdown("### 👥 Manage Group")
    new_member = st.text_input("Add New Member", placeholder="Enter name...")
    if st.button("Add Person"):
        if new_member and new_member not in st.session_state.group_members:
            st.session_state.group_members.append(new_member)
            st.success(f"Added {new_member}!")
            time.sleep(0.5)
            st.rerun()
    
    # Show current members tag-style
    st.caption("Current Members:")
    st.code(", ".join(st.session_state.group_members))

    st.divider()
    st.markdown("### 📜 History")
    if st.session_state.history:
        for txn in reversed(st.session_state.history[-5:]):
            st.caption(f"{txn['date']} • ₹{txn['total']}")
            st.markdown(f"_{txn['summary']}_")
            st.divider()
    
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.markdown("# ⚡ Dashboard")
st.markdown("Real-time settlement engine active.")
st.divider()

# Data Logic
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"item": "Groceries", "price": 1500.0, "buyer": st.session_state.group_members[0]},
        {"item": "WiFi Bill", "price": 999.0, "buyer": st.session_state.group_members[1]},
    ])

# Main Interface
c_main, c_viz = st.columns([2, 1])

with c_main:
    st.write("### 📝 Active Ledger")
    # UPDATED: The Selectbox now uses the dynamic 'group_members' list
    edited_df = st.data_editor(
        st.session_state.data, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "price": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "buyer": st.column_config.SelectboxColumn(
                "Paid By", 
                options=st.session_state.group_members, # Dynamic list!
                required=True
            )
        }
    )

# Calculation Engine
def calculate_balances(df):
    spent = defaultdict(float)
    # Filter out rows with empty buyers
    valid_rows = df[df["buyer"].isin(st.session_state.group_members)]
    
    for _, row in valid_rows.iterrows():
        if pd.notnull(row["price"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])
    
    # We use ALL known members for the split, even if they didn't buy anything
    people = st.session_state.group_members
    if not people: return {}, 0
    
    total = sum(spent.values())
    avg = total / len(people) # Split equally among everyone in the group
    return {p: spent[p] - avg for p in people}, total

balances, total_volume = calculate_balances(edited_df)

# Visualization Side Panel
with c_viz:
    st.write("### 📊 Analytics")
    st.metric("Total Volume", f"₹{total_volume:,.0f}")
    st.metric("Group Size", len(st.session_state.group_members))
    
    if st.button("💾 Save Settlement", use_container_width=True):
        if balances:
            # Create a short summary string
            summary_text = " | ".join([f"{k}: {v:+.0f}" for k,v in balances.items() if abs(v) > 1])
            st.session_state.history.append({
                "date": datetime.now().strftime("%d %b %H:%M"),
                "total": total_volume,
                "summary": summary_text
            })
            st.success("Saved!")
            time.sleep(1)
            st.rerun()

# Settlement Cards
if balances:
    st.write("### 💸 Settlement Status")
    cols = st.columns(len(balances))
    # We only show cards for people who owe or are owed (skip 0 balance)
    active_balances = {k: v for k, v in balances.items() if abs(v) > 1}
    
    if not active_balances:
        st.info("Everything is settled up! ✅")
    else:
        # Create rows of 4 columns to handle many users gracefully
        cols = st.columns(4)
        for i, (person, bal) in enumerate(active_balances.items()):
            with cols[i % 4]:
                color = "#7D56F4" if bal >= 0 else "#FF4B4B"
                label = "Receive" if bal >= 0 else "Pay"
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
                    border: 1px solid {color}40;
                    border-radius: 12px;
                    padding: 15px;
                    margin-bottom: 10px;
                    text-align: center;
                ">
                    <div style="color: #888; font-size: 12px; text-transform: uppercase;">{person}</div>
                    <div style="color: white; font-size: 20px; font-weight: bold;">₹{abs(bal):,.0f}</div>
                    <div style="color: {color}; font-size: 14px; font-weight: 600;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2,1,1])
with f1: st.caption("© 2026 Splitly Inc.")
with f2: st.markdown("[![GitHub](https://img.shields.io/badge/Code-black?logo=github)](https://github.com/samarthmagi)")
with f3: st.markdown("[![Connect](https://img.shields.io/badge/Connect-blue?logo=linkedin)](https://linkedin.com/in/samarthmagi)")

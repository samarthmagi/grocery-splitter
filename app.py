import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
import time

# 1. Page Config (Dark Mode & Wide Layout)
st.set_page_config(page_title="Splitly | Smart Expense Engine", page_icon="⚡", layout="wide")

# 2. "Awwwards" Level Custom CSS (Dark Theme, Glassmorphism, Neon Accents)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a0b2e 0%, #050505 60%);
    }
    
    /* Typography */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #ffffff !important; letter-spacing: -0.5px; }
    p, label, .stMarkdown { color: #a0a0a0 !important; }
    
    /* Input Fields (Dark & Sleek) */
    .stTextInput input, .stNumberInput input {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    /* Metric Cards (Glassmorphism + Purple Glow) */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(125, 86, 244, 0.2);
        padding: 20px;
        border-radius: 12px;
        transition: transform 0.2s;
        box-shadow: 0 4px 20px rgba(125, 86, 244, 0.1);
    }
    div[data-testid="stMetric"]:hover {
        border-color: #7D56F4;
        transform: translateY(-2px);
    }
    
    /* Buttons (Gradient Purple to Blue) */
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
    
    /* Table Styling */
    div[data-testid="stDataEditor"] {
        border: 1px solid #333;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State Management (Auth & History)
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'history' not in st.session_state: st.session_state.history = []

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("# ⚡ Splitly")
        st.markdown("### The Frictionless Way to Settle Debt.")
        st.info("Experience the future of household finance.")
        
        # Tabs for Login/Signup (Visual Only for MVP)
        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        
        with tab1:
            email = st.text_input("Email Address", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Log In →", use_container_width=True):
                    if email:
                        st.session_state.logged_in = True
                        st.session_state.user = email.split('@')[0].capitalize()
                        st.rerun()
                    else:
                        st.warning("Please enter an email.")
            with col_b2:
                # Simulated Google Login
                if st.button("Continue with Google", use_container_width=True):
                    with st.spinner("Connecting to Google..."):
                        time.sleep(1.5) # Fake loading effect
                        st.session_state.logged_in = True
                        st.session_state.user = "Demo User"
                        st.rerun()

    st.stop() # Stop here if not logged in

# --- MAIN APP UI ---

# Sidebar: User Profile & History
with st.sidebar:
    st.markdown(f"### 👋 Welcome, {st.session_state.user}")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    st.markdown("### 📜 Transaction History")
    if st.session_state.history:
        for txn in reversed(st.session_state.history[-5:]): # Show last 5
            st.caption(f"{txn['date']} - Total: ₹{txn['total']}")
            st.markdown(f"**{txn['summary']}**")
            st.divider()
    else:
        st.caption("No past settlements found.")

# Header
st.markdown("# ⚡ Dashboard")
st.markdown("Real-time settlement engine active.")
st.divider()

# Data Logic
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"item": "Server Costs", "price": 4500.0, "buyer": "Sam"},
        {"item": "API Credits", "price": 2100.0, "buyer": "Alice"},
        {"item": "Design Assets", "price": 1200.0, "buyer": "Bob"}
    ])

# Main Interface
c_main, c_viz = st.columns([2, 1])

with c_main:
    st.write("### 📝 Active Ledger")
    edited_df = st.data_editor(
        st.session_state.data, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "price": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "buyer": st.column_config.SelectboxColumn("Paid By", options=["Sam", "Alice", "Bob", "Guest"])
        }
    )

# Calculation Engine
def calculate_balances(df):
    spent = defaultdict(float)
    for _, row in df.iterrows():
        if pd.notnull(row["price"]) and pd.notnull(row["buyer"]):
            spent[str(row["buyer"]).strip()] += float(row["price"])
    
    people = list(spent.keys())
    if not people: return {}, 0
    total = sum(spent.values())
    avg = total / len(people)
    return {p: spent[p] - avg for p in people}, total

balances, total_volume = calculate_balances(edited_df)

# Visualization Side Panel
with c_viz:
    st.write("### 📊 Analytics")
    st.metric("Total Volume", f"₹{total_volume:,.0f}")
    st.metric("Active Members", len(balances) if balances else 0)
    
    # Save to History Button
    if st.button("💾 Save Settlement", use_container_width=True):
        if balances:
            summary_text = ", ".join([f"{k}: {v:+.0f}" for k,v in balances.items()])
            st.session_state.history.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "total": total_volume,
                "summary": summary_text
            })
            st.success("Saved to History!")
            time.sleep(1)
            st.rerun()

# Settlement Cards (The "Dribbble" Look)
if balances:
    st.write("### 💸 Settlement Status")
    cols = st.columns(len(balances))
    for i, (person, bal) in enumerate(balances.items()):
        with cols[i]:
            # Custom styling for positive/negative balances
            color = "#7D56F4" if bal >= 0 else "#FF4B4B" 
            label = "Receive" if bal >= 0 else "Pay"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
                border: 1px solid {color}40;
                border-radius: 12px;
                padding: 15px;
                text-align: center;
            ">
                <div style="color: #888; font-size: 12px; text-transform: uppercase;">{person}</div>
                <div style="color: white; font-size: 24px; font-weight: bold;">₹{abs(bal):,.0f}</div>
                <div style="color: {color}; font-size: 14px; font-weight: 600;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
f1, f2, f3 = st.columns([2,1,1])
with f1: st.caption("© 2026 Splitly Inc. All rights reserved.")
with f2: st.markdown("[![GitHub](https://img.shields.io/badge/Code-black?logo=github)](https://github.com/samarthmagi)")
with f3: st.markdown("[![Connect](https://img.shields.io/badge/Connect-blue?logo=linkedin)](https://linkedin.com/in/samarthmagi)")

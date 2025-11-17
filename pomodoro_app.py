"""
Standalone Pomodoro Timer App for Knowledge Vault
Run with: streamlit run pomodoro_app.py
"""
import streamlit as st
from src.pomodoro_ui import render_pomodoro_widget, render_pomodoro_page

# Page config
st.set_page_config(
    page_title="Pomodoro Timer - Knowledge Vault",
    page_icon="🍅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .main {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🍅 Pomodoro")
    st.markdown("---")

    # Compact widget for sidebar
    render_pomodoro_widget()

    st.markdown("---")
    st.caption("Knowledge Vault Pomodoro Timer")
    st.caption("Stay focused and productive!")

# Main page
render_pomodoro_page()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import io
import re
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import google.generativeai as genai
from fpdf import FPDF
def hex_to_rgba(hex_color, alpha=0.15):
    # Agar '#' hai toh use hata dein
    hex_color = hex_color.lstrip('#')
    # RGB values extract karein
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f'rgba({r}, {g}, {b}, {alpha})'
try:
    from pypdf import PdfReader
except ImportError:
    pass
# =========================================================================
# ⚙️ 1. SYSTEM INITIALIZATION & CORE RE-RUN PREVENTION
# =========================================================================
st.set_page_config(
    page_title="TraceLens AI // Cyber Forensics Command",
    page_icon="🛡️",
    layout="wide", 
    initial_sidebar_state="expanded"
)
if "forensic_dataframe" not in st.session_state:
    st.session_state.forensic_dataframe = None
if "demo_data_loaded" not in st.session_state:
    st.session_state.demo_data_loaded = False
if "gemini_api_authenticated" not in st.session_state:
    st.session_state.gemini_api_authenticated = False
if "validated_api_key" not in st.session_state:
    st.session_state.validated_api_key = None
if "ai_response_cache" not in st.session_state:
    st.session_state.ai_response_cache = ""
# =========================================================================
# 🎨 2. NEXT-LEVEL FUTURISTIC CYBER UI THEME
# =========================================================================
st.markdown("""
<style>
    @import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap)');
    :root{
        --bg-0:#030611;
        --bg-1:#060914;
        --bg-2:#0A1020;
        --panel:#0B1120;
        --panel-2:rgba(10,16,32,0.72);
        --glass:rgba(12,18,35,0.58);
        --glass-2:rgba(16,24,48,0.48);
        --line:rgba(99,102,241,0.16);
        --line-strong:rgba(129,140,248,0.32);
        --text:#E6EDF7;
        --muted:#8190B6;
        --subtle:#51607F;
        --purple:#6366F1;
        --violet:#7C3AED;
        --pink:#C026D3;
        --red:#EF4444;
        --amber:#F59E0B;
        --green:#10B981;
        --cyan:#22D3EE;
        --blue:#60A5FA;
        --shadow:0 20px 60px rgba(0,0,0,0.45);
        --shadow-soft:0 8px 30px rgba(0,0,0,0.28);
        --glow-purple:0 0 30px rgba(99,102,241,0.22);
        --glow-red:0 0 28px rgba(239,68,68,0.18);
        --radius:18px;
    }
    * { box-sizing: border-box; }
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        max-width: 100% !important;
        padding: 0rem 1.35rem 2rem 1.35rem !important;
        position: relative;
        z-index: 2;
    }
    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(99,102,241,0.12), transparent 22%),
            radial-gradient(circle at 86% 16%, rgba(34,211,238,0.10), transparent 18%),
            radial-gradient(circle at 78% 74%, rgba(192,38,211,0.10), transparent 18%),
            radial-gradient(circle at 20% 80%, rgba(124,58,237,0.08), transparent 18%),
            linear-gradient(180deg, #040714 0%, #050916 35%, #040610 100%);
        color: var(--text);
        overflow-x: hidden;
    }
    .stApp::before {
        content:'';
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(99,102,241,0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99,102,241,0.045) 1px, transparent 1px);
        background-size: 42px 42px;
        opacity: 0.7;
        pointer-events:none;
        z-index:0;
        mask-image: radial-gradient(circle at center, black 45%, transparent 100%);
        -webkit-mask-image: radial-gradient(circle at center, black 45%, transparent 100%);
    }
    .stApp::after {
        content:'';
        position: fixed;
        inset: 0;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.015) 50%, rgba(255,255,255,0.00) 100%);
        pointer-events:none;
        z-index:1;
        animation: scanFloat 9s linear infinite;
        opacity: 0.35;
    }
    @keyframes scanFloat {
        0% { transform: translateY(-8%); }
        100% { transform: translateY(8%); }
    }
    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, rgba(99,102,241,0.9), rgba(34,211,238,0.7));
        border-radius: 20px;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top right, rgba(99,102,241,0.18), transparent 28%),
            linear-gradient(180deg, rgba(7,11,22,0.98) 0%, rgba(5,9,20,0.98) 100%) !important;
        border-right: 1px solid rgba(99,102,241,0.14) !important;
        box-shadow: inset -1px 0 0 rgba(255,255,255,0.03), 10px 0 40px rgba(0,0,0,0.28);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    .sidebar-brand {
        background:
            linear-gradient(135deg, rgba(99,102,241,0.16) 0%, rgba(124,58,237,0.10) 45%, rgba(34,211,238,0.08) 100%);
        border: 1px solid rgba(129,140,248,0.16);
        border-bottom: 1px solid rgba(129,140,248,0.22);
        padding: 20px 16px 18px 16px;
        margin: 12px 10px 10px 10px;
        border-radius: 20px;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
        box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .sidebar-brand::before {
        content: '';
        position: absolute;
        top: -35px; right: -35px;
        width: 130px; height: 130px;
        background: radial-gradient(circle, rgba(99,102,241,0.25), transparent 70%);
        border-radius: 50%;
    }
    .sidebar-brand::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent 20%, rgba(255,255,255,0.04) 50%, transparent 80%);
        transform: translateX(-120%);
        animation: sheenMove 6s linear infinite;
    }
    @keyframes sheenMove {
        0% { transform: translateX(-120%); }
        100% { transform: translateX(120%); }
    }
    .sidebar-brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 800;
        background: linear-gradient(135deg, #DDE7FF, #8BA3FF 45%, #B994FF 75%, #6EE7F9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .sidebar-brand-sub {
        font-size: 10px;
        color: #6C7A98;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        margin-top: 5px;
    }
    .sidebar-section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px;
        font-weight: 700;
        color: #465370;
        letter-spacing: 2.2px;
        text-transform: uppercase;
        padding: 12px 14px 6px 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sidebar-section-label::before {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.28));
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99,102,241,0.10);
        border: 1px solid rgba(129,140,248,0.18);
        padding: 5px 11px;
        border-radius: 999px;
        font-size: 10px;
        color: #AAB9FF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.8px;
        margin-bottom: 14px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.02) inset;
    }
    .live-dot, .sidebar-status-dot {
        display: inline-block;
        width: 7px; height: 7px;
        background: #10B981;
        border-radius: 50%;
        margin-right: 2px;
        box-shadow: 0 0 10px #10B981, 0 0 18px rgba(16,185,129,0.5);
        animation: pulse-green 1.6s infinite;
    }
    @keyframes pulse-green {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.45; transform: scale(1.12); }
    }
    /* Inputs */
    label, .stWidgetLabel p, [data-testid="stWidgetLabel"] p {
        color: #7182A8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.35px;
        margin-bottom: 6px !important;
    }
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(13,18,35,0.78), rgba(8,12,24,0.72)) !important;
        border: 1px dashed rgba(99,102,241,0.32) !important;
        border-radius: 16px !important;
        padding: 14px !important;
        transition: all 0.28s ease;
        backdrop-filter: blur(14px);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(129,140,248,0.65) !important;
        background: linear-gradient(135deg, rgba(14,20,40,0.9), rgba(10,14,28,0.82)) !important;
        box-shadow: 0 0 28px rgba(99,102,241,0.12), inset 0 0 20px rgba(99,102,241,0.05);
        transform: translateY(-1px);
    }
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
        background: linear-gradient(135deg, rgba(7,11,24,0.90), rgba(11,16,33,0.80)) !important;
        border: 1px solid rgba(46,58,90,0.72) !important;
        border-radius: 14px !important;
        backdrop-filter: blur(12px);
        transition: border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.025);
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="select"]:focus-within > div {
        border-color: rgba(129,140,248,0.55) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.10), 0 0 24px rgba(99,102,241,0.10) !important;
        transform: translateY(-1px);
    }
    input, textarea, .stTextArea textarea, .stTextInput input {
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        background: transparent !important;
    }
    /* Buttons */
    div.stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        border-radius: 14px !important;
        padding: 0.76rem 1rem !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        letter-spacing: 0.85px !important;
        text-transform: uppercase !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(12px);
    }
    div.stButton > button {
        background: linear-gradient(135deg, rgba(79,70,229,0.14) 0%, rgba(124,58,237,0.10) 55%, rgba(34,211,238,0.08) 100%) !important;
        color: #A8B6D9 !important;
        border: 1px solid rgba(99,102,241,0.22) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), 0 10px 30px rgba(0,0,0,0.18);
    }
    div.stButton > button::before,
    [data-testid="stFormSubmitButton"] > button::before {
        content: '';
        position: absolute;
        top: 0; left: -120%;
        width: 70%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.14), transparent);
        transform: skewX(-20deg);
        transition: left 0.65s ease;
    }
    div.stButton > button:hover::before,
    [data-testid="stFormSubmitButton"] > button:hover::before {
        left: 150%;
    }
    div.stButton > button:hover {
        border-color: rgba(129,140,248,0.48) !important;
        color: #D4DEFF !important;
        background: linear-gradient(135deg, rgba(79,70,229,0.22) 0%, rgba(124,58,237,0.16) 55%, rgba(34,211,238,0.10) 100%) !important;
        box-shadow: 0 0 20px rgba(99,102,241,0.18), 0 10px 24px rgba(0,0,0,0.28) !important;
        transform: translateY(-2px) scale(1.01) !important;
    }
    div.stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 52%, #06B6D4 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 12px 28px rgba(79,70,229,0.34), 0 0 26px rgba(6,182,212,0.14) !important;
    }
    [data-testid="stFormSubmitButton"] > button:hover,
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4338CA 0%, #6D28D9 50%, #0891B2 100%) !important;
        box-shadow: 0 16px 34px rgba(79,70,229,0.38), 0 0 32px rgba(6,182,212,0.18) !important;
        transform: translateY(-2px) !important;
        color: #FFFFFF !important;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(8,12,24,0.78), rgba(8,12,24,0.62)) !important;
        padding: 8px;
        border-radius: 18px;
        gap: 6px;
        border: 1px solid rgba(45,58,88,0.55);
        backdrop-filter: blur(20px);
        overflow-x: auto;
        flex-wrap: nowrap;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03), var(--shadow-soft);
    }
    .stTabs [data-baseweb="tab"] {
        color: #627192 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        padding: 10px 16px;
        border-radius: 12px;
        white-space: nowrap;
        transition: all 0.2s ease;
        letter-spacing: 0.28px;
        border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #B8C7FF !important;
        background: rgba(99,102,241,0.08) !important;
        border-color: rgba(99,102,241,0.12);
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(79,70,229,0.92) 0%, rgba(109,40,217,0.94) 55%, rgba(8,145,178,0.9) 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 8px 24px rgba(79,70,229,0.30), inset 0 1px 0 rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.06);
    }
    /* Cards / Panels */
    .module-explainer,
    .metric-card,
    .patch-vector,
    .prevention-card,
    .ai-response-card,
    .hero-banner,
    .alert-banner,
    .empty-state {
        position: relative;
        overflow: hidden;
    }
    .module-explainer {
        background: linear-gradient(135deg, rgba(99,102,241,0.10) 0%, rgba(124,58,237,0.06) 45%, rgba(34,211,238,0.04) 100%);
        border: 1px solid rgba(99,102,241,0.16);
        border-left: 3px solid #6366F1;
        padding: 16px 18px;
        border-radius: 16px;
        margin-bottom: 20px;
        color: #B8CCFF;
        font-size: 13px;
        line-height: 1.65;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .module-explainer::after {
        content: '';
        position: absolute;
        top: -10px; right: -10px;
        width: 150px; height: 150px;
        background: radial-gradient(circle at top right, rgba(99,102,241,0.10), transparent 70%);
        border-radius: 50%;
    }
    .hero-banner {
        background:
            radial-gradient(circle at 80% 20%, rgba(34,211,238,0.10), transparent 16%),
            radial-gradient(circle at 12% 18%, rgba(99,102,241,0.14), transparent 18%),
            linear-gradient(135deg, rgba(10,14,28,0.95) 0%, rgba(10,14,26,0.94) 45%, rgba(7,10,18,0.98) 100%);
        border: 1px solid rgba(99,102,241,0.18);
        border-radius: 24px;
        padding: 30px 32px;
        margin: 8px 0 20px 0;
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -100px; right: -70px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(99,102,241,0.18), transparent 70%);
        border-radius: 50%;
        filter: blur(8px);
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -60px; left: 26%;
        width: 240px; height: 240px;
        background: radial-gradient(circle, rgba(124,58,237,0.10), transparent 70%);
        border-radius: 50%;
        filter: blur(8px);
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 31px;
        font-weight: 800;
        background: linear-gradient(135deg, #F5F8FF 0%, #A5B4FC 38%, #C084FC 72%, #67E8F9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
        letter-spacing: -0.8px;
        line-height: 1.15;
    }
    .hero-subtitle {
        color: #7785A6;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 1.55px;
        text-transform: uppercase;
        margin: 0;
    }
    .alert-banner {
        background: linear-gradient(135deg, rgba(15,23,42,0.86) 0%, rgba(10,14,24,0.92) 100%);
        border: 1px solid rgba(239,68,68,0.20);
        border-left: 4px solid #EF4444;
        padding: 18px 24px;
        border-radius: 18px;
        margin-bottom: 24px;
        backdrop-filter: blur(18px);
        box-shadow: 0 12px 34px rgba(0,0,0,0.24), 0 0 24px rgba(239,68,68,0.05);
    }
    .alert-banner::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 220px; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(239,68,68,0.03));
    }
    .alert-banner::after {
        content:'';
        position:absolute;
        inset:0;
        background: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.03) 50%, transparent 70%);
        transform: translateX(-120%);
        animation: sheenMove 8s linear infinite;
    }
    .alert-banner-secure {
        border-color: rgba(16,185,129,0.24);
        border-left-color: #10B981;
        box-shadow: 0 12px 34px rgba(0,0,0,0.24), 0 0 24px rgba(16,185,129,0.05);
    }
    .alert-banner-secure::before {
        background: linear-gradient(90deg, transparent, rgba(16,185,129,0.03));
    }
    .status-critical,
    .status-secure {
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        display: inline-flex;
        align-items:center;
        gap:8px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .status-critical {
        background: linear-gradient(135deg, rgba(239,68,68,0.16), rgba(220,38,38,0.08));
        color: #FDB0B0;
        border: 1px solid rgba(239,68,68,0.28);
        box-shadow: 0 0 14px rgba(239,68,68,0.10);
    }
    .status-secure {
        background: linear-gradient(135deg, rgba(16,185,129,0.16), rgba(5,150,105,0.08));
        color: #84F4C2;
        border: 1px solid rgba(16,185,129,0.28);
        box-shadow: 0 0 14px rgba(16,185,129,0.10);
    }
    .metric-card {
        background:
            linear-gradient(135deg, rgba(14,20,38,0.86) 0%, rgba(10,14,28,0.88) 100%);
        border: 1px solid rgba(40,52,80,0.72);
        border-radius: 18px;
        padding: 18px 20px;
        transition: all 0.28s ease;
        backdrop-filter: blur(16px);
        box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,0.03);
        min-height: 122px;
    }
    .metric-card:hover {
        border-color: rgba(129,140,248,0.28);
        box-shadow: 0 12px 40px rgba(0,0,0,0.32), 0 0 18px rgba(99,102,241,0.07);
        transform: translateY(-3px);
    }
    .metric-card::before {
        content:'';
        position:absolute;
        inset:0;
        background: linear-gradient(120deg, transparent 35%, rgba(255,255,255,0.035) 50%, transparent 65%);
        transform: translateX(-120%);
        transition: transform 0.8s ease;
    }
    .metric-card:hover::before {
        transform: translateX(120%);
    }
    .metric-card::after {
        content: '';
        position: absolute;
        top: -18px; right: -18px;
        width: 95px; height: 95px;
        background: radial-gradient(circle at top right, rgba(99,102,241,0.08), transparent 70%);
        border-radius: 50%;
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 9px;
        font-weight: 700;
        color: #5F6E8C;
        text-transform: uppercase;
        letter-spacing: 1.55px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #F2F6FF;
        line-height: 1;
        margin-bottom: 6px;
        text-shadow: 0 0 18px rgba(99,102,241,0.10);
    }
    .metric-sub {
        font-size: 11px;
        color: #7182A3;
        font-family: 'Inter', sans-serif;
    }
    .metric-accent-purple { border-top: 2px solid #6366F1; }
    .metric-accent-red { border-top: 2px solid #EF4444; }
    .metric-accent-green { border-top: 2px solid #10B981; }
    .metric-accent-amber { border-top: 2px solid #F59E0B; }
    /* Executive top panel */
    .executive-grid {
        display:grid;
        grid-template-columns: repeat(4, minmax(0,1fr));
        gap:14px;
        margin: 0 0 18px 0;
    }
    .exec-panel {
        background: linear-gradient(135deg, rgba(12,17,33,0.84), rgba(8,12,24,0.88));
        border:1px solid rgba(46,58,90,0.62);
        border-radius:18px;
        padding:16px 18px;
        backdrop-filter: blur(16px);
        box-shadow: var(--shadow-soft);
        position:relative;
        overflow:hidden;
        min-height:108px;
    }
    .exec-panel::after{
        content:'';
        position:absolute;
        top:-25px; right:-25px;
        width:90px; height:90px;
        background: radial-gradient(circle, rgba(99,102,241,0.15), transparent 70%);
        border-radius:50%;
    }
    .exec-kicker{
        font-family:'JetBrains Mono', monospace;
        font-size:9px;
        letter-spacing:1.6px;
        text-transform:uppercase;
        color:#61708E;
        margin-bottom:10px;
    }
    .exec-value{
        font-family:'Space Grotesk', sans-serif;
        font-size:24px;
        font-weight:800;
        color:#F4F7FF;
        line-height:1;
        margin-bottom:7px;
    }
    .exec-sub{
        color:#7A88A7;
        font-size:11px;
    }
    .exec-dot{
        display:inline-block;
        width:8px; height:8px;
        border-radius:50%;
        margin-right:7px;
        box-shadow:0 0 14px currentColor;
    }
    /* Timeline */
    .investigation-timeline{
        background: linear-gradient(135deg, rgba(9,14,28,0.78), rgba(7,10,18,0.90));
        border:1px solid rgba(99,102,241,0.14);
        border-radius:18px;
        padding:16px;
        margin: 0 0 22px 0;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-soft);
    }
    .timeline-track{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
    }
    .timeline-step{
        position:relative;
        padding:10px 14px;
        border-radius:999px;
        background: linear-gradient(135deg, rgba(99,102,241,0.10), rgba(124,58,237,0.08));
        border:1px solid rgba(99,102,241,0.16);
        color:#B8C7FF;
        font-size:10px;
        font-family:'JetBrains Mono', monospace;
        letter-spacing:0.6px;
        text-transform:uppercase;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }
    .timeline-arrow{
        color:#55637D;
        font-size:14px;
        font-family:'JetBrains Mono', monospace;
    }
    /* DataFrame */
    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(35,45,72,0.55) !important;
        box-shadow: var(--shadow-soft);
        background: rgba(8,12,24,0.5) !important;
    }
    /* Slider */
    [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
        background: linear-gradient(135deg, #4F46E5, #06B6D4) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    [data-testid="stSlider"] [role="slider"] {
        background: #818CF8 !important;
        box-shadow: 0 0 14px rgba(129,140,248,0.45) !important;
    }
    /* Info / success / warning */
    [data-testid="stInfo"],
    [data-testid="stSuccess"],
    [data-testid="stWarning"] {
        border-radius: 14px !important;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-soft);
    }
    [data-testid="stInfo"] {
        background: rgba(99,102,241,0.08) !important;
        border: 1px solid rgba(99,102,241,0.18) !important;
        color: #B8C7FF !important;
    }
    [data-testid="stSuccess"] {
        background: rgba(16,185,129,0.08) !important;
        border: 1px solid rgba(16,185,129,0.18) !important;
    }
    [data-testid="stWarning"] {
        background: rgba(245,158,11,0.08) !important;
        border: 1px solid rgba(245,158,11,0.18) !important;
    }
    [data-testid="stCheckbox"] label {
        color: #8A99B8 !important;
        font-size: 12px !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stSpinner"] {
        color: #818CF8 !important;
    }
    .empty-state {
        background: linear-gradient(135deg, rgba(12,18,34,0.84) 0%, rgba(8,11,20,0.90) 100%);
        border: 1px dashed rgba(99,102,241,0.24);
        padding: 80px 40px;
        border-radius: 24px;
        text-align: center;
        margin-top: 40px;
        backdrop-filter: blur(18px);
        box-shadow: var(--shadow);
    }
    .empty-state::before {
        content: '';
        position: absolute;
        top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 360px; height: 360px;
        background: radial-gradient(circle, rgba(99,102,241,0.08), transparent 70%);
        filter: blur(4px);
    }
    .empty-icon {
        font-size: 52px;
        margin-bottom: 16px;
        filter: drop-shadow(0 0 20px rgba(99,102,241,0.35));
    }
    .empty-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 800;
        color: #7A89A8;
        margin-bottom: 10px;
    }
    .empty-desc {
        color: #53617D;
        font-size: 13px;
        max-width: 460px;
        margin: 0 auto;
        line-height: 1.75;
        font-family: 'Inter', sans-serif;
    }
    code {
        background: rgba(99,102,241,0.10) !important;
        color: #C9D6FF !important;
        padding: 3px 7px !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        border: 1px solid rgba(99,102,241,0.15) !important;
    }
    .ai-response-card {
        background:
            radial-gradient(circle at top right, rgba(99,102,241,0.08), transparent 25%),
            linear-gradient(135deg, rgba(5,9,19,0.96) 0%, rgba(8,12,24,0.96) 100%);
        padding: 24px 24px;
        border: 1px solid rgba(99,102,241,0.18);
        border-radius: 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #D6E0F4;
        white-space: pre-wrap;
        line-height: 1.8;
        backdrop-filter: blur(18px);
        box-shadow: 0 0 44px rgba(99,102,241,0.06), inset 0 1px 0 rgba(255,255,255,0.03);
    }
    .ai-response-card::before {
        content: 'AI INTELLIGENCE STREAM';
        position: absolute;
        top: 12px; right: 16px;
        font-size: 9px;
        color: rgba(129,140,248,0.42);
        letter-spacing: 1.6px;
    }
    .patch-vector {
        background: linear-gradient(135deg, rgba(239,68,68,0.06), rgba(99,102,241,0.03));
        padding: 15px 18px;
        border-left: 3px solid #EF4444;
        border-top: 1px solid rgba(239,68,68,0.10);
        border-right: 1px solid rgba(239,68,68,0.10);
        border-bottom: 1px solid rgba(239,68,68,0.10);
        margin-bottom: 12px;
        border-radius: 14px;
        transition: all 0.22s ease;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-soft);
    }
    .patch-vector:hover {
        background: linear-gradient(135deg, rgba(239,68,68,0.10), rgba(99,102,241,0.05));
        box-shadow: 0 8px 26px rgba(239,68,68,0.08);
        transform: translateY(-2px);
    }
    .prevention-card {
        background: linear-gradient(135deg, rgba(14,20,38,0.84), rgba(10,14,28,0.88));
        border: 1px solid rgba(40,52,80,0.65);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.22s ease;
        box-shadow: var(--shadow-soft);
    }
    .prevention-card:hover {
        border-color: rgba(99,102,241,0.20);
    }
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.25), transparent);
        margin: 20px 0;
    }
    .stack-section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 800;
        color: #7282A1;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(31,41,55,0.5);
    }
    .stPlotlyChart {
        background: linear-gradient(135deg, rgba(7,11,22,0.42), rgba(7,11,22,0.16));
        border: 1px solid rgba(40,52,80,0.32);
        border-radius: 18px;
        padding: 10px 10px 4px 10px;
        box-shadow: var(--shadow-soft);
        backdrop-filter: blur(8px);
    }
    .js-plotly-plot .plotly .modebar {
        background: rgba(10,14,26,0.35) !important;
        border: 1px solid rgba(99,102,241,0.10) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    .glass-mini {
        background: linear-gradient(135deg, rgba(17,24,39,0.6), rgba(11,15,26,0.72));
        border:1px solid rgba(31,41,55,0.55);
        border-radius:12px;
        padding:10px 14px;
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-soft);
    }
    @media (max-width: 1200px) {
        .executive-grid {
            grid-template-columns: repeat(2, minmax(0,1fr));
        }
    }
    @media (max-width: 768px) {
        .hero-title { font-size: 24px; }
        .executive-grid {
            grid-template-columns: repeat(1, minmax(0,1fr));
        }
        .block-container {
            padding: 0rem 0.75rem 2rem 0.75rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)
# =========================================================================
# 📡 3. FILE FORMAT PARSER LAYER
# =========================================================================
def parse_to_dataframe(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame()
    file_name = uploaded_file.name.lower()
    if file_name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif file_name.endswith('.txt'):
        string_data = uploaded_file.read().decode("utf-8")
        lines = [line.strip() for line in string_data.split('\n') if line.strip()]
        parsed_records = []
        for index, text_str in enumerate(lines):
            time_match = re.search(r'(\d{2}):(\d{2})', text_str)
            timestamp = f"17/06/2026 {time_match.group(0)}:00" if time_match else "17/06/2026 12:00:00"
            sender_match = re.search(r'^([^:]+):', text_str)
            contact = sender_match.group(1).strip() if sender_match else f"TXT_NODE_{index+1:02d}"
            parsed_records.append({
                "timestamp": timestamp, "contact": contact, "message": text_str,
                "duration": 0, "duration_sec": 0, "payload_bytes": len(text_str)
            })
        return pd.DataFrame(parsed_records)
    elif file_name.endswith('.pdf'):
        try:
            pdf_reader = PdfReader(uploaded_file)
            pdf_lines = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    pdf_lines.extend([line.strip() for line in text.split('\n') if line.strip()])
            parsed_records = []
            for index, text_str in enumerate(pdf_lines):
                time_match = re.search(r'(\d{2}):(\d{2})', text_str)
                timestamp = f"17/06/2026 {time_match.group(0)}:00" if time_match else "17/06/2026 12:00:00"
                parsed_records.append({
                    "timestamp": timestamp, "contact": f"PDF_EXTRACT_NODE_{index+1:02d}",
                    "message": text_str[:150], "duration": 0, "duration_sec": 0, "payload_bytes": len(text_str)
                })
            return pd.DataFrame(parsed_records)
        except:
            return pd.DataFrame()
    return pd.DataFrame()
# =========================================================================
# 🧬 4. EXTRACTION PIPELINE
# =========================================================================
def extract_and_calculate_forensics(calls_file, chats_file):
    df_calls = parse_to_dataframe(calls_file)
    df_chats = parse_to_dataframe(chats_file)
    if df_calls.empty and df_chats.empty:
        return None
    consolidated_records = []
    if not df_calls.empty:
        col_map = {c.lower(): c for c in df_calls.columns}
        contact_field = col_map.get("contact") or col_map.get("phone") or df_calls.columns[0]
        time_field = col_map.get("timestamp") or col_map.get("time") or df_calls.columns[min(1, len(df_calls.columns)-1)]
        duration_field = col_map.get("duration") or df_calls.columns[min(2, len(df_calls.columns)-1)]
        for _, row in df_calls.iterrows():
            try:
                hour_match = re.search(r'(\d{2}):', str(row[time_field]))
                parsed_hour = int(hour_match.group(1)) if hour_match else 12
            except:
                parsed_hour = 12
            try:
                duration_val = float(row[duration_field])
            except:
                duration_val = 0.0
            consolidated_records.append({
                "timestamp": str(row[time_field]) if time_field in row else "17/06/2026 12:00:00", 
                "contact": str(row[contact_field]).strip(), "duration_sec": duration_val,
                "payload_bytes": 0.0, "hour": parsed_hour, "text_content": "Voice Call Audio Logged", "log_type": "Call Log"
            })
    if not df_chats.empty:
        col_map = {c.lower(): c for c in df_chats.columns}
        contact_field = col_map.get("contact") or col_map.get("sender") or df_chats.columns[0]
        time_field = col_map.get("timestamp") or col_map.get("time") or df_chats.columns[min(1, len(df_chats.columns)-1)]
        message_field = col_map.get("message") or col_map.get("text") or df_chats.columns[min(2, len(df_chats.columns)-1)]
        for _, row in df_chats.iterrows():
            raw_time_str = str(row[time_field])
            try:
                hour_match = re.search(r'(\d{2}):', raw_time_str)
                parsed_hour = int(hour_match.group(1)) if hour_match else 12
            except:
                parsed_hour = 12
            msg_body = str(row[message_field]) if message_field in df_chats.columns else "Unstructured Stream"
            consolidated_records.append({
                "timestamp": raw_time_str, "contact": str(row[contact_field]).strip(), "duration_sec": 0.0,
                "payload_bytes": float(len(msg_body)), "hour": parsed_hour, "text_content": msg_body, "log_type": "Chat Log"
            })
    master_df = pd.DataFrame(consolidated_records)
    master_df["timestamp"] = pd.to_datetime(master_df["timestamp"], errors="coerce", dayfirst=True)
    if len(master_df) < 5:
        master_df["anomaly_score"] = 50.0
        return master_df
    interaction_counts = master_df.groupby("contact")["contact"].transform("count")
    master_df["contact_frequency"] = np.log1p(interaction_counts)
    master_df["off_hour_flag"] = master_df["hour"].apply(lambda x: 1 if x >= 22 or x <= 4 else 0)
    X_raw = master_df[["duration_sec", "payload_bytes", "hour", "contact_frequency", "off_hour_flag"]].fillna(0)
    scaled_matrix = StandardScaler().fit_transform(X_raw)
    iforest = IsolationForest(contamination=0.08, random_state=42).fit(scaled_matrix)
    raw_scores = iforest.score_samples(scaled_matrix)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    if max_s != min_s:
        master_df["anomaly_score"] = np.round((1.0 - (raw_scores - min_s) / (max_s - min_s)) * 100, 1)
    else:
        master_df["anomaly_score"] = 50.0
    return master_df
# =========================================================================
# 🧠 5. AI INFERENCE MECHANISM
# =========================================================================
def run_dynamic_ai_inference(df, user_query, optional_api_key=None):
    if df is None or df.empty: 
        return "⚠️ Registry empty. Please load logs first."
    q = user_query.lower().strip()
    freq = df["contact"].value_counts()
    highest_violators_df = df.sort_values("anomaly_score", ascending=False).head(5)
    top_row = df.loc[df["anomaly_score"].idxmax()] if not df.empty else None
    top_hour = df.groupby("hour").size().idxmax() if not df.empty else 12
    count_hour = df.groupby("hour").size().max() if not df.empty else 0
    if optional_api_key:
        try:
            genai.configure(api_key=optional_api_key.strip())
            generative_model = genai.GenerativeModel("gemini-2.5-flash")
            highest_violators = highest_violators_df[["timestamp", "contact", "anomaly_score", "text_content"]].to_string()
            frequent_nodes = freq.head(5).to_string()
            busiest_hours = df.groupby("hour").size().sort_values(ascending=False).head(3).to_string()
            prompt_payload = f"""
            You are TraceLens Premium Core Intelligence AI, an advanced cyber security assistant.
            Answer the user's specific query with absolute technical accuracy using the system stats below.
            If they ask a creative, different, or custom question, synthesize your knowledge to answer them perfectly in clear Hinglish.
            --- CRITICAL LOG CONTEXT METRICS ---
            Total Parsed Log Records: {len(df)} entries
            Total Unique Nodes: {df['contact'].nunique()}
            Average Anomaly Score: {df['anomaly_score'].mean():.2f}%
            Top Active Network Nodes:
            {frequent_nodes}
            Peak Activity Hours Breakdown:
            {busiest_hours}
            Top Potential Anomaly Threat Signatures:
            {highest_violators}
            User Query: "{user_query}"
            """
            response = generative_model.generate_content(prompt_payload)
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass
    if any(k in q for k in ["hour", "time", "clock", "samay", "busiest"]):
        return f"🕒 TEMPORAL MATRIX ANALYSIS\n\nData ke computation ke mutabik sabse zyada activity {top_hour:02d}:00 Hrs par detect hui hai, jisme total {count_hour} logs operational paye gaye hain."
    if any(k in q for k in ["called", "frequent", "contact", "node", "sender", "user"]):
        return f"📊 ENDPOINT INTERCEPT INSIGHTS\n\nAapke system me sabse zyada active ya targeted node/contact '{freq.index[0]}' hai, jo pure system records me {freq.iloc[0]} baar paya gaya hai."
    if any(k in q for k in ["risk", "threat", "suspicious", "danger", "anomaly", "hack"]):
        return f"🚨 OUTLIER SECURITY WARNING\n\nPrimary threat detection engine ne node '{top_row['contact']}' ko sabse zyada high risk par flag kiya hai, jiska anomaly threat metric {top_row['anomaly_score']}% hai."
    if any(k in q for k in ["summary", "report", "stats", "all"]):
        return f"📋 COMPREHENSIVE NODE TELEMETRY REPORT\n\n• Total Scanned Records: {len(df)} entries\n• Unique Endpoints Intercepted: {df['contact'].nunique()} nodes\n• System-wide Average Risk: {df['anomaly_score'].mean():.2f}%\n• Highest Threat Signature: {top_row['contact']} ({top_row['anomaly_score']}% Risk)\n• Peak Network Hour: {top_hour:02d}:00 Hrs"
    if any(k in q for k in ["tip", "advice", "mitigate", "prevent", "secure"]):
        return f"💡 CYBER FORENSICS TACTICAL TIP\n\nSuspect node '{top_row['contact']}' ka anomaly score {top_row['anomaly_score']}% hai. Is critical vector breach se bachne ke liye firewall rule set kijiye aur off-hours (22:00 - 04:00) ke encrypted blocks ko incoming requests se immediate drop kijiye."
    return f"🤖 TRACELENS BASELINE TELEMETRY CORE\n\nAapke query '{user_query}' ke context me, dashboard data ready hai. System me is waqt total {len(df)} logs hain aur {df['contact'].nunique()} unique nodes operational layer par active hain. Current average security risk index {df['anomaly_score'].mean():.2f}% calculated hai."
# =========================================================================
# 🎛️ 6. SIDEBAR
# =========================================================================
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="hero-badge" style="margin-bottom:10px;">
        <span class="live-dot"></span>SYSTEM ONLINE
    </div>
    <div class="sidebar-brand-title">🛡️ TraceLens AI</div>
    <div class="sidebar-brand-sub">Cyber Forensics Node v2.0</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section-label">INGESTION CHANNELS</div>', unsafe_allow_html=True)
dropped_calls_file = st.sidebar.file_uploader("Call Data Logs (.csv, .txt, .pdf)", type=["csv", "txt", "pdf"], key="uploader_calls_stream")
dropped_chats_file = st.sidebar.file_uploader("Chat Script Logs (.csv, .txt, .pdf)", type=["csv", "txt", "pdf"], key="uploader_chats_stream")
st.sidebar.markdown('<div class="sidebar-section-label">ACTIONS</div>', unsafe_allow_html=True)
if st.sidebar.button("⚡ EXECUTE ANALYSIS", use_container_width=True):
    if dropped_calls_file or dropped_chats_file:
        with st.spinner("Processing forensic artifacts..."):
            st.session_state.forensic_dataframe = extract_and_calculate_forensics(dropped_calls_file, dropped_chats_file)
        st.session_state.demo_data_loaded = False
        st.session_state.ai_response_cache = ""
        st.rerun()
    else:
        st.sidebar.error("Drop verification sources first.")
if st.sidebar.button("🧪 LOAD DEMO DATASET", use_container_width=True):
    sample_nodes = ["+91 90021 55432", "compromised_mainframe_node", "+91 88812 00941", "unverified_vpn_gateway"]
    generated_mock_records = []
    for index in range(115):
        hour_window = int(np.random.choice([2, 4, 11, 15, 20, 23]))
        chosen_node = str(np.random.choice(sample_nodes, p=[0.25, 0.35, 0.20, 0.20]))
        text_payload = "Encrypted telemetry relay block sequence."
        if hour_window <= 4 and chosen_node == "compromised_mainframe_node":
            text_payload = "CRITICAL BREACH // Unauthorized ledger modifications detected. OTP bypassed: 8912"
        generated_mock_records.append({
            "timestamp": f"17/06/2026 {hour_window:02d}:{np.random.randint(10,59):02d}:00", "contact": chosen_node,
            "duration_sec": float(np.random.randint(0, 420)) if index % 2 == 0 else 0.0,
            "payload_bytes": float(np.random.randint(25, 1200)) if index % 2 != 0 else 0.0,
            "hour": hour_window, "text_content": text_payload, "log_type": "Call Log" if index % 2 == 0 else "Chat Log"
        })
    df_synthetic = pd.DataFrame(generated_mock_records)
    df_synthetic["timestamp"] = pd.to_datetime(df_synthetic["timestamp"], dayfirst=True)
    df_synthetic["anomaly_score"] = np.random.uniform(10, 62, len(df_synthetic))
    df_synthetic.loc[
        (df_synthetic["hour"] <= 4) & (df_synthetic["contact"] == "compromised_mainframe_node"),
        "anomaly_score"
    ] = np.random.uniform(
        84, 99,
        len(df_synthetic[(df_synthetic["hour"] <= 4) & (df_synthetic["contact"] == "compromised_mainframe_node")])
    )
    st.session_state.forensic_dataframe = df_synthetic
    st.session_state.demo_data_loaded = True
    st.session_state.ai_response_cache = ""
st.sidebar.markdown('<div class="sidebar-section-label">AI CORE</div>', unsafe_allow_html=True)
raw_input_key = st.sidebar.text_input("Paste Gemini API Key", type="password", placeholder="AI Key Matrix...")
cleaned_gemini_key = raw_input_key.strip()
if cleaned_gemini_key and cleaned_gemini_key != st.session_state.validated_api_key:
    if len(cleaned_gemini_key) >= 20:
        st.session_state.gemini_api_authenticated = True
        st.session_state.validated_api_key = cleaned_gemini_key
        st.sidebar.success("✅ AI Core Authenticated")
if st.session_state.gemini_api_authenticated:
    st.sidebar.markdown("""
    <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:12px; padding:10px 12px; font-family:'JetBrains Mono',monospace; font-size:10px; color:#6EE7B7; letter-spacing:0.5px; box-shadow:0 8px 20px rgba(0,0,0,0.15);">
        <span style="display:inline-block;width:7px;height:7px;background:#10B981;border-radius:50%;margin-right:6px;box-shadow:0 0 10px #10B981;"></span>GEMINI 2.5 FLASH ACTIVE
    </div>
    """, unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section-label">WORKSPACE</div>', unsafe_allow_html=True)
if st.sidebar.button("🗑️ PURGE WORKSPACE", use_container_width=True):
    st.session_state.forensic_dataframe = None
    st.session_state.demo_data_loaded = False
    st.session_state.gemini_api_authenticated = False
    st.session_state.validated_api_key = None
    st.session_state.ai_response_cache = ""
    st.rerun()
# =========================================================================
# 🏢 MAIN COMMAND PANEL
# =========================================================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">
        <span class="live-dot"></span>PRODUCTION ENVIRONMENT
    </div>
    <h1 class="hero-title">🛡️ TraceLens Premium AI</h1>
    <p class="hero-subtitle">Operational Command Deck // Unsupervised Outlier Analytics Engine</p>
</div>
""", unsafe_allow_html=True)
if st.session_state.forensic_dataframe is not None:
    current_df = st.session_state.forensic_dataframe
    global_max_risk = current_df["anomaly_score"].max()
    is_critical = global_max_risk > 78
    evaluation_style = "status-critical" if is_critical else "status-secure"
    evaluation_text = "⚡ CRITICAL VECTOR BREACH" if is_critical else "✓ INTEGRITY SEAMLESS"
    primary_suspect_id = current_df.loc[current_df["anomaly_score"].idxmax()]["contact"]
    alert_extra_class = "" if is_critical else "alert-banner-secure"
    avg_risk = current_df["anomaly_score"].mean()
    off_hour_pct = (current_df["hour"].apply(lambda x: x >= 22 or x <= 4).sum() / len(current_df) * 100) if len(current_df) > 0 else 0
    network_health = max(0, 100 - avg_risk)
    ai_conf = min(99.1, 71 + (len(current_df) / max(1, current_df["contact"].nunique())))
    st.markdown(f"""
    <div class="executive-grid">
        <div class="exec-panel">
            <div class="exec-kicker">Global Security Score</div>
            <div class="exec-value" style="color:{'#F87171' if avg_risk > 60 else '#FBBF24' if avg_risk > 40 else '#34D399'};">{max(0, 100-avg_risk):.1f}</div>
            <div class="exec-sub"><span class="exec-dot" style="color:{'#EF4444' if avg_risk > 60 else '#F59E0B' if avg_risk > 40 else '#10B981'};"></span>Computed from live anomaly baseline</div>
        </div>
        <div class="exec-panel">
            <div class="exec-kicker">Threat Exposure</div>
            <div class="exec-value" style="color:#F43F5E;">{global_max_risk:.1f}%</div>
            <div class="exec-sub"><span class="exec-dot" style="color:#F43F5E;"></span>Highest observed threat signature</div>
        </div>
        <div class="exec-panel">
            <div class="exec-kicker">AI Confidence Score</div>
            <div class="exec-value" style="color:#67E8F9;">{ai_conf:.1f}%</div>
            <div class="exec-sub"><span class="exec-dot" style="color:#22D3EE;"></span>Inference layer telemetry stability</div>
        </div>
        <div class="exec-panel">
            <div class="exec-kicker">Network Health Index</div>
            <div class="exec-value" style="color:{'#10B981' if network_health > 55 else '#F59E0B' if network_health > 30 else '#EF4444'};">{network_health:.1f}</div>
            <div class="exec-sub"><span class="exec-dot" style="color:{'#10B981' if network_health > 55 else '#F59E0B' if network_health > 30 else '#EF4444'};"></span>Derived from current traffic posture</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="investigation-timeline">
        <div class="timeline-track">
            <div class="timeline-step">Upload</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Parsing</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Detection</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Threat Analysis</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Risk Classification</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">AI Investigation</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Mitigation</div>
            <div class="timeline-arrow">→</div>
            <div class="timeline-step">Final Verdict</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card metric-accent-purple">
            <div class="metric-label">📁 Total Records</div>
            <div class="metric-value">{len(current_df):,}</div>
            <div class="metric-sub">Log entries parsed</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card metric-accent-amber">
            <div class="metric-label">🌐 Unique Nodes</div>
            <div class="metric-value">{current_df['contact'].nunique()}</div>
            <div class="metric-sub">Active endpoints</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        risk_color = "#EF4444" if avg_risk > 60 else "#F59E0B" if avg_risk > 40 else "#10B981"
        st.markdown(f"""
        <div class="metric-card metric-accent-red">
            <div class="metric-label">⚠️ Avg Risk Score</div>
            <div class="metric-value" style="color:{risk_color};">{avg_risk:.1f}%</div>
            <div class="metric-sub">System-wide average</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card metric-accent-green">
            <div class="metric-label">🎯 Peak Risk</div>
            <div class="metric-value" style="color:#EF4444;">{global_max_risk:.1f}%</div>
            <div class="metric-sub">{primary_suspect_id[:16]}{'...' if len(primary_suspect_id)>16 else ''}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="alert-banner {alert_extra_class}">
        <div style="display:flex; align-items:center; gap:24px; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:18px;">{'🚨' if is_critical else '✅'}</span>
                <div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px;">Evaluation Status</div>
                    <span class="{evaluation_style}">{evaluation_text}</span>
                </div>
            </div>
            <div style="width:1px; height:36px; background:rgba(55,65,81,0.5);"></div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px;">Primary Suspect Node</div>
                <code style="font-size:13px; color:#F43F5E !important; background:rgba(239,68,68,0.08) !important; border-color:rgba(239,68,68,0.2) !important;">{primary_suspect_id}</code>
            </div>
            <div style="width:1px; height:36px; background:rgba(55,65,81,0.5);"></div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px;">Protocol Status</div>
                <span style="color:#B8CCFF; font-size:12px; font-family:'Inter',sans-serif;">Sandbox isolation maps online</span>
            </div>
            <div style="width:1px; height:36px; background:rgba(55,65,81,0.5);"></div>
            <div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:4px;">Off-Hour Traffic</div>
                <span style="font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:800; color:#F59E0B;">{off_hour_pct:.1f}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    t_ledger, t_metrics, t_topology, t_profile, t_matrix, t_mitigation, t_prevention, t_horizon, t_action, t_commander = st.tabs([
        "📜 Time Ledger", 
        "📊 Metrics", 
        "🌐 Network Map", 
        "🔎 Node Profiler",
        "🧮 Threat Matrix", 
        "🛡️ Mitigation Hub", 
        "🔒 Prevention", 
        "🔮 Risk Horizon", 
        "⚡ Live Action", 
        "🤖 AI Commander"
    ])
    # --- TAB 1: TIME LEDGER ---
    with t_ledger:
        st.markdown("<div class='module-explainer'><b>📜 Time Ledger Array</b> — Sequential indexing timeline data arrays decrypted and parsed via isolation system matrix parameters. Every entry is ranked by anomaly weight.</div>", unsafe_allow_html=True)
        col_filter1, col_filter2 = st.columns([1, 3])
        with col_filter1:
            log_type_filter = st.selectbox("Filter by Type", ["All", "Call Log", "Chat Log"], key="ledger_filter")
        display_df = current_df.copy()
        if log_type_filter != "All":
            display_df = display_df[display_df["log_type"] == log_type_filter]
        st.dataframe(
            display_df.sort_values("timestamp", ascending=False).style.background_gradient(
                subset=["anomaly_score"], cmap="RdPu"
            ),
            use_container_width=True,
            height=450
        )
    # --- TAB 2: INTERACTIVE METRICS ---
    with t_metrics:
        st.markdown("<div class='module-explainer'><b>📊 Premium Interactive Metrics</b> — Move cursor over data clusters to inspect detailed metric configurations. All charts are interactive and zoomable.</div>", unsafe_allow_html=True)
        view_col1, view_col2 = st.columns(2)
        with view_col1:
            st.markdown("<div class='stack-section-title'>🕒 Hourly Traffic Distribution</div>", unsafe_allow_html=True)
            grouped_hourly_series = current_df.groupby("hour").size().reset_index(name="Log Count")
            fig_bar = px.bar(
                grouped_hourly_series, x="hour", y="Log Count",
                color="Log Count", color_continuous_scale=["#0F172A", "#4F46E5", "#22D3EE"],
                template="plotly_dark"
            )
            fig_bar.update_traces(
                marker_line_width=0,
                hovertemplate="<b>%{x}:00 hrs</b><br>Logs: %{y}<extra></extra>",
                opacity=0.95
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(3,7,18,0.78)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="rgba(31,41,55,0.35)", title="Hour", tickfont=dict(family="JetBrains Mono", size=10, color="#7080A0")),
                yaxis=dict(gridcolor="rgba(31,41,55,0.35)", title="Entries", tickfont=dict(family="JetBrains Mono", size=10, color="#7080A0")),
                font=dict(family="Inter", color="#C9D6F2"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        with view_col2:
            st.markdown("<div class='stack-section-title'>📌 Node Risk Ranking</div>", unsafe_allow_html=True)
            mean_score_ranking_df = current_df.groupby("contact")["anomaly_score"].mean().sort_values(ascending=False).reset_index()
            mean_score_ranking_df.columns = ["Node / Contact", "Avg Risk Score (%)"]
            mean_score_ranking_df["Avg Risk Score (%)"] = mean_score_ranking_df["Avg Risk Score (%)"].round(2)
            st.dataframe(
                mean_score_ranking_df.style.background_gradient(subset=["Avg Risk Score (%)"], cmap="Reds"),
                use_container_width=True, height=260
            )
        st.markdown("<div class='stack-section-title' style='margin-top:20px;'>📈 Isolation Forest — Anomaly Spatial Cluster Field</div>", unsafe_allow_html=True)
        fig_scatter = px.scatter(
            current_df, x="hour", y="anomaly_score",
            color="anomaly_score",
            size="anomaly_score",
            hover_data={"contact": True, "anomaly_score": True, "log_type": True},
            color_continuous_scale=[[0, "#1E1B4B"], [0.45, "#7C3AED"], [0.75, "#22D3EE"], [1, "#F43F5E"]],
            template="plotly_dark",
            size_max=18
        )
        computed_95_quantile = np.percentile(current_df["anomaly_score"], 95) if not current_df.empty else 75.0
        fig_scatter.add_shape(
            type="line",
            x0=current_df["hour"].min(), x1=current_df["hour"].max(),
            y0=computed_95_quantile, y1=computed_95_quantile,
            line=dict(color="#F43F5E", width=2, dash="dot")
        )
        fig_scatter.add_annotation(
            x=current_df["hour"].max(), y=computed_95_quantile,
            text=f" THREAT THRESHOLD ({computed_95_quantile:.1f}%)",
            showarrow=False, font=dict(color="#F43F5E", size=10, family="JetBrains Mono"),
            xanchor="right", yanchor="bottom"
        )
        fig_scatter.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Score: %{y:.1f}%<br>Hour: %{x}:00<extra></extra>",
            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.15)"))
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(3,7,18,0.78)",
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="rgba(31,41,55,0.28)", title="Ingestion Hour", tickfont=dict(family="JetBrains Mono", size=10, color="#7080A0")),
            yaxis=dict(gridcolor="rgba(31,41,55,0.28)", title="Threat Score %", tickfont=dict(family="JetBrains Mono", size=10, color="#7080A0")),
            font=dict(color="#D8E2F8")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("<div class='stack-section-title'>🍩 Log Type Distribution</div>", unsafe_allow_html=True)
        if "log_type" in current_df.columns:
            log_type_counts = current_df["log_type"].value_counts().reset_index()
            log_type_counts.columns = ["Log Type", "Count"]
            fig_donut = px.pie(
                log_type_counts, names="Log Type", values="Count",
                hole=0.68, template="plotly_dark",
                color_discrete_sequence=["#4F46E5", "#7C3AED", "#22D3EE"]
            )
            fig_donut.update_traces(
                textfont=dict(family="JetBrains Mono", size=11),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
                marker=dict(line=dict(color="rgba(255,255,255,0.05)", width=1))
            )
            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=10, b=10),
                height=220,
                legend=dict(font=dict(family="Inter", color="#7F8FB2"))
            )
            st.plotly_chart(fig_donut, use_container_width=True)
    # --- TAB 3: NETWORK TOPOGRAPHY ---
    with t_topology:
        st.markdown("<div class='module-explainer'><b>🌐 Topological Relational Mapping</b> — Zoomable, draggable canvas calculating node edge distances via mathematical positioning matrices. Node size = risk weight.</div>", unsafe_allow_html=True)
        network_relational_graph = nx.Graph()
        for _, row_data in current_df.head(30).iterrows():
            network_relational_graph.add_edge("CENTRAL_HUB", str(row_data["contact"]), weight=float(row_data["anomaly_score"]))
        network_positioning_layout = nx.spring_layout(network_relational_graph, k=0.5, seed=42)
        edge_x, edge_y = [], []
        for edge in network_relational_graph.edges():
            x0, y0 = network_positioning_layout[edge[0]]
            x1, y1 = network_positioning_layout[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.2, color='rgba(99,102,241,0.24)'),
            hoverinfo='none', mode='lines'
        )
        node_x, node_y, node_text, node_colors, node_sizes = [], [], [], [], []
        node_risk_map = current_df.groupby("contact")["anomaly_score"].mean().to_dict()
        for node in network_relational_graph.nodes():
            x, y = network_positioning_layout[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            risk = node_risk_map.get(node, 30)
            node_colors.append(risk)
            node_sizes.append(20 + risk * 0.4 if node != "CENTRAL_HUB" else 38)
            node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=8,
                title=dict(
                    text="Risk%",
                    font=dict(size=10, color="#7283A5", family="JetBrains Mono")
                ),
                tickfont=dict(size=9, color="#7283A5", family="JetBrains Mono"),
                bgcolor="rgba(0,0,0,0)",
                bordercolor="rgba(31,41,55,0.5)"
            ),
            line_width=2
        )
    )
       
            fig_network = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                template="plotly_dark",
                showlegend=False,
                hovermode='closest',
                margin=dict(b=10, l=5, r=5, t=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(3,7,18,0.78)",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=440
            )
        )
        st.plotly_chart(fig_network, use_container_width=True)
    # --- TAB 4: DEEP NODE PROFILER ---
    with t_profile:
        st.markdown("<div class='module-explainer'><b>🔎 Deep Node Profiler</b> — Select isolated communication strings to slice individual system traces. Full behavioral pattern analysis per endpoint.</div>", unsafe_allow_html=True)
        p_col1, p_col2 = st.columns([2, 1])
        with p_col1:
            chosen_target = st.selectbox("Select Target Endpoint:", current_df["contact"].unique(), key="profiler_select")
        if chosen_target:
            node_df = current_df[current_df["contact"] == chosen_target]
            avg_node_risk = node_df["anomaly_score"].mean()
            nc1, nc2, nc3 = st.columns(3)
            with nc1:
                st.markdown(f"""<div class="metric-card metric-accent-purple">
                    <div class="metric-label">Total Interactions</div>
                    <div class="metric-value">{len(node_df)}</div>
                    <div class="metric-sub">logged events</div>
                </div>""", unsafe_allow_html=True)
            with nc2:
                risk_c = "#EF4444" if avg_node_risk > 60 else "#F59E0B"
                st.markdown(f"""<div class="metric-card metric-accent-red">
                    <div class="metric-label">Avg Anomaly Score</div>
                    <div class="metric-value" style="color:{risk_c};">{avg_node_risk:.1f}%</div>
                    <div class="metric-sub">risk weight</div>
                </div>""", unsafe_allow_html=True)
            with nc3:
                off_hour_count = node_df[node_df["hour"].apply(lambda x: x >= 22 or x <= 4)].shape[0]
                st.markdown(f"""<div class="metric-card metric-accent-amber">
                    <div class="metric-label">Off-Hour Activity</div>
                    <div class="metric-value">{off_hour_count}</div>
                    <div class="metric-sub">22:00–04:00 events</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(node_df.style.background_gradient(subset=["anomaly_score"], cmap="RdPu"), use_container_width=True)
    # --- TAB 5: THREAT MATRIX ---
    with t_matrix:
        st.markdown("<div class='module-explainer'><b>🧮 Threat Matrix Engine</b> — Multivariate attribute radar maps plotted across polar mapping layouts. Vector dimensions show attack surface breadth per node.</div>", unsafe_allow_html=True)
        top_deviant_nodes = current_df.groupby("contact")[["anomaly_score", "hour", "payload_bytes"]].mean().reset_index().nlargest(4, "anomaly_score")
        fig_radar = go.Figure()
        colors = ["#6366F1", "#EF4444", "#F59E0B", "#10B981"]
        for idx, r_row in top_deviant_nodes.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[r_row["anomaly_score"], (r_row["hour"]/24)*100, np.log1p(r_row["payload_bytes"])*10],
                theta=['Threat Density', 'Time Weight', 'Data Load'],
                name=str(r_row["contact"])[:18],
                line=dict(color=colors[idx % len(colors)], width=2),
                fill='toself',
        fillcolor=hex_to_rgba(colors[idx % len(colors)], alpha=0.15) # <--- Ye correct hai
    ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, gridcolor="rgba(31,41,55,0.5)", tickfont=dict(family="JetBrains Mono", size=9, color="#7080A0")),
                angularaxis=dict(gridcolor="rgba(31,41,55,0.5)", tickfont=dict(family="Space Grotesk", size=11, color="#7D8DAF")),
                bgcolor="rgba(3,7,18,0.78)"
            ),
            showlegend=True,
            legend=dict(font=dict(family="Inter", color="#7D8DAF", size=11), bgcolor="rgba(0,0,0,0)"),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=30, r=30, t=30, b=30),
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    # --- TAB 6: MITIGATION HUB ---
    with t_mitigation:
        st.markdown("<div class='module-explainer'><b>🛡️ Mitigation Patch Hub</b> — Autonomous firewall mapping configuration strings targeted towards suspicious nodes. Apply patches to neutralize active vectors.</div>", unsafe_allow_html=True)
        highest_risk_nodes = current_df.groupby("contact")["anomaly_score"].mean().sort_values(ascending=False).head(4)
        for target_node_id, average_risk_weight in highest_risk_nodes.items():
            risk_level = "CRITICAL" if average_risk_weight > 75 else "HIGH" if average_risk_weight > 50 else "MEDIUM"
            risk_color = "#EF4444" if risk_level == "CRITICAL" else "#F59E0B" if risk_level == "HIGH" else "#6366F1"
            st.markdown(f"""
            <div class="patch-vector">
                <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:6px;">Patch Vector ID</div>
                        <code style="font-size:12px; color:#F43F5E !important;">{target_node_id}</code>
                    </div>
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:6px;">Threat Score</div>
                        <span style="font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:800; color:{risk_color};">{average_risk_weight:.1f}%</span>
                    </div>
                    <div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#5A6885; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:6px;">Severity</div>
                        <span style="background:{'rgba(239,68,68,0.12)' if risk_level=='CRITICAL' else 'rgba(245,158,11,0.12)'}; color:{risk_color}; padding:4px 10px; border-radius:999px; font-size:10px; font-weight:800; font-family:'JetBrains Mono'; border:1px solid {risk_color}40;">{risk_level}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"⚙️ Recommended firewall rule: `sudo iptables -A INPUT -s {target_node_id} -j DROP`")
     # --- TAB 7: PREVENTION CENTRE ---
    with t_prevention:
        st.markdown("<div class='module-explainer'><b>🔒 Prevention Centre</b> — Establish high-fidelity prevention strategies and rule sets to permanently fortify data flow architectures.</div>", unsafe_allow_html=True)
        p_col1, p_col2 = st.columns(2)

        with p_col1:
            st.markdown("<div class='stack-section-title'>🛡️ Rule Generator</div>", unsafe_allow_html=True)
            st.markdown('<div class="prevention-card">', unsafe_allow_html=True)
            st.checkbox("Enable Port 80/443 Traffic Rate Limiting", value=True, key="rule1")
            st.checkbox("Reject Multi-Node Ingress from Off-Hour VPN Blocks", value=True, key="rule2")
            st.checkbox("Drop Zero-Signature Log Overload Packets", value=False, key="rule3")
            st.checkbox("Flag Encrypted Payloads > 1MB from Unknown Nodes", value=True, key="rule4")
            st.checkbox("Block Repeated Auth Failures (>3 in 60s)", value=False, key="rule5")
            st.markdown('</div>', unsafe_allow_html=True)

        with p_col2:
            st.markdown("<div class='stack-section-title'>📊 Detection Thresholds</div>", unsafe_allow_html=True)
            computed_95_quantile = np.percentile(current_df["anomaly_score"], 95) if not current_df.empty else 75.0
            prevention_sensitivity = st.slider(
                "Global Isolation Threshold %",
                min_value=50, max_value=100, value=int(computed_95_quantile),
                key="prev_slider"
            )
            
            blocked_count = len(current_df[current_df["anomaly_score"] >= prevention_sensitivity])
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.06); border:1px solid rgba(239,68,68,0.15); border-radius:8px; padding:14px; margin-top:12px;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:#374151; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px;">ESTIMATED BLOCK COUNT</div>
                <div style="font-family:'Space Grotesk',sans-serif; font-size:28px; font-weight:800; color:#EF4444;">{blocked_count}</div>
                <div style="font-size:11px; color:#4B5563; margin-top:4px;">connections blocked above {prevention_sensitivity}% threshold</div>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 8: RISK HORIZON ---
    with t_horizon:
        st.markdown("<div class='module-explainer'><b>🔮 Risk Horizon Prediction</b> — Moving average forecasting structures showing calculated rolling trends. Identify escalating risk windows before they breach critical levels.</div>", unsafe_allow_html=True)
        
        df_sorted_time = current_df.sort_values("timestamp").reset_index(drop=True)
        window = max(2, len(df_sorted_time)//10)
        df_sorted_time["rolling_risk_mean"] = df_sorted_time["anomaly_score"].rolling(window=window, min_periods=1).mean()
        df_sorted_time["rolling_risk_upper"] = df_sorted_time["anomaly_score"].rolling(window=window, min_periods=1).max()
        df_sorted_time["rolling_risk_lower"] = df_sorted_time["anomaly_score"].rolling(window=window, min_periods=1).min()
        df_sorted_time["idx"] = range(len(df_sorted_time))

        fig_horizon = go.Figure()
        # Band fill
        fig_horizon.add_trace(go.Scatter(
            x=df_sorted_time["idx"], y=df_sorted_time["rolling_risk_upper"],
            mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
        ))
        fig_horizon.add_trace(go.Scatter(
            x=df_sorted_time["idx"], y=df_sorted_time["rolling_risk_lower"],
            mode='lines', fill='tonexty', fillcolor='rgba(124,58,237,0.07)',
            line=dict(width=0), showlegend=False, hoverinfo='skip'
        ))
        # Main line
        fig_horizon.add_trace(go.Scatter(
            x=df_sorted_time["idx"], y=df_sorted_time["rolling_risk_mean"],
            mode='lines', line=dict(color="#A855F7", width=2.5),
            name="Rolling Risk Mean",
            hovertemplate="Record %{x}<br>Risk: %{y:.1f}%<extra></extra>"
        ))
        fig_horizon.add_hline(
            y=78, line_color="#EF4444", line_dash="dot", line_width=1.5,
            annotation_text="CRITICAL THRESHOLD", annotation_font=dict(color="#EF4444", size=10, family="JetBrains Mono")
        )
        fig_horizon.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(3,7,18,0.8)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=360,
            xaxis=dict(gridcolor="rgba(31,41,55,0.3)", title="Log Index", tickfont=dict(family="JetBrains Mono", size=9, color="#4B5563")),
            yaxis=dict(gridcolor="rgba(31,41,55,0.3)", title="Risk Score %", tickfont=dict(family="JetBrains Mono", size=9, color="#4B5563")),
            showlegend=False
        )
        st.plotly_chart(fig_horizon, use_container_width=True)

    # --- TAB 9: LIVE ACTION ---
    with t_action:
        st.markdown("<div class='module-explainer'><b>⚡ Live Action Node</b> — Take real-time triage measures on active system artifacts. Emergency protocols and incident management.</div>", unsafe_allow_html=True)
        
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            st.markdown("<div class='stack-section-title'>🔴 Emergency Protocols</div>", unsafe_allow_html=True)
            st.button("🔴 TRIGGER CIRCUIT BREAKER (SHUTDOWN ROUTING)", key="action_shutdown")
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("📥 DOWNLOAD INCIDENT REGISTRY REPORT (CSV)", key="action_download")
            
        with act_col2:
            st.markdown("<div class='stack-section-title'>📡 System Status</div>", unsafe_allow_html=True)
            st.success("✅ Mainframe communication relay matching standard parameters.")
            
            off_hour_pct = (current_df["hour"].apply(lambda x: x >= 22 or x <= 4).sum() / len(current_df) * 100) if len(current_df) > 0 else 0
            st.markdown(f"""
            <div style="margin-top:12px; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(17,24,39,0.6); padding:10px 14px; border-radius:8px; border:1px solid rgba(31,41,55,0.5);">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#4B5563; text-transform:uppercase; letter-spacing:0.8px;">Off-Hour Traffic</span>
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:700; color:#F59E0B;">{off_hour_pct:.1f}%</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(17,24,39,0.6); padding:10px 14px; border-radius:8px; border:1px solid rgba(31,41,55,0.5);">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#4B5563; text-transform:uppercase; letter-spacing:0.8px;">Records Processed</span>
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:700; color:#818CF8;">{len(current_df):,}</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(17,24,39,0.6); padding:10px 14px; border-radius:8px; border:1px solid rgba(31,41,55,0.5);">
                    <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#4B5563; text-transform:uppercase; letter-spacing:0.8px;">Model Status</span>
                    <span style="font-family:'Space Grotesk',sans-serif; font-size:15px; font-weight:700; color:#10B981;">ACTIVE</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- TAB 10: AI COMMANDER ---
    with t_commander:
        st.markdown("<div class='module-explainer'><b>🤖 AI Commander Core</b> — Natural language interface to query operational forensic data. Powered by Gemini 2.5 Flash when API key is connected, with intelligent local fallback.</div>", unsafe_allow_html=True)
        
        output_block = st.empty()
        
        with st.form(key="foolproof_cyber_commander_form", clear_on_submit=False):
            ai_col1, ai_col2 = st.columns([4, 1])
            with ai_col1:
                user_forensic_prompt = st.text_input(
                    label="Enter Cyber Tactical Query:",
                    placeholder="e.g., Which node has highest risk? Ya koi anomaly critical hai?",
                    key="commander_input_matrix"
                )
            with ai_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                execute_query = st.form_submit_button(label="📡 TRANSMIT", use_container_width=True)
        
        # Quick query suggestions
        st.markdown("""
        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:-8px; margin-bottom:16px;">
            <span style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:4px 12px; border-radius:20px; font-size:10px; color:#818CF8; font-family:'JetBrains Mono',monospace; cursor:pointer;">Summary report</span>
            <span style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:4px 12px; border-radius:20px; font-size:10px; color:#818CF8; font-family:'JetBrains Mono',monospace; cursor:pointer;">Busiest hour?</span>
            <span style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:4px 12px; border-radius:20px; font-size:10px; color:#818CF8; font-family:'JetBrains Mono',monospace; cursor:pointer;">Most suspicious node?</span>
            <span style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:4px 12px; border-radius:20px; font-size:10px; color:#818CF8; font-family:'JetBrains Mono',monospace; cursor:pointer;">Security tips</span>
        </div>
        """, unsafe_allow_html=True)
        
        if execute_query:
            if user_forensic_prompt:
                with st.spinner("AI Engine processing forensic logs..."):
                    ai_inference_feedback = run_dynamic_ai_inference(
                        df=current_df,
                        user_query=user_forensic_prompt,
                        optional_api_key=st.session_state.validated_api_key
                    )
                st.session_state.ai_response_cache = ai_inference_feedback
            else:
                st.warning("⚠️ Query input cannot be empty.")

        if st.session_state.ai_response_cache:
            with output_block.container():
                st.markdown(
                    f"<div class='ai-response-card'>{st.session_state.ai_response_cache}</div>",
                    unsafe_allow_html=True
                )

else:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📡</div>
        <div class="empty-title">Operational Core Idle</div>
        <div class="empty-desc">
            Ingest forensic artifacts (.csv, .txt, .pdf) via the sidebar ingestion channels, 
            or load the demo dataset to initialize the multivariate anomaly detection engine.
        </div>
        <div style="margin-top:28px; display:flex; gap:12px; justify-content:center; flex-wrap:wrap;">
            <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:10px 20px; border-radius:10px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#4B5563;">
                01 → Upload logs via sidebar
            </div>
            <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:10px 20px; border-radius:10px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#4B5563;">
                02 → Execute analysis
            </div>
            <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15); padding:10px 20px; border-radius:10px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#4B5563;">
                03 → Explore 10 intelligence modules
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # =========================================================================
# 📄 PDF REPORT GENERATION & AI INVESTIGATION (INTEGRATED)
# =========================================================================

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="TraceLens AI Forensic Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Logs Analyzed: {len(df)}", ln=True)
    pdf.cell(200, 10, txt=f"Average Anomaly Score: {df['anomaly_score'].mean():.2f}%", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="Top Suspects:", ln=True)
    top_suspects = df.sort_values("anomaly_score", ascending=False).head(5)
    for _, row in top_suspects.iterrows():
        pdf.cell(200, 10, txt=f"- {row['contact']}: {row['anomaly_score']:.2f}%", ln=True)
    
    # PDF ko binary format mein return karna
    return pdf.output(dest='S').encode('latin-1')

# --- Chat Investigation AI Interface ---
st.markdown("### 🤖 Chat Investigation AI")
user_query = st.text_input("Ask AI about the forensics:", placeholder="Is node XYZ safe?")

if st.button("🔍 Run AI Analysis"):
    if st.session_state.forensic_dataframe is not None:
        with st.spinner("Analyzing artifacts..."):
            response = run_dynamic_ai_inference(st.session_state.forensic_dataframe, user_query, st.session_state.validated_api_key)
            st.markdown(f"**AI Insight:**\n\n{response}")
    else:
        st.warning("Please upload data first.")

# --- PDF Report Download Button ---
if st.session_state.forensic_dataframe is not None:
    pdf_data = generate_pdf_report(st.session_state.forensic_dataframe)
    st.download_button(
        label="📥 Download Forensic Report (PDF)",
        data=pdf_data,
        file_name="forensic_report.pdf",
        mime="application/pdf"
    )

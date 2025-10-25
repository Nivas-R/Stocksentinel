# ---- StockSentinel - Learning & Trading Intelligence ----
import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import os
import unicodedata
from fpdf import FPDF
import pytz
import time
import threading
import numpy as np
from plotly.subplots import make_subplots

# Ensure folder exists
os.makedirs("data", exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="STOCKSENTINEL",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'refresh_counter' not in st.session_state:
    st.session_state.refresh_counter = 0
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'price_alerts' not in st.session_state:
    st.session_state.price_alerts = {}
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = "Apple Inc."
if 'compact_mode' not in st.session_state:
    st.session_state.compact_mode = False
if 'compare_stocks' not in st.session_state:
    st.session_state.compare_stocks = []

# Modern Dark Professional Theme CSS
modern_dark_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@300;400;500;600;700;800&family=Roboto+Mono:wght@400;500;600&display=swap');

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .stHeaderActionElements {display: none;}

    /* Modern Dark Variables */
    :root {
        --bg-primary: #0a0e27;
        --bg-secondary: #1a1d29;
        --bg-card: #252836;
        --bg-card-hover: #2d3142;
        --text-primary: #FFFFFF;
        --text-secondary: #A0A0A0;
        --text-muted: #707070;
        --accent-teal: #00FFC6;
        --accent-cyan: #1de9b6;
        --accent-blue: #00d4ff;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(0, 255, 198, 0.3);
        --glow-teal: rgba(0, 255, 198, 0.4);
        --success: #00ff88;
        --danger: #ff4757;
        --warning: #ffa502;
        --glow-green: rgba(0, 255, 136, 0.6);
        --glow-red: rgba(255, 71, 87, 0.6);
    }

    /* Global Styles */
    * {
        font-family: 'Inter', 'Poppins', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0d1128 50%, var(--bg-primary) 100%);
        color: var(--text-primary);
    }

    /* Diagonal Grid Pattern Background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            linear-gradient(45deg, transparent 48%, rgba(0, 255, 198, 0.02) 49%, rgba(0, 255, 198, 0.02) 51%, transparent 52%),
            linear-gradient(-45deg, transparent 48%, rgba(0, 255, 198, 0.02) 49%, rgba(0, 255, 198, 0.02) 51%, transparent 52%);
        background-size: 40px 40px;
        opacity: 0.3;
        z-index: 0;
        pointer-events: none;
    }

    /* Hero Header Section */
    .hero-section {
        position: relative;
        background: linear-gradient(135deg, #1a1d29 0%, #252836 100%);
        border-radius: 16px;
        padding: 60px 40px;
        margin-bottom: 40px;
        border: 1px solid var(--border-subtle);
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 2px,
                rgba(0, 255, 198, 0.03) 2px,
                rgba(0, 255, 198, 0.03) 4px
            ),
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 2px,
                rgba(0, 255, 198, 0.03) 2px,
                rgba(0, 255, 198, 0.03) 4px
            );
        background-size: 30px 30px;
        opacity: 0.5;
        z-index: 0;
    }

    .hero-content {
        position: relative;
        z-index: 1;
    }

    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 900;
        color: var(--text-primary);
        margin: 0 0 16px 0;
        letter-spacing: -2px;
        line-height: 1.1;
    }

    .hero-title .accent {
        color: var(--accent-teal);
        text-shadow: 0 0 30px var(--glow-teal);
    }

    .hero-subtitle {
        font-size: clamp(1rem, 2vw, 1.3rem);
        color: var(--text-secondary);
        margin: 0 0 32px 0;
        font-weight: 400;
        line-height: 1.6;
    }

    .hero-cta {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--accent-teal);
        font-weight: 600;
        font-size: 1.1rem;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .hero-cta:hover {
        gap: 12px;
        text-shadow: 0 0 20px var(--glow-teal);
    }

    /* Glass Card - Modern Sharp Style */
    .glass-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-teal), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-accent);
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 255, 198, 0.15);
    }

    .glass-card:hover::before {
        opacity: 1;
    }

    .glass-card.compact {
        padding: 16px;
        margin: 12px 0;
    }

    /* Section Header */
    .section-header {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 48px 0 24px 0;
        padding: 0 0 16px 0;
        border-bottom: 2px solid var(--border-subtle);
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
    }

    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 120px;
        height: 2px;
        background: linear-gradient(90deg, var(--accent-teal), transparent);
    }

    .section-header .icon {
        color: var(--accent-teal);
        font-size: 1.6rem;
    }

    /* Metric Card */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 198, 0.1), transparent);
        transition: left 0.5s ease;
    }

    .metric-card:hover::before {
        left: 100%;
    }

    .metric-card:hover {
        transform: scale(1.05);
        border-color: var(--border-accent);
        box-shadow: 0 8px 24px rgba(0, 255, 198, 0.2);
    }

    .metric-card.compact {
        padding: 16px;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 8px;
        font-family: 'Roboto Mono', monospace;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }

    /* Stock Ticker Cards */
    .ticker-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .ticker-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 255, 198, 0.15);
    }

    .ticker-name {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .ticker-price {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 800;
        font-family: 'Roboto Mono', monospace;
        margin-bottom: 8px;
    }

    .ticker-change {
        font-size: 0.95rem;
        font-weight: 600;
        font-family: 'Roboto Mono', monospace;
    }

    /* Glowing Line Chart Styles */
    .glow-green-line {
        filter: drop-shadow(0 0 8px var(--glow-green)) drop-shadow(0 0 4px var(--glow-green));
    }

    .glow-red-line {
        filter: drop-shadow(0 0 8px var(--glow-red)) drop-shadow(0 0 4px var(--glow-red));
    }

    /* News Card */
    .news-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 24px;
        margin: 16px 0;
        transition: all 0.3s ease;
        position: relative;
    }

    .news-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent-teal);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .news-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 255, 198, 0.1);
    }

    .news-card:hover::before {
        opacity: 1;
    }

    .news-title {
        color: var(--text-primary);
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 12px;
        line-height: 1.4;
    }

    .news-description {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.7;
        margin-bottom: 16px;
    }

    /* Info Box */
    .info-box {
        background: rgba(0, 255, 198, 0.05);
        border-left: 3px solid var(--accent-teal);
        border-radius: 8px;
        padding: 16px 20px;
        margin: 16px 0;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .info-box-title {
        color: var(--accent-teal);
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tooltip */
    .tooltip-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: var(--bg-card);
        border: 1px solid var(--border-accent);
        color: var(--accent-teal);
        font-size: 0.75rem;
        cursor: help;
        margin-left: 6px;
        transition: all 0.3s ease;
    }

    .tooltip-icon:hover {
        background: var(--accent-teal);
        color: var(--bg-primary);
        transform: scale(1.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-teal), var(--accent-cyan));
        color: var(--bg-primary);
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(0, 255, 198, 0.3);
        text-transform: uppercase;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 255, 198, 0.5);
    }

    /* Status Indicator */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 12px currentColor;
    }

    .status-online { 
        background: var(--success);
        color: var(--success);
    }
    
    .status-warning { 
        background: var(--warning);
        color: var(--warning);
    }
    
    .status-error { 
        background: var(--danger);
        color: var(--danger);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(0.95); }
    }

    /* Sentiment Colors */
    .sentiment-positive { 
        color: var(--success); 
        font-weight: 600; 
    }
    
    .sentiment-negative { 
        color: var(--danger); 
        font-weight: 600; 
    }
    
    .sentiment-neutral { 
        color: var(--warning); 
        font-weight: 600; 
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { 
        background: var(--accent-teal); 
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: var(--accent-cyan); 
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-secondary);
        padding: 12px;
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 8px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-card);
        border-color: var(--border-subtle);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-teal), var(--accent-cyan));
        color: var(--bg-primary);
        border: none;
        box-shadow: 0 4px 16px rgba(0, 255, 198, 0.3);
    }

    /* Data Table Styling */
    .dataframe {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }

    .dataframe thead tr th {
        background: var(--bg-secondary) !important;
        color: var(--accent-teal) !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem !important;
        padding: 16px 12px !important;
        border-bottom: 2px solid var(--border-accent) !important;
    }

    .dataframe tbody tr {
        border-bottom: 1px solid var(--border-subtle) !important;
        transition: all 0.2s ease;
    }

    .dataframe tbody tr:hover {
        background: var(--bg-card-hover) !important;
    }

    .dataframe tbody tr td {
        color: var(--text-primary) !important;
        padding: 14px 12px !important;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 0.9rem !important;
    }

    /* Comparison Table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }

    .comparison-table th {
        background: var(--bg-secondary);
        color: var(--accent-teal);
        padding: 16px;
        text-align: left;
        font-weight: 700;
        border-bottom: 2px solid var(--border-accent);
    }

    .comparison-table td {
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 14px 16px;
        border-bottom: 1px solid var(--border-subtle);
        font-family: 'Roboto Mono', monospace;
    }

    .comparison-table tr:hover td {
        background: var(--bg-card-hover);
    }

    /* Glossary Styling */
    .glossary-term {
        background: var(--bg-card);
        border-left: 3px solid var(--accent-teal);
        border-radius: 8px;
        padding: 14px 18px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }

    .glossary-term:hover {
        background: var(--bg-card-hover);
        transform: translateX(4px);
    }

    .glossary-term strong {
        color: var(--accent-teal);
        font-size: 1.05rem;
        display: block;
        margin-bottom: 4px;
    }

    /* Learning Video Cards */
    .video-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }

    .video-card:hover {
        border-color: var(--border-accent);
        transform: translateY(-6px);
        box-shadow: 0 12px 32px rgba(0, 255, 198, 0.2);
    }

    .video-card h4 {
        color: var(--text-primary);
        margin-bottom: 12px;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .video-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .video-card button {
        background: linear-gradient(135deg, var(--accent-teal), var(--accent-cyan));
        color: var(--bg-primary);
        border: none;
        padding: 12px 28px;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }

    .video-card button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 255, 198, 0.4);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-subtitle { font-size: 1rem; }
        .section-header { font-size: 1.4rem; }
        .glass-card { padding: 16px; }
        .metric-card { padding: 16px; }
    }

    /* Fade-in Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }

    /* Loading Spinner */
    .loading-spinner {
        border: 3px solid var(--border-subtle);
        border-top: 3px solid var(--accent-teal);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Price Display */
    .price-display {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .price-display::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 255, 198, 0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    .price-display > * {
        position: relative;
        z-index: 1;
    }

    .company-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 20px;
    }

    .current-price {
        font-size: 3.5rem;
        font-weight: 900;
        font-family: 'Roboto Mono', monospace;
        margin-bottom: 12px;
    }

    .price-change {
        font-size: 1.5rem;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace;
    }

    /* AI Insight Card */
    .ai-insight {
        background: linear-gradient(135deg, rgba(0, 255, 198, 0.1), rgba(29, 233, 182, 0.05));
        border: 1px solid var(--border-accent);
        border-radius: 16px;
        padding: 28px;
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }

    .ai-insight::before {
        content: '◆';
        position: absolute;
        top: 20px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.1;
        color: var(--accent-teal);
    }

    .ai-insight-title {
        color: var(--accent-teal);
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .ai-insight-content {
        color: var(--text-secondary);
        font-size: 1.05rem;
        line-height: 1.8;
    }

    /* Score Gauge */
    .score-gauge {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
        background: conic-gradient(
            var(--accent-teal) 0deg,
            var(--accent-teal) calc(3.6deg * var(--score)),
            var(--bg-secondary) calc(3.6deg * var(--score)),
            var(--bg-secondary) 360deg
        );
    }

    .score-gauge::before {
        content: '';
        position: absolute;
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: var(--bg-card);
    }

    .score-value {
        position: relative;
        z-index: 1;
        font-size: 2rem;
        font-weight: 900;
        font-family: 'Roboto Mono', monospace;
    }

    /* Mini Chart Container */
    .mini-chart-container {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }

    .mini-chart-title {
        color: var(--accent-teal);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
"""

st.markdown(modern_dark_css, unsafe_allow_html=True)

# Sidebar with Glossary and Controls
with st.sidebar:
    st.markdown("""
    <div class="glass-card">
        <h2 style="color: var(--accent-teal); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
            <span>◈</span> Control Panel
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Compact Mode Toggle
    if st.checkbox("Compact Mode", value=st.session_state.compact_mode):
        st.session_state.compact_mode = True
    else:
        st.session_state.compact_mode = False
    
    st.markdown("---")
    
    # Quick Search
    st.markdown("### ◎ Quick Search")
    search_query = st.text_input("Search company...", placeholder="e.g., Apple, Tesla")
    
    st.markdown("---")
    
    # Quick Glossary
    with st.expander("◐ Quick Glossary", expanded=False):
        glossary_terms = {
            "Stock": "A share in the ownership of a company",
            "P/E Ratio": "Price-to-Earnings ratio - valuation metric",
            "RSI": "Relative Strength Index (0-100). >70 overbought, <30 oversold",
            "MACD": "Moving Average Convergence Divergence indicator",
            "Dividend": "Portion of profits distributed to shareholders",
            "Market Cap": "Total value of all outstanding shares",
            "Volume": "Number of shares traded in a period",
            "Bull Market": "Rising prices and investor optimism",
            "Bear Market": "Falling prices (20%+ decline) and pessimism",
            "Volatility": "Statistical measure of price fluctuation",
            "Bollinger Bands": "Volatility bands around moving average"
        }
        
        for term, definition in glossary_terms.items():
            st.markdown(f"""
            <div class="glossary-term">
                <strong>{term}</strong>
                <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">{definition}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top Movers Section
    with st.expander("◢ Market Movers", expanded=False):
        st.markdown("""
        <div class="info-box">
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                Live market data for top gainers and losers will appear here during market hours.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feedback Section
    with st.expander("◉ Feedback & Suggestions", expanded=False):
        feedback = st.text_area("Share your suggestions:", placeholder="How can we improve?")
        if st.button("Submit Feedback"):
            if feedback:
                st.success("✅ Thank you for your feedback!")
            else:
                st.warning("⚠️ Please enter your feedback")

# Hero Section
st.markdown("""
<div class="hero-section fade-in">
    <div class="hero-content">
        <h1 class="hero-title">
            STOCK<span class="accent">SENTINEL</span>
        </h1>
        <p class="hero-subtitle">
            <strong style="color: var(--accent-teal);">Learning & Trading Intelligence</strong><br>
            Real-time market analytics platform with AI-powered insights, comprehensive analysis tools,
            and educational resources to empower your investment journey.
        </p>
        <div class="hero-cta">
            Explore Platform <span style="font-size: 1.3rem;">→</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Market Status & System Info Widget
current_time = datetime.now()
ist = pytz.timezone('Asia/Kolkata')
current_time_ist = datetime.now(ist)
market_open = current_time_ist.replace(hour=9, minute=15, second=0, microsecond=0)
market_close = current_time_ist.replace(hour=15, minute=30, second=0, microsecond=0)

if market_open <= current_time_ist <= market_close:
    market_status = "OPEN"
    status_class = "status-online"
elif current_time_ist < market_open:
    market_status = "PRE-MARKET"
    status_class = "status-warning"
else:
    market_status = "CLOSED"
    status_class = "status-error"

system_col1, system_col2, system_col3, system_col4 = st.columns(4)

with system_col1:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="status-indicator {status_class}"></div>
        <div class="metric-label">Indian Market</div>
        <div style="font-size: 1.2rem; color: var(--text-primary); font-weight: 700; margin-top: 8px;">{market_status}</div>
    </div>
    """, unsafe_allow_html=True)

with system_col2:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Current Time (IST)</div>
        <div style="font-size: 1.2rem; color: var(--accent-teal); font-weight: 700; margin-top: 8px; font-family: 'Roboto Mono', monospace;">{current_time_ist.strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

with system_col3:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Trading Hours</div>
        <div style="font-size: 1rem; color: var(--text-secondary); margin-top: 8px;">9:15 AM - 3:30 PM</div>
    </div>
    """, unsafe_allow_html=True)

with system_col4:
    st.markdown(f"""
    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
        <div class="metric-label">Session Refreshes</div>
        <div style="font-size: 1.2rem; color: var(--text-primary); font-weight: 700; margin-top: 8px;">{st.session_state.refresh_counter}</div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Functions
@st.cache_data(ttl=300, show_spinner=False)
def get_latest_stock_data(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        periods_to_try = [period, "3mo", "6mo", "1y"]
        hist = pd.DataFrame()
        
        for p in periods_to_try:
            try:
                hist = stock.history(period=p, timeout=15)
                if not hist.empty:
                    break
            except:
                continue
        
        if hist.empty:
            return pd.DataFrame(), None, {}
        
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        except:
            info = {}
            current_price = hist['Close'].iloc[-1] if not hist.empty else None
        
        return hist, current_price, info
    except Exception as e:
        return pd.DataFrame(), None, {}

API_KEY = "35be8e6d38f940aea0927849daec8cbb"
analyzer = SentimentIntensityAnalyzer()

@st.cache_data(ttl=900, show_spinner=False)
def fetch_simple_news(query, limit=4):
    url = f"https://newsapi.org/v2/everything?q={query}&language=en&sortBy=publishedAt&pageSize={limit}&apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = []
            if data.get("status") == "ok" and data.get("articles"):
                for article in data["articles"]:
                    title = article.get("title")
                    description = article.get("description", "")
                    source = article.get("source", {}).get("name", "Unknown")
                    published_at = article.get("publishedAt", "")
                    url = article.get("url", "#")
                    if title and title != "[Removed]" and len(title.strip()) > 10:
                        score = analyzer.polarity_scores(f"{title} {description}")["compound"]
                        sentiment = "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"
                        try:
                            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                            relative_time = "Today" if pub_date.date() == datetime.now().date() else f"{(datetime.now().date() - pub_date.date()).days} days ago"
                        except:
                            relative_time = "Recently"
                        articles.append({"Title": title, "Description": description or "Click to read more...", "Sentiment": sentiment, "Source": source, "Time": relative_time, "Url": url, "Score": score})
            return articles
        return []
    except:
        return []

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def calculate_enhanced_analyst_score(info, stock_data, all_news):
    score = 0
    score_breakdown = {}
    
    # Momentum Score (25 points)
    momentum_score = 0
    if not stock_data.empty and len(stock_data) > 20:  # Reduced from 50
        try:
            short_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-5]) / stock_data['Close'].iloc[-5]
            if short_change > 0.05: momentum_score += 10
            elif short_change > 0.02: momentum_score += 7
            elif short_change > 0: momentum_score += 4
            
            if len(stock_data) > 10:
                med_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-10]) / stock_data['Close'].iloc[-10]
                if med_change > 0.15: momentum_score += 10
                elif med_change > 0.10: momentum_score += 7
                elif med_change > 0.05: momentum_score += 4
                elif med_change > 0: momentum_score += 2
            
            if len(stock_data) > 20:
                long_change = (stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-20]) / stock_data['Close'].iloc[-20]
                if long_change > 0.20: momentum_score += 5
                elif long_change > 0.10: momentum_score += 3
                elif long_change > 0: momentum_score += 1
        except:
            pass
    score_breakdown['Momentum'] = momentum_score
    score += momentum_score

    # Valuation Score (25 points)
    valuation_score = 0
    try:
        pe_ratio = info.get('trailingPE')
        pb_ratio = info.get('priceToBook')
        debt_equity = info.get('debtToEquity', 0)
        
        if pe_ratio and 0 < pe_ratio <= 15: valuation_score += 15
        elif pe_ratio and 15 < pe_ratio <= 25: valuation_score += 10
        elif pe_ratio and 25 < pe_ratio <= 35: valuation_score += 5
        
        if pb_ratio and 0.5 <= pb_ratio <= 3: valuation_score += 5
        elif pb_ratio and 3 < pb_ratio <= 5: valuation_score += 3
        
        if debt_equity < 0.3: valuation_score += 5
        elif debt_equity < 0.6: valuation_score += 3
        elif debt_equity < 1.0: valuation_score += 1
    except:
        pass
    score_breakdown['Valuation'] = valuation_score
    score += valuation_score
    
    # News Sentiment Score (25 points)
    sentiment_score = 0
    if all_news:
        positive = sum(1 for news in all_news if "Positive" in news["Sentiment"])
        sentiment_score = int((positive / len(all_news)) * 25)
    score_breakdown['News Sentiment'] = sentiment_score
    score += sentiment_score
    
    # Volume Analysis (15 points)
    volume_score = 0
    if not stock_data.empty and 'Volume' in stock_data.columns:
        try:
            current_volume = stock_data['Volume'].iloc[-1]
            avg_volume_20 = stock_data['Volume'].tail(min(20, len(stock_data))).mean()
            volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
            
            if volume_ratio > 2.0: volume_score += 15
            elif volume_ratio > 1.5: volume_score += 12
            elif volume_ratio > 1.2: volume_score += 8
            elif volume_ratio > 0.8: volume_score += 5
        except:
            pass
    score_breakdown['Volume Interest'] = volume_score
    score += volume_score
    
    # Market Cap Score (10 points)
    market_cap_score = 0
    try:
        market_cap = info.get('marketCap', 0)
        if market_cap > 1000000000000: market_cap_score += 10
        elif market_cap > 100000000000: market_cap_score += 8
        elif market_cap > 10000000000: market_cap_score += 6
        elif market_cap > 1000000000: market_cap_score += 4
        else: market_cap_score += 2
    except:
        pass
    score_breakdown['Market Cap'] = market_cap_score
    score += market_cap_score
    
    return min(score, 100), score_breakdown

def create_glowing_line_chart(stock_data, price_column, title):
    """Create a glowing line chart with green for up and red for down"""
    if stock_data.empty or len(stock_data) < 2:
        return None
    
    # Determine if overall trend is up or down
    first_price = stock_data[price_column].iloc[0]
    last_price = stock_data[price_column].iloc[-1]
    is_upward = last_price >= first_price
    
    # Set colors based on trend
    line_color = '#00ff88' if is_upward else '#ff4757'
    fill_color = 'rgba(0, 255, 136, 0.2)' if is_upward else 'rgba(255, 71, 87, 0.2)'
    
    fig = go.Figure()
    
    # Add glowing line
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data[price_column],
        mode='lines',
        name='Price',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={'text': title, 'font': {'size': 16, 'color': 'white'}, 'x': 0.5},
        font=dict(color='white'),
        plot_bgcolor='#0a0e27',
        paper_bgcolor='#0a0e27',
        height=300,
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

# Stock Selection
stock_options = {
    "Apple Inc.": "AAPL", "Microsoft Corp.": "MSFT", "Amazon.com Inc.": "AMZN",
    "Alphabet Inc.": "GOOGL", "Tesla Inc.": "TSLA", "Meta Platforms": "META",
    "Netflix Inc.": "NFLX", "NVIDIA Corp.": "NVDA", "Infosys Ltd.": "INFY",
    "Tata Consultancy Services": "TCS.NS", "Reliance Industries": "RELIANCE.NS",
    "HDFC Bank Ltd.": "HDFCBANK.NS", "Adani Enterprises": "ADANIENT.NS",
    "ICICI Bank Ltd.": "ICICIBANK.NS", "Wipro Ltd.": "WIPRO.NS",
    "ITC Ltd.": "ITC.NS", "State Bank of India": "SBIN.NS"
}

selected_name = st.selectbox("◎ Choose Company for Analysis:", list(stock_options.keys()), key="main_selector")
stock_ticker = stock_options[selected_name]

# Refresh Button
col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 4])
with col_refresh1:
    if st.button("↻ Refresh Data", use_container_width=True):
        st.session_state.refresh_counter += 1
        st.session_state.last_refresh = datetime.now()
        st.cache_data.clear()
        st.rerun()

# Fetch data
with st.spinner(f"Fetching data for {selected_name}..."):
    stock_data, current_price, stock_info = get_latest_stock_data(stock_ticker)
    company_news = fetch_simple_news(selected_name, 3)
    market_news = fetch_simple_news("stock market investment", 3)
    all_news = company_news + market_news

# Currency conversion
if not stock_ticker.endswith(".NS"):
    usd_to_inr = 83.2
    if not stock_data.empty:
        stock_data["Close_INR"] = stock_data["Close"] * usd_to_inr
        stock_data["Open_INR"] = stock_data["Open"] * usd_to_inr
        stock_data["High_INR"] = stock_data["High"] * usd_to_inr
        stock_data["Low_INR"] = stock_data["Low"] * usd_to_inr
    price_column = "Close_INR"
    currency_symbol = "₹"
    current_price_inr = current_price * usd_to_inr if current_price else None
else:
    price_column = "Close"
    currency_symbol = "₹"
    current_price_inr = current_price

# Live Market Ticker Section
st.markdown('<div class="section-header"><span class="icon">◢</span> Top Stocks in the Market</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <div class="info-box-title">
        ◆ What You'll See Here
    </div>
    <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
        • Real-time price updates for major market indices<br>
        • Daily percentage changes with visual indicators<br>
        • Quick comparison across global markets
    </div>
</div>
""", unsafe_allow_html=True)

major_indices = {
    "NIFTY 50": "^NSEI", 
    "SENSEX": "^BSESN", 
    "NASDAQ": "^IXIC", 
    "S&P 500": "^GSPC",
    "DOW JONES": "^DJI"
}

ticker_cols = st.columns(5)

for i, (name, symbol) in enumerate(major_indices.items()):
    with ticker_cols[i]:
        try:
            index_data, index_price, _ = get_latest_stock_data(symbol, "5d")
            if index_price and not index_data.empty and len(index_data) > 1:
                last_close = index_data["Close"].iloc[-2]
                change = index_price - last_close
                change_percent = (change / last_close) * 100 if last_close != 0 else 0
                
                change_color = "var(--success)" if change >= 0 else "var(--danger)"
                arrow = "▲" if change >= 0 else "▼"
                
                st.markdown(f"""
                <div class="ticker-card">
                    <div class="ticker-name">{name}</div>
                    <div class="ticker-price">{index_price:,.0f}</div>
                    <div class="ticker-change" style="color: {change_color};">
                        {arrow} {abs(change_percent):.2f}%
                    </div>
                    <div style="margin-top: 12px; height: 40px; background: var(--bg-secondary); border-radius: 6px;"></div>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown(f"""
            <div class="ticker-card">
                <div class="ticker-name">{name}</div>
                <div style="color: var(--text-muted); font-size: 0.9rem; margin-top: 12px;">Loading...</div>
            </div>
            """, unsafe_allow_html=True)

# Main Tabs
tabs = st.tabs([
    "◆ Dashboard & Market Overview",
    "◈ Company Insights",
    "◭ Trading & Technical Analysis",
    "◉ News & Sentiment Analysis",
    "◐ Learning Center",
    "◇ Stock Comparison Tool"
])

# TAB 1: Dashboard & Market Overview
with tabs[0]:
    st.markdown('<div class="section-header"><span class="icon">◆</span> Dashboard & Market Overview</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">
            ◆ What You'll Learn Here
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            • Overall market performance across major indices<br>
            • Real-time system status and data freshness<br>
            • Your watchlist management and tracking
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Global Market Summary
    st.markdown("### ◉ Global Market Summary")
    
    market_cols = st.columns(4)
    
    for i, (name, symbol) in enumerate(list(major_indices.items())[:4]):
        with market_cols[i]:
            try:
                index_data, index_price, _ = get_latest_stock_data(symbol, "5d")
                if index_price and not index_data.empty and len(index_data) > 1:
                    last_close = index_data["Close"].iloc[-2]
                    change = index_price - last_close
                    change_percent = (change / last_close) * 100 if last_close != 0 else 0
                    
                    change_color = "var(--success)" if change >= 0 else "var(--danger)"
                    arrow = "▲" if change >= 0 else "▼"
                    
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div style="font-size: 0.9rem; font-weight: 700; color: var(--accent-teal); margin-bottom: 12px;">{name}</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{index_price:,.0f}</div>
                        <div style="color: {change_color}; font-size: 1rem; margin-top: 8px; font-weight: 700;">
                            {arrow} {change_percent:+.2f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except:
                st.markdown(f"""
                <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                    <div style="font-size: 0.9rem; font-weight: 700; color: var(--accent-teal);">{name}</div>
                    <div style="color: var(--text-muted); font-size: 1rem;">Loading...</div>
                </div>
                """, unsafe_allow_html=True)
    
    # System Information
    st.markdown("### ◈ System Information")
    
    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    
    with info_col1:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Last Update</div>
            <div style="font-size: 1.1rem; color: var(--accent-teal); margin-top: 8px; font-family: 'Roboto Mono', monospace;">{st.session_state.last_refresh.strftime('%H:%M:%S')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Watchlist Items</div>
            <div style="font-size: 1.1rem; color: var(--text-primary); margin-top: 8px;">{len(st.session_state.watchlist)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col3:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Data Source</div>
            <div style="font-size: 1.1rem; color: var(--text-primary); margin-top: 8px;">Yahoo Finance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col4:
        st.markdown(f"""
        <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
            <div class="metric-label">Market Status</div>
            <div style="font-size: 1.1rem; color: var(--text-primary); margin-top: 8px;">{market_status}</div>
        </div>
        """, unsafe_allow_html=True)

# TAB 2: Company Insights
with tabs[1]:
    st.markdown('<div class="section-header"><span class="icon">◈</span> Company Insights</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">
            ◆ What You'll Learn Here
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            • Current stock price with real-time updates<br>
            • Company fundamentals and key financial metrics<br>
            • AI-powered analyst score and recommendations<br>
            • Add stocks to your personal watchlist
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Price Display
        if current_price and not stock_data.empty and len(stock_data) > 1:
            try:
                last_close = stock_data[price_column].iloc[-2]
                price_change = current_price_inr - last_close
                change_percent = (price_change / last_close) * 100
                
                arrow = "▲" if price_change >= 0 else "▼"
                price_color = "var(--success)" if price_change >= 0 else "var(--danger)"
                
                st.markdown(f"""
                <div class="price-display">
                    <h2 class="company-name">{selected_name}</h2>
                    <div class="current-price" style="color: {price_color};">
                        {currency_symbol}{current_price_inr:.2f}
                    </div>
                    <div class="price-change" style="color: {price_color};">
                        {arrow} {currency_symbol}{abs(price_change):.2f} ({change_percent:+.2f}%)
                    </div>
                    <p style="color: var(--text-muted); margin-top: 20px; font-size: 0.9rem;">
                        Last Updated: {stock_data.index[-1].strftime('%Y-%m-%d %H:%M')} IST
                    </p>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
        
        # Mini Price Chart with Glow
        if not stock_data.empty:
            st.markdown('<div class="mini-chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="mini-chart-title">◭ Recent Price Movement</div>', unsafe_allow_html=True)
            
            recent_data = stock_data.tail(30)  # Last 30 days
            fig_mini = create_glowing_line_chart(recent_data, price_column, "")
            if fig_mini:
                st.plotly_chart(fig_mini, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Company Information
        if stock_info:
            st.markdown("### ◐ Company Profile")
            
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-teal); margin-bottom: 12px;">Business Info</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">Sector:</strong> {stock_info.get("sector", "N/A")}<br>
                        <strong style="color: var(--text-primary);">Industry:</strong> {stock_info.get("industry", "N/A")}<br>
                        <strong style="color: var(--text-primary);">Employees:</strong> {stock_info.get("fullTimeEmployees", "N/A"):,}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col2:
                pe_ratio = stock_info.get("trailingPE", "N/A")
                pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio
                pb_ratio = stock_info.get("priceToBook", "N/A")
                pb_display = f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else pb_ratio
                roe = stock_info.get("returnOnEquity", "N/A")
                roe_display = f"{roe:.2%}" if isinstance(roe, (int, float)) else roe
                
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-teal); margin-bottom: 12px;">Valuation Metrics</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">P/E Ratio</strong> 
                        <span class="tooltip-icon">i</span>: {pe_display}<br>
                        <strong style="color: var(--text-primary);">P/B Ratio</strong> 
                        <span class="tooltip-icon">i</span>: {pb_display}<br>
                        <strong style="color: var(--text-primary);">ROE</strong> 
                        <span class="tooltip-icon">i</span>: {roe_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col3:
                market_cap = stock_info.get("marketCap", 0) / 10000000
                high_52 = stock_info.get("fiftyTwoWeekHigh", "N/A")
                high_display = f"₹{high_52:.2f}" if isinstance(high_52, (int, float)) else high_52
                low_52 = stock_info.get("fiftyTwoWeekLow", "N/A")
                low_display = f"₹{low_52:.2f}" if isinstance(low_52, (int, float)) else low_52
                
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-teal); margin-bottom: 12px;">Market Data</h5>
                    <div style="color: var(--text-secondary); line-height: 1.8;">
                        <strong style="color: var(--text-primary);">Market Cap:</strong> ₹{market_cap:.1f} Cr<br>
                        <strong style="color: var(--text-primary);">52W High:</strong> {high_display}<br>
                        <strong style="color: var(--text-primary);">52W Low:</strong> {low_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Watchlist Section
        st.markdown("### ◎ My Watchlist")
        
        if st.button(f"+ Add {selected_name}", use_container_width=True):
            if stock_ticker not in [item['symbol'] for item in st.session_state.watchlist]:
                st.session_state.watchlist.append({
                    'symbol': stock_ticker,
                    'name': selected_name,
                    'added_date': datetime.now().strftime('%Y-%m-%d %H:%M')
                })
                st.success("✅ Added to watchlist!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.info("ℹ️ Already in watchlist!")
        
        if st.session_state.watchlist:
            for item in st.session_state.watchlist:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"""
                    <div class="glass-card {'compact' if st.session_state.compact_mode else ''}" style="padding: 12px; margin: 8px 0;">
                        <strong style="color: var(--accent-teal);">{item['name']}</strong><br>
                        <small style="color: var(--text-muted);">{item['added_date']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    if st.button("×", key=f"del_{item['symbol']}", help="Remove"):
                        st.session_state.watchlist = [i for i in st.session_state.watchlist if i['symbol'] != item['symbol']]
                        st.rerun()
        else:
            st.info("◎ No stocks in watchlist")
        
        # Analyst Score
        st.markdown("### ◆ AI Analyst Score")
        score, breakdown = calculate_enhanced_analyst_score(stock_info, stock_data, all_news)
        
        # Score interpretation
        if score >= 70:
            score_color = "var(--success)"
            score_text = "Strong Buy"
            score_desc = "Highly favorable outlook"
        elif score >= 50:
            score_color = "var(--warning)"
            score_text = "Hold"
            score_desc = "Balanced risk-reward"
        else:
            score_color = "var(--danger)"
            score_text = "Caution"
            score_desc = "Exercise caution"
        
        st.markdown(f"""
        <div class="ai-insight">
            <div class="ai-insight-title">
                <span>◭</span> Overall Investment Score
            </div>
            <div style="text-align: center; margin: 24px 0;">
                <div class="score-gauge" style="--score: {score};">
                    <span class="score-value" style="color: {score_color};">{score}</span>
                </div>
                <div style="margin-top: 16px;">
                    <div style="font-size: 1.3rem; font-weight: 700; color: {score_color};">{score_text}</div>
                    <div style="color: var(--text-secondary); margin-top: 4px;">{score_desc}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Score Breakdown
        st.markdown("#### ◢ Score Breakdown")
        for category, value in breakdown.items():
            max_value = 25 if category in ['Momentum', 'Valuation', 'News Sentiment'] else (15 if category == 'Volume Interest' else 10)
            percentage = (value / max_value) * 100
            bar_color = "var(--success)" if percentage > 70 else ("var(--warning)" if percentage > 40 else "var(--danger)")
            
            st.markdown(f"""
            <div class="glass-card compact">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: var(--text-primary);">{category}</strong>
                    <span style="color: {bar_color}; font-weight: 700; font-family: 'Roboto Mono', monospace;">{value}/{max_value}</span>
                </div>
                <div style="background: var(--bg-secondary); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background: {bar_color}; width: {percentage}%; height: 100%; transition: width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Stats Panel
        st.markdown("### ◉ Quick Stats")
        if not stock_data.empty and len(stock_data) >= 5:
            try:
                today_high = stock_data[price_column].tail(1).iloc[0]
                today_low = stock_data[price_column].tail(1).iloc[0]
                avg_volume = stock_data['Volume'].tail(20).mean()
                
                st.markdown(f"""
                <div class="glass-card compact">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: var(--text-secondary);">Today's High:</span>
                        <span style="color: var(--success); font-weight: 700;">₹{today_high:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: var(--text-secondary);">Today's Low:</span>
                        <span style="color: var(--danger); font-weight: 700;">₹{today_low:.2f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Avg Volume (20D):</span>
                        <span style="color: var(--text-primary); font-weight: 700;">{int(avg_volume):,}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass

# TAB 3: Trading & Technical Analysis
with tabs[2]:
    st.markdown('<div class="section-header"><span class="icon">◭</span> Trading & Technical Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">
            ◆ What You'll Learn Here
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            • Advanced technical indicators (RSI, MACD, Bollinger Bands)<br>
            • Colorful candlestick charts with volume analysis<br>
            • Recent trading performance with detailed metrics<br>
            • Buy/Sell signals based on technical patterns
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not stock_data.empty and len(stock_data) > 10:  # Reduced from 50 to 10
        try:
            close_prices = stock_data[price_column]
            
            # Calculate indicators
            rsi = calculate_rsi(close_prices)
            macd_line, signal_line, histogram = calculate_macd(close_prices)
            upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(close_prices)
            
            # Create comprehensive chart with COLORFUL CANDLESTICKS
            fig = make_subplots(
                rows=4, cols=1,
                subplot_titles=('Colorful Candlestick Chart with Bollinger Bands', 'Volume', 'RSI', 'MACD'),
                vertical_spacing=0.08,
                row_heights=[0.4, 0.2, 0.2, 0.2]
            )
            
            # Colorful Candlestick Chart
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'] if 'Open' in stock_data.columns else stock_data[price_column],
                high=stock_data['High'] if 'High' in stock_data.columns else stock_data[price_column],
                low=stock_data['Low'] if 'Low' in stock_data.columns else stock_data[price_column],
                close=stock_data[price_column],
                name='Price',
                increasing_line_color='#00ff88',  # Bright green
                increasing_fillcolor='#00ff88',
                decreasing_line_color='#ff4757',  # Bright red
                decreasing_fillcolor='#ff4757',
                increasing_line_width=2,
                decreasing_line_width=2
            ), row=1, col=1)
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=stock_data.index, y=upper_bb, name='Upper BB', 
                                    line=dict(color='rgba(255,255,255,0.3)', dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=lower_bb, fill='tonexty', name='Lower BB',
                                    line=dict(color='rgba(255,255,255,0.3)', dash='dash'),
                                    fillcolor='rgba(0, 255, 198, 0.1)'), row=1, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=middle_bb, name='SMA 20',
                                    line=dict(color='#FFFFFF', width=2)), row=1, col=1)
            
            # Volume
            colors = ['#00ff88' if stock_data[price_column].iloc[i] >= stock_data[price_column].iloc[i-1] 
                     else '#ff4757' for i in range(1, len(stock_data))]
            colors.insert(0, '#ff4757')
            fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], name='Volume',
                                marker_color=colors, opacity=0.7), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=stock_data.index, y=rsi, name='RSI',
                                    line=dict(color='#00FFC6', width=3)), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ff4757", line_width=2, row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", line_width=2, row=3, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=stock_data.index, y=macd_line, name='MACD',
                                    line=dict(color='#00FFC6', width=3)), row=4, col=1)
            fig.add_trace(go.Scatter(x=stock_data.index, y=signal_line, name='Signal',
                                    line=dict(color='#ffa502', width=2)), row=4, col=1)
            colors_hist = ['#00ff88' if h >= 0 else '#ff4757' for h in histogram]
            fig.add_trace(go.Bar(x=stock_data.index, y=histogram, name='Histogram',
                                marker_color=colors_hist, opacity=0.6), row=4, col=1)
            
            fig.update_layout(
                title={'text': f'{selected_name} - Technical Analysis Dashboard', 
                      'font': {'size': 20, 'color': 'white'}, 'x': 0.5},
                font=dict(color='white'),
                plot_bgcolor='#0a0e27',
                paper_bgcolor='#0a0e27',
                height=1000,
                showlegend=True,
                hovermode='x unified',
                xaxis_rangeslider_visible=False
            )
            
            fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', showgrid=True)
            fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', showgrid=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical Indicators Summary
            st.markdown("### ◎ Technical Indicators Summary")
            ind_col1, ind_col2, ind_col3, ind_col4 = st.columns(4)
            
            with ind_col1:
                current_rsi = rsi.iloc[-1] if not rsi.empty and pd.notna(rsi.iloc[-1]) else None
                if current_rsi:
                    rsi_signal = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
                    rsi_color = "var(--danger)" if current_rsi > 70 else "var(--success)" if current_rsi < 30 else "var(--warning)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {rsi_color};">{current_rsi:.1f}</div>
                        <div class="metric-label">RSI <span class="tooltip-icon">i</span></div>
                        <div style="color: {rsi_color}; font-size: 0.85rem; margin-top: 8px; font-weight: 600;">{rsi_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col2:
                current_macd = macd_line.iloc[-1] if not macd_line.empty and pd.notna(macd_line.iloc[-1]) else None
                current_signal = signal_line.iloc[-1] if not signal_line.empty and pd.notna(signal_line.iloc[-1]) else None
                if current_macd and current_signal:
                    macd_signal = "Bullish" if current_macd > current_signal else "Bearish"
                    macd_color = "var(--success)" if current_macd > current_signal else "var(--danger)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {macd_color};">{current_macd:.2f}</div>
                        <div class="metric-label">MACD <span class="tooltip-icon">i</span></div>
                        <div style="color: {macd_color}; font-size: 0.85rem; margin-top: 8px; font-weight: 600;">{macd_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col3:
                current_price_val = close_prices.iloc[-1]
                current_bb_upper = upper_bb.iloc[-1] if not upper_bb.empty else None
                current_bb_lower = lower_bb.iloc[-1] if not lower_bb.empty else None
                if current_bb_upper and current_bb_lower:
                    bb_position = ((current_price_val - current_bb_lower) / (current_bb_upper - current_bb_lower)) * 100
                    if current_price_val > current_bb_upper:
                        bb_signal = "Above Upper"
                        bb_color = "var(--danger)"
                    elif current_price_val < current_bb_lower:
                        bb_signal = "Below Lower"
                        bb_color = "var(--success)"
                    else:
                        bb_signal = "Within Bands"
                        bb_color = "var(--warning)"
                    
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {bb_color};">{bb_position:.1f}%</div>
                        <div class="metric-label">BB Position <span class="tooltip-icon">i</span></div>
                        <div style="color: {bb_color}; font-size: 0.85rem; margin-top: 8px; font-weight: 600;">{bb_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with ind_col4:
                if 'Volume' in stock_data.columns:
                    current_volume = stock_data['Volume'].iloc[-1]
                    avg_volume_20 = stock_data['Volume'].tail(min(20, len(stock_data))).mean()
                    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
                    volume_signal = "High" if volume_ratio > 1.5 else "Low" if volume_ratio < 0.7 else "Normal"
                    volume_color = "var(--success)" if volume_ratio > 1.5 else "var(--danger)" if volume_ratio < 0.7 else "var(--warning)"
                    st.markdown(f"""
                    <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                        <div class="metric-value" style="color: {volume_color};">{volume_ratio:.1f}x</div>
                        <div class="metric-label">Volume Ratio <span class="tooltip-icon">i</span></div>
                        <div style="color: {volume_color}; font-size: 0.85rem; margin-top: 8px; font-weight: 600;">{volume_signal}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Recent Trading Performance Table
            st.markdown("### ◢ Recent Trading Performance")
            
            if not stock_data.empty:
                try:
                    last_10 = stock_data.tail(10).copy()
                    display_data = []
                    
                    for idx in last_10.index:
                        row_data = last_10.loc[idx]
                        
                        if price_column == "Close_INR":
                            open_price = row_data.get("Open_INR", row_data.get("Open", 0) * 83.2)
                            high_price = row_data.get("High_INR", row_data.get("High", 0) * 83.2)
                            low_price = row_data.get("Low_INR", row_data.get("Low", 0) * 83.2)
                            close_price = row_data.get("Close_INR", row_data.get("Close", 0) * 83.2)
                        else:
                            open_price = row_data.get("Open", 0)
                            high_price = row_data.get("High", 0)
                            low_price = row_data.get("Low", 0)
                            close_price = row_data.get("Close", 0)
                        
                        volume = row_data.get("Volume", 0)
                        
                        display_data.append({
                            "Date": idx.strftime('%Y-%m-%d'),
                            "Open (₹)": f"₹{open_price:.2f}",
                            "High (₹)": f"₹{high_price:.2f}",
                            "Low (₹)": f"₹{low_price:.2f}",
                            "Close (₹)": f"₹{close_price:.2f}",
                            "Volume": f"{int(volume):,}",
                        })
                    
                    for i in range(1, len(display_data)):
                        prev_close = float(display_data[i-1]["Close (₹)"].replace("₹", "").replace(",", ""))
                        curr_close = float(display_data[i]["Close (₹)"].replace("₹", "").replace(",", ""))
                        
                        daily_change = curr_close - prev_close
                        change_percent = (daily_change / prev_close * 100) if prev_close != 0 else 0
                        
                        display_data[i]["Daily Change"] = f"₹{daily_change:+.2f}"
                        display_data[i]["Change %"] = f"{change_percent:+.2f}%"
                    
                    display_data[0]["Daily Change"] = "N/A"
                    display_data[0]["Change %"] = "N/A"
                    
                    display_df = pd.DataFrame(display_data)
                    display_df = display_df.set_index("Date")
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=450
                    )
                    
                except Exception as e:
                    st.error(f"⚠️ Error displaying trading data: {str(e)}")
                    
        except Exception as e:
            st.error(f"⚠️ Error creating technical analysis: {e}")
    else:
        st.markdown("""
        <div class="info-box">
            <div class="info-box-title">ℹ️ Limited Data Available</div>
            <div style="color: var(--text-secondary);">
                Displaying available data with reduced timeframe. Some technical indicators may have limited accuracy with fewer data points.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show whatever data is available
        if not stock_data.empty:
            fig_simple = create_glowing_line_chart(stock_data, price_column, f"{selected_name} - Price Movement")
            if fig_simple:
                st.plotly_chart(fig_simple, use_container_width=True)

# TAB 4: News & Sentiment Analysis
with tabs[3]:
    st.markdown('<div class="section-header"><span class="icon">◉</span> News & Sentiment Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">
            ◆ What You'll Learn Here
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            • Latest news articles related to the selected company<br>
            • AI-powered sentiment analysis of news content<br>
            • Overall market sentiment indicators<br>
            • Direct links to full articles for detailed reading
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sentiment Analysis Overview
    st.markdown("### ◭ Sentiment Summary")
    
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: var(--accent-teal); margin-bottom: 16px;">What is Sentiment Analysis?</h4>
        <p style="color: var(--text-secondary); line-height: 1.8;">
            Sentiment analysis uses natural language processing to determine the emotional tone of news articles. 
            Positive sentiment indicates optimistic market outlook, while negative sentiment suggests concerns. 
            This helps investors gauge market psychology and potential price movements.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if all_news:
        positive_count = sum(1 for news in all_news if "Positive" in news["Sentiment"])
        negative_count = sum(1 for news in all_news if "Negative" in news["Sentiment"])
        neutral_count = len(all_news) - positive_count - negative_count
        
        sent_col1, sent_col2, sent_col3, sent_col4 = st.columns(4)
        
        with sent_col1:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--success);">{positive_count}</div>
                <div class="metric-label">Positive News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col2:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--warning);">{neutral_count}</div>
                <div class="metric-label">Neutral News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col3:
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: var(--danger);">{negative_count}</div>
                <div class="metric-label">Negative News</div>
            </div>
            """, unsafe_allow_html=True)
        
        with sent_col4:
            overall = "Positive" if positive_count > negative_count else "Negative" if negative_count > positive_count else "Neutral"
            color = "var(--success)" if overall == "Positive" else "var(--danger)" if overall == "Negative" else "var(--warning)"
            
            st.markdown(f"""
            <div class="metric-card {'compact' if st.session_state.compact_mode else ''}">
                <div class="metric-value" style="color: {color}; font-size: 1.5rem;">{overall}</div>
                <div class="metric-label">Overall Sentiment</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sentiment Chart
        fig_sentiment = go.Figure(data=[go.Pie(
            labels=['Positive', 'Neutral', 'Negative'],
            values=[positive_count, neutral_count, negative_count],
            marker_colors=['#00ff88', '#ffa502', '#ff4757'],
            hole=.4,
            textfont_size=14,
            textfont_color='white'
        )])
        
        fig_sentiment.update_layout(
            title="Sentiment Distribution",
            font=dict(color='white'),
            paper_bgcolor='#0a0e27',
            plot_bgcolor='#0a0e27',
            height=400
        )
        
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # News Articles
        st.markdown("### ◎ Latest News Articles")
        
        for news in all_news:
            sentiment_class = "sentiment-neutral"
            if "Positive" in news["Sentiment"]:
                sentiment_class = "sentiment-positive"
            elif "Negative" in news["Sentiment"]:
                sentiment_class = "sentiment-negative"
            
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{news['Title']}</div>
                <div class="news-description">{news['Description'][:200]}... 
                    <a href="{news['Url']}" target="_blank" style="color: var(--accent-teal); font-weight: 600; text-decoration: none;">
                        Read Full Article →
                    </a>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border-subtle);">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <span class="{sentiment_class}" style="padding: 6px 16px; background: rgba(0, 255, 198, 0.1); border: 1px solid var(--border-accent); border-radius: 6px;">
                            {news['Sentiment']}
                        </span>
                        <span style="color: var(--accent-teal); font-weight: 600;">◉ {news['Source']}</span>
                    </div>
                    <div style="color: var(--text-muted); font-size: 0.85rem;">◐ {news['Time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Unable to fetch news at the moment. Please refresh the page.")

# TAB 5: Learning Center
with tabs[4]:
    st.markdown('<div class="section-header"><span class="icon">◐</span> Learning Center</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: var(--accent-teal); margin-bottom: 20px;">◭ Master the Stock Market</h3>
        <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.8;">
            Welcome to your comprehensive guide to stock market investing. Whether you're a complete beginner 
            or looking to enhance your knowledge, we've got you covered with curated video tutorials and 
            expert insights in multiple languages!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Video Tutorials Section
    st.markdown("### ◎ Video Tutorials")
    
    # Language tabs
    lang_tabs = st.tabs(["◆ English", "◆ Tamil", "◆ Hindi"])
    
    # English Videos
    with lang_tabs[0]:
        st.markdown("#### English Tutorials")
        
        eng_col1, eng_col2, eng_col3 = st.columns(3)
        
        with eng_col1:
            st.markdown("""
            <div class="video-card">
                <h4>Stock Market for Beginners</h4>
                <p>Complete guide to understanding stock market basics and building wealth.</p>
                <a href="https://youtu.be/p7HKvqRI_Bo" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with eng_col2:
            st.markdown("""
            <div class="video-card">
                <h4>How to Invest in Stocks</h4>
                <p>Step-by-step guide on choosing stocks and making your first investment.</p>
                <a href="https://youtu.be/8Ij7A1VCB7I" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with eng_col3:
            st.markdown("""
            <div class="video-card">
                <h4>Candlestick Patterns</h4>
                <p>Master candlestick chart reading and make informed trading decisions.</p>
                <a href="https://youtu.be/tW13N4Hll88" target="_blank" style="text-decoration: none;">
                    <button>▶ Watch Tutorial</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        # Key Learnings
        st.markdown("#### ◆ Key Learnings for Beginners")
        st.markdown("""
        <div class="glass-card">
            <ul style="color: var(--text-secondary); line-height: 2; list-style-position: inside;">
                <li><strong style="color: var(--accent-teal);">Understanding Market Basics:</strong> Learn what stocks are and how markets operate</li>
                <li><strong style="color: var(--accent-teal);">Investment Strategies:</strong> Discover different approaches to building your portfolio</li>
                <li><strong style="color: var(--accent-teal);">Technical Analysis:</strong> Master chart reading and pattern recognition</li>
                <li><strong style="color: var(--accent-teal);">Risk Management:</strong> Learn to protect your capital and minimize losses</li>
                <li><strong style="color: var(--accent-teal);">Long-term Wealth:</strong> Understand compounding and disciplined investing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Tamil Videos
    with lang_tabs[1]:
        st.markdown("#### Tamil Tutorials")
        
        tam_col1, tam_col2, tam_col3 = st.columns(3)
        
        with tam_col1:
            st.markdown("""
            <div class="video-card">
                <h4>பங்கு சந்தை அடிப்படைகள்</h4>
                <p>தொடக்கநிலையாளர்களுக்கான பங்கு சந்தை முழுமையான வழிகாட்டி</p>
                <a href="https://youtu.be/RfOKl-ya5BY" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with tam_col2:
            st.markdown("""
            <div class="video-card">
                <h4>பங்கு முதலீட் எப்படி செய்வது</h4>
                <p>பங்குகளை தேர்வு செய்தல் மற்றும் முதலீட் செய்வதற்கான வழிமுறைகள்</p>
                <a href="https://youtu.be/64SziSDJTNU" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with tam_col3:
            st.markdown("""
            <div class="video-card">
                <h4>கேண்டில்ஸ்டிக் வாசிப்பு</h4>
                <p>கேண்டில்ஸ்டிக் விளக்கப்படங்களை படிக்க கற்றுக்கொள்ளுங்கள்</p>
                <a href="https://youtu.be/Jpvi6r4wCvA" target="_blank" style="text-decoration: none;">
                    <button>▶ வீடியோ பாருங்க</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # Hindi Videos
    with lang_tabs[2]:
        st.markdown("#### Hindi Tutorials")
        
        hin_col1, hin_col2, hin_col3 = st.columns(3)
        
        with hin_col1:
            st.markdown("""
            <div class="video-card">
                <h4>शेयर बाजार की बुनियादी बातें</h4>
                <p>शुरुआती लोगों के लिए शेयर बाजार की संपूर्ण गाइड</p>
                <a href="https://youtu.be/hsbhN7i7H8E" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with hin_col2:
            st.markdown("""
            <div class="video-card">
                <h4>शेयर में निवेश कैसे करें</h4>
                <p>शेयर चुनने और निवेश करने के लिए चरण-दर-चरण मार्गदर्शिका</p>
                <a href="https://youtu.be/BeVw7UH_i9U" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        with hin_col3:
            st.markdown("""
            <div class="video-card">
                <h4>कैंडलस्टिक चार्ट पढ़ना</h4>
                <p>कैंडलस्टिक चार्ट और पैटर्न को समझें और सीखें</p>
                <a href="https://youtu.be/lQpulkxLHe0" target="_blank" style="text-decoration: none;">
                    <button>▶ वीडियो देखें</button>
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Educational Content
    st.markdown("### ◢ Educational Resources")
    
    learn_tabs = st.tabs([
        "◆ Basics",
        "◈ Key Concepts",
        "◭ Common Mistakes",
        "◉ Pro Tips"
    ])
    
    with learn_tabs[0]:
        st.markdown("#### Stock Market Fundamentals")
        
        basics_col1, basics_col2 = st.columns(2)
        
        with basics_col1:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: var(--accent-teal); margin-bottom: 16px;">◆ What is a Stock?</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    A stock represents ownership in a company. When you buy a stock, you become a partial owner 
                    (shareholder) of that company. As the company grows and becomes more valuable, your stock 
                    can increase in value too.
                </p>
                <br>
                <h4 style="color: var(--accent-teal); margin-bottom: 16px;">◈ How Does Trading Work?</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    Trading involves buying and selling stocks through stock exchanges (like NSE and BSE in India). 
                    You place orders through a broker, and trades are executed when buyers and sellers agree on a price.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with basics_col2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: var(--accent-teal); margin-bottom: 16px;">◭ Bull vs Bear Markets</h4>
                <p style="color: var(--text-secondary); line-height: 1.8;">
                    <strong style="color: var(--success);">Bull Market:</strong> Period of rising stock prices, 
                    investor optimism, and economic growth. Investors are confident and buying.<br><br>
                    <strong style="color: var(--danger);">Bear Market:</strong> Period of falling stock prices (usually 
                    20%+ decline), pessimism, and economic concerns. Investors are cautious and selling.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="color: var(--accent-teal); margin-bottom: 20px;">◉ Technical vs Fundamental Analysis</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 20px;">
                <div style="border-left: 3px solid var(--accent-teal); padding-left: 16px;">
                    <h5 style="color: var(--text-primary); margin-bottom: 12px;">Technical Analysis</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Studies price movements, charts, and patterns to predict future price movements. 
                        Uses indicators like RSI, MACD, moving averages. Best for short-term trading.
                    </p>
                </div>
                <div style="border-left: 3px solid var(--accent-teal); padding-left: 16px;">
                    <h5 style="color: var(--text-primary); margin-bottom: 12px;">Fundamental Analysis</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Evaluates company's financial health, earnings, management, industry position. 
                        Uses ratios like P/E, ROE, debt-to-equity. Best for long-term investing.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with learn_tabs[1]:
        st.markdown("#### Essential Stock Market Concepts")
        
        concept_col1, concept_col2 = st.columns(2)
        
        with concept_col1:
            concepts = {
                "Market Capitalization": "Total value of all company shares. Large-cap (>₹20,000 Cr), Mid-cap (₹5,000-20,000 Cr), Small-cap (<₹5,000 Cr)",
                "P/E Ratio": "Price-to-Earnings ratio. Shows how much investors pay per rupee of earnings. Lower P/E may indicate undervaluation.",
                "Dividend": "Portion of company profits distributed to shareholders. Provides regular income along with potential capital gains."
            }
            
            for term, explanation in concepts.items():
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-teal); margin-bottom: 10px;">◆ {term}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{explanation}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with concept_col2:
            concepts2 = {
                "IPO": "Initial Public Offering - when a private company first sells shares to the public, becoming a publicly traded company.",
                "Volatility": "Measure of price fluctuation. High volatility means bigger price swings, higher risk but potential for higher returns.",
                "Liquidity": "How easily you can buy or sell a stock without affecting its price. High liquidity means you can trade quickly at fair prices."
            }
            
            for term, explanation in concepts2.items():
                st.markdown(f"""
                <div class="glass-card">
                    <h5 style="color: var(--accent-teal); margin-bottom: 10px;">◆ {term}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{explanation}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with learn_tabs[2]:
        st.markdown("#### Common Beginner Mistakes to Avoid")
        
        mistakes = [
            ("Investing Without Research", "Never invest in a company without understanding its business model, financials, and future prospects."),
            ("Emotional Trading", "Don't let fear or greed drive your decisions. Stick to your investment plan and strategy."),
            ("Following Tips Blindly", "Avoid investing based on hot tips from friends or social media without your own analysis."),
            ("Not Diversifying", "Don't put all your money in one stock. Spread investments across sectors to reduce risk."),
            ("Trying to Time the Market", "Consistently predicting market tops and bottoms is nearly impossible. Focus on time IN the market."),
            ("Overtrading", "Frequent buying and selling increases costs and rarely beats a disciplined long-term approach."),
            ("Ignoring Risk Management", "Always set stop losses and never invest more than you can afford to lose."),
            ("Reacting to News Impulsively", "Market news often creates short-term volatility. Focus on long-term fundamentals.")
        ]
        
        for i in range(0, len(mistakes), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                title, desc = mistakes[i]
                st.markdown(f"""
                <div class="glass-card" style="border-left: 3px solid var(--danger);">
                    <h5 style="color: var(--danger); margin-bottom: 10px;">× {title}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if i + 1 < len(mistakes):
                with col2:
                    title, desc = mistakes[i + 1]
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 3px solid var(--danger);">
                        <h5 style="color: var(--danger); margin-bottom: 10px;">× {title}</h5>
                        <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with learn_tabs[3]:
        st.markdown("#### Professional Trading Tips")
        
        tips = [
            ("Create an Investment Plan", "Define your goals, risk tolerance, time horizon, and investment strategy before you start."),
            ("Set Realistic Expectations", "Aim for consistent 12-15% annual returns rather than chasing unrealistic 100% gains."),
            ("Never Stop Learning", "Markets evolve constantly. Keep educating yourself through books, courses, and analysis."),
            ("Start Small", "Begin with amounts you're comfortable losing while you learn. Gradually increase as you gain experience."),
            ("Track Your Performance", "Maintain a trading journal. Analyze your wins and losses to improve your strategy."),
            ("Do Your Due Diligence", "Read annual reports, understand company financials, and analyze industry trends before investing."),
            ("Be Patient", "Wealth creation through stocks takes time. Avoid the temptation of quick gains."),
            ("Use Stop Losses", "Protect your capital by setting automatic sell orders at predetermined loss levels.")
        ]
        
        for i in range(0, len(tips), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                title, desc = tips[i]
                st.markdown(f"""
                <div class="glass-card" style="border-left: 3px solid var(--success);">
                    <h5 style="color: var(--success); margin-bottom: 10px;">✓ {title}</h5>
                    <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
            
            if i + 1 < len(tips):
                with col2:
                    title, desc = tips[i + 1]
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 3px solid var(--success);">
                        <h5 style="color: var(--success); margin-bottom: 10px;">✓ {title}</h5>
                        <p style="color: var(--text-secondary); line-height: 1.7;">{desc}</p>
                    </div>
                    """, unsafe_allow_html=True)

# TAB 6: Stock Comparison Tool
with tabs[5]:
    st.markdown('<div class="section-header"><span class="icon">◇</span> Stock Comparison Tool</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <div class="info-box-title">
            ◆ Compare Multiple Stocks
        </div>
        <div style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7;">
            • Select 2-3 stocks to compare side-by-side<br>
            • View key metrics, performance, and fundamentals<br>
            • Make informed decisions based on comparative analysis
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stock Selection for Comparison
    st.markdown("### ◎ Select Stocks to Compare")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        stock1 = st.selectbox("Stock 1", list(stock_options.keys()), key="comp1")
    with comp_col2:
        stock2 = st.selectbox("Stock 2", list(stock_options.keys()), index=1, key="comp2")
    with comp_col3:
        stock3 = st.selectbox("Stock 3 (Optional)", ["None"] + list(stock_options.keys()), key="comp3")
    
    if st.button("◭ Compare Stocks", use_container_width=True):
        stocks_to_compare = [stock1, stock2]
        if stock3 != "None":
            stocks_to_compare.append(stock3)
        
        # Fetch data for all selected stocks
        comparison_data = []
        
        for stock_name in stocks_to_compare:
            ticker = stock_options[stock_name]
            data, price, info = get_latest_stock_data(ticker, "1mo")
            
            if not ticker.endswith(".NS") and price:
                price = price * 83.2
            
            if price and info:
                comparison_data.append({
                    "Company": stock_name,
                    "Current Price (₹)": f"₹{price:.2f}" if price else "N/A",
                    "Market Cap (Cr)": f"₹{info.get('marketCap', 0) / 10000000:.1f}" if info.get('marketCap') else "N/A",
                    "P/E Ratio": f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "N/A",
                    "P/B Ratio": f"{info.get('priceToBook', 'N/A'):.2f}" if isinstance(info.get('priceToBook'), (int, float)) else "N/A",
                    "52W High (₹)": f"₹{info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekHigh'), (int, float)) else "N/A",
                    "52W Low (₹)": f"₹{info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if isinstance(info.get('fiftyTwoWeekLow'), (int, float)) else "N/A",
                    "Sector": info.get('sector', 'N/A'),
                    "Industry": info.get('industry', 'N/A')
                })
        
        if comparison_data:
            st.markdown("### ◢ Comparison Results")
            
            # Create comparison table
            df_comparison = pd.DataFrame(comparison_data)
            df_comparison = df_comparison.set_index("Company")
            
            st.dataframe(df_comparison, use_container_width=True, height=400)
            
            # Price comparison chart
            st.markdown("### ◭ Price Comparison (Last 30 Days)")
            
            fig_comparison = go.Figure()
            
            for stock_name in stocks_to_compare:
                ticker = stock_options[stock_name]
                data, _, _ = get_latest_stock_data(ticker, "1mo")
                
                if not data.empty:
                    price_col = "Close"
                    if not ticker.endswith(".NS"):
                        data["Close"] = data["Close"] * 83.2
                    
                    fig_comparison.add_trace(go.Scatter(
                        x=data.index,
                        y=data["Close"],
                        mode='lines',
                        name=stock_name,
                        line=dict(width=3),
                        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:.2f}<extra></extra>'
                    ))
            
            fig_comparison.update_layout(
                title={'text': 'Stock Price Comparison', 'font': {'size': 18, 'color': 'white'}, 'x': 0.5},
                font=dict(color='white'),
                plot_bgcolor='#0a0e27',
                paper_bgcolor='#0a0e27',
                height=500,
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True, title="Date"),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True, title="Price (₹)"),
                hovermode='x unified',
                legend=dict(bgcolor='rgba(0,0,0,0.5)', bordercolor='var(--border-accent)', borderwidth=1)
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
        else:
            st.warning("⚠️ Unable to fetch comparison data. Please try again.")

# Footer
st.markdown("""
<div style="margin-top: 80px; padding: 40px 0; border-top: 2px solid var(--border-subtle); text-align: center;">
    <h2 style="color: var(--accent-teal); margin-bottom: 20px; font-size: 2rem;">STOCKSENTINEL</h2>
    <p style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 24px;">
        <strong style="color: var(--accent-teal);">Learning & Trading Intelligence</strong>
    </p>
    <div style="display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; margin-bottom: 24px;">
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◆</span> Real-time Data
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◉</span> News Analysis
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◭</span> Technical Indicators
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◈</span> AI Insights
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◎</span> Watchlist
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◐</span> Learning Hub
        </span>
        <span style="color: var(--text-secondary); display: flex; align-items: center; gap: 8px;">
            <span style="color: var(--accent-teal);">◇</span> Stock Comparison
        </span>
    </div>
    <div style="background: rgba(0, 255, 198, 0.05); border: 1px solid var(--border-accent); border-radius: 12px; padding: 24px; margin: 24px auto; max-width: 900px;">
        <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.7; margin: 0;">
            <strong style="color: var(--warning);">⚠️ Disclaimer:</strong> This tool is designed for educational and informational purposes only. 
            Stock market investments involve substantial risk. Past performance does not guarantee future results. 
            Always consult with qualified financial advisors before making investment decisions. 
            The creators of this tool are not responsible for any financial losses.
        </p>
    </div>
    <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 24px;">
        Built with ❤️ using Streamlit | Powered by yfinance & NewsAPI
    </p>
    <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 12px;">
        © 2024 StockSentinel. All rights reserved.
    </p>
</div>
""", unsafe_allow_html=True)

# System Online Indicator
st.markdown(f"""
<div style="position: fixed; bottom: 20px; right: 20px; background: var(--bg-card); 
     color: white; padding: 12px 20px; border: 1px solid var(--border-accent); border-radius: 8px; font-size: 0.85rem; z-index: 1000; 
     box-shadow: 0 8px 24px rgba(0, 255, 198, 0.3);">
    <div style="display: flex; align-items: center; gap: 10px;">
        <div class="status-indicator status-online"></div>
        <span>System Online | {current_time_ist.strftime('%H:%M:%S')}</span>
    </div>
</div>
""", unsafe_allow_html=True)
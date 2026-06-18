
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from src.models import SalesForecaster
from datetime import datetime, timedelta
from io import BytesIO

# ======================================================================
# PAGE CONFIGURATION
# ======================================================================
st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================
# NETFLIX-INSPIRED DARK THEME
# Background: #080810  |  Surface: #0d0d1a / #12121f
# Text: #ffffff / #e0e0e0 / #888  |  Accent: #e50914 (red) + #ffd700 (gold)
# ======================================================================
st.markdown("""
<style>
    /* ── FONTS ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    *, *::before, *::after {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    /* ── ROOT BACKGROUND ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: #080810;
        color: #e0e0e0;
    }

    /* subtle grid overlay */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(229,9,20,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(229,9,20,0.025) 1px, transparent 1px);
        background-size: 48px 48px;
        pointer-events: none;
        z-index: 0;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: #0d0d1a !important;
        border-right: 1px solid #1e1e3a !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stFileUploader > div {
        background: #12121f !important;
        border: 1px solid #2a2a45 !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
    }
    section[data-testid="stSidebar"] label {
        color: #888 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }
    /* Sidebar slider track */
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: #2a2a45 !important;
    }
    section[data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: #e50914 !important;
    }

    /* ── SIDEBAR SECTION BLOCKS ── */
    .sidebar-block {
        background: #12121f;
        border: 1px solid #1e1e3a;
        border-radius: 14px;
        padding: 1rem 1.1rem 1.1rem;
        margin-bottom: 0.9rem;
    }
    .sidebar-block-title {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #555 !important;
        margin-bottom: 0.7rem;
    }

    /* ── MAIN HEADER ── */
    .nf-header {
        background: #0d0d1a;
        border: 1px solid #1e1e3a;
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin: 0.5rem 0 2rem;
        position: relative;
        overflow: hidden;
    }
    .nf-header::after {
        content: "";
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, #e50914 0%, #ffd700 100%);
        border-radius: 4px 0 0 4px;
    }
    .nf-header-badge {
        display: inline-block;
        padding: 3px 10px;
        background: rgba(229,9,20,0.12);
        border: 1px solid rgba(229,9,20,0.35);
        border-radius: 50px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: #e50914;
        margin-bottom: 0.7rem;
    }
    .nf-header h1 {
        font-size: clamp(1.6rem, 3.5vw, 2.4rem);
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin: 0 0 0.35rem;
    }
    .nf-header h1 span {
        color: #e50914;
    }
    .nf-header p {
        font-size: 0.92rem;
        color: #555;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: #0d0d1a;
        border: 1px solid #1e1e3a;
        border-radius: 12px;
        padding: 0.35rem;
        margin-bottom: 1.75rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 1.25rem;
        border-radius: 9px;
        background: transparent !important;
        color: #555 !important;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.03em;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #e50914 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(229,9,20,0.4) !important;
    }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: #1e1e3a !important;
        color: #ccc !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding: 0 !important;
    }

    /* ── SECTION HEADINGS ── */
    .section-label {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1.1rem;
    }
    .section-label-line {
        width: 3px;
        height: 1.1rem;
        background: #e50914;
        border-radius: 2px;
        flex-shrink: 0;
    }
    .section-label h3 {
        font-size: 1rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.01em;
    }
    .section-label span {
        font-size: 0.75rem;
        color: #555;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-left: 0.3rem;
    }

    /* ── METRIC CARDS ── */
    .nf-card {
        background: #0d0d1a;
        border: 1px solid #1e1e3a;
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
        height: 100%;
    }
    .nf-card:hover {
        border-color: #e50914;
        box-shadow: 0 8px 28px rgba(229,9,20,0.18);
        transform: translateY(-3px);
    }
    .nf-card-icon {
        font-size: 1.3rem;
        margin-bottom: 0.6rem;
        display: block;
        opacity: 0.85;
    }
    .nf-card-label {
        font-size: 0.68rem;
        color: #555;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.35rem;
    }
    .nf-card-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .nf-card-value.accent {
        color: #e50914;
    }
    .nf-card-value.gold {
        color: #ffd700;
    }
    .nf-card-sub {
        font-size: 0.7rem;
        color: #444;
        margin-top: 0.4rem;
        font-weight: 500;
    }
    .nf-card-trend-up {
        display: inline-block;
        font-size: 0.72rem;
        color: #22c55e;
        background: rgba(34,197,94,0.1);
        border-radius: 50px;
        padding: 2px 8px;
        margin-top: 0.4rem;
        font-weight: 600;
    }
    .nf-card-trend-down {
        display: inline-block;
        font-size: 0.72rem;
        color: #e50914;
        background: rgba(229,9,20,0.1);
        border-radius: 50px;
        padding: 2px 8px;
        margin-top: 0.4rem;
        font-weight: 600;
    }

    /* ── ACCURACY BADGE CARDS ── */
    .acc-card {
        background: #0d0d1a;
        border: 1px solid #1e1e3a;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    .acc-card-label {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #555;
        margin-bottom: 0.6rem;
    }
    .acc-card-val {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.04em;
    }
    .acc-card-desc {
        font-size: 0.72rem;
        color: #444;
        margin-top: 0.35rem;
    }
    .acc-good  { color: #22c55e; }
    .acc-warn  { color: #ffd700; }
    .acc-bad   { color: #e50914; }
    .acc-blue  { color: #60a5fa; }

    /* ── DIVIDER ── */
    .nf-divider {
        height: 1px;
        background: #1e1e3a;
        margin: 1.5rem 0;
    }

    /* ── BUTTONS ── */
    .stButton > button {
        background: #e50914 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.75rem !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.03em !important;
        box-shadow: 0 4px 18px rgba(229,9,20,0.35) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        background: #c0070f !important;
        box-shadow: 0 8px 28px rgba(229,9,20,0.55) !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button:active {
        transform: scale(0.97) !important;
    }

    /* Sidebar buttons softer */
    section[data-testid="stSidebar"] .stButton > button {
        background: #12121f !important;
        border: 1px solid #2a2a45 !important;
        color: #e0e0e0 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #1e1e3a !important;
        border-color: #e50914 !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: #12121f !important;
        color: #e0e0e0 !important;
        border: 1px solid #2a2a45 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        border-color: #e50914 !important;
        color: #ffffff !important;
        background: #1e1e3a !important;
    }

    /* ── PROGRESS BAR ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #e50914, #ffd700) !important;
        border-radius: 4px;
    }
    .stProgress > div > div {
        background: #1e1e3a !important;
        border-radius: 4px;
    }

    /* ── ALERTS / INFO ── */
    .stAlert {
        background: #12121f !important;
        border-color: #1e1e3a !important;
        color: #e0e0e0 !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="notification"] {
        background: #12121f !important;
        border-radius: 12px !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid #1e1e3a !important;
    }
    .stDataFrame thead th {
        background: #12121f !important;
        color: #555 !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        border-bottom: 1px solid #1e1e3a !important;
    }
    .stDataFrame tbody td {
        background: #0d0d1a !important;
        color: #e0e0e0 !important;
        border-bottom: 1px solid #1a1a2e !important;
        font-size: 0.88rem !important;
    }
    .stDataFrame tbody tr:hover td {
        background: #12121f !important;
    }

    /* ── EXPANDER ── */
    details > summary {
        background: #12121f !important;
        border: 1px solid #1e1e3a !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        padding: 0.6rem 1rem !important;
        cursor: pointer;
    }
    details[open] > summary {
        border-radius: 10px 10px 0 0 !important;
        border-bottom-color: transparent !important;
    }
    details > div {
        background: #0d0d1a !important;
        border: 1px solid #1e1e3a !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
    }

    /* ── SPINNER ── */
    .stSpinner > div {
        border-top-color: #e50914 !important;
    }

    /* ── SUCCESS / WARNING / ERROR ── */
    .stSuccess { background: rgba(34,197,94,0.08) !important; border-color: rgba(34,197,94,0.2) !important; }
    .stWarning { background: rgba(255,215,0,0.08) !important; border-color: rgba(255,215,0,0.2) !important; }
    .stError   { background: rgba(229,9,20,0.08) !important; border-color: rgba(229,9,20,0.2) !important; }
    .stInfo    { background: rgba(96,165,250,0.06) !important; border-color: rgba(96,165,250,0.15) !important; }

    /* ── FOOTER ── */
    .nf-footer {
        text-align: center;
        padding: 2rem 0 1.5rem;
        color: #333;
        font-size: 0.75rem;
        border-top: 1px solid #1e1e3a;
        margin-top: 3rem;
        letter-spacing: 0.04em;
    }
    .nf-footer a { color: #e50914; text-decoration: none; }
    .nf-footer a:hover { color: #ffd700; }

    /* ════════════════════════════════════════════
       ── STREAMLIT HEADER BAR
       The top bar with Deploy + hamburger menu
    ════════════════════════════════════════════ */
    header[data-testid="stHeader"] {
        background: #0d0d1a !important;
        border-bottom: 1px solid #1e1e3a !important;
        backdrop-filter: blur(10px);
    }
    /* Red accent line under the header */
    header[data-testid="stHeader"]::after {
        content: "";
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #e50914 0%, transparent 60%);
    }
    /* Top decoration bar Streamlit renders */
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, #e50914, #ffd700) !important;
        height: 3px !important;
    }
    /* Deploy button */
    button[data-testid="baseButton-header"] {
        background: #12121f !important;
        border: 1px solid #2a2a45 !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.3rem 0.9rem !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    button[data-testid="baseButton-header"]:hover {
        border-color: #e50914 !important;
        color: #ffffff !important;
        background: #1e1e3a !important;
    }
    /* Hamburger / three-dot menu button */
    button[data-testid="baseButton-headerNoPadding"] {
        color: #555 !important;
        background: transparent !important;
        border: none !important;
        transition: color 0.2s !important;
    }
    button[data-testid="baseButton-headerNoPadding"]:hover {
        color: #e50914 !important;
    }
    /* Toolbar actions area */
    [data-testid="stToolbar"] {
        background: transparent !important;
    }

    /* ════════════════════════════════════════════
       ── FILE UPLOAD DROPZONE
       The white drag-and-drop zone
    ════════════════════════════════════════════ */
    section[data-testid="stFileUploadDropzone"] {
        background: #0d0d1a !important;
        border: 1.5px dashed #2a2a45 !important;
        border-radius: 14px !important;
        transition: border-color 0.25s, background 0.25s !important;
        padding: 1.2rem !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: #e50914 !important;
        background: rgba(229,9,20,0.04) !important;
    }
    /* Upload cloud icon */
    section[data-testid="stFileUploadDropzone"] svg {
        fill: #444 !important;
        width: 2rem !important;
        height: 2rem !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover svg {
        fill: #e50914 !important;
    }
    /* "Drag and drop file here" text */
    [data-testid="stFileDropzoneInstructions"] span {
        color: #888 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    /* "Limit 200MB per file • CSV" */
    [data-testid="stFileDropzoneInstructions"] small {
        color: #444 !important;
        font-size: 0.72rem !important;
    }
    /* "Browse files" button */
    section[data-testid="stFileUploadDropzone"] button {
        background: #12121f !important;
        border: 1px solid #2a2a45 !important;
        border-radius: 8px !important;
        color: #e0e0e0 !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        padding: 0.35rem 1rem !important;
        margin-top: 0.5rem !important;
        box-shadow: none !important;
        transition: border-color 0.2s, background 0.2s !important;
    }
    section[data-testid="stFileUploadDropzone"] button:hover {
        background: #1e1e3a !important;
        border-color: #e50914 !important;
        color: #ffffff !important;
    }

    /* ════════════════════════════════════════════
       ── st.table  (HTML <table> — fully CSS-controllable)
       Replaces canvas-based st.dataframe grid
    ════════════════════════════════════════════ */
    [data-testid="stTable"] {
        width: 100% !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid #1e1e3a !important;
    }
    [data-testid="stTable"] table {
        width: 100% !important;
        border-collapse: collapse !important;
        background: #0d0d1a !important;
        color: #e0e0e0 !important;
        font-size: 0.88rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stTable"] thead tr {
        background: #12121f !important;
        border-bottom: 2px solid #1e1e3a !important;
    }
    [data-testid="stTable"] thead th {
        background: #12121f !important;
        color: #555 !important;
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        padding: 0.75rem 1rem !important;
        border: none !important;
        white-space: nowrap !important;
    }
    [data-testid="stTable"] tbody tr {
        border-bottom: 1px solid #1a1a2e !important;
        transition: background 0.15s !important;
    }
    [data-testid="stTable"] tbody tr:hover {
        background: #12121f !important;
    }
    [data-testid="stTable"] tbody td {
        background: transparent !important;
        color: #e0e0e0 !important;
        padding: 0.65rem 1rem !important;
        border: none !important;
        font-variant-numeric: tabular-nums !important;
    }
    /* Index column */
    [data-testid="stTable"] tbody th {
        background: #12121f !important;
        color: #444 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.65rem 1rem !important;
        border: none !important;
        border-right: 1px solid #1e1e3a !important;
    }
    /* Sales / numeric values get accent color */
    [data-testid="stTable"] tbody td:last-child {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* ════════════════════════════════════════════
       ── st.dataframe canvas grid wrapper
       The canvas pixels can't be CSS-recolored,
       but we style the surrounding chrome
    ════════════════════════════════════════════ */
    [data-testid="stDataFrame"] > div {
        background: #0d0d1a !important;
        border: 1px solid #1e1e3a !important;
        border-radius: 12px !important;
    }
    .dvn-scroller,
    .glideDataEditor,
    .dvn-scroll-inner,
    .dvn-stack {
        background: #0d0d1a !important;
        border-radius: 12px !important;
    }
    .dvn-scroller::-webkit-scrollbar { width: 6px; height: 6px; }
    .dvn-scroller::-webkit-scrollbar-track { background: #0d0d1a; }
    .dvn-scroller::-webkit-scrollbar-thumb { background: #2a2a45; border-radius: 4px; }
    .dvn-scroller::-webkit-scrollbar-thumb:hover { background: #e50914; }

    /* ════════════════════════════════════════════
       ── GLOBAL SCROLLBAR (whole page)
    ════════════════════════════════════════════ */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #080810; }
    ::-webkit-scrollbar-thumb { background: #2a2a45; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #e50914; }

    /* ── RESPONSIVE ── */
    @media (max-width: 768px) {
        .nf-header { padding: 1.4rem 1.5rem; }
        .nf-header h1 { font-size: 1.5rem; }
        .nf-card-value { font-size: 1.4rem; }
    }
</style>
""", unsafe_allow_html=True)


# ======================================================================
# PLOTLY CHART DEFAULTS (dark, transparent bg)
# ======================================================================
CHART_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#888', size=12, family='Inter, sans-serif'),
    xaxis=dict(
        gridcolor='#1e1e3a', linecolor='#1e1e3a',
        tickcolor='#444', tickfont=dict(color='#666', size=11),
        title_font=dict(color='#555')
    ),
    yaxis=dict(
        gridcolor='#1e1e3a', linecolor='#1e1e3a',
        tickcolor='#444', tickfont=dict(color='#666', size=11),
        title_font=dict(color='#555')
    ),
    legend=dict(
        bgcolor='rgba(13,13,26,0.85)',
        bordercolor='#1e1e3a',
        borderwidth=1,
        font=dict(color='#888', size=12)
    ),
    margin=dict(l=48, r=24, t=32, b=40),
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='#0d0d1a',
        bordercolor='#2a2a45',
        font=dict(color='#e0e0e0', size=12)
    )
)


def html_table(dataframe):
    """Render a DataFrame as a fully inline-styled HTML table.
    Bypasses Streamlit CSS scoping and canvas rendering entirely."""
    rows_html = ""
    for i, row in dataframe.iterrows():
        cells = f"""<td style="
                padding:0.6rem 1rem;
                color:#555;
                font-size:0.75rem;
                font-weight:600;
                border-right:1px solid #1e1e3a;
                white-space:nowrap;
            ">{i}</td>"""
        for col, val in row.items():
            is_num = str(val).startswith('$') or (isinstance(val, (int, float)))
            val_color = "#ffffff" if is_num else "#e0e0e0"
            val_weight = "700" if is_num else "400"
            cells += f"""<td style="
                padding:0.6rem 1rem;
                color:{val_color};
                font-weight:{val_weight};
                font-size:0.88rem;
                border-right:1px solid #12121f;
                white-space:nowrap;
                font-variant-numeric:tabular-nums;
            ">{val}</td>"""
        bg = "#0d0d1a" if int(str(i)) % 2 == 0 else "#0a0a16"
        rows_html += f'<tr style="background:{bg};border-bottom:1px solid #1a1a2e;" onmouseover="this.style.background=\'#12121f\'" onmouseout="this.style.background=\'{bg}\'">{cells}</tr>'

    header_cells = '<th style="padding:0.65rem 1rem;color:#444;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;border-right:1px solid #1e1e3a;white-space:nowrap;">#</th>'
    for col in dataframe.columns:
        header_cells += f'<th style="padding:0.65rem 1rem;color:#555;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;border-right:1px solid #1e1e3a;white-space:nowrap;">{col}</th>'

    html = f"""
    <div style="
        width:100%;
        overflow-x:auto;
        border-radius:14px;
        border:1px solid #1e1e3a;
        background:#0d0d1a;
        margin-bottom:1rem;
    ">
      <table style="
          width:100%;
          border-collapse:collapse;
          font-family:'Inter',-apple-system,sans-serif;
          background:#0d0d1a;
      ">
        <thead>
          <tr style="background:#12121f;border-bottom:2px solid #1e1e3a;">
            {header_cells}
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def section(title, subtitle=""):
    sub = f' <span>{subtitle}</span>' if subtitle else ''
    st.markdown(f"""
    <div class="section-label">
        <div class="section-label-line"></div>
        <h3>{title}{sub}</h3>
    </div>
    """, unsafe_allow_html=True)


def metric_card(icon, label, value, sub="", color="white"):
    color_class = {"red": "accent", "gold": "gold"}.get(color, "")
    return f"""
    <div class="nf-card">
        <span class="nf-card-icon">{icon}</span>
        <div class="nf-card-label">{label}</div>
        <div class="nf-card-value {color_class}">{value}</div>
        <div class="nf-card-sub">{sub}</div>
    </div>
    """


# ======================================================================
# HEADER
# ======================================================================
st.markdown("""
<div class="nf-header">
    <div class="nf-header-badge">AI ANALYTICS</div>
    <h1>Sales <span>Forecasting</span> Dashboard</h1>
    <p>ARIMA · SARIMA · Exponential Smoothing · Time-Series Intelligence</p>
</div>
""", unsafe_allow_html=True)


# ======================================================================
# SIDEBAR
# ======================================================================
with st.sidebar:
    st.markdown('<div class="sidebar-block">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block-title">📁 Data Source</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload CSV (date, sales)",
        type=['csv'],
        label_visibility="collapsed"
    )
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Custom data loaded")
    else:
        try:
            df = pd.read_csv('data/sales_data.csv')
            st.info("📊 Using sample data")
        except FileNotFoundError:
            st.error("❌ Data file missing. Upload a CSV.")
            st.stop()
    st.markdown('</div>', unsafe_allow_html=True)

    if 'date' not in df.columns or 'sales' not in df.columns:
        st.error("❌ CSV must have columns: 'date', 'sales'")
        st.stop()

    st.markdown('<div class="sidebar-block">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block-title">📊 Dataset</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Records", f"{len(df):,}")
    c2.metric("Days", f"{len(df)}")
    st.caption(
        f"**{pd.to_datetime(df['date']).min().strftime('%b %d, %Y')}**"
        f" → **{pd.to_datetime(df['date']).max().strftime('%b %d, %Y')}**"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-block">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block-title">🤖 Algorithm</div>', unsafe_allow_html=True)
    model_type = st.selectbox(
        "Algorithm",
        ["ARIMA", "SARIMA", "Exponential Smoothing", "Auto ARIMA"],
        label_visibility="collapsed",
        help="ARIMA: linear trends. SARIMA: seasonal patterns. Exp.Smoothing: trend+seasonality. Auto: searches best params."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-block">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block-title">⚙️ Parameters</div>', unsafe_allow_html=True)

    if model_type == "ARIMA":
        p = st.slider("AR order (p)", 0, 10, 5)
        d = st.slider("Differencing (d)", 0, 2, 1)
        q = st.slider("MA order (q)", 0, 10, 2)
        order = (p, d, q)
    elif model_type == "SARIMA":
        colA, colB = st.columns(2)
        p = colA.slider("p", 0, 5, 1);  d = colA.slider("d", 0, 2, 1);  q = colA.slider("q", 0, 5, 1)
        P = colB.slider("P", 0, 5, 1);  D = colB.slider("D", 0, 2, 1);  Q = colB.slider("Q", 0, 5, 1)
        s = st.slider("Seasonal period (s)", 2, 365, 12)
        order = (p, d, q);  seasonal_order = (P, D, Q, s)
    elif model_type == "Exponential Smoothing":
        seasonality = st.slider("Seasonal period", 2, 365, 7)
    else:
        st.caption("Auto ARIMA searches for the best (p, d, q) automatically.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-block">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-block-title">📅 Forecast Horizon</div>', unsafe_allow_html=True)
    forecast_days = st.slider("Days to forecast", 7, 365, 90, 7)
    st.markdown('</div>', unsafe_allow_html=True)


# ======================================================================
# TABS
# ======================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊  Overview",
    "🔮  Forecast",
    "📈  Accuracy",
    "💾  Export"
])


# ──────────────────────────────────────────────────────────────────────
# TAB 1 — DATA OVERVIEW
# ──────────────────────────────────────────────────────────────────────
with tab1:
    # KPI row
    section("Key Performance Indicators", "Last full period")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(metric_card("📊", "Average Daily Sales", f"${df['sales'].mean():,.0f}", "Mean across all records"), unsafe_allow_html=True)
    with kpi2:
        st.markdown(metric_card("📈", "Peak Day", f"${df['sales'].max():,.0f}", "Highest single day", color="gold"), unsafe_allow_html=True)
    with kpi3:
        st.markdown(metric_card("📉", "Low Day", f"${df['sales'].min():,.0f}", "Lowest single day", color="red"), unsafe_allow_html=True)
    with kpi4:
        st.markdown(metric_card("📐", "Std Deviation", f"±${df['sales'].std():,.0f}", "Day-to-day variability"), unsafe_allow_html=True)

    st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

    # Historical trend
    section("Historical Trend", "Full date range")
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Scatter(
        x=df['date'], y=df['sales'],
        mode='lines',
        name='Daily Sales',
        line=dict(color='#e50914', width=2),
        fill='tozeroy',
        fillcolor='rgba(229,9,20,0.06)',
        hovertemplate='<b>%{x}</b><br>Sales: $%{y:,.0f}<extra></extra>'
    ))
    fig_hist.update_layout(
        height=380,
        **CHART_LAYOUT,
        yaxis_title='Sales ($)',
    )
    fig_hist.update_xaxes(rangeslider_visible=True, rangeslider_thickness=0.04)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

    # Distribution + box side by side
    section("Distribution Analysis")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=df['sales'], nbinsx=50, name='Distribution',
            marker=dict(color='#e50914', opacity=0.75, line=dict(color='#c0070f', width=0.5))
        ))
        fig_dist.update_layout(height=300, title_text='Sales Frequency', title_font=dict(color='#888', size=13), **CHART_LAYOUT)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_d2:
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=df['sales'], name='Sales',
            marker=dict(color='#ffd700', outliercolor='#e50914'),
            line=dict(color='#ffd700'),
            fillcolor='rgba(255,215,0,0.07)',
            boxmean=True
        ))
        fig_box.update_layout(height=300, title_text='Sales Spread', title_font=dict(color='#888', size=13), **CHART_LAYOUT)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

    # Raw data table — inline HTML guarantees white text on dark bg
    section("Raw Data", f"{len(df):,} records")
    display_df = df.head(30).copy()
    display_df['sales'] = display_df['sales'].apply(lambda x: f"${x:,.2f}")
    html_table(display_df)


# ──────────────────────────────────────────────────────────────────────
# TAB 2 — FORECAST
# ──────────────────────────────────────────────────────────────────────
with tab2:
    section(f"{model_type} Forecast", f"{forecast_days}-day horizon")

    btn_col = st.columns([1, 2, 1])
    with btn_col[1]:
        forecast_btn = st.button("🚀  Generate Forecast", type="primary", use_container_width=True)

    if forecast_btn:
        prog = st.progress(0)
        status = st.empty()

        status.info("⚙️ Initialising forecaster…")
        prog.progress(0.12)

        import time
        time.sleep(0.3)

        try:
            forecaster = SalesForecaster(df)
            train, test = forecaster.train_test_split(test_size=90)
            last_date = pd.to_datetime(df['date'].max())
            forecast_dates = [last_date + timedelta(days=x) for x in range(1, forecast_days + 1)]

            status.info(f"🤖 Training {model_type} model…")
            prog.progress(0.4)

            if model_type == "ARIMA":
                model, forecast_values, conf_int = forecaster.arima_forecast(order=order, periods=forecast_days)
                lower, upper = conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values
            elif model_type == "SARIMA":
                model, forecast_values, conf_int = forecaster.sarima_forecast(
                    order=order, seasonal_order=seasonal_order, periods=forecast_days
                )
                lower, upper = conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values
            elif model_type == "Exponential Smoothing":
                model, forecast_values = forecaster.exponential_smoothing_forecast(
                    periods=forecast_days, seasonal_periods=seasonality
                )
                se = df['sales'].std()
                lower, upper = forecast_values - 1.96 * se, forecast_values + 1.96 * se
            else:
                model, forecast_values, best_order = forecaster.auto_arima_forecast(periods=forecast_days)
                st.success(f"✅ Best ARIMA order found: {best_order}")
                se = df['sales'].std()
                lower, upper = forecast_values - 1.96 * se, forecast_values + 1.96 * se

            prog.progress(0.72)
            status.info("🎨 Rendering chart…")

            # Forecast chart
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(
                x=df['date'], y=df['sales'],
                name='Historical',
                mode='lines',
                line=dict(color='#60a5fa', width=1.5),
                hovertemplate='<b>%{x}</b><br>Actual: $%{y:,.0f}<extra></extra>'
            ))
            fig_fc.add_trace(go.Scatter(
                x=forecast_dates + list(reversed(forecast_dates)),
                y=list(upper) + list(reversed(lower)),
                fill='toself',
                fillcolor='rgba(229,9,20,0.09)',
                line=dict(color='rgba(229,9,20,0)'),
                name='95% Confidence',
                hoverinfo='skip'
            ))
            fig_fc.add_trace(go.Scatter(
                x=forecast_dates, y=forecast_values,
                name='Forecast',
                mode='lines',
                line=dict(color='#e50914', width=2.5),
                hovertemplate='<b>%{x}</b><br>Forecast: $%{y:,.0f}<extra></extra>'
            ))
            fig_fc.update_layout(
                height=460,
                yaxis_title='Sales ($)',
                **CHART_LAYOUT
            )
            prog.progress(0.92)
            st.plotly_chart(fig_fc, use_container_width=True)

            # Forecast KPI row
            st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)
            section("Forecast Summary", f"Next {forecast_days} days")
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                st.markdown(metric_card("📊", "Avg Daily Forecast", f"${np.mean(forecast_values):,.0f}", "Mean prediction"), unsafe_allow_html=True)
            with f2:
                st.markdown(metric_card("📈", "Peak Forecast Day", f"${np.max(forecast_values):,.0f}", "Highest predicted", color="gold"), unsafe_allow_html=True)
            with f3:
                st.markdown(metric_card("📉", "Low Forecast Day", f"${np.min(forecast_values):,.0f}", "Lowest predicted", color="red"), unsafe_allow_html=True)
            with f4:
                st.markdown(metric_card("💰", "Total Revenue Est.", f"${np.sum(forecast_values):,.0f}", f"Over {forecast_days} days"), unsafe_allow_html=True)

            # Save to session
            st.session_state['forecast'] = pd.DataFrame({
                'date': forecast_dates,
                'forecast': forecast_values,
                'lower_bound': lower,
                'upper_bound': upper
            })

            prog.empty(); status.empty()

        except Exception as e:
            prog.empty(); status.error(f"❌ {str(e)}")

    else:
        st.info("👆 Select your model in the sidebar, then click **Generate Forecast**.")


# ──────────────────────────────────────────────────────────────────────
# TAB 3 — ACCURACY
# ──────────────────────────────────────────────────────────────────────
with tab3:
    section("Model Accuracy", "Backtest on last 90 days")

    eval_btn = st.button("📊  Evaluate Model", type="primary")

    if eval_btn:
        with st.spinner("Running backtest…"):
            try:
                forecaster = SalesForecaster(df)
                train, test = forecaster.train_test_split(test_size=90)

                if model_type == "ARIMA":
                    _, pred, _ = forecaster.arima_forecast(order=order, periods=90)
                elif model_type == "SARIMA":
                    _, pred, _ = forecaster.sarima_forecast(order=order, seasonal_order=seasonal_order, periods=90)
                elif model_type == "Exponential Smoothing":
                    _, pred = forecaster.exponential_smoothing_forecast(periods=90, seasonal_periods=seasonality)
                else:
                    _, pred, _ = forecaster.auto_arima_forecast(periods=90)

                metrics = forecaster.calculate_metrics(test['sales'].values, pred)

                # Accuracy KPI cards
                mape_class = "acc-good" if metrics['MAPE'] < 10 else ("acc-warn" if metrics['MAPE'] < 20 else "acc-bad")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"""
                    <div class="acc-card">
                        <div class="acc-card-label">MAPE</div>
                        <div class="acc-card-val {mape_class}">{metrics['MAPE']}%</div>
                        <div class="acc-card-desc">Mean Absolute % Error</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m2:
                    st.markdown(f"""
                    <div class="acc-card">
                        <div class="acc-card-label">RMSE</div>
                        <div class="acc-card-val acc-blue">${metrics['RMSE']:,.0f}</div>
                        <div class="acc-card-desc">Root Mean Squared Error</div>
                    </div>
                    """, unsafe_allow_html=True)
                with m3:
                    st.markdown(f"""
                    <div class="acc-card">
                        <div class="acc-card-label">MAE</div>
                        <div class="acc-card-val acc-blue">${metrics['MAE']:,.0f}</div>
                        <div class="acc-card-desc">Mean Absolute Error</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

                # Actual vs Predicted chart
                section("Actual vs Predicted", "Last 90-day window")
                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Scatter(
                    x=test['date'], y=test['sales'],
                    name='Actual',
                    mode='lines+markers',
                    line=dict(color='#60a5fa', width=2),
                    marker=dict(size=3.5, color='#60a5fa')
                ))
                fig_cmp.add_trace(go.Scatter(
                    x=test['date'], y=pred,
                    name='Predicted',
                    mode='lines+markers',
                    line=dict(color='#e50914', width=2, dash='dot'),
                    marker=dict(size=3.5, color='#e50914')
                ))
                fig_cmp.update_layout(height=380, yaxis_title='Sales ($)', **CHART_LAYOUT)
                st.plotly_chart(fig_cmp, use_container_width=True)

                st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

                # Residual error chart
                section("Residual Error", "Predicted − Actual")
                residuals = pred - test['sales'].values
                fig_res = go.Figure()
                fig_res.add_trace(go.Bar(
                    x=test['date'], y=residuals,
                    name='Residual',
                    marker=dict(
                        color=['#e50914' if r < 0 else '#22c55e' for r in residuals],
                        opacity=0.75
                    )
                ))
                fig_res.add_hline(y=0, line_color='#444', line_width=1)
                fig_res.update_layout(height=260, yaxis_title='Error ($)', **CHART_LAYOUT)
                st.plotly_chart(fig_res, use_container_width=True)

                st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)

                # Performance verdict
                if metrics['MAPE'] < 10:
                    st.success(f"🎯 **Excellent** — MAPE of {metrics['MAPE']}% is under 10%. This model is production-ready.")
                elif metrics['MAPE'] < 20:
                    st.info(f"✅ **Good** — MAPE of {metrics['MAPE']}%. Acceptable for most business forecasting use cases.")
                else:
                    st.warning(f"⚠️ **Needs tuning** — MAPE of {metrics['MAPE']}% exceeds 20%. Try adjusting parameters or switching models.")

            except Exception as e:
                st.error(f"❌ {str(e)}")
    else:
        st.info("👆 Click **Evaluate Model** to run the backtest and see accuracy metrics.")


# ──────────────────────────────────────────────────────────────────────
# TAB 4 — EXPORT
# ──────────────────────────────────────────────────────────────────────
with tab4:
    section("Export Forecast Data")

    if 'forecast' in st.session_state:
        forecast_df = st.session_state['forecast']

        # Preview table — inline HTML, white text guaranteed on dark bg
        preview_df = forecast_df.head(20).copy()
        preview_df['forecast']     = preview_df['forecast'].apply(lambda x: f"${x:,.2f}")
        preview_df['lower_bound']  = preview_df['lower_bound'].apply(lambda x: f"${x:,.2f}")
        preview_df['upper_bound']  = preview_df['upper_bound'].apply(lambda x: f"${x:,.2f}")
        html_table(preview_df)

        st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)
        section("Download", f"{len(forecast_df)} rows")

        dl1, dl2 = st.columns(2)
        with dl1:
            csv = forecast_df.to_csv(index=False)
            st.download_button(
                label="📥  Download as CSV",
                data=csv,
                file_name=f'forecast_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        with dl2:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                forecast_df.to_excel(writer, index=False, sheet_name='Forecast')
            st.download_button(
                label="📥  Download as Excel",
                data=output.getvalue(),
                file_name=f'forecast_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
    else:
        st.info("⚠️ No forecast yet — go to the **Forecast** tab and generate one first.")


# ======================================================================
# FOOTER
# ======================================================================
st.markdown("""
<div class="nf-footer">
    Built with
    <a href="https://streamlit.io" target="_blank">Streamlit</a> ·
    <a href="https://www.statsmodels.org" target="_blank">Statsmodels</a> ·
    <a href="https://plotly.com" target="_blank">Plotly</a>
    &nbsp;·&nbsp; © 2026 Sales Forecasting Dashboard
</div>
""", unsafe_allow_html=True)

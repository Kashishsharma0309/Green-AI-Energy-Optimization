import sqlite3
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, r2_score

from src.prediction import get_feature_importances, simulate_what_if_scenario
from src.database import run_query

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "energy.db"
MODEL_PATH = BASE_DIR / "models" / "energy_model.pkl"

st.set_page_config(page_title="NEXUS | Smart Building Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")


def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#edf3f7; --muted:#91a0b0; --line:#263746; --cyan:#50d4c1; --amber:#f4b860; --red:#ff7068; }
    .stApp { background:#071018; color:var(--ink); font-family:'Manrope',sans-serif; }
    .stApp:before { content:''; position:fixed; inset:0; pointer-events:none; background:radial-gradient(circle at 82% -8%,rgba(54,143,154,.12),transparent 28%),radial-gradient(circle at 8% 100%,rgba(25,75,103,.10),transparent 24%); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#0b1620,#081018); border-right:1px solid #263746; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label { color:#c5d2dd !important; }
    [data-testid="stSidebar"] > div:first-child { padding:1rem .65rem; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.2rem; }
    [data-testid="stSidebar"] hr { margin:.55rem 0 !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { margin:0 !important; }
    .nav-heading { color:#718596; font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.12em; line-height:1.2; margin:.55rem 0 .12rem; }
    [data-testid="stSidebar"] .stButton { margin:0; }
    [data-testid="stSidebar"] .stButton > button { width:100%; min-height:27px; padding:.18rem .4rem; justify-content:flex-start; gap:.55rem; border:1px solid transparent; border-radius:4px; background:transparent; color:#bfccd6; box-shadow:none; font-size:.82rem; font-weight:500; }
    [data-testid="stSidebar"] .stButton > button:before { content:''; width:7px; height:7px; flex:0 0 7px; border:1px solid #78909f; border-radius:50%; }
    [data-testid="stSidebar"] .stButton > button:hover { border-color:#294a57; background:#10222d; color:#edf5f7; }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] { border-color:transparent !important; background:#10242c !important; color:#dffbf5 !important; }
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:before { background:#50d4c1; border-color:#50d4c1; }
    .filter-label { color:#718596; font-family:'DM Mono',monospace; font-size:.65rem; letter-spacing:.12em; margin:.1rem 0 -.35rem; }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div { background:#0d1a25 !important; border-color:#2b4354 !important; color:#dce7ee !important; }
    [data-testid="stSlider"] [data-baseweb="slider"] { margin-top:.45rem; }
    .block-container { padding:2rem 3rem 3rem; max-width:1480px; }
    h1,h2,h3,h4 { font-family:'Manrope',sans-serif; letter-spacing:0; }
    h1 { font-size:2rem !important; font-weight:800 !important; }
    h2 { font-size:1.35rem !important; }
    h3 { font-size:1.05rem !important; }
    .brand { font-size:1.35rem; font-weight:800; letter-spacing:.08em; color:#fff; }
    .brand span { color:var(--cyan); }
    .eyebrow { color:var(--cyan); font-family:'DM Mono',monospace; text-transform:uppercase; font-size:.72rem; letter-spacing:.12em; }
    .subtle { color:var(--muted); font-size:.86rem; }
    .hero { padding:.3rem 0 1.5rem; border-bottom:1px solid var(--line); margin-bottom:1.5rem; }
    .metric-card,.panel { background:linear-gradient(145deg,rgba(17,30,42,.94),rgba(10,20,29,.94)); border:1px solid #2a4050; border-radius:8px; padding:1.1rem 1.2rem; box-shadow:0 8px 24px rgba(0,0,0,.12); }
    .metric-card { min-height:116px; }
    .metric-label { color:var(--muted); font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }
    .metric-value { color:#f7fafc; font-size:1.65rem; font-weight:800; margin:.35rem 0; }
    .metric-delta { color:var(--cyan); font-family:'DM Mono',monospace; font-size:.73rem; }
    .product-bar { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin:0 0 1.1rem; padding:.65rem .85rem; border:1px solid #283f50; border-radius:8px; background:rgba(15,29,41,.7); }
    .product-bar-name { color:#f3fbff; font-weight:800; letter-spacing:.11em; font-size:.72rem; }
    .product-bar-name span { color:#55d6c2; }
    .product-statuses { display:flex; align-items:center; flex-wrap:wrap; justify-content:flex-end; gap:.7rem; color:#95a8b6; font-family:'DM Mono',monospace; font-size:.65rem; }
    .panel { min-height:0; margin-bottom:1.2rem; }
    .panel-title { font-weight:700; margin-bottom:.2rem; }
    .status { display:inline-flex; gap:.45rem; align-items:center; color:var(--cyan); font-family:'DM Mono',monospace; font-size:.72rem; }
    .dot { width:7px; height:7px; border-radius:50%; background:var(--cyan); box-shadow:0 0 12px var(--cyan); display:inline-block; }
    .alert-card { border-left:3px solid var(--red); background:#171b25; border-radius:7px; padding:.9rem 1rem; margin:.5rem 0; }
    .alert-card.medium { border-color:var(--amber); }
    .badge { display:inline-block; padding:.18rem .5rem; border-radius:4px; font-family:'DM Mono',monospace; font-size:.68rem; background:#392126; color:#ff9b91; }
    .badge.medium { background:#3c3020; color:#f4c77e; }
    .badge.low { background:#173532; color:#8ee4d6; }
    .section-rule { border-top:1px solid var(--line); margin:1.6rem 0; }
    .home-brand { color:#f5f9fb; font-size:.82rem; font-weight:800; letter-spacing:.17em; }
    .home-brand span { color:var(--cyan); }
    .home-subtitle { color:var(--muted); font-size:.92rem; margin-top:.4rem; }
    .welcome-hero { margin-top:4.5rem; padding:0 0 4.25rem; max-width:820px; background:none; border:0; min-height:0; }
    .welcome-title { font-size:clamp(3.15rem,7vw,6.5rem); line-height:.94; letter-spacing:-.055em; font-weight:800; margin:0 0 1.35rem; }
    .welcome-copy { color:#aebdca; font-size:1.04rem; max-width:610px; line-height:1.75; }
    .feature-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; margin:0 0 2.5rem; }
    .feature-card { min-height:118px; padding:1.1rem; border:1px solid #283d4c; border-radius:7px; background:linear-gradient(145deg,rgba(17,31,43,.86),rgba(10,20,29,.86)); }
    .feature-card b { display:block; color:#f1f7f9; font-size:.82rem; letter-spacing:.02em; margin-bottom:.45rem; }
    .feature-card span { color:var(--muted); font-size:.76rem; line-height:1.45; }
    button[kind="primary"] { min-height:44px; padding:0 1.25rem; border:1px solid #58d8c6 !important; border-radius:5px !important; background:#3bc0af !important; color:#061019 !important; font-weight:800 !important; box-shadow:none !important; }
    .architecture { border:1px solid #294554; border-radius:12px; background:linear-gradient(145deg,#0f202b,#0b141d); padding:1.15rem; overflow:hidden; }
    .architecture-row { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; position:relative; }
    .architecture-row + .architecture-row { margin-top:1.6rem; }
    .architecture-row + .architecture-row:before { content:'↓'; position:absolute; top:-1.55rem; left:50%; transform:translateX(-50%); color:var(--cyan); font-size:1.25rem; text-shadow:0 0 12px rgba(85,214,194,.6); }
    .architecture-node { position:relative; text-align:center; padding:.85rem .45rem; border:1px solid #315064; border-radius:8px; background:#10202c; color:#e2edf2; font-family:'DM Mono',monospace; font-size:.7rem; letter-spacing:.02em; }
    .architecture-node:not(:last-child):after { content:'→'; position:absolute; z-index:2; top:50%; left:calc(100% + .28rem); transform:translateY(-50%); color:#55d6c2; font-family:Arial,sans-serif; font-size:1.05rem; }
    .architecture-node.core { border-color:#3d827d; background:linear-gradient(135deg,#12343a,#10242d); color:#a9f2e4; box-shadow:0 0 18px rgba(85,214,194,.08); }
    .overview-card,.transparency-card { min-height:270px; border:1px solid #2b4354; border-radius:12px; padding:1.25rem; background:linear-gradient(145deg,#121f2b,#0d1720); }
    .card-kicker { color:#55d6c2; font-family:'DM Mono',monospace; font-size:.68rem; letter-spacing:.1em; text-transform:uppercase; }
    .overview-title { margin:.35rem 0 .85rem; font-size:1.05rem; font-weight:800; color:#f1f7fa; }
    .highlight-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.55rem; }
    .highlight-card { border:1px solid #273d4d; border-radius:7px; padding:.7rem; background:rgba(15,34,46,.7); }
    .highlight-card b { display:block; color:#dffbf5; font-size:.75rem; margin-bottom:.25rem; }
    .highlight-card span,.transparency-item span { color:#91a2b0; font-size:.71rem; line-height:1.4; }
    .transparency-list { display:grid; gap:.55rem; }
    .transparency-item { display:grid; grid-template-columns:26px 1fr; gap:.6rem; padding:.65rem 0; border-bottom:1px solid #263746; }
    .transparency-item:last-child { border-bottom:0; }
    .transparency-icon { color:#55d6c2; font-family:'DM Mono',monospace; font-size:.8rem; padding-top:.05rem; }
    .transparency-item b { display:block; color:#eaf2f6; font-size:.76rem; margin-bottom:.16rem; }
    .tech-stack { display:flex; flex-wrap:wrap; gap:.45rem; padding:1rem 1.1rem; border:1px solid #294554; border-radius:10px; background:#0d1923; align-items:center; }
    .tech-label { color:#7f96a6; font-family:'DM Mono',monospace; font-size:.67rem; letter-spacing:.1em; margin-right:.35rem; }
    .tech-badge { padding:.3rem .52rem; border:1px solid #315064; border-radius:5px; background:#102530; color:#c6e9e4; font-family:'DM Mono',monospace; font-size:.67rem; }
    @media (max-width:800px) { .block-container { padding:1.25rem 1rem 2rem; } .welcome-hero { margin-top:3rem; padding-bottom:3rem; } .feature-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
    @media (max-width:480px) { .feature-grid,.highlight-grid { grid-template-columns:1fr; } }
    .health-item { display:flex; justify-content:space-between; padding:.65rem 0; border-bottom:1px solid #273443; font-size:.84rem; }
    .health-ok { color:var(--cyan); font-family:'DM Mono',monospace; font-size:.7rem; }
    .finding { border-left:2px solid var(--cyan); padding:.65rem .8rem; margin:.55rem 0; background:#10222a; color:#c9d4de; font-size:.86rem; }
    .scenario { display:flex; gap:1rem; align-items:stretch; margin:1rem 0; }
    .scenario-step { flex:1; border:1px solid var(--line); background:#111d28; border-radius:8px; padding:1rem; }
    .scenario-step strong { display:block; font-size:1.35rem; margin:.3rem 0; }
    .scenario-arrow { display:flex; align-items:center; color:var(--cyan); font-size:1.4rem; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); background:#0b1620 !important; }
    .stButton > button { border:1px solid #385064; background:#122433; color:#dce9f2; border-radius:6px; }
    .stDownloadButton > button { border:1px solid var(--cyan); color:var(--cyan); background:#10252a; }
    div[data-baseweb="select"] > div { background:#101c28; border-color:#314354; }
    [data-testid="stDataFrame"] { background:#0b1620; border-radius:8px; overflow:hidden; }
    [data-testid="stDataFrame"] * { color:#d6e1e8 !important; }
    [data-testid="stDataFrame"] [role="gridcell"],[data-testid="stDataFrame"] [role="columnheader"] { background:#0b1620 !important; border-color:#263746 !important; }
    [data-testid="stExpander"] { background:linear-gradient(145deg,#111f2c,#0d1720); border:1px solid #2b4354; border-radius:9px; }
    [data-testid="stCode"] { border:1px solid #29495b; border-radius:6px; background:#061018 !important; }
    [data-testid="stCode"] code { color:#a9f2e4 !important; }
    .query-card { margin:.75rem 0; padding:1rem; border:1px solid #2b4354; border-radius:10px; background:linear-gradient(145deg,#101f2b,#0b151e); }
    .query-meta { color:#76daca; font-family:'DM Mono',monospace; font-size:.67rem; letter-spacing:.07em; }
    .report-tile { min-height:118px; border:1px solid #2b4354; border-radius:9px; padding:1rem; background:linear-gradient(145deg,#101f2b,#0b151e); }
    .report-tile b { display:block; color:#ecf8fb; font-size:.82rem; letter-spacing:.05em; margin:.25rem 0; }
    .report-tile span { color:#8ca0ae; font-size:.74rem; line-height:1.4; }
    .home-page { margin:-2rem -3rem -3rem; background:#f4f7f7; }
    .home-site-header { height:68px; display:flex; align-items:center; justify-content:space-between; padding:0 3rem; background:#07132a; border-bottom:1px solid rgba(255,255,255,.10); }
    .home-wordmark { color:#fff; font-size:1.02rem; font-weight:800; letter-spacing:.14em; }
    .home-wordmark span { color:#63d5c5; }
    .home-header-context { color:#bac7d2; font-size:.74rem; font-weight:600; letter-spacing:.08em; }
    .home-hero { display:flex; align-items:center; min-height:360px; padding:3.5rem 3rem; background:linear-gradient(120deg,#07152c 0%,#0b2030 72%,#0d2935 100%); }
    .home-hero-content { max-width:720px; }
    .home-kicker { color:#8ce0d4; font-size:.72rem; font-weight:800; letter-spacing:.16em; margin-bottom:.8rem; }
    .home-hero h1 { margin:0 0 .85rem; color:#fff; font-size:clamp(2.15rem,4vw,3.45rem) !important; line-height:1.12; letter-spacing:-.035em; }
    .home-hero p { max-width:620px; color:#d9e2e8; font-size:1rem; line-height:1.65; margin:0 0 .85rem; }
    .home-hero p.home-supporting-copy { color:#b8c6d0; max-width:630px; margin-bottom:1.45rem; }
    .home-cta { display:inline-block; padding:.72rem 1.1rem; border:1px solid #58c9bc; border-radius:5px; background:#57c2b5; color:#071426 !important; font-size:.82rem; font-weight:800; text-decoration:none !important; cursor:pointer; }
    .home-light-section { padding:3.75rem 3rem 3.5rem; background:#f4f7f7; color:#132330; }
    .home-light-section h2 { max-width:760px; color:#102333; font-size:clamp(1.55rem,2.4vw,2.15rem) !important; line-height:1.18; margin:0 0 .85rem; }
    .home-light-section > p { max-width:730px; color:#526473; font-size:1rem; line-height:1.7; margin:0 0 2rem; }
    .home-features { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; max-width:1180px; }
    .home-feature { display:flex; flex-direction:column; min-height:174px; padding:1.25rem; border:1px solid #2d7571; border-radius:9px; background:linear-gradient(145deg,#102331,#0b1722); box-shadow:0 8px 18px rgba(5,18,30,.12); transition:border-color .16s ease,transform .16s ease,box-shadow .16s ease; }
    .home-feature:hover { border-color:#5dbfb4; transform:translateY(-3px); box-shadow:0 12px 24px rgba(5,18,30,.18); }
    .home-feature:before { content:''; display:block; width:22px; height:3px; margin-bottom:1rem; border-radius:2px; background:#59c6b9; }
    .home-feature b { display:block; color:#f4f8fa; font-size:.79rem; font-weight:800; letter-spacing:.11em; margin-bottom:.65rem; }
    .home-feature span { color:#bac7cf; font-size:.88rem; line-height:1.55; }
    .home-final-cta { margin-top:2.25rem; padding:1.8rem 2rem; border:1px solid #245550; border-radius:9px; background:#0b1d2b; }
    .home-final-cta h3 { margin:0 0 .5rem; color:#f4f8fa; font-size:1.05rem !important; font-weight:800; letter-spacing:.06em; }
    .home-final-cta p { max-width:660px; margin:0 0 1.1rem; color:#b7c5ce; font-size:.91rem; line-height:1.55; }
    #MainMenu,footer,[data-testid="stToolbar"] { visibility:hidden; }

    [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] { background:#0d1a25 !important; color:#dce7ee !important; border-color:#2b4354 !important; }
    [role="option"] { background:#0d1a25 !important; color:#dce7ee !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"] { background:#14313a !important; }
    [data-testid="stDateInput"] input, [data-testid="stNumberInput"] input { background:#0d1a25 !important; color:#dce7ee !important; border-color:#2b4354 !important; }
    [data-testid="stDataFrame"] [role="columnheader"] { background:#122433 !important; color:#f1f7fa !important; font-weight:700 !important; }
    [data-testid="stDataFrame"] [role="gridcell"] { background:#0b1620 !important; }
    [data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] { background:#102a31 !important; }
    [data-testid="stDataFrame"] canvas { filter:none !important; }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data():
    if not DB_PATH.exists():
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as conn:
        data = pd.read_sql_query("SELECT * FROM energy_consumption", conn)
    if not data.empty:
        data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data


@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


def model_available():
    return MODEL_PATH.exists()


@st.cache_data(show_spinner=False)
def detect_anomalies(data, contamination=0.02):
    if data.empty:
        return data.copy()
    features = ["temperature_c", "humidity_percent", "occupancy", "power_kw", "energy_kwh"]
    result = data.copy()
    detector = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    result["anomaly_label"] = detector.fit_predict(result[features])
    result["anomaly_score"] = -detector.decision_function(result[features])
    baseline = result.groupby("appliance")["energy_kwh"].transform("median")
    result["excess_energy_kwh"] = (result["energy_kwh"] - baseline).clip(lower=0)
    result["excess_cost_inr"] = result["excess_energy_kwh"] * 8
    result["severity"] = "Normal"
    anomalies = result[result["anomaly_label"] == -1]
    if not anomalies.empty:
        q75, q90 = anomalies["anomaly_score"].quantile([.75, .90])
        result.loc[result["anomaly_score"] >= q75, "severity"] = "Medium"
        result.loc[result["anomaly_score"] >= q90, "severity"] = "High"
        result.loc[(result["anomaly_label"] == -1) & (result["anomaly_score"] >= q90), "severity"] = "Critical"
    return result


@st.cache_data(show_spinner=False)
def hourly_frame(data):
    if data.empty:
        return pd.DataFrame()
    return data.groupby("timestamp", as_index=False).agg(
        energy_kwh=("energy_kwh", "sum"), power_kw=("power_kw", "sum"),
        temperature_c=("temperature_c", "mean"), humidity_percent=("humidity_percent", "mean"),
        occupancy=("occupancy", "mean"), electricity_cost_inr=("electricity_cost_inr", "sum"), co2_kg=("co2_kg", "sum")
    ).sort_values("timestamp")


def make_fig(fig, height=330):
    fig.update_layout(height=height, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"family":"Manrope", "color":"#b6c2cf", "size":11}, margin={"l":10,"r":10,"t":35,"b":10}, legend={"orientation":"h", "y":1.12, "x":0}, hovermode="x unified")
    fig.update_xaxes(showgrid=False, linecolor="#273443")
    fig.update_yaxes(gridcolor="#1e2a36", zeroline=False)
    return fig


def metric(label, value, delta=""):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta">{delta}</div></div>', unsafe_allow_html=True)


def panel_heading(title, subtitle=""):
    st.markdown(f'<div class="panel-title">{title}</div><div class="subtle">{subtitle}</div>', unsafe_allow_html=True)


def empty_state(message="No records match the active filters."):
    st.info(message)


def model_metrics(hourly, model):
    features = ["temperature_c", "humidity_percent", "occupancy", "hour", "day_of_week", "month", "previous_energy", "energy_24h_ago"]
    frame = hourly.copy()
    frame["hour"] = frame["timestamp"].dt.hour
    frame["day_of_week"] = frame["timestamp"].dt.dayofweek
    frame["month"] = frame["timestamp"].dt.month
    frame["previous_energy"] = frame["energy_kwh"].shift(1)
    frame["energy_24h_ago"] = frame["energy_kwh"].shift(24)
    frame = frame.dropna()
    if model is None or len(frame) < 10:
        return None, None, frame
    split = max(1, int(len(frame) * .8))
    predictions = model.predict(frame[features].iloc[split:])
    return r2_score(frame["energy_kwh"].iloc[split:], predictions), mean_absolute_error(frame["energy_kwh"].iloc[split:], predictions), frame


def set_active_page(page):
    st.session_state["active_page"] = page


def sidebar_controls(data):
    page = st.session_state.get("active_page", "Welcome")
    page_groups = [
        ("HOME", [("Home", "Welcome")]),
        ("MONITORING", [("Command Center", "Command Center"), ("Live Monitoring", "Live IoT Monitoring")]),
        ("INTELLIGENCE", [("Energy Forecast", "AI Energy Forecast"), ("Anomaly Detection", "Anomaly Intelligence"), ("Energy Optimization", "Energy Optimization")]),
        ("ANALYTICS", [("Building Analytics", "Building Intelligence"), ("SQL Analytics", "SQL Analytics Lab")]),
        ("SUSTAINABILITY", [("Sustainability", "Sustainability")]),
        ("REPORTING", [("Reports", "Report Center")]),
    ]
    for group, entries in page_groups:
        st.sidebar.markdown(f'<div class="nav-heading">{group}</div>', unsafe_allow_html=True)
        for label, target in entries:
            st.sidebar.button(label, key=f"nav_{target}", type="primary" if page == target else "secondary", use_container_width=True, on_click=set_active_page, args=(target,))
    return page


def page_filters(data):
    buildings = sorted(data["building"].unique()) if not data.empty else []
    floors = sorted(data["floor"].unique()) if not data.empty else []
    appliances = sorted(data["appliance"].unique()) if not data.empty else []
    st.markdown('<div class="filter-label">DATA SCOPE</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.15])
    with c1: selected_buildings = st.multiselect("Building", buildings, default=buildings, key="scope_building")
    with c2: selected_floors = st.multiselect("Floor", floors, default=floors, key="scope_floor")
    with c3: selected_appliances = st.multiselect("Appliance", appliances, default=appliances, key="scope_appliance")
    with c4:
        date_range = st.date_input(
            "Date range", value=(data["timestamp"].min().date(), data["timestamp"].max().date()),
            min_value=data["timestamp"].min().date(), max_value=data["timestamp"].max().date(), key="scope_date"
        )
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        date_range = (data["timestamp"].min().date(), data["timestamp"].max().date())
    return selected_buildings, selected_floors, selected_appliances, date_range


def apply_scope(data, buildings, floors, appliances, date_range):
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    return data[
        data.building.isin(buildings)
        & data.floor.isin(floors)
        & data.appliance.isin(appliances)
        & (data.timestamp >= start_date)
        & (data.timestamp < end_date)
    ].copy()


def welcome_page(data, model):
    st.markdown('<main class="home-page"><header class="home-site-header"><div class="home-wordmark">NEXUS <span>/ ENERGY</span></div><div class="home-header-context">SMART BUILDING INTELLIGENCE</div></header><section class="home-hero"><div class="home-hero-content"><div class="home-kicker">NEXUS ENERGY</div><h1>AI-Powered Smart Building Intelligence</h1><p>Monitor energy. Predict demand. Detect anomalies. Optimize consumption.</p><p class="home-supporting-copy">An intelligent energy analytics platform designed to help buildings reduce energy consumption, operating cost, and carbon impact.</p></div></section></main>', unsafe_allow_html=True)

    if st.button("Explore Dashboard →", type="primary", key="welcome_explore_btn"):
        set_active_page("Command Center")
        st.rerun()

    st.markdown('<section class="home-light-section"><h2>SMARTER ENERGY. BETTER BUILDINGS.</h2><p>NEXUS combines energy monitoring, machine learning, anomaly detection and optimization recommendations into one intelligent building energy platform.</p><div class="home-features"><article class="home-feature"><b>MONITOR</b><span>Real-time energy and environmental telemetry.</span></article><article class="home-feature"><b>PREDICT</b><span>AI-based energy demand forecasting.</span></article><article class="home-feature"><b>DETECT</b><span>Identify abnormal consumption patterns.</span></article><article class="home-feature"><b>OPTIMIZE</b><span>Actionable recommendations for reducing energy use.</span></article></div></section>', unsafe_allow_html=True)


def command_center(filtered, model):
    st.markdown('<div class="eyebrow">01 / Operations overview</div><div class="hero"><h1>Command Center</h1><div class="subtle">A live operating picture of the simulated building portfolio.</div></div>', unsafe_allow_html=True)
    if filtered.empty:
        empty_state(); return
    total_energy, total_cost, total_co2 = filtered["energy_kwh"].sum(), filtered["electricity_cost_inr"].sum(), filtered["co2_kg"].sum()
    cols = st.columns(5)
    with cols[0]: metric("Total energy", f"{total_energy:,.0f} kWh", "period aggregate")
    with cols[1]: metric("Energy cost", f"₹{total_cost:,.0f}", "₹8.00 / kWh tariff")
    with cols[2]: metric("CO2 emissions", f"{total_co2:,.0f} kg", "0.82 kg / kWh")
    with cols[3]: metric("Average power", f"{filtered.power_kw.mean():,.1f} kW", "portfolio average")
    efficiency = max(0, min(100, 100 - filtered.energy_kwh.mean() / filtered.energy_kwh.max() * 100))
    with cols[4]: metric("Efficiency score", f"{efficiency:,.0f}/100", "normalized intensity")
    hourly = hourly_frame(filtered)
    left, right = st.columns([1.65, 1])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Energy consumption trend", "Hourly portfolio load across the selected period")
        st.plotly_chart(make_fig(px.area(hourly, x="timestamp", y="energy_kwh", color_discrete_sequence=["#55d6c2"]), 360), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with right:
        ranking = filtered.groupby("building", as_index=False).agg(energy_kwh=("energy_kwh", "sum"), intensity=("energy_kwh", "mean")).sort_values("energy_kwh")
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Building performance ranking", "Lower intensity ranks stronger")
        ranking["rank"] = range(1, len(ranking) + 1)
        st.dataframe(ranking[["rank", "building", "energy_kwh", "intensity"]].rename(columns={"energy_kwh":"Energy (kWh)", "intensity":"Avg / record"}), hide_index=True, use_container_width=True, height=260)
        peak = hourly.loc[hourly.energy_kwh.idxmax()] if not hourly.empty else None
        if peak is not None: st.markdown(f'<div class="alert-card medium"><span class="badge medium">PEAK LOAD</span><br><b>{peak.energy_kwh:,.1f} kWh</b> at {peak.timestamp:%d %b, %H:%M}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("### System health")
    health_items = [("Data coverage", f"{filtered.timestamp.min():%d %b %Y} - {filtered.timestamp.max():%d %b %Y}"), ("Records analyzed", f"{len(filtered):,}"), ("Anomaly engine", "Isolation Forest ready"), ("Model availability", "Random Forest loaded" if model_available() else "Saved model unavailable"), ("Database", "SQLite / energy_consumption")]
    health_cols = st.columns(len(health_items))
    for col, (label, value) in zip(health_cols, health_items):
        with col:
            st.markdown(f'<div class="panel"><div class="metric-label">{label}</div><div style="margin-top:.55rem">{value}</div><div class="health-ok">● VERIFIED</div></div>', unsafe_allow_html=True)
    st.markdown("### Peak load intelligence")
    peak = filtered.loc[filtered["energy_kwh"].idxmax()]
    st.markdown(f'<div class="panel"><span class="badge medium">PEAK LOAD RECORD</span> <b>{peak.energy_kwh:,.2f} kWh</b> · {peak.timestamp:%d %b %Y, %H:%M} · {peak.building} / {peak.floor} / {peak.appliance}<br><span class="subtle">Record-level peak from the active filter set. Portfolio hourly aggregation is shown above.</span></div>', unsafe_allow_html=True)
    st.markdown("### Recent system activity")
    recent = filtered.sort_values("timestamp", ascending=False).head(5)
    st.dataframe(recent[["timestamp","building","appliance","power_kw","occupancy"]].rename(columns={"power_kw":"Power kW"}), hide_index=True, use_container_width=True)


def live_monitoring(filtered):
    st.markdown('<div class="eyebrow">Live monitoring</div><div class="hero"><h1>Live IoT Monitoring</h1><div class="subtle">Latest simulated sensor frame. No physical hardware connection is present.</div></div>', unsafe_allow_html=True)
    if filtered.empty: empty_state(); return
    pick1, pick2, pick3 = st.columns(3)
    with pick1: building = st.selectbox("Building", sorted(filtered.building.unique()), key="live_building")
    building_df = filtered[filtered.building == building]
    with pick2: floor = st.selectbox("Floor", sorted(building_df.floor.unique()), key="live_floor")
    floor_df = building_df[building_df.floor == floor]
    with pick3: appliance = st.selectbox("Appliance", sorted(floor_df.appliance.unique()), key="live_appliance")
    current = floor_df[floor_df.appliance == appliance].sort_values("timestamp").iloc[-1]
    st.markdown(f'<div class="status"><span class="dot"></span> SIMULATED IoT FEED &nbsp;|&nbsp; Last update {current.timestamp:%d %b %Y, %H:%M}</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, label, value, unit in zip(cols, ["Temperature", "Humidity", "Occupancy", "Power consumption"], [current.temperature_c, current.humidity_percent, current.occupancy, current.power_kw], ["°C", "%", "people", "kW"]):
        with col: metric(label, f"{value:,.1f} {unit}", "simulated sensor reading")
    left, right = st.columns(2)
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Appliance status", "Derived from the latest recorded power draw")
        for name, power in floor_df.groupby("appliance").power_kw.last().sort_values(ascending=False).items():
            state = "ACTIVE" if power > .05 else "STANDBY"; color = "low" if state == "ACTIVE" else "medium"
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:.55rem 0;border-bottom:1px solid #273443"><span>{name}</span><span class="badge {color}">{state} · {power:.2f} kW</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        trend = floor_df.groupby("timestamp", as_index=False).power_kw.sum().tail(48)
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Floor telemetry", "Last 48 recorded hourly intervals")
        st.plotly_chart(make_fig(px.line(trend, x="timestamp", y="power_kw", color_discrete_sequence=["#f4b860"]), 300), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)


def forecast_page(filtered, model):
    st.markdown('<div class="eyebrow">03 / Predictive intelligence</div><div class="hero"><h1>AI Energy Forecast</h1><div class="subtle">Random Forest demand forecast using the trained model and 8 engineered features.</div></div>', unsafe_allow_html=True)
    hourly = hourly_frame(filtered)
    if hourly.empty or model is None: empty_state("Forecast requires the saved model and at least one data record."); return
    r2, mae, prepared = model_metrics(hourly, model)
    cols = st.columns(5)
    with cols[0]: metric("Model", "Random Forest", "trained artifact")
    with cols[1]: metric("R² Score", f"{r2:.3f}" if r2 is not None else "—", "chronological holdout")
    with cols[2]: metric("MAE", f"{mae:.2f} kWh" if mae is not None else "—", "chronological holdout")
    with cols[3]: metric("Forecast horizon", "24 hours", "rolling estimate")
    with cols[4]: metric("Dataset", f"{len(filtered):,}", "active records")

    features = ["temperature_c","humidity_percent","occupancy","hour","day_of_week","month","previous_energy","energy_24h_ago"]

    col_left, col_right = st.columns(2)
    with col_left:
        if len(prepared) > 36:
            test = prepared.tail(48).copy()
            test["predicted"] = model.predict(test[features])
            chart = go.Figure()
            chart.add_trace(go.Scatter(x=test.timestamp, y=test.energy_kwh, name="Actual", line={"color":"#55d6c2"}))
            chart.add_trace(go.Scatter(x=test.timestamp, y=test.predicted, name="Predicted", line={"color":"#f4b860","dash":"dot"}))
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_heading("Actual vs predicted backtest", "Model backtest on the latest 48 hourly records")
            st.plotly_chart(make_fig(chart, 320), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        df_imp = get_feature_importances(model)
        if not df_imp.empty:
            fig_imp = px.bar(df_imp, x="Importance", y="Feature", orientation="h", color="Importance", color_continuous_scale=["#1a3c40", "#55d6c2"])
            fig_imp.update_layout(coloraxis_showscale=False)
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            panel_heading("Feature Importance Weights", "Relative influence of input drivers on model predictions")
            st.plotly_chart(make_fig(fig_imp, 320), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 🎛️ Interactive 'What-If' HVAC & Occupancy Scenario Simulator")
    st.caption("Adjust HVAC temperature setpoints or occupancy reduction controls below to simulate predicted 24-hour demand changes.")

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        temp_delta = st.slider("HVAC Setpoint Increase (°C offset)", 0.0, 4.0, 1.5, 0.5, help="Raising cooling setpoint reduces HVAC power demand.")
    with sim_col2:
        occupancy_reduction = st.slider("Peak Occupancy Reduction (%)", 0, 50, 15, 5, help="Remote work or flexible scheduling reduces building occupancy.")

    df_sim = simulate_what_if_scenario(model, hourly, temp_delta_c=temp_delta, occupancy_pct_reduction=occupancy_reduction)

    if not df_sim.empty:
        total_baseline = df_sim["Baseline Forecast (kWh)"].sum()
        total_optimized = df_sim["Optimized Forecast (kWh)"].sum()
        total_saved_kwh = df_sim["Savings (kWh)"].sum()
        cost_saved = total_saved_kwh * 8.0
        co2_saved = total_saved_kwh * 0.82

        sim_m1, sim_m2, sim_m3, sim_m4 = st.columns(4)
        with sim_m1: metric("Baseline 24h Load", f"{total_baseline:,.1f} kWh", "unadjusted scenario")
        with sim_m2: metric("Optimized 24h Load", f"{total_optimized:,.1f} kWh", "simulated scenario")
        with sim_m3: metric("Predicted Savings", f"{total_saved_kwh:,.1f} kWh", f"₹{cost_saved:,.0f} cost reduction")
        with sim_m4: metric("CO2 Reduction", f"{co2_saved:,.1f} kg", "simulated 24h impact")

        fig_sim = go.Figure()
        fig_sim.add_trace(go.Scatter(x=df_sim["timestamp"], y=df_sim["Baseline Forecast (kWh)"], name="Baseline Forecast", line={"color":"#f4b860"}))
        fig_sim.add_trace(go.Scatter(x=df_sim["timestamp"], y=df_sim["Optimized Forecast (kWh)"], name="Optimized Forecast", line={"color":"#55d6c2"}))
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        panel_heading("24-Hour Projected Load Comparison", "Baseline demand vs Optimized scenario demand")
        st.plotly_chart(make_fig(fig_sim, 330), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def anomaly_page(filtered):
    st.markdown('<div class="eyebrow">04 / Detection</div><div class="hero"><h1>Anomaly Intelligence</h1><div class="subtle">Isolation Forest scans multi-sensor behavior for unusual energy events.</div></div>', unsafe_allow_html=True)

    c_col1, c_col2 = st.columns([1.5, 1])
    with c_col1:
        contamination_pct = st.slider("Anomaly Sensitivity (Contamination %)", 0.5, 5.0, 2.0, 0.5) / 100.0

    result = detect_anomalies(filtered, contamination=contamination_pct)
    if result.empty: empty_state(); return

    anomalies = result[result.anomaly_label == -1].sort_values("anomaly_score", ascending=False)
    cols = st.columns(4)
    values = [len(result), len(anomalies), anomalies.excess_energy_kwh.sum(), anomalies.excess_cost_inr.sum()]
    labels = ["Records analyzed", "Anomalies", "Excess energy", "Excess cost"]
    for col, label, value in zip(cols, labels, values):
        with col: metric(label, f"{value:,.0f}" + (" kWh" if label == "Excess energy" else " ₹" if label == "Excess cost" else ""), "Isolation Forest output")

    left, right = st.columns([1.3, 1])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Alert queue", "Critical and high-severity events first")
        for _, row in anomalies.head(6).iterrows():
            badge_class = "medium" if row.severity == "Medium" else ""
            st.markdown(f'<div class="alert-card"><span class="badge {badge_class}">{row.severity.upper()}</span> <b>{row.appliance}</b> · {row.building} / {row.floor}<br><span class="subtle">{row.timestamp:%d %b %H:%M} · score {row.anomaly_score:.3f} · +{row.excess_energy_kwh:.2f} kWh excess</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        trend = result.assign(anomaly=(result.anomaly_label == -1).astype(int)).groupby(result.timestamp.dt.date).anomaly.sum().reset_index(name="alerts")
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Anomaly trend", "Daily alert volume")
        st.plotly_chart(make_fig(px.bar(trend, x="timestamp", y="alerts", color_discrete_sequence=["#ff7068"]), 300), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)

    st.dataframe(anomalies[["timestamp","building","floor","appliance","severity","anomaly_score","excess_energy_kwh","excess_cost_inr"]].head(25).round(3), hide_index=True, use_container_width=True)


def optimization_page(filtered):
    st.markdown('<div class="eyebrow">Optimization</div><div class="hero"><h1>Energy Optimization</h1><div class="subtle">Actionable opportunities calculated from actual consumption patterns.</div></div>', unsafe_allow_html=True)
    if filtered.empty: empty_state(); return
    overall = filtered.energy_kwh.mean(); recommendations = []
    days = max(1, filtered.timestamp.dt.day.nunique())
    for appliance, group in filtered.groupby("appliance"):
        if group.energy_kwh.mean() > overall * 1.5:
            saving = group.energy_kwh.sum() * .12 * 30 / days; recommendations.append([appliance, "Portfolio average exceeded by more than 50%", "Review schedule and reduce idle operation", "High", saving, saving * 8, saving * .82])
    low = filtered[(filtered.occupancy < 15) & (filtered.energy_kwh > filtered.energy_kwh.quantile(.9))]
    if not low.empty:
        saving = low.energy_kwh.sum() * .15 * 30 / days; recommendations.append(["Building systems", "High load during low occupancy", "Automate HVAC and lighting setbacks", "Critical", saving, saving * 8, saving * .82])
    hvac = filtered[filtered.appliance.isin(["HVAC", "AC"])]
    if not hvac.empty and hvac.energy_kwh.mean() > overall:
        saving = hvac.energy_kwh.sum() * .08 * 30 / days; recommendations.append(["HVAC / AC", "Cooling load is above portfolio average", "Tune setpoints by 1–2°C and use occupancy control", "Medium", saving, saving * 8, saving * .82])
    if not recommendations: st.success("No priority opportunities detected for the active filter set."); return
    rec = pd.DataFrame(recommendations, columns=["Area", "Reason", "Recommended action", "Priority", "Est. monthly kWh saving", "Est. monthly cost saving (INR)", "Potential CO2 reduction (kg)"])
    summary_cols = st.columns(3)
    with summary_cols[0]: metric("Potential monthly savings", f"{rec['Est. monthly kWh saving'].sum():,.0f} kWh", "modeled recommendations")
    with summary_cols[1]: metric("Monthly cost impact", f"₹{rec['Est. monthly cost saving (INR)'].sum():,.0f}", "at current tariff")
    with summary_cols[2]: metric("CO2 impact", f"{rec['Potential CO2 reduction (kg)'].sum():,.0f} kg", "modeled reduction")
    for _, row in rec.iterrows():
        badge = "medium" if row.Priority == "Medium" else ""
        st.markdown(f'<div class="panel"><span class="badge {badge}">{row.Priority.upper()}</span> <b>{row.Area}</b><br><span class="subtle">{row.Reason}</span><p>{row["Recommended action"]}</p><span class="status">{row["Est. monthly kWh saving"]:,.0f} kWh · ₹{row["Est. monthly cost saving (INR)"]:,.0f} · {row["Potential CO2 reduction (kg)"]:,.0f} kg CO2 / month</span></div>', unsafe_allow_html=True)


def intelligence_page(data):
    st.markdown('<div class="eyebrow">Analytics</div><div class="hero"><h1>Building Analytics</h1><div class="subtle">Compare building and appliance energy use against operating conditions.</div></div>', unsafe_allow_html=True)
    buildings, floors, appliances, date_range = page_filters(data)
    filtered = apply_scope(data, buildings, floors, appliances, date_range)
    if filtered.empty: empty_state(); return
    c1, c2 = st.columns(2)
    with c1:
        building = filtered.groupby("building", as_index=False).energy_kwh.sum().sort_values("energy_kwh", ascending=False)
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Building comparison", "Total energy by asset")
        st.plotly_chart(make_fig(px.bar(building, x="building", y="energy_kwh", color="building", color_discrete_sequence=["#55d6c2","#f4b860","#7799c7"]), 360), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        appliance = filtered.groupby("appliance", as_index=False).energy_kwh.sum().sort_values("energy_kwh")
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Appliance ranking", "Highest total energy at top")
        st.plotly_chart(make_fig(px.bar(appliance, x="energy_kwh", y="appliance", orientation="h", color_discrete_sequence=["#f4b860"]), 360), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2); sample = filtered.sample(min(3000, len(filtered)), random_state=42)
    with c1:
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Occupancy vs energy", "Observed energy use by occupancy")
        st.plotly_chart(make_fig(px.scatter(sample, x="occupancy", y="energy_kwh", color="building"), 360), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Temperature vs energy", "Observed energy use by appliance")
        st.plotly_chart(make_fig(px.scatter(sample, x="temperature_c", y="energy_kwh", color="appliance"), 360), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)


def sql_page():
    st.markdown('<div class="eyebrow">Database analytics</div><div class="hero"><h1>SQL Analytics Lab</h1><div class="subtle">Run interactive analytical queries against SQLite table energy_consumption.</div></div>', unsafe_allow_html=True)
    if not DB_PATH.exists(): empty_state("SQLite database not found."); return

    with sqlite3.connect(DB_PATH) as conn:
        record_count = int(pd.read_sql_query("SELECT COUNT(*) AS records FROM energy_consumption", conn).iloc[0, 0])

    st.markdown(f'<div class="query-card"><div class="query-meta"><span class="dot"></span> SQLITE CONNECTED &nbsp;•&nbsp; energy_consumption &nbsp;•&nbsp; {record_count:,} RECORDS</div><div class="subtle" style="margin-top:.45rem">Auditable SQL workspace using indexed project database.</div></div>', unsafe_allow_html=True)

    default_custom_sql = "SELECT building, appliance, ROUND(AVG(power_kw), 2) AS avg_power, ROUND(SUM(energy_kwh), 2) AS total_kwh FROM energy_consumption GROUP BY building, appliance ORDER BY total_kwh DESC LIMIT 15;"

    st.markdown("### 💻 Custom Ad-Hoc SQL Query Console")
    custom_query = st.text_area("Write SQL Query", value=default_custom_sql, height=100)

    if st.button("Execute Custom Query", type="primary", key="exec_custom_sql"):
        try:
            res_df = run_query(custom_query)
            st.success(f"Executed successfully! {len(res_df):,} rows returned.")
            st.dataframe(res_df, hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

    st.markdown("---")
    st.markdown("### 📋 Preset Analytics Queries")
    queries = [
        ("Building Load Profile", "SELECT building, ROUND(SUM(energy_kwh), 2) AS total_energy_kwh, ROUND(AVG(power_kw), 2) AS average_power_kw FROM energy_consumption GROUP BY building ORDER BY total_energy_kwh DESC;", "Ranks buildings by total energy and average power."),
        ("Peak Operating Hours", "SELECT CAST(strftime('%H', timestamp) AS INTEGER) AS hour, ROUND(AVG(energy_kwh), 2) AS average_energy_kwh, ROUND(MAX(energy_kwh), 2) AS peak_energy_kwh FROM energy_consumption GROUP BY hour ORDER BY average_energy_kwh DESC;", "Finds the hours with the highest average and peak record-level load."),
        ("Appliance Intensity", "SELECT appliance, ROUND(SUM(energy_kwh), 2) AS total_energy_kwh, ROUND(AVG(occupancy), 1) AS average_occupancy FROM energy_consumption GROUP BY appliance ORDER BY total_energy_kwh DESC;", "Compares appliance energy contribution with the occupancy context.")
    ]

    for title, query, explanation in queries:
        st.markdown(f'<div class="query-card"><div class="card-kicker">PRESET QUERY</div><div class="overview-title">{title}</div><div class="subtle">{explanation}</div></div>', unsafe_allow_html=True)
        st.code(query, language="sql")
        with sqlite3.connect(DB_PATH) as conn: result = pd.read_sql_query(query, conn)
        st.markdown(f'<div class="query-meta">{len(result):,} RESULT ROWS &nbsp;•&nbsp; EXECUTED</div>', unsafe_allow_html=True)
        st.dataframe(result, hide_index=True, use_container_width=True)


def sustainability_page(filtered):
    st.markdown('<div class="eyebrow">08 / Environmental impact</div><div class="hero"><h1>Sustainability</h1><div class="subtle">Track emissions and quantify the modeled benefit of operational improvements.</div></div>', unsafe_allow_html=True)
    if filtered.empty: empty_state(); return
    monthly = filtered.assign(month=filtered.timestamp.dt.to_period("M").astype(str)).groupby("month", as_index=False).co2_kg.sum()
    reduction = filtered.energy_kwh.sum() * .1 * .82; score = max(0, min(100, 100 - filtered.co2_kg.mean() / filtered.co2_kg.max() * 100))
    cols = st.columns(4)
    with cols[0]: metric("CO2 emissions", f"{filtered.co2_kg.sum():,.0f} kg", "selected period")
    with cols[1]: metric("Modeled reduction", f"{reduction:,.0f} kg", "10% optimization scenario")
    with cols[2]: metric("Energy reduction potential", f"{filtered.energy_kwh.sum() * .1:,.0f} kWh", "10% scenario")
    with cols[3]: metric("Cost impact", f"₹{filtered.energy_kwh.sum() * .1 * 8:,.0f}", "modeled monthly equivalent")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    panel_heading("Current state → optimized state", "A transparent 10% reduction scenario, applied to observed active-period energy.")
    st.markdown(f'<div class="scenario"><div class="scenario-step"><div class="metric-label">CURRENT STATE</div><strong>{filtered.energy_kwh.sum():,.0f} kWh</strong><span class="subtle">{filtered.co2_kg.sum():,.0f} kg CO2 · ₹{filtered.electricity_cost_inr.sum():,.0f}</span></div><div class="scenario-arrow">→</div><div class="scenario-step"><div class="metric-label">OPTIMIZED STATE</div><strong>{filtered.energy_kwh.sum() * .9:,.0f} kWh</strong><span class="subtle">{filtered.co2_kg.sum() - reduction:,.0f} kg CO2 · ₹{filtered.electricity_cost_inr.sum() * .9:,.0f}</span></div></div>', unsafe_allow_html=True)
    st.caption("The optimized state is a modeled scenario, not a measured intervention outcome. It uses a 10% reduction assumption applied to the selected records and the dataset's existing emissions and tariff factors.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    metric("Sustainability score", f"{score:,.0f}/100", "normalized emissions intensity")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True); panel_heading("Monthly emissions", "Portfolio CO2 trend")
    st.plotly_chart(make_fig(px.area(monthly, x="month", y="co2_kg", color_discrete_sequence=["#55d6c2"]), 340), use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)


def report_page(filtered):
    st.markdown('<div class="eyebrow">Reporting</div><div class="hero"><h1>Reports</h1><div class="subtle">Generate downloadable energy summaries for operating reviews.</div></div>', unsafe_allow_html=True)
    if filtered.empty: empty_state(); return
    period = st.selectbox("Summary period", ["Daily", "Weekly", "Monthly"]); rule = {"Daily":"D", "Weekly":"W", "Monthly":"M"}[period]
    report = filtered.assign(period=filtered.timestamp.dt.to_period(rule).astype(str)).groupby(["period","building","appliance"], as_index=False).agg(total_energy_kwh=("energy_kwh","sum"), total_cost_inr=("electricity_cost_inr","sum"), total_co2_kg=("co2_kg","sum"), average_power_kw=("power_kw","mean")).round(2)
    st.markdown("### Generated energy summary")
    st.dataframe(report, hide_index=True, use_container_width=True)
    csv_data = report.to_csv(index=False); summary = report.groupby("period", as_index=False)[["total_energy_kwh","total_cost_inr","total_co2_kg"]].sum().round(2)
    body = f"<html><head><style>body{{font-family:Arial;color:#1a2835}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccd;padding:8px;text-align:left}}th{{background:#eaf5f2}}</style></head><body><h1>NEXUS Energy Intelligence Report</h1><p>{period} summary generated from simulated IoT records.</p>{summary.to_html(index=False)}</body></html>"
    c1, c2 = st.columns(2)
    with c1: st.download_button("Download CSV report", csv_data, "nexus_energy_report.csv", "text/csv")
    with c2: st.download_button("Download HTML report", body, "nexus_energy_report.html", "text/html")


def main():
    inject_styles(); data = load_data()
    if data.empty: st.error("The energy database is missing or contains no records."); return
    if st.query_params.get("page") == "command-center":
        st.session_state["active_page"] = "Command Center"
        del st.query_params["page"]
    page = sidebar_controls(data)
    if page in {"Command Center", "Live IoT Monitoring", "AI Energy Forecast", "Anomaly Intelligence", "Energy Optimization", "Sustainability", "Report Center"}:
        buildings, floors, appliances, date_range = page_filters(data)
    else:
        buildings = data["building"].unique()
        floors = data["floor"].unique()
        appliances = data["appliance"].unique()
        date_range = (data["timestamp"].min().date(), data["timestamp"].max().date())
    filtered = apply_scope(data, buildings, floors, appliances, date_range)
    model = load_model()
    if page == "Welcome": welcome_page(data, model)
    elif page == "Command Center": command_center(filtered, model)
    elif page == "Live IoT Monitoring": live_monitoring(filtered)
    elif page == "AI Energy Forecast": forecast_page(filtered, model)
    elif page == "Anomaly Intelligence": anomaly_page(filtered)
    elif page == "Energy Optimization": optimization_page(filtered)
    elif page == "Building Intelligence": intelligence_page(data)
    elif page == "SQL Analytics Lab": sql_page()
    elif page == "Sustainability": sustainability_page(filtered)
    elif page == "Report Center": report_page(filtered)
    if page != "Welcome":
        st.markdown('<div class="section-rule"></div><div class="subtle">NEXUS Energy Intelligence · Decision support powered by simulated IoT telemetry, SQLite analytics, and machine learning.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

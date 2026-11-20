# ============================================================
# VIALINK · Sidebar con ancho nativo (sin conflicto de animación)
# ============================================================

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import polyline
import time
import json
from openai import OpenAI
import base64
from pathlib import Path

def cargar_logo_base64(ruta="assets/logo.png"):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

LOGO_B64 = cargar_logo_base64()

st.set_page_config(
    page_title="Vialink · Rutas de Apodaca",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "tipo_transporte" not in st.session_state:
    st.session_state.tipo_transporte = "Todos"

TIPO_COLORES = {
    "Todos":      {"bg": "#F2F6FC", "primary": "#0866E9", "accent": "#DBEAFE"},
    "Camión":     {"bg": "#F0FDF4", "primary": "#15803D", "accent": "#DCFCE7"},
    "Metro":      {"bg": "#EFF6FF", "primary": "#1D4ED8", "accent": "#DBEAFE"},
    "Transmetro": {"bg": "#FEF2F2", "primary": "#DC2626", "accent": "#FEE2E2"},
}

_color = TIPO_COLORES[st.session_state.tipo_transporte]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: {_color['bg']} !important; transition: background 0.4s ease; }}
#MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; height: 0; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stHeader"] {{ background: transparent; height: 0; }}

/* ============================================================
   BOTONES NATIVOS DE STREAMLIT (solo tamaño, sin position)
   ============================================================ */
[data-testid="stSidebarCollapsedControl"] button {{
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    min-height: 44px !important;
    background: {_color['primary']} !important;
    color: #FFFFFF !important;
    border: 2px solid #FFFFFF !important;
    border-radius: 10px !important;
    box-shadow: 0 3px 12px rgba(8,102,233,0.4) !important;
}}
[data-testid="stSidebarCollapsedControl"] button svg {{
    color: #FFFFFF !important;
}}

[data-testid="stSidebarCollapseButton"] button {{
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    background: #FFFFFF !important;
    color: {_color['primary']} !important;
    border: 2px solid {_color['primary']} !important;
    border-radius: 50% !important;
}}
[data-testid="stSidebarCollapseButton"] button svg {{
    color: {_color['primary']} !important;
}}
[data-testid="stSidebarCollapseButton"] button:hover {{
    background: {_color['primary']} !important;
}}
[data-testid="stSidebarCollapseButton"] button:hover svg {{
    color: #FFFFFF !important;
}}

/* ============================================================
   SIDEBAR — SOLO COLOR DE FONDO, SIN ANCHO FORZADO
   Streamlit maneja el ancho y la animación nativamente
   ============================================================ */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarUserContent"] {{
    background-color: #071B49 !important;
    background-image: none !important;
}}
[data-testid="stSidebar"] * {{ color: #E6EDFF !important; }}

.sidebar-brand {{
    display: flex; flex-direction: column; align-items: flex-start;
    gap: 10px; padding: 16px 8px 22px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 18px;
}}
.sidebar-brand .logo {{
    width: 90px; height: 90px;
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; background: transparent;
}}
.sidebar-brand h1 {{
    margin: 8px 0 0 0 !important;
    font-size: 32px !important; font-weight: 800 !important;
    color: #FFFFFF !important; letter-spacing: -1px !important;
    line-height: 1 !important;
}}
.sidebar-brand p {{
    margin: 4px 0 0 0 !important; font-size: 13px !important;
    color: #8FA4CC !important; font-weight: 500 !important;
}}

.tipo-selector-label {{
    font-size: 12px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #8FA4CC !important;
    margin: 4px 0 8px 4px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] > label {{ display: none; }}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {{
    background: rgba(255,255,255,0.05);
    padding: 6px; border-radius: 12px; gap: 4px;
    display: flex; flex-direction: column;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {{
    padding: 10px 14px !important; border-radius: 8px !important;
    transition: all 0.2s ease;
    font-weight: 500 !important; font-size: 14px !important;
    color: #B8C5E0 !important; cursor: pointer;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.08);
}}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
    background: {_color['primary']} !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}}
[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) * {{
    color: #FFFFFF !important;
}}

[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stButton"] > button {{
    width: 100% !important;
    background: transparent !important;
    color: #B8C5E0 !important;
    border: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    transition: all 0.2s ease;
    box-shadow: none !important;
    margin: 2px 0 !important;
}}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {{
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {{
    background: {_color['primary']} !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(8, 102, 233, 0.4) !important;
}}

/* ============================================================
   HERO BANNER
   ============================================================ */
.hero-banner {{
    position: relative;
    background:
        linear-gradient(115deg, rgba(7,27,73,0.92) 0%, {_color['primary']}C7 100%),
        url('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1800&q=80') center/cover;
    border-radius: 22px;
    padding: 48px 42px;
    color: #FFFFFF;
    margin-bottom: 26px;
    overflow: hidden;
    box-shadow: 0 20px 40px -20px rgba(7,27,73,0.5);
    transition: background 0.4s ease;
    min-height: 140px;
}}
.hero-banner::before {{
    content: '';
    position: absolute; right: -80px; top: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, {_color['primary']}99, transparent 70%);
    border-radius: 50%;
}}
.hero-banner h1 {{ font-size: 34px; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.5px; color: #FFFFFF; }}
.hero-banner p  {{ font-size: 16px; margin: 0; color: #D5E1FF; }}

.vl-card {{
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 4px 20px -8px rgba(7, 27, 73, 0.12);
    border: 1px solid #E6EDFF;
    margin-bottom: 16px;
    min-height: 60px;
}}
.vl-card h4 {{
    margin: 0 0 12px 0; font-size: 14px; font-weight: 700;
    color: #071B49; display: flex; align-items: center; gap: 8px;
    text-transform: uppercase; letter-spacing: 0.4px;
}}
.vl-card h3 {{ margin: 0 0 6px 0; font-size: 19px; font-weight: 700; color: #071B49; }}
.vl-card p  {{ margin: 4px 0; color: #4A5A78; font-size: 14px; }}
.vl-card .label {{ font-size: 11px; color: #8A97B0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
.vl-card .value {{ font-size: 22px; font-weight: 700; color: #071B49; margin-top: 2px; }}

.vl-pill {{
    display: inline-block; background: {_color['accent']}; color: {_color['primary']};
    padding: 5px 12px; border-radius: 100px;
    font-size: 12px; font-weight: 600; margin: 3px 6px 3px 0;
}}
.vl-pill.green {{ background: #DCFCE7; color: #15803D; }}
.vl-pill.orange {{ background: #FFEDD5; color: #C2410C; }}
.vl-pill.blue {{ background: #DBEAFE; color: #1D4ED8; }}

.status-dot {{
    display: inline-block; width: 8px; height: 8px;
    background: #22C55E; border-radius: 50%; margin-right: 8px;
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
    animation: pulse 2s infinite;
}}
@keyframes pulse {{
    0%, 100% {{ box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2); }}
    50%      {{ box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.1); }}
}}

.topbar-loc, .topbar-prof {{
    display: flex; align-items: center; justify-content: center;
    height: 46px;
    background: #FFFFFF;
    border: 1px solid #E6EDFF;
    border-radius: 12px;
    color: #071B49; font-weight: 600; font-size: 13px; gap: 6px;
}}
.topbar-prof {{
    background: linear-gradient(135deg, {_color['primary']}, {_color['primary']}DD);
    color: #FFFFFF; border: none; width: 46px;
    font-weight: 700; font-size: 16px;
    box-shadow: 0 4px 14px {_color['primary']}4D;
}}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {{
    background: #FFFFFF !important;
    border: 1px solid #E6EDFF !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    color: #071B49 !important;
}}
[data-testid="stTextInput"] input {{ height: 46px; }}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {{
    border-color: {_color['primary']} !important;
    box-shadow: 0 0 0 3px {_color['primary']}26 !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background: #FFFFFF !important;
    border: 1px solid #E6EDFF !important;
    border-radius: 12px !important;
    color: #071B49 !important;
    min-height: 46px;
}}

.section-title {{ font-size: 22px; font-weight: 800; color: #071B49; margin: 6px 0 14px 0; letter-spacing: -0.3px; }}

.chat-bubble-user {{
    background: {_color['primary']}; color: white;
    padding: 12px 16px; border-radius: 16px 16px 4px 16px;
    margin: 8px 0 8px auto; max-width: 78%; font-size: 14px;
    box-shadow: 0 4px 14px {_color['primary']}4D;
}}
.chat-bubble-ai {{
    background: #FFFFFF; color: #071B49;
    padding: 12px 16px; border-radius: 16px 16px 16px 4px;
    margin: 8px auto 8px 0; max-width: 78%;
    border: 1px solid #E6EDFF; font-size: 14px;
}}

.notif-item {{
    background: #FFFFFF;
    border-left: 4px solid {_color['primary']};
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px -4px rgba(7,27,73,0.1);
}}
.notif-item.warning {{ border-left-color: #F59E0B; }}
.notif-item.info    {{ border-left-color: {_color['primary']}; }}
.notif-item h5 {{ margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: #071B49; }}
.notif-item p  {{ margin: 0; font-size: 13px; color: #4A5A78; }}
.notif-item .meta {{ font-size: 11px; color: #8A97B0; margin-top: 6px; }}

.stButton > button[kind="primary"] {{
    background: {_color['primary']} !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border: none !important;
    box-shadow: 0 4px 14px {_color['primary']}4D !important;
}}

.tipo-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 8px 14px; border-radius: 100px;
    background: {_color['accent']}; color: {_color['primary']};
    font-weight: 700; font-size: 13px;
}}

/* ============================================================
   MÓVIL
   ============================================================ */
@media (max-width: 768px) {{
    [data-testid="stHorizontalBlock"] {{ flex-direction: column !important; gap: 0 !important; }}
    [data-testid="stHorizontalBlock"] > [data-testid="column"],
    [data-testid="column"] {{
        width: 100% !important; flex: 1 1 100% !important;
        min-width: 100% !important; margin-bottom: 8px !important;
    }}

    .sidebar-brand {{ padding: 12px 6px 16px 6px; gap: 8px; }}
    .sidebar-brand .logo {{ width: 60px !important; height: 60px !important; border-radius: 12px; }}
    .sidebar-brand h1 {{ font-size: 26px !important; }}
    .sidebar-brand p {{ font-size: 12px !important; }}

    .hero-banner {{
        padding: 24px 20px !important;
        border-radius: 16px !important;
        margin-bottom: 16px !important;
        min-height: 100px !important;
    }}
    .hero-banner h1 {{ font-size: 22px !important; line-height: 1.2 !important; }}
    .hero-banner p  {{ font-size: 13px !important; }}
    .hero-banner::before {{ width: 200px; height: 200px; right: -60px; top: -60px; }}

    .vl-card {{ padding: 14px 16px !important; border-radius: 14px !important; margin-bottom: 12px !important; min-height: 56px !important; }}
    .vl-card h4 {{ font-size: 12px !important; margin-bottom: 8px !important; }}
    .vl-card h3 {{ font-size: 16px !important; }}
    .vl-card p  {{ font-size: 13px !important; }}
    .vl-card .value {{ font-size: 18px !important; }}
    .vl-card .label {{ font-size: 10px !important; }}

    .section-title {{ font-size: 18px !important; margin: 4px 0 10px !important; }}

    .topbar-loc, .topbar-prof {{ height: 40px !important; font-size: 12px !important; }}
    .topbar-prof {{ width: 40px !important; font-size: 14px !important; }}
    .tipo-badge {{ padding: 6px 10px !important; font-size: 12px !important; }}

    .vl-pill {{ font-size: 11px !important; padding: 4px 10px !important; }}

    .chat-bubble-user, .chat-bubble-ai {{ max-width: 90% !important; font-size: 13px !important; }}

    [data-testid="stTextInput"] input {{ font-size: 16px !important; height: 44px !important; }}
    [data-testid="stSelectbox"] > div > div {{ font-size: 15px !important; min-height: 44px !important; }}

    .stButton > button {{ min-height: 44px !important; font-size: 14px !important; padding: 10px 14px !important; }}

    .main .block-container,
    [data-testid="stAppViewContainer"] > .main > div {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }}

    [data-testid="stTabs"] [data-baseweb="tab"] {{
        padding: 10px 14px !important; font-size: 14px !important;
    }}

    [data-testid="stAppViewContainer"] {{ overflow-x: hidden !important; }}
    * {{ max-width: 100vw; box-sizing: border-box; }}
}}

@media (max-width: 400px) {{
    .hero-banner h1 {{ font-size: 19px !important; }}
    .hero-banner {{ padding: 20px 16px !important; }}
    .vl-card {{ padding: 12px 14px !important; }}
    .sidebar-brand h1 {{ font-size: 22px !important; }}
    .sidebar-brand .logo {{ width: 50px !important; height: 50px !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS
# ============================================================
RUTAS = {
    "1 · Directa Pilares Andalucía UTE": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Pilares", "lat": 25.81018, "lon": -100.25840},
            {"nombre": "Andalucía", "lat": 25.780, "lon": -100.220},
            {"nombre": "Apodaca Centro", "lat": 25.78027, "lon": -100.18790},
            {"nombre": "UTE", "lat": 25.750, "lon": -100.200},
        ],
        "municipios": "Apodaca", "horario": "05:00 - 23:00",
        "frecuencia": "10-15 min", "longitud": "≈ 35 km", "duracion": "≈ 80 min", "tipo": "Directa",
    },
    "41 · Directa Colinas Hospital Metropolitano": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Colinas", "lat": 25.790, "lon": -100.210},
            {"nombre": "Hospital Metropolitano", "lat": 25.73076, "lon": -100.19908},
        ],
        "municipios": "Apodaca, San Nicolás", "horario": "05:00 - 23:00",
        "frecuencia": "10 min", "longitud": "≈ 20 km", "duracion": "≈ 50 min", "tipo": "Directa",
    },
    "105 · Alimentadora San Martín Metropolitano": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "San Martín", "lat": 25.750, "lon": -100.210},
            {"nombre": "Hospital Metropolitano", "lat": 25.73076, "lon": -100.19908},
        ],
        "municipios": "Apodaca, San Nicolás", "horario": "05:00 - 23:00",
        "frecuencia": "10 min", "longitud": "≈ 12 km", "duracion": "≈ 35 min", "tipo": "Alimentadora",
    },
    "109 · Alimentadora Aeropuerto Exposición": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Aeropuerto", "lat": 25.778, "lon": -100.106},
            {"nombre": "Exposición", "lat": 25.670, "lon": -100.330},
        ],
        "municipios": "Apodaca, Monterrey", "horario": "05:00 - 23:00",
        "frecuencia": "15 min", "longitud": "≈ 25 km", "duracion": "≈ 60 min", "tipo": "Alimentadora",
    },
    "160 · Remanente Guadalupe Apodaca": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Guadalupe", "lat": 25.680, "lon": -100.250},
            {"nombre": "Apodaca Centro", "lat": 25.78027, "lon": -100.18790},
        ],
        "municipios": "Guadalupe, Apodaca", "horario": "05:00 - 23:00",
        "frecuencia": "10 min", "longitud": "≈ 22 km", "duracion": "≈ 55 min", "tipo": "Remanente",
    },
    "213 · Directa Soriana Sendero Capellanía": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Soriana Sendero", "lat": 25.76331, "lon": -100.19122},
            {"nombre": "Capellanía", "lat": 25.750, "lon": -100.185},
        ],
        "municipios": "Apodaca", "horario": "05:00 - 23:00",
        "frecuencia": "10 min", "longitud": "≈ 8 km", "duracion": "≈ 25 min", "tipo": "Directa",
    },
    "219 · Remanente Provivienda": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Provivienda", "lat": 25.700, "lon": -100.215},
            {"nombre": "Tréboles", "lat": 25.760, "lon": -100.205},
        ],
        "municipios": "Apodaca, Guadalupe", "horario": "05:00 - 22:00",
        "frecuencia": "8-12 min", "longitud": "≈ 28 km", "duracion": "≈ 75 min", "tipo": "Remanente",
    },
    "527 · Troncal Vistas del Río Apodaca": {
        "color": "#22c55e",
        "paradas": [
            {"nombre": "Vistas del Río", "lat": 25.700, "lon": -100.250},
            {"nombre": "Monumento", "lat": 25.720, "lon": -100.230},
            {"nombre": "Apodaca Centro", "lat": 25.78027, "lon": -100.18790},
        ],
        "municipios": "Apodaca, Juárez", "horario": "05:00 - 23:00",
        "frecuencia": "10 min", "longitud": "≈ 30 km", "duracion": "≈ 80 min", "tipo": "Troncal",
    },
}

METRO = {
    "Línea 1 · Talleres / San Bernabé": {
        "color": "#1D4ED8",
        "estaciones": [
            {"nombre": "Talleres", "lat": 25.750, "lon": -100.350},
            {"nombre": "San Nicolás", "lat": 25.735, "lon": -100.320},
            {"nombre": "Sendero", "lat": 25.720, "lon": -100.290},
            {"nombre": "Universidad", "lat": 25.710, "lon": -100.280},
            {"nombre": "Cuauhtémoc", "lat": 25.690, "lon": -100.310},
            {"nombre": "Padre Mier", "lat": 25.680, "lon": -100.315},
            {"nombre": "Zaragoza", "lat": 25.675, "lon": -100.320},
            {"nombre": "Exposición", "lat": 25.670, "lon": -100.330},
            {"nombre": "San Bernabé", "lat": 25.665, "lon": -100.350},
        ],
        "conexion_apodaca": "Conecta con rutas de Apodaca en Sendero y San Nicolás.",
    },
    "Línea 2 · Sendero / Gral. I. Zaragoza": {
        "color": "#1D4ED8",
        "estaciones": [
            {"nombre": "Sendero", "lat": 25.720, "lon": -100.290},
            {"nombre": "San Nicolás", "lat": 25.735, "lon": -100.320},
            {"nombre": "Universidad", "lat": 25.710, "lon": -100.280},
            {"nombre": "Padre Mier", "lat": 25.680, "lon": -100.315},
            {"nombre": "Zaragoza", "lat": 25.675, "lon": -100.320},
            {"nombre": "Gral. I. Zaragoza", "lat": 25.660, "lon": -100.340},
        ],
        "conexion_apodaca": "Conecta con rutas de Apodaca en Sendero y San Nicolás.",
    },
    "Línea 3 · Hospital / Hospital Metropolitano": {
        "color": "#1D4ED8",
        "estaciones": [
            {"nombre": "Hospital", "lat": 25.685, "lon": -100.305},
            {"nombre": "Hospital Metropolitano (Apodaca)", "lat": 25.715, "lon": -100.210},
        ],
        "conexion_apodaca": "Llega directo a Apodaca en la estación Hospital Metropolitano.",
    },
}

TRANSMETRO = {
    "Transmetro L1 · Talleres - Centro": {
        "color": "#DC2626",
        "paradas": [
            {"nombre": "Talleres", "lat": 25.750, "lon": -100.350},
            {"nombre": "San Nicolás", "lat": 25.735, "lon": -100.320},
            {"nombre": "Sendero", "lat": 25.720, "lon": -100.290},
            {"nombre": "Universidad", "lat": 25.710, "lon": -100.280},
            {"nombre": "Cuauhtémoc", "lat": 25.690, "lon": -100.310},
            {"nombre": "Padre Mier", "lat": 25.680, "lon": -100.315},
        ],
        "municipios": "Monterrey, San Nicolás",
        "horario": "05:00 - 23:00", "frecuencia": "8 min",
        "longitud": "≈ 20 km", "duracion": "≈ 45 min", "tipo": "Transmetro",
    },
    "Transmetro L2 · Lincoln - Centro": {
        "color": "#DC2626",
        "paradas": [
            {"nombre": "Lincoln", "lat": 25.735, "lon": -100.280},
            {"nombre": "Ruiz Cortines", "lat": 25.720, "lon": -100.300},
            {"nombre": "Universidad", "lat": 25.710, "lon": -100.280},
            {"nombre": "Padre Mier", "lat": 25.680, "lon": -100.315},
        ],
        "municipios": "Monterrey, San Nicolás",
        "horario": "05:00 - 23:00", "frecuencia": "10 min",
        "longitud": "≈ 18 km", "duracion": "≈ 40 min", "tipo": "Transmetro",
    },
    "Transmetro L3 · Hospital Metropolitano - Centro": {
        "color": "#DC2626",
        "paradas": [
            {"nombre": "Hospital Metropolitano", "lat": 25.73076, "lon": -100.19908},
            {"nombre": "Apodaca Centro", "lat": 25.78027, "lon": -100.18790},
            {"nombre": "Sendero", "lat": 25.720, "lon": -100.290},
            {"nombre": "Padre Mier", "lat": 25.680, "lon": -100.315},
        ],
        "municipios": "Apodaca, Monterrey",
        "horario": "05:00 - 23:00", "frecuencia": "12 min",
        "longitud": "≈ 25 km", "duracion": "≈ 55 min", "tipo": "Transmetro",
    },
}

# ============================================================
# HELPERS
# ============================================================
def catalogo_por_tipo(tipo):
    if tipo == "Camión": return dict(RUTAS)
    if tipo == "Metro": return dict(METRO)
    if tipo == "Transmetro": return dict(TRANSMETRO)
    return {**RUTAS, **TRANSMETRO, **METRO}

def get_ruta_info(nombre):
    if nombre in METRO:
        m = METRO[nombre]
        return {
            "color": m["color"], "paradas": m.get("estaciones", []),
            "municipios": "Monterrey y área metropolitana",
            "horario": "05:00 - 23:30", "frecuencia": "5-10 min",
            "longitud": "—", "duracion": "—", "tipo": "Metro", "es_metro": True,
        }
    if nombre in TRANSMETRO: return {**TRANSMETRO[nombre], "es_metro": False}
    if nombre in RUTAS: return {**RUTAS[nombre], "es_metro": False}
    return None

def primer_nombre(tipo):
    cat = catalogo_por_tipo(tipo)
    return list(cat.keys())[0] if cat else None

@st.cache_data(show_spinner=False)
def obtener_ruta_por_calles(paradas_tuple):
    coordenadas_osrm = ";".join([f"{lon},{lat}" for lat, lon in paradas_tuple])
    url = f"http://router.project-osrm.org/route/v1/driving/{coordenadas_osrm}?overview=full&geometries=polyline"
    for intento in range(2):
        try:
            respuesta = requests.get(url, timeout=15)
            respuesta.raise_for_status()
            datos = respuesta.json()
            if datos.get("code") == "Ok" and datos.get("routes"):
                return polyline.decode(datos["routes"][0]["geometry"])
        except Exception:
            if intento == 1: return None
            time.sleep(1)
    return None

def crear_mapa_base(zoom=12, centro=(25.740, -100.220)):
    return folium.Map(location=list(centro), zoom_start=zoom, tiles="OpenStreetMap")

def agregar_ruta_al_mapa(mapa, nombre_ruta, datos):
    paradas_tuple = tuple((p["lat"], p["lon"]) for p in datos["paradas"])
    ruta_real = obtener_ruta_por_calles(paradas_tuple)
    if ruta_real:
        folium.PolyLine(locations=ruta_real, color=datos["color"], weight=5, opacity=0.85,
                        tooltip=f"Ruta: {nombre_ruta}").add_to(mapa)
    else:
        coords = [(p["lat"], p["lon"]) for p in datos["paradas"]]
        folium.PolyLine(locations=coords, color=datos["color"], weight=4, opacity=0.7,
                        dash_array="8 6", tooltip=f"Ruta aprox: {nombre_ruta}").add_to(mapa)
    for i, parada in enumerate(datos["paradas"]):
        color_marcador = "green" if i == 0 else ("red" if i == len(datos["paradas"]) - 1 else "blue")
        folium.CircleMarker(
            location=[parada["lat"], parada["lon"]], radius=8,
            color=datos["color"], fill=True, fill_color=color_marcador, fill_opacity=1,
            popup=folium.Popup(f"<b>{parada['nombre']}</b><br>Ruta: {nombre_ruta}", max_width=250),
            tooltip=parada["nombre"],
        ).add_to(mapa)

def agregar_metro_al_mapa(mapa, nombre_linea, datos):
    coords = [(e["lat"], e["lon"]) for e in datos["estaciones"]]
    if len(coords) < 2: return
    folium.PolyLine(locations=coords, color=datos["color"], weight=6, opacity=0.9,
                    dash_array="10 5", tooltip=f"Metro: {nombre_linea}").add_to(mapa)
    for est in datos["estaciones"]:
        folium.Marker(
            location=[est["lat"], est["lon"]],
            icon=folium.Icon(color="blue", icon="subway", prefix="fa"),
            popup=folium.Popup(f"<b>{est['nombre']}</b><br>{nombre_linea}", max_width=250),
            tooltip=est["nombre"],
        ).add_to(mapa)

def dibujar_ruta_generica(mapa, nombre):
    if nombre in METRO: agregar_metro_al_mapa(mapa, nombre, METRO[nombre])
    elif nombre in TRANSMETRO: agregar_ruta_al_mapa(mapa, nombre, TRANSMETRO[nombre])
    elif nombre in RUTAS: agregar_ruta_al_mapa(mapa, nombre, RUTAS[nombre])

def buscar_ruta_por_nombre(nombre_ruta: str) -> str:
    resultados = []
    for nombre, d in {**RUTAS, **TRANSMETRO}.items():
        if nombre_ruta.lower() in nombre.lower():
            resultados.append(f"**{nombre}**\n- Municipios: {d['municipios']}\n- Horario: {d['horario']}\n- Frecuencia: {d['frecuencia']}\n- Paradas: {', '.join(p['nombre'] for p in d['paradas'])}")
    return "\n\n".join(resultados) if resultados else "No encontré rutas con ese nombre."

def buscar_ruta_por_parada(parada: str) -> str:
    resultados = []
    for nombre, d in {**RUTAS, **TRANSMETRO}.items():
        coinciden = [p["nombre"] for p in d["paradas"] if parada.lower() in p["nombre"].lower()]
        if coinciden:
            resultados.append(f"**{nombre}** pasa por: {', '.join(coinciden)}")
    return "\n".join(resultados) if resultados else "No encontré rutas que pasen por esa parada."

def obtener_info_metro(linea: str) -> str:
    resultados = [
        f"**{nombre}**\n- Estaciones: {', '.join(e['nombre'] for e in d['estaciones'])}\n- Conexión Apodaca: {d['conexion_apodaca']}"
        for nombre, d in METRO.items() if linea.lower() in nombre.lower()
    ]
    return "\n\n".join(resultados) if resultados else "No encontré esa línea del metro."

def listar_todas_rutas() -> str:
    return "\n".join(f"- [Camión] {n}" for n in RUTAS) + "\n" + "\n".join(f"- [Transmetro] {n}" for n in TRANSMETRO)

def listar_lineas_metro() -> str:
    return "\n".join(f"- {n}" for n in METRO.keys())

tools = [
    {"type": "function", "function": {"name": "buscar_ruta_por_nombre", "description": "Busca rutas por nombre.", "parameters": {"type": "object", "properties": {"nombre_ruta": {"type": "string"}}, "required": ["nombre_ruta"]}}},
    {"type": "function", "function": {"name": "buscar_ruta_por_parada", "description": "Busca rutas por parada.", "parameters": {"type": "object", "properties": {"parada": {"type": "string"}}, "required": ["parada"]}}},
    {"type": "function", "function": {"name": "obtener_info_metro", "description": "Info de una línea del Metro.", "parameters": {"type": "object", "properties": {"linea": {"type": "string"}}, "required": ["linea"]}}},
    {"type": "function", "function": {"name": "listar_todas_rutas", "description": "Lista todas las rutas.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "listar_lineas_metro", "description": "Lista líneas del Metro.", "parameters": {"type": "object", "properties": {}}}},
]

def ejecutar_herramienta(nombre, args):
    if nombre == "buscar_ruta_por_nombre": return buscar_ruta_por_nombre(args.get("nombre_ruta", ""))
    if nombre == "buscar_ruta_por_parada": return buscar_ruta_por_parada(args.get("parada", ""))
    if nombre == "obtener_info_metro":    return obtener_info_metro(args.get("linea", ""))
    if nombre == "listar_todas_rutas":    return listar_todas_rutas()
    if nombre == "listar_lineas_metro":   return listar_lineas_metro()
    return "Función no reconocida."

def get_metro_connections(route_data):
    found = []
    for nombre_linea, datos in METRO.items():
        for est in datos["estaciones"]:
            for parada in route_data.get("paradas", []):
                if est["nombre"].split(" (")[0].lower() in parada["nombre"].lower():
                    found.append((nombre_linea, est["nombre"]))
    return list({f"{l} · {e}" for l, e in found})

def get_nearby_routes(route_name, route_data):
    propias = {p["nombre"] for p in route_data.get("paradas", [])}
    nearby = []
    for nombre, d in {**RUTAS, **TRANSMETRO}.items():
        if nombre == route_name: continue
        if propias & {p["nombre"] for p in d["paradas"]}: nearby.append(nombre)
    return nearby[:4]

def planificar(origen, destino):
    o, d = origen.lower().strip(), destino.lower().strip()
    if not o or not d: return [], [], []
    todas = {**RUTAS, **TRANSMETRO}
    rutas_o, rutas_d = {}, {}
    for nombre, data in todas.items():
        po = next((p["nombre"] for p in data["paradas"] if o in p["nombre"].lower()), None)
        pd = next((p["nombre"] for p in data["paradas"] if d in p["nombre"].lower()), None)
        if po: rutas_o[nombre] = po
        if pd: rutas_d[nombre] = pd
    directas = list(set(rutas_o) & set(rutas_d))
    transbordos = []
    for ra in rutas_o:
        for rb in rutas_d:
            if ra == rb: continue
            shared = ({p["nombre"] for p in todas[ra]["paradas"]} & {p["nombre"] for p in todas[rb]["paradas"]})
            if shared: transbordos.append((ra, rb, list(shared)[0]))
    return directas, transbordos, list(rutas_o) + list(rutas_d)

# ============================================================
# ALERTAS COMUNITARIAS
# ============================================================
if "alertas_locales" not in st.session_state:
    st.session_state.alertas_locales = [
        {
            "autor": "Sistema Vialink", "tipo": "Otro", "ruta": "General",
            "mensaje": "Bienvenido al foro comunitario. Aquí puedes reportar retrasos, cambios de recorrido o cualquier aviso útil.",
            "severidad": "Baja", "created_at": time.strftime("%Y-%m-%d %H:%M"),
        }
    ]

def publicar_alerta(autor, tipo, ruta, mensaje, severidad):
    alerta = {
        "autor": autor, "tipo": tipo, "ruta": ruta,
        "mensaje": mensaje, "severidad": severidad,
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.alertas_locales.insert(0, alerta)
    return True

# ============================================================
# SESSION STATE
# ============================================================
if "current_view" not in st.session_state:
    st.session_state.current_view = "Inicio"
if "selected_route" not in st.session_state:
    st.session_state.selected_route = primer_nombre(st.session_state.tipo_transporte)
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{
        "role": "system",
        "content": (
            "Eres Vialink IA, un asistente experto en transporte público de la Zona Metropolitana de Monterrey. "
            "Puedes consultar rutas de camión, líneas de Transmetro y líneas de Metro. "
            "Usa SIEMPRE las herramientas disponibles antes de responder."
        ),
    }]

# ============================================================
# CALLBACKS
# ============================================================
def _cambiar_tipo():
    nuevo = st.session_state.tipo_selector
    st.session_state.tipo_transporte = nuevo
    st.session_state.selected_route = primer_nombre(nuevo)

def _cambiar_vista(nombre):
    st.session_state.current_view = nombre

def _ir_a_mapa():
    st.session_state.current_view = "Mapa en tiempo real"

def _ir_a_planificador():
    st.session_state.current_view = "Planificador de rutas"

def _seleccionar_ruta(nombre):
    st.session_state.selected_route = nombre
    st.session_state.current_view = "Mapa en tiempo real"

# ============================================================
# SIDEBAR
# ============================================================
MENU = [
    ("🏠", "Inicio"),
    ("🗺️", "Mapa en tiempo real"),
    ("📍", "Planificador de rutas"),
    ("🚌", "Información de líneas"),
    ("🔔", "Notificaciones"),
    ("🚨", "Alertas Comunitarias"),
    ("🤖", "Asistente IA"),
    ("⚙️", "Configuración"),
]

with st.sidebar:
    if LOGO_B64:
        logo_html = f'<div class="logo"><img src="data:image/png;base64,{LOGO_B64}" style="width:100%;height:100%;object-fit:contain;border-radius:16px;"></div>'
    else:
        logo_html = f'<div class="logo" style="background: linear-gradient(135deg, {_color["primary"]}, {_color["primary"]}DD); font-size: 40px;">🚌</div>'

    st.markdown(
        f"""
        <div class="sidebar-brand">
            {logo_html}
            <h1>Vialink</h1>
            <p>Muévete mejor</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="tipo-selector-label">Tipo de transporte</div>', unsafe_allow_html=True)
    tipos = ["Todos", "Camión", "Metro", "Transmetro"]
    st.radio(
        "Tipo de transporte", tipos,
        index=tipos.index(st.session_state.tipo_transporte),
        key="tipo_selector",
        label_visibility="collapsed",
        on_change=_cambiar_tipo,
    )

    st.markdown("---")

    for icon, name in MENU:
        is_active = st.session_state.current_view == name
        st.button(
            f"{icon}   {name}", key=f"menu_{name}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
            on_click=_cambiar_vista,
            args=(name,),
        )

# ============================================================
# TOP BAR
# ============================================================
tb = st.columns([5, 1.6, 1.3, 0.7])
with tb[0]:
    top_search = st.text_input(
        "Buscar", placeholder="🔍  Buscar ruta...",
        label_visibility="collapsed", key="top_search",
    )
with tb[1]:
    st.markdown('<div class="topbar-loc">📍 Apodaca, NL</div>', unsafe_allow_html=True)
with tb[2]:
    tipo_actual = st.session_state.tipo_transporte
    iconos_tipo = {"Todos": "🌐", "Camión": "🚌", "Metro": "🚇", "Transmetro": "🚍"}
    st.markdown(f'<div class="tipo-badge">{iconos_tipo[tipo_actual]} {tipo_actual}</div>', unsafe_allow_html=True)
with tb[3]:
    st.markdown('<div class="topbar-prof">V</div>', unsafe_allow_html=True)

if top_search:
    coincidencias = [r for r in catalogo_por_tipo(st.session_state.tipo_transporte) if top_search.lower() in r.lower()]
    if coincidencias:
        st.markdown("**Sugerencias:**")
        cols_chip = st.columns(min(len(coincidencias), 4))
        for i, r in enumerate(coincidencias[:4]):
            with cols_chip[i]:
                st.button(r, key=f"chip_{i}", use_container_width=True,
                          on_click=_seleccionar_ruta, args=(r,))

# ============================================================
# VISTAS
# ============================================================
def render_inicio():
    st.markdown(
        """
        <div class="hero-banner">
            <h1>Transporte Público de Apodaca</h1>
            <p>Rutas más inteligentes, una ciudad más conectada</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cat = catalogo_por_tipo(st.session_state.tipo_transporte)
    if st.session_state.selected_route not in cat:
        st.session_state.selected_route = primer_nombre(st.session_state.tipo_transporte)

    col_left, col_center, col_right = st.columns([1.05, 2.4, 1.15], gap="medium")

    with col_left:
        st.markdown('<div class="vl-card"><h4>🎯 ¿Qué quieres hacer?</h4>', unsafe_allow_html=True)
        st.button("🗺️  Ver mapa completo", use_container_width=True, on_click=_ir_a_mapa)
        st.button("📍  Planear mi viaje", use_container_width=True, on_click=_ir_a_planificador)
        st.markdown("</div>", unsafe_allow_html=True)

        etiqueta = "Línea" if st.session_state.tipo_transporte == "Metro" else "Ruta"
        st.markdown(f'<div class="vl-card"><h4>🚏 Selecciona</h4>', unsafe_allow_html=True)
        selected = st.selectbox(
            f"{etiqueta}:", list(cat.keys()),
            index=list(cat.keys()).index(st.session_state.selected_route),
            label_visibility="collapsed",
        )
        st.session_state.selected_route = selected
        st.markdown("</div>", unsafe_allow_html=True)

        d = get_ruta_info(st.session_state.selected_route)
        st.markdown(
            f"""
            <div class="vl-card">
                <h4>📊 Información</h4>
                <div class="label">Tipo</div><div class="value" style="font-size:15px;">{d['tipo']}</div>
                <div class="label" style="margin-top:10px;">Horario</div><div class="value" style="font-size:15px;">{d['horario']}</div>
                <div class="label" style="margin-top:10px;">Frecuencia</div><div class="value">{d['frecuencia']}</div>
                <div class="label" style="margin-top:10px;">Distancia</div><div class="value">{d['longitud']}</div>
                <div class="label" style="margin-top:10px;">Duración</div><div class="value">{d['duracion']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_center:
        d = get_ruta_info(st.session_state.selected_route)
        st.markdown(
            f"""
            <div class="vl-card" style="padding:14px 18px;">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;">
                    <div style="flex:1;min-width:180px;">
                        <h3>{st.session_state.selected_route}</h3>
                        <p style="color:#4A5A78;font-size:13px;margin:2px 0;">{d['tipo']} · {d['municipios']}</p>
                    </div>
                    <div>
                        <span class="status-dot"></span>
                        <span style="font-size:12px;font-weight:600;color:#15803D;">Programado</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        mapa = crear_mapa_base(zoom=11)
        with st.spinner("Calculando recorrido..."):
            dibujar_ruta_generica(mapa, st.session_state.selected_route)
        st_folium(mapa, width=None, height=380, returned_objects=[])

    with col_right:
        d = get_ruta_info(st.session_state.selected_route)
        st.markdown(
            f"""
            <div class="vl-card">
                <h4>⏱️ Tiempo de llegada</h4>
                <p style="font-size:13px;">Sin datos en tiempo real.</p>
                <p><b>Frecuencia:</b> {d['frecuencia']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        paradas_lista = d.get("paradas", [])
        if paradas_lista:
            st.markdown(
                f"""
                <div class="vl-card">
                    <h4>📍 Recorrido</h4>
                    <p><b>Origen:</b> {paradas_lista[0]['nombre']}</p>
                    <p><b>Destino:</b> {paradas_lista[-1]['nombre']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        cercanas = get_nearby_routes(st.session_state.selected_route, d)
        html_cerc = "".join(f'<span class="vl-pill">{r.split(" · ")[0]}</span>' for r in cercanas) or '<span class="vl-pill">Sin rutas cercanas</span>'
        st.markdown(f'<div class="vl-card"><h4>🚏 Líneas cercanas</h4>{html_cerc}</div>', unsafe_allow_html=True)

        metro_conn = get_metro_connections(d)
        metro_html = "".join(f'<span class="vl-pill blue">{c}</span>' for c in metro_conn) or '<span class="vl-pill">Sin conexión</span>'
        st.markdown(f'<div class="vl-card"><h4>🚇 Conexión Metro</h4>{metro_html}</div>', unsafe_allow_html=True)

def render_mapa():
    st.markdown('<div class="section-title">🗺️ Mapa en tiempo real</div>', unsafe_allow_html=True)

    cat = catalogo_por_tipo(st.session_state.tipo_transporte)
    if st.session_state.selected_route not in cat:
        st.session_state.selected_route = primer_nombre(st.session_state.tipo_transporte)

    top = st.columns([2, 2])
    with top[0]:
        ruta_sel = st.selectbox(
            "Ruta a visualizar", list(cat.keys()),
            index=list(cat.keys()).index(st.session_state.selected_route),
        )
        st.session_state.selected_route = ruta_sel
    with top[1]:
        mostrar_metro = st.checkbox("Mostrar Metro", value=True)

    mapa = crear_mapa_base(zoom=11)
    with st.spinner("Calculando recorrido..."):
        dibujar_ruta_generica(mapa, st.session_state.selected_route)
        if mostrar_metro and st.session_state.selected_route not in METRO:
            for nombre, datos in METRO.items():
                agregar_metro_al_mapa(mapa, nombre, datos)

    d = get_ruta_info(st.session_state.selected_route)
    st.markdown(
        f"""
        <div class="vl-card" style="padding:12px 16px;">
            <span class="status-dot"></span>
            <b style="font-size:14px;color:#071B49;">{st.session_state.selected_route}</b>
            <span class="vl-pill green" style="margin-left:6px;">{d['tipo']}</span>
            <span class="vl-pill blue">Frec: {d['frecuencia']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st_folium(mapa, width=None, height=440, returned_objects=[])
    st.caption("Recorridos por calles reales vía OSRM. Sin GPS en tiempo real.")

def render_planificador():
    st.markdown('<div class="section-title">📍 Planificador de rutas</div>', unsafe_allow_html=True)
    st.caption("Escribe una calle, colonia o parada.")

    origen = st.text_input("Origen", placeholder="Ej. Asturias", key="plan_origen")
    destino = st.text_input("Destino", placeholder="Ej. Apodaca Centro", key="plan_destino")
    buscar = st.button("🔍 Buscar ruta", type="primary", use_container_width=True)

    if buscar or (origen and destino):
        if not origen or not destino:
            st.info("Escribe un origen y un destino.")
            return
        directas, transbordos, _ = planificar(origen, destino)

        if directas:
            st.markdown('<div class="section-title" style="font-size:18px;margin-top:20px;">✅ Rutas directas</div>', unsafe_allow_html=True)
            for r in directas:
                datos = get_ruta_info(r)
                st.markdown(
                    f"""
                    <div class="vl-card">
                        <h3>{r}</h3>
                        <span class="vl-pill">{datos['tipo']}</span>
                        <span class="vl-pill green">{datos['municipios']}</span>
                        <p style="margin-top:8px;">Duración: <b>{datos['duracion']}</b> · Frecuencia: <b>{datos['frecuencia']}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.button(f"Ver en el mapa", key=f"ver_{r}", use_container_width=True,
                          on_click=_seleccionar_ruta, args=(r,))

        if transbordos:
            st.markdown('<div class="section-title" style="font-size:18px;margin-top:20px;">🔄 Transbordos</div>', unsafe_allow_html=True)
            for ra, rb, punto in transbordos[:5]:
                st.markdown(
                    f"""
                    <div class="vl-card">
                        <p style="font-size:14px;">Toma <b>{ra.split(' · ')[0]}</b>, transborda en <b>{punto}</b> y continúa en <b>{rb.split(' · ')[0]}</b>.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if not directas and not transbordos:
            st.warning("No encontramos conexión. Prueba otras palabras.")

def render_lineas():
    st.markdown('<div class="section-title">🚌 Información de líneas</div>', unsafe_allow_html=True)
    tipo = st.session_state.tipo_transporte
    if tipo == "Metro": _render_tab_metro()
    elif tipo == "Camión": _render_tab_camiones()
    elif tipo == "Transmetro": _render_tab_transmetro()
    else:
        tab1, tab2, tab3 = st.tabs(["🚌 Camiones", "🚇 Metro", "🚍 Transmetro"])
        with tab1: _render_tab_camiones()
        with tab2: _render_tab_metro()
        with tab3: _render_tab_transmetro()

def _render_tab_camiones():
    for nombre, datos in RUTAS.items():
        st.markdown(
            f"""
            <div class="vl-card" style="margin-bottom:10px;">
                <h3>{nombre}</h3>
                <span class="vl-pill">{datos['tipo']}</span>
                <span class="vl-pill green">{datos['municipios']}</span>
                <p style="font-size:13px;margin-top:8px;color:#4A5A78;">
                    Frecuencia {datos['frecuencia']} · {datos['longitud']} · {datos['duracion']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Ver mapa", key=f"inf_cam_{nombre}", use_container_width=True,
                  on_click=_seleccionar_ruta, args=(nombre,))

def _render_tab_metro():
    for nombre, datos in METRO.items():
        estaciones = ", ".join(e["nombre"] for e in datos["estaciones"])
        st.markdown(
            f"""
            <div class="vl-card">
                <h3>{nombre}</h3>
                <p style="font-size:13px;color:#4A5A78;">{estaciones}</p>
                <p style="font-size:13px;margin-top:8px;"><b>Apodaca:</b> {datos['conexion_apodaca']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

def _render_tab_transmetro():
    for nombre, datos in TRANSMETRO.items():
        st.markdown(
            f"""
            <div class="vl-card" style="margin-bottom:10px;">
                <h3>{nombre}</h3>
                <span class="vl-pill">{datos['tipo']}</span>
                <span class="vl-pill green">{datos['municipios']}</span>
                <p style="font-size:13px;margin-top:8px;color:#4A5A78;">
                    Frecuencia {datos['frecuencia']} · {datos['longitud']} · {datos['duracion']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Ver mapa", key=f"inf_tm_{nombre}", use_container_width=True,
                  on_click=_seleccionar_ruta, args=(nombre,))

def render_notificaciones():
    st.markdown('<div class="section-title">🔔 Notificaciones</div>', unsafe_allow_html=True)
    st.caption("Avisos e incidencias del servicio.")
    st.markdown(
        """
        <div class="notif-item info">
            <h5>Bienvenido a Vialink</h5>
            <p>Esta sección mostrará cambios de recorrido y retrasos en tiempo real cuando estén disponibles.</p>
            <div class="meta">Sistema · Ahora</div>
        </div>
        <div class="notif-item warning">
            <h5>Sin alertas activas</h5>
            <p>No hay avisos publicados por los operadores.</p>
            <div class="meta">Operadores · Estado actual</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Suscribirme a notificaciones", type="primary", use_container_width=True):
        st.success("Te has suscrito (prototipo).")

def render_alertas():
    st.markdown('<div class="section-title">🚨 Alertas Comunitarias</div>', unsafe_allow_html=True)
    st.caption("Comparte avisos útiles para otros usuarios.")

    rutas_alerta = ["General"] + list({**RUTAS, **TRANSMETRO, **METRO}.keys())

    with st.form("form_alerta", clear_on_submit=True):
        st.markdown("#### 📢 Publicar alerta")
        autor = st.text_input("Tu nombre o alias", placeholder="Ej. Juan M.")
        ruta = st.selectbox("Ruta (opcional)", rutas_alerta)
        tipo = st.selectbox("Tipo", ["Retraso", "Cambio de recorrido", "Falla de unidad", "Otro"])
        mensaje = st.text_area("¿Qué está pasando?", placeholder="Ej. La ruta 219 no pasa por Miguel Alemán.", height=90)
        severidad = st.select_slider("Severidad", options=["Baja", "Media", "Alta"], value="Media")
        enviado = st.form_submit_button("📢 Publicar alerta", type="primary", use_container_width=True)
        if enviado:
            if not autor.strip() or not mensaje.strip():
                st.error("Escribe tu nombre y el mensaje.")
            else:
                publicar_alerta(autor.strip(), tipo, ruta, mensaje.strip(), severidad)
                st.success("¡Alerta publicada!")

    st.markdown("---")
    alertas = st.session_state.alertas_locales
    if not alertas:
        st.info("Aún no hay alertas.")
        return

    filtro = st.selectbox("Filtrar por tipo", ["Todas", "Retraso", "Cambio de recorrido", "Falla de unidad", "Otro"])
    st.markdown(f"**{len(alertas)} alertas**")

    if filtro != "Todas":
        alertas = [a for a in alertas if a.get("tipo") == filtro]

    for alerta in alertas:
        sev = alerta.get("severidad", "Media")
        colores = {"Alta": "#DC2626", "Media": "#F59E0B", "Baja": "#15803D"}
        color = colores.get(sev, "#0866E9")
        iconos = {"Retraso": "⏱️", "Cambio de recorrido": "🔄", "Falla de unidad": "🔧", "Otro": "ℹ️"}
        icono = iconos.get(alerta.get("tipo", "Otro"), "📌")
        fecha = str(alerta.get("created_at", ""))[:16].replace("T", " ")
        st.markdown(
            f"""
            <div class="vl-card" style="border-left: 4px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
                    <div style="flex:1;">
                        <h4 style="margin:0 0 6px 0; color:#071B49; font-size:14px;">
                            {icono} {alerta.get('tipo', 'Otro')} · {alerta.get('ruta') or 'General'}
                        </h4>
                        <p style="font-size:13px; color:#4A5A78; margin:6px 0;">{alerta.get('mensaje', '')}</p>
                        <p style="font-size:11px; color:#8A97B0; margin-top:8px;">
                            Por <b>{alerta.get('autor', 'Anónimo')}</b> · {fecha}
                        </p>
                    </div>
                    <span class="vl-pill" style="background:{color}20; color:{color}; white-space:nowrap;">{sev}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def render_asistente():
    st.markdown('<div class="section-title">🤖 Asistente IA</div>', unsafe_allow_html=True)
    st.caption("Pregunta sobre rutas, paradas y Metro.")

    try:
        client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    except Exception:
        st.error("⚠️ Falta la API Key de Groq en `.streamlit/secrets.toml`.")
        return

    MODELO = "openai/gpt-oss-120b"

    for msg in st.session_state.chat_messages:
        if msg["role"] == "system": continue
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant" and msg.get("content"):
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

        with st.spinner("Consultando..."):
            try:
                response = client.chat.completions.create(
                    model=MODELO, messages=st.session_state.chat_messages,
                    tools=tools, tool_choice="auto",
                )
                msg = response.choices[0].message
                while msg.tool_calls:
                    st.session_state.chat_messages.append({
                        "role": "assistant", "content": msg.content or "",
                        "tool_calls": [
                            {"id": tc.id, "type": "function",
                             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                            for tc in msg.tool_calls
                        ],
                    })
                    for tc in msg.tool_calls:
                        args = json.loads(tc.function.arguments)
                        resultado = ejecutar_herramienta(tc.function.name, args)
                        st.session_state.chat_messages.append({
                            "role": "tool", "tool_call_id": tc.id, "content": resultado,
                        })
                    response = client.chat.completions.create(model=MODELO, messages=st.session_state.chat_messages)
                    msg = response.choices[0].message
                final = msg.content or "No pude responder."
                st.session_state.chat_messages.append({"role": "assistant", "content": final})
                st.markdown(f'<div class="chat-bubble-ai">{final}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

def render_configuracion():
    st.markdown('<div class="section-title">⚙️ Configuración</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="vl-card">
            <h4>ℹ️ Acerca de Vialink</h4>
            <p>Prototipo de plataforma de movilidad para la Zona Metropolitana de Monterrey.</p>
            <p style="margin-top:8px;font-size:12px;color:#4A5A78;">
                Versión 1.9 · Sidebar con ancho nativo.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    mostrar_alertas = st.toggle("Recibir notificaciones", value=False)
    if mostrar_alertas:
        st.success("Notificaciones activadas.")
    if st.button("Borrar conversación del asistente", use_container_width=True):
        st.session_state.chat_messages = [{
            "role": "system",
            "content": "Eres Vialink IA, experto en transporte público de la Zona Metropolitana de Monterrey.",
        }]
        st.success("Conversación eliminada.")

# ============================================================
# ROUTER
# ============================================================
view = st.session_state.current_view
if view == "Inicio": render_inicio()
elif view == "Mapa en tiempo real": render_mapa()
elif view == "Planificador de rutas": render_planificador()
elif view == "Información de líneas": render_lineas()
elif view == "Notificaciones": render_notificaciones()
elif view == "Alertas Comunitarias": render_alertas()
elif view == "Asistente IA": render_asistente()
elif view == "Configuración": render_configuracion()

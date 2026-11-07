# ============================================================
# VIALINK · Aplicación de transporte público de Apodaca
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
# ============================================================
# CARGA DEL LOGO LOCAL
# ============================================================
def cargar_logo_base64(ruta="assets/logo.png"):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

LOGO_B64 = cargar_logo_base64()
# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Vialink · Rutas de Apodaca",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS GLOBAL
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #F2F6FC; }

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; height: 0; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stHeader"] { background: transparent; height: 0; }

/* ============ SIDEBAR ============ */
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarUserContent"] {
    background-color: #071B49 !important;
    background-image: none !important;
}
[data-testid="stSidebar"] * { color: #E6EDFF !important; }
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button { color: #E6EDFF !important; }

/* ANCHO: 24vw ≈ 1/4 de la pantalla */
[data-testid="stSidebar"],
section[data-testid="stSidebar"] {
    width: 24vw !important;
    min-width: 260px !important;
    max-width: 400px !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
    width: 24vw !important;
    min-width: 260px !important;
    max-width: 400px !important;
}

/* Brand Vialink */
.sidebar-brand {
    display: flex; flex-direction: column; align-items: flex-start;
    gap: 10px; padding: 20px 8px 26px 8px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 22px;
}
.sidebar-brand .logo {
    width: 250px; height: 250px;
    background: linear-gradient(135deg, #0866E9, #0A75FF);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 34px;
    box-shadow: 0 6px 22px rgba(8, 102, 233, 0.5);
}
.sidebar-brand h1 {
    margin: 8px 0 0 0 !important;
    font-size: 38px !important;
    font-weight: 800 !important;
    color: #FFFFFF !important;
    letter-spacing: -1.5px !important;
    line-height: 1 !important;
}
.sidebar-brand p {
    margin: 4px 0 0 0 !important;
    font-size: 14px !important;
    color: #8FA4CC !important;
    font-weight: 500 !important;
}

/* Botones del menú */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] [data-testid="stButton"] > button,
[data-testid="stSidebar"] button[kind="secondary"] {
    width: 100% !important;
    background: transparent !important;
    color: #B8C5E0 !important;
    border: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 12px 18px !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    transition: all 0.2s ease;
    box-shadow: none !important;
    margin: 2px 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover,
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] button[kind="primary"] {
    background: #0866E9 !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 20px rgba(8, 102, 233, 0.45) !important;
}
[data-testid="stSidebar"] button[kind="primary"]:hover {
    background: #0A75FF !important;
}

/* HERO BANNER */
.hero-banner {
    position: relative;
    background:
        linear-gradient(115deg, rgba(7,27,73,0.92) 0%, rgba(8,102,233,0.78) 100%),
        url('https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1800&q=80') center/cover;
    border-radius: 22px;
    padding: 48px 42px;
    color: #FFFFFF;
    margin-bottom: 26px;
    overflow: hidden;
    box-shadow: 0 20px 40px -20px rgba(7,27,73,0.5);
}
.hero-banner::before {
    content: '';
    position: absolute; right: -80px; top: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(8,102,233,0.55), transparent 70%);
    border-radius: 50%;
}
.hero-banner h1 { font-size: 34px; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.5px; color: #FFFFFF; }
.hero-banner p  { font-size: 16px; margin: 0; color: #D5E1FF; }

/* TARJETAS */
.vl-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 20px 22px;
    box-shadow: 0 4px 20px -8px rgba(7, 27, 73, 0.12);
    border: 1px solid #E6EDFF;
    margin-bottom: 16px;
}
.vl-card h4 {
    margin: 0 0 12px 0; font-size: 14px; font-weight: 700;
    color: #071B49; display: flex; align-items: center; gap: 8px;
    text-transform: uppercase; letter-spacing: 0.4px;
}
.vl-card h3 { margin: 0 0 6px 0; font-size: 19px; font-weight: 700; color: #071B49; }
.vl-card p  { margin: 4px 0; color: #4A5A78; font-size: 14px; }
.vl-card .label { font-size: 11px; color: #8A97B0; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.vl-card .value { font-size: 22px; font-weight: 700; color: #071B49; margin-top: 2px; }

.vl-pill {
    display: inline-block; background: #E6EDFF; color: #0866E9;
    padding: 5px 12px; border-radius: 100px;
    font-size: 12px; font-weight: 600; margin: 3px 6px 3px 0;
}
.vl-pill.green { background: #DCFCE7; color: #15803D; }
.vl-pill.orange { background: #FFEDD5; color: #C2410C; }
.vl-pill.blue { background: #DBEAFE; color: #1D4ED8; }

.status-dot {
    display: inline-block; width: 8px; height: 8px;
    background: #22C55E; border-radius: 50%; margin-right: 8px;
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.2); }
    50%      { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.1); }
}

/* TOPBAR */
.topbar-loc, .topbar-prof {
    display: flex; align-items: center; justify-content: center;
    height: 46px;
    background: #F2F6FC;
    border: 1px solid #E6EDFF;
    border-radius: 12px;
    color: #071B49; font-weight: 600; font-size: 13px; gap: 6px;
}
.topbar-prof {
    background: linear-gradient(135deg, #0866E9, #0A75FF);
    color: #FFFFFF; border: none; width: 46px;
    font-weight: 700; font-size: 16px;
    box-shadow: 0 4px 14px rgba(8,102,233,0.3);
}

/* Inputs */
[data-testid="stTextInput"] input {
    background: #FFFFFF !important;
    border: 1px solid #E6EDFF !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    color: #071B49 !important;
    height: 46px;
}
[data-testid="stTextInput"] input:focus {
    border-color: #0866E9 !important;
    box-shadow: 0 0 0 3px rgba(8,102,233,0.15) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1px solid #E6EDFF !important;
    border-radius: 12px !important;
    color: #071B49 !important;
}

.section-title { font-size: 22px; font-weight: 800; color: #071B49; margin: 6px 0 14px 0; letter-spacing: -0.3px; }

/* Chat */
.chat-bubble-user {
    background: #0866E9; color: white;
    padding: 12px 16px; border-radius: 16px 16px 4px 16px;
    margin: 8px 0 8px auto; max-width: 78%; font-size: 14px;
    box-shadow: 0 4px 14px rgba(8,102,233,0.3);
}
.chat-bubble-ai {
    background: #FFFFFF; color: #071B49;
    padding: 12px 16px; border-radius: 16px 16px 16px 4px;
    margin: 8px auto 8px 0; max-width: 78%;
    border: 1px solid #E6EDFF; font-size: 14px;
}

/* Notificación */
.notif-item {
    background: #FFFFFF;
    border-left: 4px solid #0866E9;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px -4px rgba(7,27,73,0.1);
}
.notif-item.warning { border-left-color: #F59E0B; }
.notif-item.info    { border-left-color: #0866E9; }
.notif-item h5 { margin: 0 0 4px 0; font-size: 14px; font-weight: 700; color: #071B49; }
.notif-item p  { margin: 0; font-size: 13px; color: #4A5A78; }
.notif-item .meta { font-size: 11px; color: #8A97B0; margin-top: 6px; }

.stButton > button[kind="primary"] {
    background: #0866E9 !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(8, 102, 233, 0.3) !important;
}
.stButton > button[kind="primary"]:hover { background: #0A75FF !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATOS
# ============================================================
RUTAS = {
    "A-3 · Circuito Contigo (Asturias - Cd. Natura)": {
        "color": "#2563eb",
        "paradas": [
            {"nombre": "Asturias", "lat": 25.741, "lon": -100.188},
            {"nombre": "Triana", "lat": 25.735, "lon": -100.195},
            {"nombre": "Rincón de Galicia", "lat": 25.728, "lon": -100.203},
            {"nombre": "Cd. Natura", "lat": 25.721, "lon": -100.211},
        ],
        "municipios": "Apodaca", "horario": "05:00 - 09:00 / 17:00 - 21:00",
        "frecuencia": "15 min", "longitud": "20.5 km", "duracion": "50 min", "tipo": "Circuito Contigo",
    },
    "A-8 · Circuito Contigo (Lomas de la Paz - Apodaca Centro)": {
        "color": "#16a34a",
        "paradas": [
            {"nombre": "Lomas de la Paz", "lat": 25.755, "lon": -100.205},
            {"nombre": "Pueblo Nuevo", "lat": 25.748, "lon": -100.198},
            {"nombre": "Real Hacienda Huinalá", "lat": 25.740, "lon": -100.190},
            {"nombre": "Rincón de Huinalá", "lat": 25.735, "lon": -100.185},
            {"nombre": "Villa de San Carlos", "lat": 25.728, "lon": -100.180},
            {"nombre": "Apodaca Centro", "lat": 25.720, "lon": -100.175},
        ],
        "municipios": "Apodaca", "horario": "05:00 - 09:00 / 17:00 - 21:00",
        "frecuencia": "20 min", "longitud": "21.5 km", "duracion": "60 min", "tipo": "Circuito Contigo",
    },
    "A-14 · Circuito Contigo (Nuevo Amanecer - Fresnos)": {
        "color": "#dc2626",
        "paradas": [
            {"nombre": "Nuevo Amanecer", "lat": 25.760, "lon": -100.215},
            {"nombre": "Santa Cecilia", "lat": 25.752, "lon": -100.208},
            {"nombre": "Fresnos", "lat": 25.745, "lon": -100.200},
            {"nombre": "Ex Hacienda San Francisco", "lat": 25.738, "lon": -100.192},
        ],
        "municipios": "Apodaca", "horario": "05:00 - 09:00 / 17:00 - 21:00",
        "frecuencia": "20 min", "longitud": "18 km", "duracion": "45 min", "tipo": "Circuito Contigo",
    },
    "Vistas del Río - Apodaca (Ruta directa)": {
        "color": "#7c3aed",
        "paradas": [
            {"nombre": "Vistas del Río", "lat": 25.700, "lon": -100.250},
            {"nombre": "Centro de Apodaca", "lat": 25.720, "lon": -100.175},
            {"nombre": "Huinalá", "lat": 25.735, "lon": -100.190},
            {"nombre": "El Sabinal", "lat": 25.745, "lon": -100.200},
        ],
        "municipios": "Apodaca, Juárez", "horario": "04:30 - 23:30",
        "frecuencia": "10-15 min", "longitud": "46 km", "duracion": "90 min", "tipo": "Ruta directa",
    },
    "219 · Provivienda - Tréboles": {
        "color": "#ec4899",
        "paradas": [
            {"nombre": "Adolfo López Mateos (Terminal Grupo Trees)", "lat": 25.695, "lon": -100.215},
            {"nombre": "Adolfo López Mateos (Soriana Las Quintas)", "lat": 25.700, "lon": -100.225},
            {"nombre": "Adolfo López Mateos (Ruíz Cortines)", "lat": 25.708, "lon": -100.235},
            {"nombre": "Pilastra (Adolfo López Mateos)", "lat": 25.712, "lon": -100.240},
            {"nombre": "Pío XII (San Martín)", "lat": 25.715, "lon": -100.245},
            {"nombre": "Río San Juan (Guadalajara)", "lat": 25.718, "lon": -100.238},
            {"nombre": "México (Loma Redonda)", "lat": 25.720, "lon": -100.225},
            {"nombre": "Guadalajara (Acapulco)", "lat": 25.723, "lon": -100.215},
            {"nombre": "Guadalajara (Camino a Huinalá)", "lat": 25.726, "lon": -100.205},
            {"nombre": "México (Comercial Treviño Apodaca)", "lat": 25.730, "lon": -100.195},
            {"nombre": "Héctor Caballero (Arenal)", "lat": 25.735, "lon": -100.188},
            {"nombre": "16 de Septiembre (Valle del Norte)", "lat": 25.738, "lon": -100.185},
            {"nombre": "Miguel Alemán (Plaza Sendero La Fe)", "lat": 25.745, "lon": -100.190},
            {"nombre": "Miguel Alemán (Plaza Las Américas)", "lat": 25.750, "lon": -100.195},
            {"nombre": "Miguel Alemán (Parque Kalos Apodaca)", "lat": 25.755, "lon": -100.200},
            {"nombre": "Colector (Florencia - Albania)", "lat": 25.760, "lon": -100.205},
        ],
        "municipios": "Apodaca, Guadalupe", "horario": "05:00 - 22:00",
        "frecuencia": "8-12 min", "longitud": "28 km", "duracion": "75 min", "tipo": "Ruta urbana",
    },
}

METRO = {
    "Línea 1 · Talleres / San Bernabé": {
        "color": "#e11d48",
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
        "color": "#f97316",
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
        "color": "#0d9488",
        "estaciones": [
            {"nombre": "Hospital", "lat": 25.685, "lon": -100.305},
            {"nombre": "Hospital Metropolitano (Apodaca)", "lat": 25.715, "lon": -100.210},
        ],
        "conexion_apodaca": "Llega directo a Apodaca en la estación Hospital Metropolitano.",
    },
}

# ============================================================
# OSRM
# ============================================================
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
            if intento == 1:
                return None
            time.sleep(1)
    return None

# ============================================================
# MAPAS
# ============================================================
def crear_mapa_base(zoom=12, centro=(25.720, -100.240)):
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
    if len(coords) < 2:
        return
    folium.PolyLine(locations=coords, color=datos["color"], weight=6, opacity=0.9,
                    dash_array="10 5", tooltip=f"Metro: {nombre_linea}").add_to(mapa)
    for est in datos["estaciones"]:
        folium.Marker(
            location=[est["lat"], est["lon"]],
            icon=folium.Icon(color="darkblue", icon="subway", prefix="fa"),
            popup=folium.Popup(f"<b>{est['nombre']}</b><br>{nombre_linea}", max_width=250),
            tooltip=est["nombre"],
        ).add_to(mapa)

# ============================================================
# HERRAMIENTAS DEL CHATBOT
# ============================================================
def buscar_ruta_por_nombre(nombre_ruta: str) -> str:
    resultados = [
        f"**{nombre}**\n- Municipios: {d['municipios']}\n- Horario: {d['horario']}\n"
        f"- Frecuencia: {d['frecuencia']}\n- Paradas: {', '.join(p['nombre'] for p in d['paradas'])}"
        for nombre, d in RUTAS.items() if nombre_ruta.lower() in nombre.lower()
    ]
    return "\n\n".join(resultados) if resultados else "No encontré rutas con ese nombre."

def buscar_ruta_por_parada(parada: str) -> str:
    resultados = [
        f"**{nombre}** pasa por: {', '.join(p['nombre'] for p in d['paradas'] if parada.lower() in p['nombre'].lower())}"
        for nombre, d in RUTAS.items()
        if any(parada.lower() in p["nombre"].lower() for p in d["paradas"])
    ]
    return "\n".join(resultados) if resultados else "No encontré rutas que pasen por esa parada."

def obtener_info_metro(linea: str) -> str:
    resultados = [
        f"**{nombre}**\n- Estaciones: {', '.join(e['nombre'] for e in d['estaciones'])}\n"
        f"- Conexión Apodaca: {d['conexion_apodaca']}"
        for nombre, d in METRO.items() if linea.lower() in nombre.lower()
    ]
    return "\n\n".join(resultados) if resultados else "No encontré esa línea del metro."

def listar_todas_rutas() -> str:
    return "\n".join(f"- {n}" for n in RUTAS.keys())

def listar_lineas_metro() -> str:
    return "\n".join(f"- {n}" for n in METRO.keys())

tools = [
    {"type": "function", "function": {"name": "buscar_ruta_por_nombre", "description": "Busca rutas por nombre o número.", "parameters": {"type": "object", "properties": {"nombre_ruta": {"type": "string"}}, "required": ["nombre_ruta"]}}},
    {"type": "function", "function": {"name": "buscar_ruta_por_parada", "description": "Busca rutas que pasen por una parada o calle.", "parameters": {"type": "object", "properties": {"parada": {"type": "string"}}, "required": ["parada"]}}},
    {"type": "function", "function": {"name": "obtener_info_metro", "description": "Devuelve estaciones y conexiones de una línea del Metro.", "parameters": {"type": "object", "properties": {"linea": {"type": "string"}}, "required": ["linea"]}}},
    {"type": "function", "function": {"name": "listar_todas_rutas", "description": "Lista todas las rutas de camión disponibles.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "listar_lineas_metro", "description": "Lista todas las líneas del Metro disponibles.", "parameters": {"type": "object", "properties": {}}}},
]

def ejecutar_herramienta(nombre, args):
    if nombre == "buscar_ruta_por_nombre": return buscar_ruta_por_nombre(args.get("nombre_ruta", ""))
    if nombre == "buscar_ruta_por_parada": return buscar_ruta_por_parada(args.get("parada", ""))
    if nombre == "obtener_info_metro":    return obtener_info_metro(args.get("linea", ""))
    if nombre == "listar_todas_rutas":    return listar_todas_rutas()
    if nombre == "listar_lineas_metro":   return listar_lineas_metro()
    return "Función no reconocida."

# ============================================================
# HELPERS
# ============================================================
def get_metro_connections(route_data):
    found = []
    for nombre_linea, datos in METRO.items():
        for est in datos["estaciones"]:
            for parada in route_data["paradas"]:
                if est["nombre"].split(" (")[0].lower() in parada["nombre"].lower():
                    found.append((nombre_linea, est["nombre"]))
    return list({f"{l} · {e}" for l, e in found})

def get_nearby_routes(route_name, route_data):
    propias = {p["nombre"] for p in route_data["paradas"]}
    nearby = []
    for nombre, d in RUTAS.items():
        if nombre == route_name:
            continue
        if propias & {p["nombre"] for p in d["paradas"]}:
            nearby.append(nombre)
    return nearby[:4]

def planificar(origen, destino):
    o, d = origen.lower().strip(), destino.lower().strip()
    if not o or not d:
        return [], [], []
    rutas_o, rutas_d = {}, {}
    for nombre, data in RUTAS.items():
        po = next((p["nombre"] for p in data["paradas"] if o in p["nombre"].lower()), None)
        pd = next((p["nombre"] for p in data["paradas"] if d in p["nombre"].lower()), None)
        if po: rutas_o[nombre] = po
        if pd: rutas_d[nombre] = pd
    directas = list(set(rutas_o) & set(rutas_d))
    transbordos = []
    for ra in rutas_o:
        for rb in rutas_d:
            if ra == rb:
                continue
            shared = ({p["nombre"] for p in RUTAS[ra]["paradas"]}
                      & {p["nombre"] for p in RUTAS[rb]["paradas"]})
            if shared:
                transbordos.append((ra, rb, list(shared)[0]))
    return directas, transbordos, list(rutas_o) + list(rutas_d)

# ============================================================
# SESSION STATE
# ============================================================
if "current_view" not in st.session_state:
    st.session_state.current_view = "Inicio"
if "selected_route" not in st.session_state:
    st.session_state.selected_route = list(RUTAS.keys())[0]
if "selected_metro" not in st.session_state:
    st.session_state.selected_metro = list(METRO.keys())[0]
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{
        "role": "system",
        "content": (
            "Eres Vialink IA, un asistente experto en transporte público de la Zona Metropolitana de Monterrey. "
            "Usa SIEMPRE las herramientas disponibles para consultar rutas y metro antes de responder; "
            "no inventes rutas ni horarios. Responde en español, claro y amable. "
            "Si el usuario pide 'cómo llegar', identifica qué rutas pasan por esos puntos usando "
            "buscar_ruta_por_parada y sugiere la mejor combinación. Si no hay información, dilo con honestidad."
        ),
    }]

# ============================================================
# SIDEBAR
# ============================================================
MENU = [
    ("🏠", "Inicio"),
    ("🗺️", "Mapa en tiempo real"),
    ("📍", "Planificador de rutas"),
    ("🚌", "Información de líneas"),
    ("🔔", "Notificaciones"),
    ("🤖", "Asistente IA"),
    ("⚙️", "Configuración"),
]

with st.sidebar:
    if LOGO_B64:
        logo_html = f'<div class="logo"><img src="data:image/png;base64,{LOGO_B64}" style="width:100%;height:100%;object-fit:contain;border-radius:16px;"></div>'
    else:
        logo_html = '<div class="logo">🚌</div>'

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

    for icon, name in MENU:
        is_active = st.session_state.current_view == name
        clicked = st.button(
            f"{icon}   {name}",
            key=f"menu_{name}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        )
        if clicked:
            st.session_state.current_view = name
            st.rerun()

# ============================================================
# TOP BAR
# ============================================================
tb = st.columns([5, 1.6, 0.7])
with tb[0]:
    top_search = st.text_input(
        "Buscar",
        placeholder="🔍  Buscar ruta, parada o destino...",
        label_visibility="collapsed",
        key="top_search",
    )
with tb[1]:
    st.markdown(
        '<div class="topbar-loc">📍 Apodaca, Nuevo León</div>',
        unsafe_allow_html=True,
    )
with tb[2]:
    st.markdown('<div class="topbar-prof">V</div>', unsafe_allow_html=True)

if top_search:
    coincidencias = [r for r in RUTAS if top_search.lower() in r.lower()]
    if coincidencias:
        st.markdown("**Sugerencias:**")
        cols_chip = st.columns(min(len(coincidencias), 4))
        for i, r in enumerate(coincidencias[:4]):
            with cols_chip[i]:
                if st.button(r, key=f"chip_{i}", use_container_width=True):
                    st.session_state.selected_route = r
                    st.session_state.current_view = "Inicio"
                    st.rerun()

# ============================================================
# VISTA: INICIO
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

    col_left, col_center, col_right = st.columns([1.05, 2.4, 1.15], gap="medium")

    with col_left:
        st.markdown('<div class="vl-card"><h4>🎯 ¿Qué quieres hacer?</h4>', unsafe_allow_html=True)
        if st.button("🗺️  Ver mapa completo", use_container_width=True):
            st.session_state.current_view = "Mapa en tiempo real"
            st.rerun()
        if st.button("📍  Planear mi viaje", use_container_width=True):
            st.session_state.current_view = "Planificador de rutas"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="vl-card"><h4>🚌 Selecciona una ruta</h4>', unsafe_allow_html=True)
        selected = st.selectbox(
            "Ruta:",
            list(RUTAS.keys()),
            index=list(RUTAS.keys()).index(st.session_state.selected_route),
            label_visibility="collapsed",
        )
        st.session_state.selected_route = selected
        st.markdown("</div>", unsafe_allow_html=True)

        d = RUTAS[st.session_state.selected_route]
        st.markdown(
            f"""
            <div class="vl-card">
                <h4>📊 Información de la ruta</h4>
                <div class="label">Horario</div><div class="value" style="font-size:15px;">{d['horario']}</div>
                <div class="label" style="margin-top:10px;">Frecuencia</div><div class="value">{d['frecuencia']}</div>
                <div class="label" style="margin-top:10px;">Distancia</div><div class="value">{d['longitud']}</div>
                <div class="label" style="margin-top:10px;">Duración estimada</div><div class="value">{d['duracion']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metro_conn = get_metro_connections(d)
        metro_html = "".join(f'<span class="vl-pill blue">{c}</span>' for c in metro_conn) or '<span class="vl-pill">Sin conexión directa</span>'
        st.markdown(
            f'<div class="vl-card"><h4>🚇 Conexiones con Metrorrey</h4>{metro_html}</div>',
            unsafe_allow_html=True,
        )

    with col_center:
        d = RUTAS[st.session_state.selected_route]
        st.markdown(
            f"""
            <div class="vl-card" style="padding:16px 22px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <h3>{st.session_state.selected_route}</h3>
                        <p style="color:#4A5A78;font-size:13px;margin:2px 0;">{d['tipo']} · {d['municipios']}</p>
                    </div>
                    <div>
                        <span class="status-dot"></span>
                        <span style="font-size:13px;font-weight:600;color:#15803D;">Servicio programado</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        mapa = crear_mapa_base(zoom=12)
        with st.spinner("Calculando recorrido por calles..."):
            agregar_ruta_al_mapa(mapa, st.session_state.selected_route, d)
        st_folium(mapa, width=None, height=520, returned_objects=[])

    with col_right:
        d = RUTAS[st.session_state.selected_route]

        st.markdown(
            f"""
            <div class="vl-card">
                <h4>⏱️ Tiempo de llegada</h4>
                <p style="font-size:13px;">Sin datos en tiempo real disponibles.</p>
                <p><b>Frecuencia programada:</b> {d['frecuencia']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="vl-card">
                <h4>📍 Siguiente parada</h4>
                <p style="font-size:13px;">Disponible cuando compartas tu ubicación.</p>
                <p><b>Origen:</b> {d['paradas'][0]['nombre']}</p>
                <p><b>Destino:</b> {d['paradas'][-1]['nombre']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cercanas = get_nearby_routes(st.session_state.selected_route, d)
        html_cerc = "".join(f'<span class="vl-pill">{r.split(" · ")[0]}</span>' for r in cercanas) or '<span class="vl-pill">Sin rutas cercanas</span>'
        st.markdown(
            f'<div class="vl-card"><h4>🚏 Otras líneas cercanas</h4>{html_cerc}</div>',
            unsafe_allow_html=True,
        )

        metro_conn = get_metro_connections(d)
        metro_html = "".join(f'<span class="vl-pill blue">{c}</span>' for c in metro_conn) or '<span class="vl-pill">Sin conexión directa</span>'
        st.markdown(
            f'<div class="vl-card"><h4>🚇 Conexión Metrorrey</h4>{metro_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="vl-card">
                <h4>⭐ Calificación</h4>
                <p style="font-size:13px;">Sé el primero en calificar esta ruta.</p>
                <p style="font-size:22px;">☆☆☆☆☆</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# VISTA: MAPA
# ============================================================
def render_mapa():
    st.markdown('<div class="section-title">🗺️ Mapa en tiempo real</div>', unsafe_allow_html=True)

    top = st.columns([2, 2])
    with top[0]:
        ruta_sel = st.selectbox(
            "Ruta a visualizar",
            list(RUTAS.keys()),
            index=list(RUTAS.keys()).index(st.session_state.selected_route),
        )
        st.session_state.selected_route = ruta_sel
    with top[1]:
        mostrar_metro = st.checkbox("Mostrar también las líneas del Metro", value=True)

    mapa = crear_mapa_base(zoom=12)
    with st.spinner("Calculando recorrido por calles..."):
        agregar_ruta_al_mapa(mapa, st.session_state.selected_route, RUTAS[st.session_state.selected_route])
        if mostrar_metro:
            for nombre, datos in METRO.items():
                agregar_metro_al_mapa(mapa, nombre, datos)

    d = RUTAS[st.session_state.selected_route]
    st.markdown(
        f"""
        <div class="vl-card" style="padding:14px 22px;">
            <span class="status-dot"></span>
            <b style="font-size:15px;color:#071B49;">{st.session_state.selected_route}</b>
            <span class="vl-pill green" style="margin-left:10px;">{d['tipo']}</span>
            <span class="vl-pill orange">{d['horario']}</span>
            <span class="vl-pill blue">Frecuencia: {d['frecuencia']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st_folium(mapa, width=None, height=640, returned_objects=[])
    st.caption("Los recorridos siguen las calles reales mediante OSRM. No se muestran posiciones GPS en tiempo real.")

# ============================================================
# VISTA: PLANIFICADOR
# ============================================================
def render_planificador():
    st.markdown('<div class="section-title">📍 Planificador de rutas</div>', unsafe_allow_html=True)
    st.caption("Escribe una calle, colonia o parada. Ejemplo: 'Miguel Alemán', 'Asturias', 'Apodaca Centro'.")

    cols = st.columns([2.2, 2.2, 0.9])
    with cols[0]:
        origen = st.text_input("Origen", placeholder="Ej. Asturias", key="plan_origen")
    with cols[1]:
        destino = st.text_input("Destino", placeholder="Ej. Apodaca Centro", key="plan_destino")
    with cols[2]:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        buscar = st.button("Buscar ruta", type="primary", use_container_width=True)

    if buscar or (origen and destino):
        if not origen or not destino:
            st.info("Escribe un origen y un destino para buscar conexiones.")
            return
        directas, transbordos, _ = planificar(origen, destino)

        if directas:
            st.markdown('<div class="section-title" style="font-size:18px;margin-top:20px;">✅ Rutas directas</div>', unsafe_allow_html=True)
            for r in directas:
                datos = RUTAS[r]
                st.markdown(
                    f"""
                    <div class="vl-card">
                        <h3>{r}</h3>
                        <span class="vl-pill">{datos['tipo']}</span>
                        <span class="vl-pill green">{datos['municipios']}</span>
                        <span class="vl-pill orange">{datos['horario']}</span>
                        <p style="margin-top:8px;">Duración: <b>{datos['duracion']}</b> · Frecuencia: <b>{datos['frecuencia']}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Ver en el mapa", key=f"ver_{r}"):
                    st.session_state.selected_route = r
                    st.session_state.current_view = "Mapa en tiempo real"
                    st.rerun()

        if transbordos:
            st.markdown('<div class="section-title" style="font-size:18px;margin-top:20px;">🔄 Conexiones con transbordo</div>', unsafe_allow_html=True)
            for ra, rb, punto in transbordos[:5]:
                st.markdown(
                    f"""
                    <div class="vl-card">
                        <p style="font-size:14px;margin-bottom:6px;">Toma <b>{ra.split(' · ')[0]}</b>, transborda en <b>{punto}</b> y continúa en <b>{rb.split(' · ')[0]}</b>.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if not directas and not transbordos:
            st.warning("No encontramos una conexión directa entre esos puntos. Prueba con otras palabras o revisa el mapa de rutas.")

# ============================================================
# VISTA: INFORMACIÓN DE LÍNEAS
# ============================================================
def render_lineas():
    st.markdown('<div class="section-title">🚌 Información de líneas</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Rutas de camión", "Líneas de Metrorrey"])

    with tab1:
        for nombre, datos in RUTAS.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(
                    f"""
                    <div class="vl-card" style="margin-bottom:10px;">
                        <h3>{nombre}</h3>
                        <span class="vl-pill">{datos['tipo']}</span>
                        <span class="vl-pill green">{datos['municipios']}</span>
                        <span class="vl-pill orange">{datos['horario']}</span>
                        <p style="font-size:13px;margin-top:8px;color:#4A5A78;">
                            Frecuencia {datos['frecuencia']} · {datos['longitud']} · {datos['duracion']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
                if st.button("Ver mapa", key=f"inf_{nombre}", use_container_width=True):
                    st.session_state.selected_route = nombre
                    st.session_state.current_view = "Mapa en tiempo real"
                    st.rerun()

    with tab2:
        for nombre, datos in METRO.items():
            estaciones = ", ".join(e["nombre"] for e in datos["estaciones"])
            st.markdown(
                f"""
                <div class="vl-card">
                    <h3>{nombre}</h3>
                    <p style="font-size:13px;color:#4A5A78;">{estaciones}</p>
                    <p style="font-size:13px;margin-top:8px;"><b>Conexión Apodaca:</b> {datos['conexion_apodaca']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ============================================================
# VISTA: NOTIFICACIONES
# ============================================================
def render_notificaciones():
    st.markdown('<div class="section-title">🔔 Notificaciones</div>', unsafe_allow_html=True)
    st.caption("Aquí aparecerán los avisos e incidencias del servicio cuando estén disponibles.")

    st.markdown(
        """
        <div class="notif-item info">
            <h5>Bienvenido a Vialink</h5>
            <p>Esta sección mostrará cambios de recorrido, retrasos y avisos operativos en tiempo real. Por ahora el sistema no recibe reportes oficiales.</p>
            <div class="meta">Sistema · Ahora</div>
        </div>

        <div class="notif-item warning">
            <h5>Sin alertas activas</h5>
            <p>No hay avisos publicados por los operadores del transporte público. Cuando existan, aparecerán aquí.</p>
            <div class="meta">Operadores · Estado actual</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Suscribirme a notificaciones de mis rutas", type="primary"):
        st.success("Te has suscrito. (Función de prototipo.)")

# ============================================================
# VISTA: ASISTENTE IA
# ============================================================
def render_asistente():
    st.markdown('<div class="section-title">🤖 Asistente IA</div>', unsafe_allow_html=True)
    st.caption("Pregunta lo que quieras sobre rutas, paradas y Metrorrey. El asistente consulta los datos reales de la app.")

    try:
        client = OpenAI(
            api_key=st.secrets["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )
    except Exception:
        st.error("⚠️ Falta la API Key de Groq. Agrégala en `.streamlit/secrets.toml` como `GROQ_API_KEY = 'gsk_...'`.")
        return

    MODELO = "openai/gpt-oss-120b"

    for msg in st.session_state.chat_messages:
        if msg["role"] == "system":
            continue
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant" and msg.get("content"):
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.markdown(f'<div class="chat-bubble-user">{prompt}</div>', unsafe_allow_html=True)

        with st.spinner("Consultando rutas..."):
            try:
                response = client.chat.completions.create(
                    model=MODELO,
                    messages=st.session_state.chat_messages,
                    tools=tools,
                    tool_choice="auto",
                )
                msg = response.choices[0].message

                while msg.tool_calls:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": msg.content or "",
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
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": resultado,
                        })
                    response = client.chat.completions.create(
                        model=MODELO,
                        messages=st.session_state.chat_messages,
                    )
                    msg = response.choices[0].message

                final = msg.content or "No pude generar una respuesta."
                st.session_state.chat_messages.append({"role": "assistant", "content": final})
                st.markdown(f'<div class="chat-bubble-ai">{final}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error al consultar Groq: {e}")
                st.caption("Si el error menciona 'rate limit', espera unos segundos y vuelve a intentar.")

# ============================================================
# VISTA: CONFIGURACIÓN
# ============================================================
def render_configuracion():
    st.markdown('<div class="section-title">⚙️ Configuración</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="vl-card">
            <h4>ℹ️ Acerca de Vialink</h4>
            <p>Prototipo de plataforma de movilidad para la Zona Metropolitana de Monterrey.</p>
            <p style="margin-top:8px;font-size:13px;color:#4A5A78;">
                Versión 1.0 · Datos de rutas y horarios de ejemplo · Recorridos calculados por OSRM ·
                Asistente IA impulsado por Groq.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vl-card">
            <h4>🔧 Preferencias</h4>
            <p style="font-size:13px;color:#4A5A78;">Las preferencias se guardan solo durante tu sesión.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    mostrar_alertas = st.toggle("Recibir notificaciones de cambios en el servicio", value=False)
    if mostrar_alertas:
        st.success("Notificaciones activadas (función de prototipo).")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Borrar conversación del asistente"):
        st.session_state.chat_messages = [{
            "role": "system",
            "content": (
                "Eres Vialink IA, un asistente experto en transporte público de la Zona Metropolitana de Monterrey. "
                "Usa SIEMPRE las herramientas disponibles."
            ),
        }]
        st.success("Conversación eliminada.")

# ============================================================
# ROUTER
# ============================================================
view = st.session_state.current_view
if view == "Inicio":
    render_inicio()
elif view == "Mapa en tiempo real":
    render_mapa()
elif view == "Planificador de rutas":
    render_planificador()
elif view == "Información de líneas":
    render_lineas()
elif view == "Notificaciones":
    render_notificaciones()
elif view == "Asistente IA":
    render_asistente()
elif view == "Configuración":
    render_configuracion()
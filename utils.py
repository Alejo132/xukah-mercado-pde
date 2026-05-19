import streamlit as st
import pandas as pd
import base64
import os

BLACK  = "#0a0a0a"
WHITE  = "#ffffff"
GRAY_1 = "#f5f5f5"
GRAY_2 = "#e8e8e8"
GRAY_3 = "#9ca3af"
GOLD   = "#c9a84c"
DARK   = "#141414"

PLOTLY_BASE = dict(
    plot_bgcolor=WHITE, paper_bgcolor=WHITE,
    font=dict(family="Inter", size=12, color=BLACK),
    margin=dict(l=0, r=10, t=15, b=10),
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def logo_b64():
    path = os.path.join(BASE_DIR, "xukah_logo.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


@st.cache_data
def cargar_datos():
    path = os.path.join(BASE_DIR, "propiedades_pde.csv")
    df = pd.read_csv(path)
    df["precio_usd"]        = pd.to_numeric(df["precio_usd"], errors="coerce")
    df["m2"]                = pd.to_numeric(df["m2"], errors="coerce")
    df["dormitorios"]       = pd.to_numeric(df["dormitorios"], errors="coerce")
    df["anio_construccion"] = pd.to_numeric(df["anio_construccion"], errors="coerce")
    df["latitud"]           = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"]          = pd.to_numeric(df["longitud"], errors="coerce")
    df = df[df["precio_usd"] > 20_000]
    df["precio_m2"] = (df["precio_usd"] / df["m2"]).where(df["m2"] > 10).round(0)
    df["precio_m2"] = df["precio_m2"].where(df["precio_m2"] < 25_000)
    df["zona"]      = df["zona"].fillna("Sin zona")
    # mediana por zona para oportunidades
    mediana_zona = df.groupby("zona")["precio_usd"].median().rename("mediana_zona")
    df = df.join(mediana_zona, on="zona")
    df["pct_vs_mediana"] = ((df["precio_usd"] - df["mediana_zona"]) / df["mediana_zona"] * 100).round(1)
    return df


BASE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: {GRAY_1}; }}
.main {{ background-color: {GRAY_1}; }}
.block-container {{ padding-top: 0; padding-bottom: 2rem; }}
.xukah-header {{
    background: {BLACK}; padding: 1.6rem 4rem; display: flex;
    align-items: center; gap: 2rem; margin-bottom: 1.8rem;
    margin-top: -4rem; margin-left: -4rem; margin-right: -4rem;
}}
.xukah-header-text h1 {{
    font-family: 'Montserrat', sans-serif; font-size: 1.4rem; font-weight: 700;
    color: {WHITE}; margin: 0; letter-spacing: 2px; text-transform: uppercase;
}}
.xukah-header-text p {{
    font-size: 0.75rem; color: {GOLD}; margin: 0.2rem 0 0;
    letter-spacing: 3px; text-transform: uppercase; font-weight: 500;
}}
.xukah-divider {{ width: 1px; height: 44px; background: #333; margin: 0 0.5rem; }}
.xukah-report-label {{ font-family: 'Montserrat', sans-serif; font-size: 0.65rem; color: {GRAY_3}; letter-spacing: 2px; text-transform: uppercase; }}
.xukah-report-title {{ font-family: 'Montserrat', sans-serif; font-size: 0.95rem; color: {WHITE}; font-weight: 600; }}
.kpi-card {{
    background: {WHITE}; border-radius: 4px; padding: 1.2rem 1.4rem;
    border-top: 3px solid {BLACK}; box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}}
.kpi-card.gold {{ border-top-color: {GOLD}; }}
.kpi-label {{ font-size: 0.68rem; color: {GRAY_3}; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.4rem; }}
.kpi-value {{ font-family: 'Montserrat', sans-serif; font-size: 1.65rem; font-weight: 700; color: {BLACK}; line-height: 1.1; }}
.kpi-delta {{ font-size: 0.73rem; color: {GRAY_3}; margin-top: 0.3rem; }}
.section-header {{
    font-family: 'Montserrat', sans-serif; font-size: 0.7rem; font-weight: 700;
    color: {BLACK}; letter-spacing: 2.5px; text-transform: uppercase;
    padding-bottom: 0.5rem; border-bottom: 2px solid {BLACK}; margin-bottom: 1rem; margin-top: 0.5rem;
}}
section[data-testid="stSidebar"] {{ background-color: {DARK}; border-right: 1px solid #222; }}
section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {{
    color: {GRAY_3} !important; font-size: 0.7rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;
}}
.stDownloadButton button, .stButton button {{
    background-color: {BLACK}; color: {WHITE}; border: none; border-radius: 2px;
    font-family: 'Montserrat', sans-serif; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase; padding: 0.6rem 1.4rem;
}}
.stDownloadButton button:hover, .stButton button:hover {{ background-color: {GOLD}; color: {BLACK}; }}
.xukah-footer {{
    text-align: center; padding: 2rem 0 1rem; color: {GRAY_3};
    font-size: 0.68rem; letter-spacing: 1.5px; text-transform: uppercase;
    border-top: 1px solid {GRAY_2}; margin-top: 2rem;
}}
.opp-badge {{
    display: inline-block; padding: 2px 10px; border-radius: 2px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;
}}
.opp-verde {{ background: #dcfce7; color: #166534; }}
.opp-rojo  {{ background: #fee2e2; color: #991b1b; }}
</style>
"""


def render_header(logo, subtitulo="Punta del Este · Maldonado · 2016–2026"):
    logo_html = f'<img src="data:image/png;base64,{logo}" style="height:44px;filter:brightness(0) invert(1)">' if logo else ""
    st.markdown(f"""
    <div class="xukah-header">
        {logo_html}
        <div class="xukah-divider"></div>
        <div class="xukah-header-text">
            <h1>Xukah Real Estate</h1>
            <p>Invierte · Comercializa</p>
        </div>
        <div style="margin-left:auto;text-align:right">
            <div class="xukah-report-label">Reporte de mercado</div>
            <div class="xukah-report-title">{subtitulo}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_sidebar_logo(logo):
    if logo:
        st.markdown(
            f'<div style="padding:1rem 0 0.5rem;text-align:center">'
            f'<img src="data:image/png;base64,{logo}" style="height:32px;filter:brightness(0) invert(1)">'
            f'</div>', unsafe_allow_html=True
        )
    st.markdown("---")


def kpi(label, value, delta="", gold=False):
    cls = "kpi-card gold" if gold else "kpi-card"
    return (f'<div class="{cls}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-delta">{delta}</div>'
            f'</div>')


def footer():
    st.markdown("""
    <div class="xukah-footer">
        Xukah Real Estate &nbsp;·&nbsp; Reporte de mercado Punta del Este &nbsp;·&nbsp;
        Datos: InfoCasas mayo 2026 &nbsp;·&nbsp; Documento confidencial de uso interno
    </div>""", unsafe_allow_html=True)

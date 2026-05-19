import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import base64
import os

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Xukah · Análisis de Mercado PDE",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Xukah Brand Colors ────────────────────────────────────────────────────────
BLACK   = "#0a0a0a"
WHITE   = "#ffffff"
GRAY_1  = "#f5f5f5"   # fondo página
GRAY_2  = "#e8e8e8"   # bordes
GRAY_3  = "#9ca3af"   # texto secundario
GOLD    = "#c9a84c"   # acento dorado para lujo
DARK    = "#141414"   # sidebar

# ── Logo en base64 ────────────────────────────────────────────────────────────
def logo_b64():
    path = os.path.join(os.path.dirname(__file__), "xukah_logo.png")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo = logo_b64()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {GRAY_1};
}}

.main {{ background-color: {GRAY_1}; }}
.block-container {{ padding-top: 0; padding-bottom: 2rem; }}

/* ── Header ── */
.xukah-header {{
    background: {BLACK};
    padding: 1.8rem 2.5rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    margin-bottom: 1.8rem;
    margin-top: -4rem;
    margin-left: -4rem;
    margin-right: -4rem;
    padding-left: 4rem;
    padding-right: 4rem;
}}
.xukah-header-text h1 {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.55rem;
    font-weight: 700;
    color: {WHITE};
    margin: 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.xukah-header-text p {{
    font-size: 0.8rem;
    color: {GOLD};
    margin: 0.2rem 0 0;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 500;
}}
.xukah-divider {{
    width: 1px;
    height: 48px;
    background: #333;
    margin: 0 0.5rem;
}}
.xukah-report-label {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.7rem;
    color: {GRAY_3};
    letter-spacing: 2px;
    text-transform: uppercase;
}}
.xukah-report-title {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1rem;
    color: {WHITE};
    font-weight: 600;
    letter-spacing: 1px;
}}

/* ── KPI Cards ── */
.kpi-card {{
    background: {WHITE};
    border-radius: 4px;
    padding: 1.3rem 1.5rem;
    border-top: 3px solid {BLACK};
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}}
.kpi-card.gold {{ border-top-color: {GOLD}; }}
.kpi-label {{
    font-size: 0.7rem;
    color: {GRAY_3};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem;
}}
.kpi-value {{
    font-family: 'Montserrat', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: {BLACK};
    line-height: 1.1;
}}
.kpi-delta {{
    font-size: 0.75rem;
    color: {GRAY_3};
    margin-top: 0.3rem;
}}

/* ── Section headers ── */
.section-header {{
    font-family: 'Montserrat', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: {BLACK};
    letter-spacing: 2.5px;
    text-transform: uppercase;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid {BLACK};
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {DARK};
    border-right: 1px solid #222;
}}
section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {{
    color: {GRAY_3} !important;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}}
section[data-testid="stSidebar"] hr {{
    border-color: #2a2a2a;
}}

/* ── Download button ── */
.stDownloadButton button {{
    background-color: {BLACK};
    color: {WHITE};
    border: none;
    border-radius: 2px;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.6rem 1.4rem;
}}
.stDownloadButton button:hover {{
    background-color: {GOLD};
    color: {BLACK};
}}

/* ── Dataframe ── */
.dataframe {{ font-size: 0.82rem; }}

/* ── Footer ── */
.xukah-footer {{
    text-align: center;
    padding: 2rem 0 1rem;
    color: {GRAY_3};
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-top: 1px solid {GRAY_2};
    margin-top: 2rem;
}}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
logo_html = f'<img src="data:image/png;base64,{logo}" style="height:48px;filter:brightness(0) invert(1)">' if logo else ""

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
        <div class="xukah-report-title">Punta del Este · Maldonado · 2016–2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    path = os.path.join(os.path.dirname(__file__), "propiedades_pde.csv")
    df = pd.read_csv(path)
    df["precio_usd"]         = pd.to_numeric(df["precio_usd"], errors="coerce")
    df["m2"]                 = pd.to_numeric(df["m2"], errors="coerce")
    df["dormitorios"]        = pd.to_numeric(df["dormitorios"], errors="coerce")
    df["anio_construccion"]  = pd.to_numeric(df["anio_construccion"], errors="coerce")
    df["latitud"]            = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"]           = pd.to_numeric(df["longitud"], errors="coerce")
    df = df[df["precio_usd"] > 20_000]
    df["precio_m2"] = (df["precio_usd"] / df["m2"]).where(df["m2"] > 10).round(0)
    df["precio_m2"] = df["precio_m2"].where(df["precio_m2"] < 25_000)
    df["zona"]      = df["zona"].fillna("Sin zona")
    return df

df = cargar_datos()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    if logo:
        st.markdown(
            f'<div style="padding:1rem 0 0.5rem;text-align:center">'
            f'<img src="data:image/png;base64,{logo}" style="height:36px;filter:brightness(0) invert(1)">'
            f'</div>', unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;letter-spacing:2px;color:#666;text-transform:uppercase;margin-bottom:0.8rem">Filtros</div>', unsafe_allow_html=True)

    zonas_disp = sorted(df["zona"].dropna().unique())
    zonas_sel  = st.multiselect("Zona", zonas_disp, default=zonas_disp)

    precio_min = int(df["precio_usd"].min())
    precio_max = int(df["precio_usd"].quantile(0.99))
    rango_precio = st.slider(
        "Precio (U$S)",
        min_value=precio_min, max_value=precio_max,
        value=(precio_min, precio_max), step=10_000, format="$%d",
    )

    dorms_disp = sorted(df["dormitorios"].dropna().unique().astype(int).tolist())
    dorms_sel  = st.multiselect("Dormitorios", dorms_disp, default=dorms_disp)

    estados   = ["Todos", "A estrenar (entregado)", "En construcción (futuro)", "En pozo"]
    estado_sel = st.selectbox("Estado", estados)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.65rem;color:#444;text-align:center;padding-top:0.5rem">'
        'Fuente: InfoCasas · Mayo 2026<br>Uso interno — Xukah Real Estate'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Filtros ───────────────────────────────────────────────────────────────────
mask = (
    df["zona"].isin(zonas_sel if zonas_sel else zonas_disp)
    & df["precio_usd"].between(*rango_precio)
    & df["dormitorios"].isin(dorms_sel if dorms_sel else dorms_disp)
)
if estado_sel == "A estrenar (entregado)":
    mask &= df["anio_construccion"].between(2016, 2026)
elif estado_sel == "En construcción (futuro)":
    mask &= df["anio_construccion"] > 2026
elif estado_sel == "En pozo":
    mask &= df["anio_construccion"].isna() | (df["anio_construccion"] == 0)

dff = df[mask].copy()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total        = len(dff)
precio_prom  = dff["precio_usd"].mean()
precio_med   = dff["precio_usd"].median()
pm2_med      = dff["precio_m2"].median()
n_zonas      = dff["zona"].nunique()
en_desarrollo = int(dff[dff["anio_construccion"] > 2026].shape[0])

k1, k2, k3, k4, k5 = st.columns(5)
cards = [
    (k1, "Total propiedades", f"{total:,}", f"{n_zonas} zonas relevadas", ""),
    (k2, "Precio promedio", f"U$S {precio_prom:,.0f}", "media del mercado filtrado", "gold"),
    (k3, "Precio mediano", f"U$S {precio_med:,.0f}", "50° percentil del mercado", ""),
    (k4, "Precio mediano / m²", f"U$S {pm2_med:,.0f}" if pd.notna(pm2_med) else "N/D", "por metro cuadrado", "gold"),
    (k5, "En desarrollo futuro", f"{en_desarrollo:,}", "entrega estimada 2027+", ""),
]
for col, label, val, delta, extra_class in cards:
    with col:
        st.markdown(
            f'<div class="kpi-card {extra_class}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div>'
            f'<div class="kpi-delta">{delta}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Fila 1: Precio por zona + Histograma ─────────────────────────────────────
col1, col2 = st.columns([1.3, 1])

PLOTLY_BASE = dict(
    plot_bgcolor=WHITE, paper_bgcolor=WHITE,
    font=dict(family="Inter", size=12, color=BLACK),
    margin=dict(l=0, r=10, t=15, b=10),
)

with col1:
    st.markdown('<div class="section-header">Precio mediano por zona</div>', unsafe_allow_html=True)
    por_zona = (
        dff.groupby("zona")
        .agg(precio_mediano=("precio_usd", "median"), cantidad=("id", "count"))
        .query("cantidad >= 3")
        .sort_values("precio_mediano", ascending=True)
        .tail(15)
    )
    fig = px.bar(
        por_zona, x="precio_mediano", y=por_zona.index,
        orientation="h",
        color="precio_mediano",
        color_continuous_scale=[[0, "#e0e0e0"], [1, BLACK]],
        text=por_zona["precio_mediano"].apply(lambda x: f"U$S {x:,.0f}"),
        custom_data=[por_zona["cantidad"]],
    )
    fig.update_traces(
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Mediana: U$S %{x:,.0f}<br>Propiedades: %{customdata[0]}<extra></extra>",
    )
    fig.update_layout(
        height=430, coloraxis_showscale=False,
        xaxis=dict(title="", showgrid=True, gridcolor=GRAY_2, tickformat="$,.0f"),
        yaxis=dict(title=""),
        **PLOTLY_BASE,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Distribución de precios</div>', unsafe_allow_html=True)
    fig2 = px.histogram(
        dff[dff["precio_usd"] <= dff["precio_usd"].quantile(0.97)],
        x="precio_usd", nbins=40,
        color_discrete_sequence=[BLACK],
        opacity=0.85,
    )
    fig2.add_vline(
        x=precio_med, line_dash="dash", line_color=GOLD, line_width=2,
        annotation_text=f"Mediana  U$S {precio_med:,.0f}",
        annotation_position="top right",
        annotation_font_color=GOLD, annotation_font_size=11,
    )
    fig2.update_layout(
        height=430,
        xaxis=dict(title="Precio (U$S)", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        yaxis=dict(title="Propiedades", showgrid=True, gridcolor=GRAY_2),
        **PLOTLY_BASE,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Fila 2: Box plot + Evolución anual ───────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">Precio / m² por cantidad de dormitorios</div>', unsafe_allow_html=True)
    df_m2 = dff[dff["precio_m2"].notna() & dff["dormitorios"].notna()].copy()
    df_m2["dorms_label"] = df_m2["dormitorios"].astype(int).apply(
        lambda x: f"{x} dorm." if x <= 4 else "5+ dorm."
    )
    fig3 = px.box(
        df_m2, x="dorms_label", y="precio_m2",
        color="dorms_label",
        color_discrete_sequence=["#d4d4d4", "#a3a3a3", "#737373", "#404040", BLACK],
        points=False,
    )
    fig3.update_layout(
        height=390, showlegend=False,
        xaxis=dict(title="Dormitorios"),
        yaxis=dict(title="U$S / m²", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        **PLOTLY_BASE,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-header">Volumen y precio por año de entrega</div>', unsafe_allow_html=True)
    df_anio = dff[
        dff["anio_construccion"].notna()
        & dff["anio_construccion"].between(2016, 2030)
    ].copy()
    por_anio = (
        df_anio.groupby("anio_construccion")
        .agg(cantidad=("id", "count"), precio_prom=("precio_usd", "mean"))
        .reset_index()
    )
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(
        go.Bar(x=por_anio["anio_construccion"], y=por_anio["cantidad"],
               name="Propiedades", marker_color=BLACK, opacity=0.85),
        secondary_y=False,
    )
    fig4.add_trace(
        go.Scatter(x=por_anio["anio_construccion"], y=por_anio["precio_prom"],
                   name="Precio prom.", line=dict(color=GOLD, width=2.5),
                   mode="lines+markers", marker=dict(size=6)),
        secondary_y=True,
    )
    fig4.update_layout(
        height=390, legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis=dict(showgrid=False, dtick=1, tickangle=-45),
        yaxis=dict(title="Cantidad", showgrid=True, gridcolor=GRAY_2),
        yaxis2=dict(tickformat="$,.0f", title="Precio prom. U$S"),
        **PLOTLY_BASE,
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Mapa ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Mapa de mercado — Punta del Este</div>', unsafe_allow_html=True)

df_mapa = dff[dff["latitud"].notna() & dff["longitud"].notna()].copy()

if not df_mapa.empty:
    lat_c = df_mapa["latitud"].median()
    lon_c = df_mapa["longitud"].median()
    m = folium.Map(location=[lat_c, lon_c], zoom_start=13, tiles="CartoDB positron")

    def color_precio(p):
        if pd.isna(p):     return "#94a3b8"
        if p < 200_000:    return "#6b7280"
        if p < 500_000:    return "#374151"
        if p < 1_000_000:  return GOLD
        return "#7c2d12"

    sample = df_mapa.sample(min(1000, len(df_mapa)), random_state=42)
    for _, row in sample.iterrows():
        popup_html = (
            f"<div style='font-family:Inter,sans-serif;font-size:12px;width:220px'>"
            f"<b style='font-size:13px'>{str(row['titulo'])[:55]}</b><br>"
            f"<span style='color:#6b7280'>{row['zona']}</span><br><br>"
            f"<b>U$S {row['precio_usd']:,.0f}</b>"
            f"{'  ·  ' + str(int(row['dormitorios'])) + ' dorms.' if pd.notna(row.get('dormitorios')) else ''}<br>"
            f"{'Año: ' + str(int(row['anio_construccion'])) if pd.notna(row.get('anio_construccion')) and row['anio_construccion'] > 0 else ''}<br><br>"
            f"<a href='{row['link']}' target='_blank' style='color:#c9a84c;font-weight:600'>Ver en InfoCasas →</a>"
            f"</div>"
        )
        folium.CircleMarker(
            location=[row["latitud"], row["longitud"]],
            radius=5, color=color_precio(row["precio_usd"]),
            fill=True, fill_opacity=0.8, weight=1,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    legend = """
    <div style="position:fixed;bottom:28px;left:28px;background:white;padding:12px 16px;
                border-radius:4px;box-shadow:0 2px 12px rgba(0,0,0,0.12);
                font-family:Inter,sans-serif;font-size:11px;z-index:1000;border-top:3px solid #0a0a0a">
        <b style="letter-spacing:1px;text-transform:uppercase;font-size:10px">Precio U$S</b><br><br>
        <span style="color:#6b7280">●</span> &lt; 200k &nbsp;&nbsp;
        <span style="color:#374151">●</span> 200k–500k<br>
        <span style="color:#c9a84c">●</span> 500k–1M &nbsp;
        <span style="color:#7c2d12">●</span> &gt; 1M
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    st_folium(m, height=500, use_container_width=True)
else:
    st.info("Sin coordenadas disponibles para el filtro actual.")

# ── Fila final: Ranking + Scatter ─────────────────────────────────────────────
col5, col6 = st.columns([1, 1.2])

with col5:
    st.markdown('<div class="section-header">Ranking de zonas</div>', unsafe_allow_html=True)
    ranking = (
        dff.groupby("zona")
        .agg(cantidad=("id", "count"), precio_med=("precio_usd", "median"), precio_m2_med=("precio_m2", "median"))
        .sort_values("cantidad", ascending=False)
        .head(12).reset_index()
    )
    ranking["Precio mediano"] = ranking["precio_med"].apply(lambda x: f"U$S {x:,.0f}")
    ranking["U$S / m²"]       = ranking["precio_m2_med"].apply(lambda x: f"U$S {x:,.0f}" if pd.notna(x) else "—")
    st.dataframe(
        ranking[["zona", "cantidad", "Precio mediano", "U$S / m²"]].rename(columns={"zona": "Zona", "cantidad": "Propiedades"}),
        hide_index=True, use_container_width=True, height=400,
    )

with col6:
    st.markdown('<div class="section-header">Relación precio vs. superficie</div>', unsafe_allow_html=True)
    df_sc = dff[dff["m2"].between(15, 400) & dff["precio_usd"].notna()].copy()
    top_zonas = df_sc["zona"].value_counts().head(8).index.tolist()
    df_sc["zona_plot"] = df_sc["zona"].where(df_sc["zona"].isin(top_zonas), other="Otras")
    colores = ["#0a0a0a","#374151","#6b7280","#9ca3af","#d1d5db",GOLD,"#92400e","#b45309"]
    fig5 = px.scatter(
        df_sc.sample(min(700, len(df_sc)), random_state=1),
        x="m2", y="precio_usd", color="zona_plot",
        opacity=0.6, color_discrete_sequence=colores,
        hover_data={"titulo": True, "dormitorios": True, "zona": True},
    )
    fig5.update_layout(
        height=400,
        xaxis=dict(title="Superficie (m²)", showgrid=True, gridcolor=GRAY_2),
        yaxis=dict(title="Precio (U$S)", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        legend=dict(title="Zona"),
        **PLOTLY_BASE,
    )
    st.plotly_chart(fig5, use_container_width=True)

# ── Tabla + Export ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Listado completo de propiedades</div>', unsafe_allow_html=True)

busqueda = st.text_input("", placeholder="Buscar por título, zona o palabra clave...")
df_tabla = dff.copy()
if busqueda:
    m_b = (
        df_tabla["titulo"].str.contains(busqueda, case=False, na=False)
        | df_tabla["zona"].str.contains(busqueda, case=False, na=False)
    )
    df_tabla = df_tabla[m_b]

cols = ["titulo", "zona", "precio_usd", "dormitorios", "banos", "m2", "precio_m2", "anio_construccion", "link"]
df_display = (
    df_tabla[cols]
    .rename(columns={
        "titulo": "Título", "zona": "Zona", "precio_usd": "Precio U$S",
        "dormitorios": "Dorms", "banos": "Baños", "m2": "m²",
        "precio_m2": "U$S/m²", "anio_construccion": "Año entrega", "link": "Link",
    })
    .sort_values("Precio U$S", ascending=False)
)

st.dataframe(
    df_display, hide_index=True, use_container_width=True, height=440,
    column_config={
        "Precio U$S":    st.column_config.NumberColumn(format="U$S %d"),
        "U$S/m²":        st.column_config.NumberColumn(format="U$S %d"),
        "Link":          st.column_config.LinkColumn("Enlace"),
        "Año entrega":   st.column_config.NumberColumn(format="%d"),
    },
)

col_dl, _ = st.columns([1, 5])
with col_dl:
    csv = df_tabla[cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Exportar CSV", csv,
        file_name="xukah_mercado_pde.csv", mime="text/csv",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="xukah-footer">
    Xukah Real Estate &nbsp;·&nbsp; Reporte de mercado Punta del Este &nbsp;·&nbsp;
    Datos: InfoCasas mayo 2026 &nbsp;·&nbsp; Documento confidencial de uso interno
</div>
""", unsafe_allow_html=True)

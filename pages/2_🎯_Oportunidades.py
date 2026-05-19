import streamlit as st
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

st.set_page_config(page_title="Oportunidades · Xukah", page_icon="🎯", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

logo = logo_b64()
render_header(logo, "Detector de Oportunidades")

df = cargar_datos()

with st.sidebar:
    render_sidebar_logo(logo)
    st.markdown('<div style="font-size:0.7rem;letter-spacing:2px;color:#666;text-transform:uppercase;margin-bottom:0.8rem">Filtros</div>', unsafe_allow_html=True)
    umbral = st.slider("Descuento mínimo vs mediana de zona (%)", 5, 40, 15)
    zonas_disp = sorted(df["zona"].dropna().unique())
    zonas_sel  = st.multiselect("Zonas", zonas_disp, default=zonas_disp)
    precio_max = st.number_input("Precio máximo (U$S)", value=1_000_000, step=50_000)

# Filtrar oportunidades
opps = df[
    (df["pct_vs_mediana"] <= -umbral)
    & df["zona"].isin(zonas_sel if zonas_sel else zonas_disp)
    & (df["precio_usd"] <= precio_max)
].copy()
opps = opps.sort_values("pct_vs_mediana")

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
ahorro_prom = (opps["mediana_zona"] - opps["precio_usd"]).mean()
mejor = opps.iloc[0] if len(opps) else None

with k1:
    st.markdown(kpi("Oportunidades detectadas", f"{len(opps):,}", f"con ≥{umbral}% bajo mediana"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi("Ahorro promedio", f"U$S {ahorro_prom:,.0f}" if len(opps) else "—", "vs. precio mediano de zona", gold=True), unsafe_allow_html=True)
with k3:
    val = f"U$S {mejor['precio_usd']:,.0f}" if mejor is not None else "—"
    st.markdown(kpi("Mejor oportunidad", val, f"{mejor['pct_vs_mediana']:.1f}% bajo mediana" if mejor is not None else ""), unsafe_allow_html=True)
with k4:
    zonas_con_opps = opps["zona"].nunique()
    st.markdown(kpi("Zonas con oportunidades", str(zonas_con_opps), "zonas distintas"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if opps.empty:
    st.info(f"No hay propiedades con más de {umbral}% de descuento vs. la mediana de su zona. Bajá el umbral.")
    st.stop()

# ── Gráfico: oportunidades por zona ──────────────────────────────────────────
col1, col2 = st.columns([1, 1.4])

with col1:
    st.markdown('<div class="section-header">Oportunidades por zona</div>', unsafe_allow_html=True)
    por_zona = opps.groupby("zona").agg(
        cantidad=("id", "count"),
        descuento_prom=("pct_vs_mediana", "mean")
    ).sort_values("cantidad", ascending=True).tail(12)
    fig = px.bar(
        por_zona, x="cantidad", y=por_zona.index, orientation="h",
        color="descuento_prom",
        color_continuous_scale=[[0, GOLD], [1, "#7c2d12"]],
        text="cantidad",
    )
    fig.update_layout(
        height=380, coloraxis_showscale=False,
        xaxis=dict(title="Cantidad", showgrid=True, gridcolor=GRAY_2),
        yaxis_title="", **PLOTLY_BASE
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Precio real vs. mediana de zona</div>', unsafe_allow_html=True)
    muestra = opps.head(30).copy()
    muestra["label"] = muestra["titulo"].str[:35] + "..."
    fig2 = px.scatter(
        muestra, x="mediana_zona", y="precio_usd",
        color="zona", size_max=10, opacity=0.8,
        hover_data={"titulo": True, "zona": True, "pct_vs_mediana": True},
        color_discrete_sequence=[BLACK, GOLD, "#6b7280", "#92400e", "#374151", "#b45309"],
    )
    rango = [min(muestra["precio_usd"].min(), muestra["mediana_zona"].min()),
             max(muestra["precio_usd"].max(), muestra["mediana_zona"].max())]
    fig2.add_shape(type="line", x0=rango[0], y0=rango[0], x1=rango[1], y1=rango[1],
                   line=dict(color=GRAY_3, dash="dash", width=1))
    fig2.add_annotation(x=rango[1], y=rango[1], text="Precio = Mediana",
                        showarrow=False, font=dict(color=GRAY_3, size=10), xanchor="right")
    fig2.update_layout(
        height=380,
        xaxis=dict(title="Mediana zona (U$S)", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        yaxis=dict(title="Precio propiedad (U$S)", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tabla de oportunidades ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Listado de oportunidades</div>', unsafe_allow_html=True)

busqueda = st.text_input("", placeholder="Buscar por zona o título...")
df_tab = opps.copy()
if busqueda:
    df_tab = df_tab[
        df_tab["titulo"].str.contains(busqueda, case=False, na=False)
        | df_tab["zona"].str.contains(busqueda, case=False, na=False)
    ]

cols = ["titulo", "zona", "precio_usd", "mediana_zona", "pct_vs_mediana", "dormitorios", "m2", "link"]
df_show = df_tab[cols].rename(columns={
    "titulo": "Título", "zona": "Zona", "precio_usd": "Precio U$S",
    "mediana_zona": "Mediana zona", "pct_vs_mediana": "% vs mediana",
    "dormitorios": "Dorms", "m2": "m²", "link": "Link"
}).sort_values("% vs mediana")

st.dataframe(
    df_show, hide_index=True, use_container_width=True, height=420,
    column_config={
        "Precio U$S":   st.column_config.NumberColumn(format="U$S %d"),
        "Mediana zona": st.column_config.NumberColumn(format="U$S %d"),
        "% vs mediana": st.column_config.NumberColumn(format="%.1f%%"),
        "Link":         st.column_config.LinkColumn("Enlace"),
    },
)

col_dl, _ = st.columns([1, 5])
with col_dl:
    csv = df_tab[cols].to_csv(index=False).encode("utf-8")
    st.download_button("Exportar oportunidades CSV", csv, "xukah_oportunidades.csv", "text/csv")

footer()

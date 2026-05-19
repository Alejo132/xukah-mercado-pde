import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

st.set_page_config(page_title="Comparador · Xukah", page_icon="📊", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

logo = logo_b64()
render_header(logo, "Comparador de Zonas")

df = cargar_datos()

with st.sidebar:
    render_sidebar_logo(logo)
    st.markdown('<div style="font-size:0.7rem;letter-spacing:2px;color:#666;text-transform:uppercase;margin-bottom:0.8rem">Selección</div>', unsafe_allow_html=True)
    zonas_disp = sorted(df["zona"].dropna().unique())
    zonas_sel  = st.multiselect("Zonas a comparar (máx 4)", zonas_disp, default=zonas_disp[:3], max_selections=4)
    dorms_fil  = st.multiselect("Dormitorios", sorted(df["dormitorios"].dropna().unique().astype(int).tolist()), default=[1,2,3])

if len(zonas_sel) < 2:
    st.info("Seleccioná al menos 2 zonas en el panel lateral.")
    st.stop()

dff = df[df["zona"].isin(zonas_sel) & df["dormitorios"].isin(dorms_fil)].copy()

# ── Tabla resumen ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Resumen comparativo</div>', unsafe_allow_html=True)

resumen = []
for zona in zonas_sel:
    z = dff[dff["zona"] == zona]
    resumen.append({
        "Zona": zona,
        "Propiedades": len(z),
        "Precio mediano": f"U$S {z['precio_usd'].median():,.0f}" if len(z) else "—",
        "Precio promedio": f"U$S {z['precio_usd'].mean():,.0f}" if len(z) else "—",
        "Mediano / m²": f"U$S {z['precio_m2'].median():,.0f}" if z['precio_m2'].notna().any() else "—",
        "m² promedio": f"{z['m2'].mean():,.0f} m²" if z['m2'].notna().any() else "—",
        "Precio mínimo": f"U$S {z['precio_usd'].min():,.0f}" if len(z) else "—",
        "Precio máximo": f"U$S {z['precio_usd'].max():,.0f}" if len(z) else "—",
    })

st.dataframe(pd.DataFrame(resumen), hide_index=True, use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Gráficos lado a lado ──────────────────────────────────────────────────────
col1, col2 = st.columns(2)
COLORES = [BLACK, GOLD, "#6b7280", "#92400e"]

with col1:
    st.markdown('<div class="section-header">Precio mediano por zona</div>', unsafe_allow_html=True)
    medianas = [dff[dff["zona"]==z]["precio_usd"].median() for z in zonas_sel]
    fig = go.Figure(go.Bar(
        x=zonas_sel, y=medianas,
        marker_color=COLORES[:len(zonas_sel)],
        text=[f"U$S {v:,.0f}" for v in medianas],
        textposition="outside",
    ))
    fig.update_layout(
        height=360, yaxis=dict(tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        xaxis_title="", yaxis_title="U$S", showlegend=False, **PLOTLY_BASE
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Precio mediano por m²</div>', unsafe_allow_html=True)
    pm2s = [dff[dff["zona"]==z]["precio_m2"].median() for z in zonas_sel]
    fig2 = go.Figure(go.Bar(
        x=zonas_sel, y=pm2s,
        marker_color=COLORES[:len(zonas_sel)],
        text=[f"U$S {v:,.0f}" if pd.notna(v) else "—" for v in pm2s],
        textposition="outside",
    ))
    fig2.update_layout(
        height=360, yaxis=dict(tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        xaxis_title="", yaxis_title="U$S/m²", showlegend=False, **PLOTLY_BASE
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown('<div class="section-header">Distribución de precios por zona</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    for i, zona in enumerate(zonas_sel):
        z = dff[dff["zona"]==zona]["precio_usd"].dropna()
        fig3.add_trace(go.Box(y=z, name=zona, marker_color=COLORES[i], boxpoints=False))
    fig3.update_layout(
        height=360, yaxis=dict(tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        showlegend=False, **PLOTLY_BASE
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown('<div class="section-header">Volumen por dormitorios</div>', unsafe_allow_html=True)
    fig4 = go.Figure()
    dorms_labels = sorted(dff["dormitorios"].dropna().unique().astype(int))
    for i, zona in enumerate(zonas_sel):
        z = dff[dff["zona"]==zona]
        counts = [len(z[z["dormitorios"]==d]) for d in dorms_labels]
        fig4.add_trace(go.Bar(
            name=zona, x=[f"{d} dorm." for d in dorms_labels],
            y=counts, marker_color=COLORES[i],
        ))
    fig4.update_layout(
        height=360, barmode="group",
        yaxis=dict(showgrid=True, gridcolor=GRAY_2, title="Propiedades"),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig4, use_container_width=True)

footer()

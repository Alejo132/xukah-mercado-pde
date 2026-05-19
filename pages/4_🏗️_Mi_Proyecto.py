import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

st.set_page_config(page_title="Mi Proyecto · Xukah", page_icon="🏗️", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

logo = logo_b64()
render_header(logo, "Posicionamiento de Proyecto vs. Mercado")

df = cargar_datos()

# ── Inputs del proyecto ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">Datos del proyecto</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    nombre_proy    = st.text_input("Nombre del proyecto", value="Proyecto Xukah PDE")
    zona_proy      = st.selectbox("Zona", sorted(df["zona"].unique()))
    estado_proy    = st.selectbox("Estado", ["En pozo", "En construcción", "A estrenar"])
with col_b:
    precio_proy    = st.number_input("Precio de lanzamiento (U$S)", value=350_000, step=10_000)
    m2_proy        = st.number_input("Superficie promedio (m²)", value=90, step=5)
    dorms_proy     = st.selectbox("Dormitorios", [1, 2, 3, 4, 5], index=1)
with col_c:
    unidades_proy  = st.number_input("Total de unidades", value=30, step=1)
    unidades_vend  = st.number_input("Unidades vendidas / reservadas", value=0, step=1)
    entrega_proy   = st.number_input("Año de entrega estimado", value=2027, step=1, min_value=2024, max_value=2035)

# ── Mercado de referencia ─────────────────────────────────────────────────────
mercado = df[(df["zona"] == zona_proy) & (df["dormitorios"] == dorms_proy)].copy()
mercado_zona = df[df["zona"] == zona_proy].copy()

pm2_proy   = precio_proy / m2_proy if m2_proy > 0 else 0
pm2_mkt    = mercado["precio_m2"].median()
pmed_mkt   = mercado["precio_usd"].median()
pct_pm2    = ((pm2_proy - pm2_mkt) / pm2_mkt * 100) if pd.notna(pm2_mkt) and pm2_mkt > 0 else None
pct_precio = ((precio_proy - pmed_mkt) / pmed_mkt * 100) if pd.notna(pmed_mkt) and pmed_mkt > 0 else None
absorcion  = (unidades_vend / unidades_proy * 100) if unidades_proy > 0 else 0
valor_total = precio_proy * unidades_proy
vendido_val = precio_proy * unidades_vend

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">Posicionamiento del proyecto</div>', unsafe_allow_html=True)

r1, r2, r3, r4, r5 = st.columns(5)
with r1:
    st.markdown(kpi("Valor total del proyecto", f"U$S {valor_total:,.0f}", f"{unidades_proy} unidades"), unsafe_allow_html=True)
with r2:
    pct_str = f"{'▲' if pct_precio and pct_precio > 0 else '▼'} {abs(pct_precio):.1f}% vs mediana zona" if pct_precio else "sin ref."
    st.markdown(kpi("Precio vs. mercado", f"U$S {precio_proy:,.0f}", pct_str, gold=(pct_precio is not None and pct_precio < 0)), unsafe_allow_html=True)
with r3:
    pm2_str = f"{'▲' if pct_pm2 and pct_pm2 > 0 else '▼'} {abs(pct_pm2):.1f}% vs zona" if pct_pm2 else "sin ref."
    st.markdown(kpi("Precio / m²", f"U$S {pm2_proy:,.0f}", pm2_str), unsafe_allow_html=True)
with r4:
    st.markdown(kpi("Absorción", f"{absorcion:.0f}%", f"U$S {vendido_val:,.0f} vendido", gold=absorcion > 50), unsafe_allow_html=True)
with r5:
    comp_zona = len(mercado)
    st.markdown(kpi("Competencia en zona", f"{comp_zona}", f"props. similares en {zona_proy}"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráficos ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Precio/m² del proyecto vs. competencia en zona</div>', unsafe_allow_html=True)
    df_comp = mercado[mercado["precio_m2"].notna()].copy()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df_comp["precio_m2"], nbinsx=25,
        marker_color=GRAY_2, name="Mercado zona",
        hovertemplate="U$S %{x:,.0f}<br>Count: %{y}<extra></extra>",
    ))
    fig.add_vline(
        x=pm2_proy, line_color=GOLD, line_width=3, line_dash="solid",
        annotation_text=f"  {nombre_proy}<br>  U$S {pm2_proy:,.0f}/m²",
        annotation_position="top right",
        annotation_font_color=GOLD, annotation_font_size=11,
    )
    if pd.notna(pm2_mkt):
        fig.add_vline(
            x=pm2_mkt, line_color=BLACK, line_width=1.5, line_dash="dash",
            annotation_text=f"  Mediana U$S {pm2_mkt:,.0f}",
            annotation_position="top left",
            annotation_font_color=BLACK, annotation_font_size=10,
        )
    fig.update_layout(
        height=370, showlegend=False,
        xaxis=dict(title="U$S / m²", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        yaxis=dict(title="Propiedades", showgrid=True, gridcolor=GRAY_2),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Precio total del proyecto vs. competencia</div>', unsafe_allow_html=True)
    df_zona = mercado_zona[mercado_zona["precio_usd"].notna()].copy()
    fig2 = go.Figure()
    fig2.add_trace(go.Box(
        y=df_zona["precio_usd"], name="Mercado zona",
        marker_color=GRAY_2, boxpoints=False, line_color=GRAY_3,
    ))
    fig2.add_trace(go.Scatter(
        x=["Mercado zona"], y=[precio_proy],
        mode="markers",
        marker=dict(color=GOLD, size=16, symbol="diamond", line=dict(color=BLACK, width=2)),
        name=nombre_proy,
    ))
    fig2.update_layout(
        height=370, showlegend=True,
        yaxis=dict(title="Precio U$S", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Ventas simuladas ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Simulación de ventas y flujo de ingresos</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    velocidad = st.slider("Velocidad de venta (unidades/mes)", 1, 10, 3)
    meses = list(range(0, int(unidades_proy / velocidad) + 2))
    vendidas = [min(int(v * velocidad + unidades_vend), unidades_proy) for v in meses]
    ingresos_acum = [v * precio_proy for v in vendidas]
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=meses, y=vendidas, name="Unidades vendidas", marker_color=BLACK, yaxis="y"))
    fig3.add_trace(go.Scatter(
        x=meses, y=ingresos_acum, name="Ingresos acum. U$S",
        line=dict(color=GOLD, width=2.5), mode="lines+markers", yaxis="y2"
    ))
    fig3.update_layout(
        height=340,
        xaxis=dict(title="Meses desde lanzamiento", showgrid=False),
        yaxis=dict(title="Unidades", showgrid=True, gridcolor=GRAY_2),
        yaxis2=dict(title="Ingresos U$S", overlaying="y", side="right", tickformat="$,.0f"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("**Resumen financiero del proyecto**")
    ingreso_total   = precio_proy * unidades_proy
    margen_estimado = st.slider("Margen bruto estimado (%)", 10, 50, 25)
    costo_total     = ingreso_total * (1 - margen_estimado / 100)
    ganancia        = ingreso_total - costo_total

    data_fin = {
        "Concepto": ["Valor bruto del proyecto", "Costo estimado de desarrollo", "Ganancia bruta estimada"],
        "Monto U$S": [ingreso_total, costo_total, ganancia],
    }
    df_fin = pd.DataFrame(data_fin)

    fig4 = go.Figure(go.Bar(
        x=df_fin["Concepto"], y=df_fin["Monto U$S"],
        marker_color=[BLACK, GRAY_3, GOLD],
        text=[f"U$S {v:,.0f}" for v in df_fin["Monto U$S"]],
        textposition="outside",
    ))
    fig4.update_layout(
        height=340, showlegend=False,
        yaxis=dict(tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        xaxis_title="",
        **PLOTLY_BASE
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown(f"""
    | | |
    |---|---|
    | **Ingreso total** | U$S {ingreso_total:,.0f} |
    | **Costo estimado** | U$S {costo_total:,.0f} |
    | **Ganancia bruta** | U$S {ganancia:,.0f} |
    | **Margen** | {margen_estimado}% |
    | **Meses para vender todo** | ~{int(unidades_proy / velocidad)} meses |
    """)

footer()

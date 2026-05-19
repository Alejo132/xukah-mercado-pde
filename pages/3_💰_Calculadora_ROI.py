import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

st.set_page_config(page_title="ROI · Xukah", page_icon="💰", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

logo = logo_b64()
render_header(logo, "Calculadora de Retorno de Inversión")

df = cargar_datos()

# ── Inputs ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Parámetros de la inversión</div>', unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)

with col_i1:
    st.markdown("**Propiedad**")
    precio_compra   = st.number_input("Precio de compra (U$S)", value=300_000, step=10_000)
    zona_ref        = st.selectbox("Zona de referencia", sorted(df["zona"].unique()))
    m2_prop         = st.number_input("Superficie (m²)", value=80, step=5)
    dormitorios_ref = st.selectbox("Dormitorios", [1, 2, 3, 4, 5], index=1)

with col_i2:
    st.markdown("**Costos de compra (Uruguay)**")
    itp             = st.slider("ITP y escribanía (%)", 0.0, 10.0, 6.5, 0.5)
    gastos_anuales  = st.slider("Gastos anuales / mantenimiento (%)", 0.0, 5.0, 2.0, 0.5)
    st.markdown("**Financiación**")
    pct_financiado  = st.slider("Porcentaje financiado (%)", 0, 80, 0, 5)
    tasa_anual      = st.slider("Tasa de interés anual (%)", 3.0, 15.0, 7.0, 0.5) if pct_financiado > 0 else 0.0
    anos_credito    = st.slider("Plazo del crédito (años)", 5, 25, 15) if pct_financiado > 0 else 0

with col_i3:
    st.markdown("**Rentabilidad**")
    alquiler_mensual = st.number_input("Alquiler mensual estimado (U$S)", value=1_500, step=100)
    ocupacion_pct    = st.slider("Ocupación estimada (%)", 50, 100, 85)
    apreciacion_anual = st.slider("Apreciación anual estimada (%)", 0.0, 10.0, 3.5, 0.5)
    anos_inversion   = st.slider("Horizonte de inversión (años)", 1, 20, 10)

# ── Cálculos ──────────────────────────────────────────────────────────────────
gastos_compra    = precio_compra * (itp / 100)
inversion_total  = precio_compra + gastos_compra
capital_propio   = inversion_total * (1 - pct_financiado / 100)
monto_financiado = inversion_total * (pct_financiado / 100)

# Cuota mensual hipoteca
if pct_financiado > 0 and anos_credito > 0:
    tasa_mensual = tasa_anual / 100 / 12
    n_cuotas = anos_credito * 12
    cuota_mensual = monto_financiado * (tasa_mensual * (1 + tasa_mensual)**n_cuotas) / ((1 + tasa_mensual)**n_cuotas - 1)
    total_intereses = cuota_mensual * n_cuotas - monto_financiado
else:
    cuota_mensual    = 0
    total_intereses  = 0

# Ingresos y egresos anuales
alquiler_anual    = alquiler_mensual * 12 * (ocupacion_pct / 100)
egresos_anuales   = precio_compra * (gastos_anuales / 100) + cuota_mensual * 12
ingreso_neto_anual = alquiler_anual - egresos_anuales

# Valor final de la propiedad
valor_final = precio_compra * ((1 + apreciacion_anual / 100) ** anos_inversion)
plusvalia   = valor_final - precio_compra

# Totales
total_ingresos_alquiler = ingreso_neto_anual * anos_inversion
ganancia_total = total_ingresos_alquiler + plusvalia
roi_total = (ganancia_total / capital_propio) * 100
roi_anual = ((1 + ganancia_total / capital_propio) ** (1 / anos_inversion) - 1) * 100
cap_rate  = (alquiler_anual / precio_compra) * 100
payback   = capital_propio / (ingreso_neto_anual + plusvalia / anos_inversion) if (ingreso_neto_anual + plusvalia / anos_inversion) > 0 else None

# Referencia de mercado
zona_df   = df[(df["zona"] == zona_ref) & (df["dormitorios"] == dormitorios_ref) & df["precio_m2"].notna()]
pm2_zona  = zona_df["precio_m2"].median()
pm2_prop  = precio_compra / m2_prop if m2_prop > 0 else 0
pct_vs_m  = ((pm2_prop - pm2_zona) / pm2_zona * 100) if pd.notna(pm2_zona) and pm2_zona > 0 else None

# ── KPIs resultado ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">Resultados de la simulación</div>', unsafe_allow_html=True)

r1, r2, r3, r4, r5 = st.columns(5)
with r1:
    st.markdown(kpi("Inversión total", f"U$S {inversion_total:,.0f}", f"Capital propio: U$S {capital_propio:,.0f}"), unsafe_allow_html=True)
with r2:
    color = roi_anual > 0
    st.markdown(kpi("ROI anual", f"{roi_anual:.1f}%", f"ROI total {anos_inversion}a: {roi_total:.0f}%", gold=color), unsafe_allow_html=True)
with r3:
    st.markdown(kpi("Cap rate", f"{cap_rate:.2f}%", "ingreso bruto / precio compra"), unsafe_allow_html=True)
with r4:
    pb = f"{payback:.1f} años" if payback and payback > 0 else "No aplica"
    st.markdown(kpi("Payback estimado", pb, "recupero de inversión"), unsafe_allow_html=True)
with r5:
    if pct_vs_m is not None:
        label = f"{'▲' if pct_vs_m > 0 else '▼'} {abs(pct_vs_m):.1f}% vs mercado"
        color_vs = pct_vs_m < 0
        st.markdown(kpi("Precio/m² vs zona", f"U$S {pm2_prop:,.0f}", label, gold=color_vs), unsafe_allow_html=True)
    else:
        st.markdown(kpi("Precio/m² propiedad", f"U$S {pm2_prop:,.0f}", "sin referencia de zona"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráficos ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">Flujo de caja acumulado</div>', unsafe_allow_html=True)
    anos = list(range(0, anos_inversion + 1))
    flujo_acum = [-capital_propio]
    for a in range(1, anos_inversion + 1):
        val_prop_a = precio_compra * ((1 + apreciacion_anual / 100) ** a)
        equity_a   = val_prop_a - (monto_financiado if a < anos_credito else 0)
        flujo_acum.append(-capital_propio + ingreso_neto_anual * a + (equity_a - precio_compra))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=anos, y=flujo_acum,
        mode="lines+markers",
        line=dict(color=GOLD, width=2.5),
        marker=dict(color=[BLACK if v < 0 else GOLD for v in flujo_acum], size=7),
        fill="tozeroy",
        fillcolor="rgba(201,168,76,0.1)",
        name="Flujo acumulado",
    ))
    fig.add_hline(y=0, line_color=GRAY_3, line_dash="dash", line_width=1)
    fig.update_layout(
        height=360, showlegend=False,
        xaxis=dict(title="Años", dtick=1, showgrid=True, gridcolor=GRAY_2),
        yaxis=dict(title="U$S", tickformat="$,.0f", showgrid=True, gridcolor=GRAY_2),
        **PLOTLY_BASE
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">Composición del retorno</div>', unsafe_allow_html=True)
    labels = ["Ingresos netos alquiler", "Plusvalía estimada", "Gastos de compra"]
    values = [max(total_ingresos_alquiler, 0), max(plusvalia, 0), gastos_compra]
    colors = [GOLD, BLACK, GRAY_3]
    fig2 = go.Figure(go.Pie(
        labels=labels, values=values,
        marker_colors=colors,
        hole=0.55,
        textinfo="label+percent",
        textfont_size=11,
    ))
    fig2.add_annotation(
        text=f"U$S {ganancia_total:,.0f}", x=0.5, y=0.5,
        font=dict(size=13, color=BLACK, family="Montserrat"), showarrow=False
    )
    fig2.update_layout(height=360, showlegend=False, **PLOTLY_BASE)
    st.plotly_chart(fig2, use_container_width=True)

# ── Tabla anual detallada ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">Proyección año a año</div>', unsafe_allow_html=True)
rows = []
for a in range(1, anos_inversion + 1):
    val_prop = precio_compra * ((1 + apreciacion_anual / 100) ** a)
    rows.append({
        "Año": a,
        "Valor propiedad": f"U$S {val_prop:,.0f}",
        "Ingreso alquiler neto": f"U$S {ingreso_neto_anual:,.0f}",
        "Plusvalía acumulada": f"U$S {val_prop - precio_compra:,.0f}",
        "Retorno acumulado": f"U$S {ingreso_neto_anual * a + (val_prop - precio_compra):,.0f}",
        "ROI acumulado": f"{((ingreso_neto_anual * a + (val_prop - precio_compra)) / capital_propio * 100):.1f}%",
    })
st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=300)

footer()

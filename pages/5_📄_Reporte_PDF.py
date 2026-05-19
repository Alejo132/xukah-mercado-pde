import streamlit as st
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import io, os, sys, base64, unicodedata
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import *

def txt(s):
    """Elimina tildes y caracteres especiales para compatibilidad con fpdf."""
    if s is None:
        return ""
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")

st.set_page_config(page_title="Reporte PDF · Xukah", page_icon="📄", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

logo = logo_b64()
render_header(logo, "Generador de Reporte PDF")

df = cargar_datos()

# ── Configuración del reporte ──────────────────────────────────────────────────
st.markdown('<div class="section-header">Configurar reporte</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    cliente     = st.text_input("Nombre del cliente / empresa", value="")
    preparado   = st.text_input("Preparado por", value="Xukah Real Estate")
with col2:
    zonas_sel   = st.multiselect("Zonas a incluir", sorted(df["zona"].unique()), default=sorted(df["zona"].unique())[:5])
    titulo_rep  = st.text_input("Título del reporte", value="Análisis de Mercado Inmobiliario")
with col3:
    incluir_opps = st.checkbox("Incluir sección de oportunidades", value=True)
    umbral_opp   = st.slider("Descuento mínimo oportunidades (%)", 5, 30, 15) if incluir_opps else 15
    incluir_tabla = st.checkbox("Incluir tabla de propiedades (top 30)", value=True)

# ── Generador PDF ─────────────────────────────────────────────────────────────
def generar_pdf():
    dff = df[df["zona"].isin(zonas_sel)] if zonas_sel else df

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Colores marca
    negro   = (10, 10, 10)
    dorado  = (201, 168, 76)
    gris    = (107, 114, 128)
    bg_gris = (245, 245, 245)

    # ── Portada ───────────────────────────────────────────────────────────────
    pdf.set_fill_color(*negro)
    pdf.rect(0, 0, 210, 60, "F")

    logo_path = os.path.join(BASE_DIR, "xukah_logo.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=15, y=10, h=20)

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 35)
    pdf.cell(180, 10, "XUKAH REAL ESTATE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*dorado)
    pdf.cell(180, 6, "INVIERTE - COMERCIALIZA", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(68)
    pdf.set_text_color(*negro)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(180, 10, txt(titulo_rep).upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*gris)
    pdf.cell(180, 7, "Punta del Este - Maldonado - Edificios 2016-2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(*dorado)
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)

    fecha = datetime.now().strftime("%d de %B de %Y")
    meta_rows = [
        ("Fecha", fecha),
        ("Preparado por", preparado),
    ]
    if cliente:
        meta_rows.insert(0, ("Cliente", cliente))

    pdf.set_font("Helvetica", "", 10)
    for label, val in meta_rows:
        pdf.set_text_color(*gris)
        pdf.cell(45, 7, txt(label) + ":", new_x=XPos.RIGHT, new_y=YPos.LAST)
        pdf.set_text_color(*negro)
        pdf.cell(130, 7, txt(val), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(8)

    # ── Sección: KPIs generales ───────────────────────────────────────────────
    def seccion(titulo):
        pdf.set_fill_color(*negro)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(180, 8, f"  {txt(titulo).upper()}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)
        pdf.set_text_color(*negro)

    def kpi_row(items):
        w = 180 // len(items)
        y0 = pdf.get_y()
        for label, val, sub in items:
            x0 = pdf.get_x()
            pdf.set_fill_color(*bg_gris)
            pdf.set_draw_color(*dorado)
            pdf.set_line_width(0.3)
            pdf.rect(pdf.get_x(), y0, w - 2, 22, "FD")
            pdf.set_xy(x0 + 2, y0 + 2)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*gris)
            pdf.cell(w - 4, 4, txt(label).upper(), new_x=XPos.RIGHT, new_y=YPos.LAST)
            pdf.set_xy(x0 + 2, y0 + 7)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(*negro)
            pdf.cell(w - 4, 7, txt(val), new_x=XPos.RIGHT, new_y=YPos.LAST)
            pdf.set_xy(x0 + 2, y0 + 15)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(*gris)
            pdf.cell(w - 4, 4, txt(sub), new_x=XPos.RIGHT, new_y=YPos.LAST)
            pdf.set_x(x0 + w)
        pdf.set_y(y0 + 25)

    seccion("Resumen del mercado")
    kpi_row([
        ("Total propiedades", f"{len(dff):,}", f"{dff['zona'].nunique()} zonas"),
        ("Precio mediano", f"U$S {dff['precio_usd'].median():,.0f}", "50 percentil"),
        ("Precio promedio", f"U$S {dff['precio_usd'].mean():,.0f}", "media del mercado"),
        ("Precio mediano/m2", f"U$S {dff['precio_m2'].median():,.0f}", "por metro cuadrado"),
    ])
    pdf.ln(2)

    # ── Tabla: precio por zona ────────────────────────────────────────────────
    seccion("Precio mediano por zona (top 10)")

    por_zona = (
        dff.groupby("zona")
        .agg(cantidad=("id","count"), mediana=("precio_usd","median"), pm2=("precio_m2","median"))
        .query("cantidad >= 3")
        .sort_values("mediana", ascending=False)
        .head(10)
        .reset_index()
    )

    headers = ["Zona", "Propiedades", "Precio mediano", "Precio/m²"]
    col_ws  = [70, 30, 45, 35]
    pdf.set_fill_color(*negro)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    for h, w in zip(headers, col_ws):
        pdf.cell(w, 7, h, fill=True, border=0, new_x=XPos.RIGHT, new_y=YPos.LAST)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for i, row in por_zona.iterrows():
        bg = bg_gris if i % 2 == 0 else (255, 255, 255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*negro)
        vals = [
            txt(row["zona"]),
            str(int(row["cantidad"])),
            f"U$S {row['mediana']:,.0f}",
            f"U$S {row['pm2']:,.0f}" if pd.notna(row["pm2"]) else "-",
        ]
        for v, w in zip(vals, col_ws):
            pdf.cell(w, 6, txt(v), fill=True, new_x=XPos.RIGHT, new_y=YPos.LAST)
        pdf.ln()

    pdf.ln(5)

    # ── Oportunidades ─────────────────────────────────────────────────────────
    if incluir_opps:
        opps = dff[dff["pct_vs_mediana"] <= -umbral_opp].sort_values("pct_vs_mediana").head(15)
        if not opps.empty:
            pdf.add_page()
            seccion(f"Oportunidades detectadas (>{umbral_opp}% bajo mediana de zona)")

            headers2 = ["Titulo", "Zona", "Precio U$S", "% vs mediana", "Link"]
            col_ws2  = [65, 32, 28, 25, 30]
            pdf.set_fill_color(*negro)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 7)
            for h, w in zip(headers2, col_ws2):
                pdf.cell(w, 7, h, fill=True, new_x=XPos.RIGHT, new_y=YPos.LAST)
            pdf.ln()

            pdf.set_font("Helvetica", "", 7)
            for i, (_, row) in enumerate(opps.iterrows()):
                bg = bg_gris if i % 2 == 0 else (255, 255, 255)
                pdf.set_fill_color(*bg)
                pdf.set_text_color(*negro)
                titulo_c = txt(str(row["titulo"]))[:42] + ("..." if len(str(row["titulo"])) > 42 else "")
                vals2 = [
                    titulo_c,
                    txt(str(row["zona"]))[:18],
                    f"U$S {row['precio_usd']:,.0f}",
                    f"{row['pct_vs_mediana']:.1f}%",
                    txt(str(row.get("link","")))[:30],
                ]
                for v, w in zip(vals2, col_ws2):
                    pdf.cell(w, 6, txt(v), fill=True, new_x=XPos.RIGHT, new_y=YPos.LAST)
                pdf.ln()
            pdf.ln(5)

    # ── Tabla de propiedades ──────────────────────────────────────────────────
    if incluir_tabla:
        if pdf.get_y() > 200:
            pdf.add_page()
        seccion("Listado de propiedades (top 30 por precio)")
        top30 = dff.sort_values("precio_usd", ascending=False).head(30)
        headers3 = ["Titulo", "Zona", "Precio U$S", "Dorms", "m2", "U$S/m2"]
        col_ws3  = [65, 32, 28, 15, 18, 22]
        pdf.set_fill_color(*negro)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 7)
        for h, w in zip(headers3, col_ws3):
            pdf.cell(w, 7, h, fill=True, new_x=XPos.RIGHT, new_y=YPos.LAST)
        pdf.ln()
        pdf.set_font("Helvetica", "", 7)
        for i, (_, row) in enumerate(top30.iterrows()):
            bg = bg_gris if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*bg)
            pdf.set_text_color(*negro)
            titulo_c = txt(str(row["titulo"]))[:42] + ("..." if len(str(row["titulo"])) > 42 else "")
            vals3 = [
                titulo_c,
                txt(str(row["zona"]))[:18],
                f"U$S {row['precio_usd']:,.0f}",
                str(int(row["dormitorios"])) if pd.notna(row.get("dormitorios")) else "-",
                f"{row['m2']:.0f}" if pd.notna(row.get("m2")) else "-",
                f"U$S {row['precio_m2']:,.0f}" if pd.notna(row.get("precio_m2")) else "-",
            ]
            for v, w in zip(vals3, col_ws3):
                pdf.cell(w, 6, v, fill=True, new_x=XPos.RIGHT, new_y=YPos.LAST)
            pdf.ln()

    # ── Footer de cada página ─────────────────────────────────────────────────
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*gris)
    pdf.cell(0, 5, f"Xukah Real Estate - {txt(titulo_rep)} - {txt(fecha)} - Documento confidencial", align="C")

    return pdf.output()


# ── Preview y descarga ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

col_prev, col_info = st.columns([1, 2])
with col_prev:
    if st.button("Generar reporte PDF"):
        with st.spinner("Generando PDF..."):
            pdf_bytes = generar_pdf()
        st.success(f"Reporte generado: {len(pdf_bytes) // 1024} KB")
        nombre_archivo = f"xukah_mercado_pde_{datetime.now().strftime('%Y%m')}.pdf"
        st.download_button(
            "Descargar PDF",
            data=pdf_bytes,
            file_name=nombre_archivo,
            mime="application/pdf",
        )

with col_info:
    zonas_str = ", ".join(zonas_sel[:5]) + ("..." if len(zonas_sel) > 5 else "") if zonas_sel else "todas"
    st.markdown(f"""
    **El PDF incluirá:**
    - Portada con logo Xukah y datos del cliente
    - KPIs: total propiedades, precio mediano, promedio, precio/m²
    - Tabla de precio mediano por zona (top 10)
    {"- Sección de oportunidades (propiedades ≥" + str(umbral_opp) + "% bajo mediana)" if incluir_opps else ""}
    {"- Listado de las 30 propiedades más caras" if incluir_tabla else ""}

    **Zonas seleccionadas:** {zonas_str}
    """)

footer()

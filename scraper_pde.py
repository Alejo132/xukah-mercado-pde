import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

ANO_MINIMO = datetime.now().year - 10  # últimos 10 años

FUENTES = [
    {
        "nombre": "a-estrenar",
        "url_base": "https://www.infocasas.com.uy/venta/apartamentos/maldonado/a-estrenar/pagina{}",
        "max_paginas": 102,
    },
    {
        "nombre": "en-construccion",
        "url_base": "https://www.infocasas.com.uy/venta/apartamentos/maldonado/en-construccion/pagina{}",
        "max_paginas": 15,
    },
    {
        "nombre": "en-pozo",
        "url_base": "https://www.infocasas.com.uy/venta/apartamentos/maldonado/en-pozo/pagina{}",
        "max_paginas": 15,
    },
    {
        "nombre": "punta-del-este-general",
        "url_base": "https://www.infocasas.com.uy/venta/apartamentos/punta-del-este/pagina{}",
        "max_paginas": 50,
    },
]


def extraer_zona(locations):
    if not locations or not isinstance(locations, dict):
        return None
    for key in ("neighbourhood", "zone", "commune", "city", "state"):
        val = locations.get(key)
        if isinstance(val, list) and val:
            return val[0].get("name")
        if isinstance(val, dict) and val.get("name"):
            return val.get("name")
    return None


def parsear_pagina(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"    Error: {e}")
        return [], False

    soup = BeautifulSoup(resp.text, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        return [], False

    data = json.loads(script.string)
    search = data["props"]["pageProps"]["fetchResult"]["searchFast"]
    items = search.get("data", [])
    hay_mas = search.get("paginatorInfo", {}).get("hasMorePages", False)

    propiedades = []
    for item in items:
        anio = item.get("construction_year") or 0
        antiguedad = item.get("antiquity")

        # Filtrar por últimos 10 años: año de construcción conocido y reciente,
        # o en construcción/pozo (anio = 0 o futuro), o antigüedad <= 10
        es_reciente = (
            (anio and anio >= ANO_MINIMO)
            or (anio == 0)  # en pozo/construcción sin año definido
            or (isinstance(antiguedad, (int, float)) and antiguedad <= 10)
            or item.get("isProject")
        )

        if not es_reciente:
            continue

        propiedades.append({
            "id": item.get("id"),
            "titulo": item.get("title"),
            "precio_usd": item.get("price_amount_usd"),
            "dormitorios": item.get("bedrooms"),
            "banos": item.get("bathrooms"),
            "m2": item.get("m2") or item.get("m2apto"),
            "m2_construidos": item.get("m2Built"),
            "zona": extraer_zona(item.get("locations")),
            "latitud": item.get("latitude"),
            "longitud": item.get("longitude"),
            "anio_construccion": anio if anio else None,
            "antiguedad_anos": antiguedad,
            "es_proyecto": item.get("isProject", False),
            "estado": item.get("constStatesID"),
            "link": "https://www.infocasas.com.uy" + item.get("link", ""),
            "imagen": item.get("img"),
        })

    return propiedades, hay_mas


def scrapear_fuente(fuente):
    nombre = fuente["nombre"]
    url_base = fuente["url_base"]
    max_pags = fuente["max_paginas"]

    print(f"\n[{nombre}] Scrapeando hasta {max_pags} páginas...")
    todas = []
    ids_vistos = set()

    for i in range(1, max_pags + 1):
        url = url_base.format(i)
        props, hay_mas = parsear_pagina(url)

        nuevas = [p for p in props if p["id"] not in ids_vistos]
        ids_vistos.update(p["id"] for p in nuevas)
        todas.extend(nuevas)

        print(f"  Pág {i}: {len(props)} totales → {len(nuevas)} nuevas recientes | acumulado: {len(todas)}")

        if not hay_mas:
            print(f"  Sin más páginas en {nombre}.")
            break

        time.sleep(random.uniform(1.0, 2.0))

    return todas


def main():
    print(f"Scrapeando Punta del Este / Maldonado — edificios desde {ANO_MINIMO}")
    todas = []
    ids_globales = set()

    for fuente in FUENTES:
        props = scrapear_fuente(fuente)
        nuevas = [p for p in props if p["id"] not in ids_globales]
        ids_globales.update(p["id"] for p in nuevas)
        todas.extend(nuevas)
        print(f"  → {len(nuevas)} propiedades únicas agregadas. Total global: {len(todas)}")

    df = pd.DataFrame(todas)
    df.to_csv("propiedades_pde.csv", index=False)

    print(f"\n{'='*50}")
    print(f"TOTAL: {len(df)} propiedades únicas guardadas en propiedades_pde.csv")
    print(f"\nPor zona:")
    print(df["zona"].value_counts().head(15).to_string())
    print(f"\nPrecio promedio: U$S {df['precio_usd'].dropna().mean():,.0f}")
    print(f"Precio mediano:  U$S {df['precio_usd'].dropna().median():,.0f}")
    return df


if __name__ == "__main__":
    main()

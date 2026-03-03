import requests, os
import pandas as pd
from datetime import datetime

URL_API = "https://app.loveat.la/api/diner/rapanui.cordoba/menu/44994"
DOLAR_URL = "https://api.comparadolar.ar/usd"
CSV = "rapanui_precios.csv"

def obtener_dolar():
    try:
        bn = next((x for x in requests.get(DOLAR_URL, timeout=10).json()
                   if x.get("slug") == "banco-nacion"), None)
        return float(bn["ask"]) if bn else 1.0
    except Exception:
        return 1.0

def main():
    print("RAPANUIBOT iniciando...")
    dolar = obtener_dolar()
    print("Dolar BN: " + str(dolar))
    hoy = datetime.now().strftime("%Y-%m-%d")
    try:
        data = requests.get(URL_API, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
    except Exception as e:
        print("Error API: " + str(e)); return
    rows = []
    for cat in data.get("categories", []):
        cat_name = cat.get("name", "")
        for plate in cat.get("plates", []):
            for size in plate.get("sizes", []):
                precio = float(size.get("price", 0) or 0)
                nombre = size.get("itemName", "").strip()
                if precio > 0 and nombre:
                    rows.append({
                        "Fecha": hoy,
                        "Categoria": cat_name,
                        "Producto": nombre,
                        "ID": size.get("id", ""),
                        "Precio_ARS": precio,
                        "Precio_USD": round(precio / dolar, 2),
                        "Dolar_ARS": dolar
                    })
    if not rows:
        print("Sin productos."); return
    df = pd.DataFrame(rows)
    if os.path.exists(CSV):
        dh = pd.read_csv(CSV)
        dh["Fecha"] = pd.to_datetime(dh["Fecha"]).dt.strftime("%Y-%m-%d")
        dh = dh[dh["Fecha"] != hoy]
        df = pd.concat([dh, df], ignore_index=True)
    df.to_csv(CSV, index=False)
    print("OK: " + str(len(rows)) + " productos para " + hoy)

if __name__ == "__main__":
    main()

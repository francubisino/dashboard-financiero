#!/usr/bin/env python3
"""
Script reutilizable: obtiene la variación % mensual del año en curso para:
  - UVA (BCRA)
  - IPC argentino (INDEC / inflación mensual)
  - CER (BCRA)
  - Dólar MEP
  - CEDEAR SPY
  - CEDEAR QQQ

Guarda los datos en benchmarks.json con formato:
  [ {"indicador": "...", "mes": "YYYY-MM", "valor": 1.23}, ... ]
  (también se puede leer como "indicador;mes;valor")

Fuentes:
  - El Tablero (API pública BCRA/INDEC): UVA, CER, IPC
  - Yahoo Finance chart API: CEDEARs SPY.BA y QQQ.BA
  - Dolarito / scraping ligero o fallback para MEP (ver notas)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, date
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
ANIO_ACTUAL = datetime.now().year
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
}
TIMEOUT = 25
OUT_JSON = "benchmarks.json"

# IDs El Tablero (https://eltablero.ar/docs)
ID_UVA = 31
ID_CER = 30
ID_IPC = 27  # Inflación mensual (%)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def mes_str(d: date | datetime | str) -> str:
    if isinstance(d, str):
        d = d[:10]
        return d[:7]
    return f"{d.year:04d}-{d.month:02d}"


def pct_change(prev: float, curr: float) -> float | None:
    if prev is None or curr is None or prev == 0:
        return None
    return round((curr / prev - 1.0) * 100.0, 4)


def get_json(url: str, params: dict | None = None) -> Any:
    r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# El Tablero: series diarias → cierre de mes → variación %
# ---------------------------------------------------------------------------
def serie_eltablero(serie_id: int, anio: int) -> list[dict]:
    """Devuelve lista de {fecha, valor} del año pedido (y un poco antes para el 1er mes)."""
    desde = f"{anio - 1}-12-01"
    hasta = f"{anio}-12-31"
    url = f"https://eltablero.ar/api/series/{serie_id}"
    data = get_json(url, {"desde": desde, "hasta": hasta})
    puntos = data.get("puntos") or []
    return [{"fecha": p["fecha"][:10], "valor": float(p["valor"])} for p in puntos]


def cierres_mensuales(puntos: list[dict], anio: int) -> dict[str, float]:
    """Último valor disponible de cada mes del año (y dic del año anterior)."""
    by_mes: dict[str, float] = {}
    for p in puntos:
        m = mes_str(p["fecha"])
        # nos quedamos con el último del mes (la serie viene ordenada)
        by_mes[m] = p["valor"]
    # filtrar solo lo que nos interesa
    out = {}
    for m, v in by_mes.items():
        y = int(m[:4])
        if y == anio or (y == anio - 1 and m.endswith("-12")):
            out[m] = v
    return out


def variaciones_desde_cierres(cierres: dict[str, float], anio: int) -> list[dict]:
    """Calcula var % mes a mes para los meses del año."""
    meses = sorted(m for m in cierres if m.startswith(str(anio)))
    res = []
    for m in meses:
        prev_y, prev_m = (int(m[:4]), int(m[5:7]))
        if prev_m == 1:
            prev_key = f"{prev_y - 1}-12"
        else:
            prev_key = f"{prev_y}-{prev_m - 1:02d}"
        prev_val = cierres.get(prev_key)
        curr_val = cierres[m]
        v = pct_change(prev_val, curr_val)
        if v is not None:
            res.append({"mes": m, "valor": v})
    return res


def obtener_uva(anio: int) -> list[dict]:
    puntos = serie_eltablero(ID_UVA, anio)
    cierres = cierres_mensuales(puntos, anio)
    return variaciones_desde_cierres(cierres, anio)


def obtener_cer(anio: int) -> list[dict]:
    puntos = serie_eltablero(ID_CER, anio)
    cierres = cierres_mensuales(puntos, anio)
    return variaciones_desde_cierres(cierres, anio)


def obtener_ipc(anio: int) -> list[dict]:
    """IPC ya viene como variación % mensual."""
    puntos = serie_eltablero(ID_IPC, anio)
    res = []
    for p in puntos:
        m = mes_str(p["fecha"])
        if m.startswith(str(anio)):
            res.append({"mes": m, "valor": round(float(p["valor"]), 4)})
    return sorted(res, key=lambda x: x["mes"])


# ---------------------------------------------------------------------------
# Yahoo Finance: CEDEARs (precios mensuales)
# ---------------------------------------------------------------------------
def yahoo_mensual(ticker: str, anio: int) -> list[dict]:
    """
    Usa el endpoint chart de Yahoo con interval=1mo.
    Devuelve variación % mes a mes del año.
    Reintenta ante 429.
    """
    import time

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    params = {"interval": "1mo", "range": "2y"}
    data = None
    last_err = None
    for intento in range(4):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 429:
                time.sleep(2 + intento * 2)
                continue
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            last_err = e
            time.sleep(1 + intento)
    if data is None:
        raise RuntimeError(f"Yahoo {ticker}: {last_err}")

    result = (data.get("chart") or {}).get("result") or []
    if not result:
        raise RuntimeError(f"Sin datos Yahoo para {ticker}")
    res0 = result[0]
    timestamps = res0.get("timestamp") or []
    closes = (res0.get("indicators") or {}).get("quote", [{}])[0].get("close") or []

    by_mes: dict[str, float] = {}
    for ts, cl in zip(timestamps, closes):
        if cl is None:
            continue
        d = datetime.fromtimestamp(ts, tz=__import__("datetime").timezone.utc).date()
        m = mes_str(d)
        by_mes[m] = float(cl)

    cierres = {
        m: v
        for m, v in by_mes.items()
        if m.startswith(str(anio)) or (m.startswith(str(anio - 1)) and m.endswith("-12"))
    }
    return variaciones_desde_cierres(cierres, anio)


def obtener_spy(anio: int) -> list[dict]:
    return yahoo_mensual("SPY.BA", anio)


def obtener_qqq(anio: int) -> list[dict]:
    return yahoo_mensual("QQQ.BA", anio)


# ---------------------------------------------------------------------------
# Dólar MEP (bolsa) – api.argentinadatos.com
# ---------------------------------------------------------------------------
def obtener_mep(anio: int) -> list[dict]:
    """
    Histórico de dólar bolsa (MEP) desde api.argentinadatos.com
    (casa = 'bolsa'). Usa precio de venta al cierre de cada mes.
    """
    url = "https://api.argentinadatos.com/v1/cotizaciones/dolares"
    data = get_json(url)
    by_mes: dict[str, float] = {}
    for row in data:
        if row.get("casa") != "bolsa":
            continue
        fecha = row.get("fecha") or ""
        if not fecha:
            continue
        m = mes_str(fecha)
        venta = row.get("venta")
        if venta is None:
            continue
        by_mes[m] = float(venta)  # último valor del mes

    cierres = {
        m: v
        for m, v in by_mes.items()
        if m.startswith(str(anio)) or (m.startswith(str(anio - 1)) and m.endswith("-12"))
    }
    if not cierres:
        print("[AVISO] Sin datos de Dólar MEP para el período.", file=sys.stderr)
        return []
    return variaciones_desde_cierres(cierres, anio)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    anio = ANIO_ACTUAL
    print(f"Obteniendo variaciones mensuales del año {anio}...")

    indicadores = [
        ("UVA", obtener_uva),
        ("IPC", obtener_ipc),
        ("CER", obtener_cer),
        ("Dolar_MEP", obtener_mep),
        ("CEDEAR_SPY", obtener_spy),
        ("CEDEAR_QQQ", obtener_qqq),
    ]

    registros: list[dict] = []
    for nombre, fn in indicadores:
        try:
            print(f"  → {nombre}...", end=" ", flush=True)
            series = fn(anio)
            for item in series:
                registros.append(
                    {
                        "indicador": nombre,
                        "mes": item["mes"],
                        "valor": item["valor"],
                    }
                )
            print(f"OK ({len(series)} meses)")
            # pausa breve entre llamadas a Yahoo / APIs externas
            import time
            time.sleep(1.2)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)

    # Ordenar por indicador y mes
    registros.sort(key=lambda r: (r["indicador"], r["mes"]))

    # Formato alternativo plano "indicador;mes;valor"
    lineas = [f"{r['indicador']};{r['mes']};{r['valor']}" for r in registros]

    payload = {
        "anio": anio,
        "generado": datetime.now().isoformat(timespec="seconds"),
        "formato_plano": lineas,
        "datos": registros,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nGuardado: {OUT_JSON}  ({len(registros)} registros)")
    print("Formato plano (ejemplo):")
    for ln in lineas[:6]:
        print(" ", ln)
    if len(lineas) > 6:
        print("  ...")


if __name__ == "__main__":
    main()

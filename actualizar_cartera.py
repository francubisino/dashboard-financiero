"""
Actualizador Automático de Cartera de Inversiones (Filtro de Renta Fija y Letras)
Autor: Quant Developer / Sr. Python Dev
Descripción: Descarga el boleto de bolsa desde Gmail, filtra y descarta instrumentos 
             de renta fija/letras/bonos, mapea las especies restantes a Tickers y 
             actualiza la cartera en Excel.
"""

import email
from email.header import decode_header
from datetime import datetime, timedelta
import imaplib
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Union
import sys
from bs4 import BeautifulSoup
import openpyxl

# ==========================================
# CONFIGURACIÓN GENERAL Y RUTAS
# ==========================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent
RUTA_CARTERA = BASE_DIR / "cartera.xlsm"

"""
Módulo de Ingesta de Credenciales desde Variables de Entorno (GitHub Secrets)
Autor: Quant Developer / Sr. Python Dev
"""

# Lectura segura desde variables de entorno inyectadas por GitHub Actions
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")

# Control de presencia de credenciales previo a la ejecución
if not GMAIL_USER or not GMAIL_PASSWORD:
    print("[!] ERROR CRÍTICO: No se encontraron las variables de entorno GMAIL_USER o GMAIL_PASSWORD.")
    print("Asegúrate de configurarlas en GitHub Secrets o en tu entorno local.")
    sys.exit(1)
    
IMAP_SERVER = "imap.gmail.com"

ASUNTO_BUSQUEDA = "Invertir en Bolsa - Adjunto archivo"

# ==========================================
# PATRONES DE ESPECIES A DESCARTAR
# ==========================================
PATRONES_EXCLUIDOS = [
    "BONO",
    "LETRA",
    "CAPITALIZABLE",
    "ESPECIES VARIAS",
    "LT REP",
    "LT TESORO",
    "L.T. NAC"
]

# ==========================================
# DICCIONARIO DE HOMOLOGACIÓN DE ESPECIES
# ==========================================
MAPEO_ESPECIES = {
    "00457 PAMPA HOLDING": "PAMP",
    "08006 CEDEAR COCA-COLA COMPANY": "KO",
    "08009 CEDEAR AMER. EXPR": "AXP",
    "08012 CEDEAR CAATERPIL": "CAT",
    "08013 CEDEAR CHEVRON C": "CVX",
    "08024 INT BUSINESS MACHINES COMPANY (IBM)": "IBM",
    "08028 Cedear JP Morgan": "JPM",
    "08030 CEDEAR MCDONALDS'S CORPORATION": "MCD",
    "08032 CEDEAR DE MICROSOFT CORP.": "MSFT",
    "08037 CEDEAR PROCTER": "PG",
    "08042 United Technologies Corp.": "RTX",
    "08044 Wal-Mart Stores Inc.": "WMT",
    "08124 CEDEAR ELI LILLY AND COMPANY": "LLY",
    "08125 CEDEAR LOCKHEED MARTIN CORPORATION": "LMT",
    "08142 ORACLE CORPORATION": "ORCL",
    "08146 CEDEAR PEPSICO INC. ESC.": "PEP",
    "08281 CEDEAR BANK OF AMERICA COORP": "BA.C",
    "08288 CEDEAR VERIZON": "VZ",
    "08297 CEDEAR TAIWAN SE": "TSM",
    "08434 CEDEAR FREEPORT": "FCX",
    "08442 CEDEAR ALPHABET INC. CL  A": "GOOGL",
    "08442 CEDEAR ALPHABET INC. CL A": "GOOGL",
    "08444 CEDEAR MERCADOLIBRE INC": "MELI",
    "08445 CEDEAR APPLE COMPUTER INC": "AAPL",
    "08467 CEDEAR META PLATFORMS INC.": "META",
    "08468 CEDEAR AMAZON. COM, INC": "AMZN",
    "08469 CEDEAR NVIDIA CORPORATION": "NVDA",
    "08474 CEDEAR NETFLIX, INC.": "NFLX",
    "08477 CEDEAR PAYPAL": "PYPL",
    "08479 CEDEAR TESLA INC": "TSLA",
    "08481 CEDEAR ADVANCED MICRO DEVICES": "AMD",
    "08526 CEDEAR PETROLEO BRASILEIRO S.A.": "PBR",
    "08527 CEDEAR VISTA OIL & GAS": "VIST",
    "08529 CEDEAR BERKSHIRE HATHWAY INC": "BRK-B",
    "08531 CEDEAR BROADCOM INC.": "AVGO",
    "08537 CEDEAR MASTERCARD INC.": "MA",
    "08541 CEDEAR UNITEDHEALTH GROUP INC": "UNH",
    "08549 CEDEAR SPDR S&P 500": "SPY",
    "08550 INVESCO QQQ TRUST CEDEAR": "QQQ",
    "08554 CEDEAR ENERGY SELECT SECTOR SPDR FUND": "XLE",
    "08556 ISHARES MSCI BRAZIL CAP": "EWZ",
    "08575 CEDEAR MICRON TECHNOLOGY INC": "MU",
    "08577 CEDEAR UBER TECHNOLOGIES INC": "UBER",
    "08596 CEDEAR NU HOLDINGS LTD/CAYMAN ISLANDS": "NU",
    "08597 CEDEAR PAGSEGURO DIGITAL LTD": "PAGS",
    "08628 CEDEAR STONECO LTD": "STNE",
    "08658 CEDEAR ETF SPDR GOLD TRUST": "GLD",
    "08672 CEDEAR THE HEALTH CARE SELECT SECT SPDR": "XLV",
    "08673 CEDEAR THE CONSUMER STAPLES SELECT": "XLC",
    "08677 CEDEAR ASML HOLDING NV": "ASML",
    "08681 CEDEAR CONSTELLATION ENERGY CORPORATION": "CEG",
    "08687 CEDEARV VISTRA CORPORATION": "VST",
    "08691 CEDEAR ETF ISHARES SILVER TRUST": "SLV",
    "08697 CEDEAR UTILITIES SELECT SECTOR SPDR FUND": "XLU",
    "08719 CEDEAR  GLOBAL X COPPER MINERS ETF": "COPX",
    "08719 CEDEAR GLOBAL X COPPER MINERS ETF": "COPX",
    "08741 CEDEAR SPACE EXP TECH CORP.": "SPCX"
}


def conectar_gmail_y_descargar_adjunto(dias_atras: int = 1) -> List[Path]:
    """Se conecta a Gmail vía IMAP y descarga los adjuntos .htm del día anterior."""
    archivos_descargados: List[Path] = []
    fecha_objetivo = datetime.now() - timedelta(days=dias_atras)
    fecha_imap = fecha_objetivo.strftime("%d-%b-%Y")

    logging.info(f"Conectando a Gmail ({GMAIL_USER}) para buscar correos del {fecha_imap}...")

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USER, GMAIL_PASSWORD)
        mail.select("inbox")

        criterio_busqueda = f'(ON "{fecha_imap}")'
        status, messages = mail.search(None, criterio_busqueda)

        if status != "OK" or not messages[0]:
            logging.warning(f"No se encontraron correos recibidos el {fecha_imap}.")
            mail.logout()
            return archivos_descargados

        msg_ids = messages[0].split()
        for msg_id in msg_ids:
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    if subject.strip().startswith(ASUNTO_BUSQUEDA):
                        for part in msg.walk():
                            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition") is None:
                                continue

                            filename = part.get_filename()
                            if filename:
                                filename_decoded, enc = decode_header(filename)[0]
                                if isinstance(filename_decoded, bytes):
                                    filename = filename_decoded.decode(enc if enc else "utf-8")

                                if filename.lower().endswith((".htm", ".html")):
                                    ruta_guardado = BASE_DIR / filename
                                    with open(ruta_guardado, "wb") as f:
                                        f.write(part.get_payload(decode=True))
                                    logging.info(f"✔ Adjunto guardado: {ruta_guardado.name}")
                                    archivos_descargados.append(ruta_guardado)

        mail.logout()
    except Exception as e:
        logging.error(f"Error durante la conexión o descarga de Gmail: {str(e)}")
        raise

    return archivos_descargados


def parsear_boleto_htm(ruta_htm: Path) -> List[Dict[str, Any]]:
    """Parsea el boleto HTM, filtra especies no deseadas y extrae las operaciones válidas."""
    logging.info(f"Analizando archivo de boleto HTML: {ruta_htm.name}...")
    operaciones: List[Dict[str, Any]] = []

    with open(ruta_htm, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    tablas_principales = soup.find_all("table")
    
    for idx, tabla in enumerate(tablas_principales):
        headers = [th.get_text(strip=True) for th in tabla.find_all("th")]
        
        if "Operación" in headers and "Especie" in headers:
            filas = tabla.find_all("tr")[1:]
            if not filas:
                continue
            cols_cabecera = [td.get_text(strip=True) for td in filas[0].find_all("td")]
            
            if len(cols_cabecera) >= 5:
                operacion_texto = cols_cabecera[2].upper()
                especie_texto = cols_cabecera[4].strip()

                # --- NUEVA VALIDACIÓN: CONTROL DE ESPECIES EXCLUIDAS ---
                especie_upper = especie_texto.upper()
                if any(patron in especie_upper for patron in PATRONES_EXCLUIDOS):
                    logging.info(f"  [x] Especie excluida por filtro de patrón: '{especie_texto}'. Omitiendo...")
                    continue

                tipo_op = "COMPRA" if "COMPRA" in operacion_texto else ("VENTA" if "VENTA" in operacion_texto else None)
                
                if idx + 1 < len(tablas_principales):
                    tabla_detalle = tablas_principales[idx + 1]
                    headers_detalle = [th.get_text(strip=True) for th in tabla_detalle.find_all("th")]
                    
                    if "Cantidad" in headers_detalle:
                        filas_detalle = tabla_detalle.find_all("tr")[1:]
                        if filas_detalle:
                            cols_detalle = [td.get_text(strip=True) for td in filas_detalle[0].find_all("td")]
                            if cols_detalle:
                                raw_cantidad = cols_detalle[0].replace("*", "").strip()
                                try:
                                    cantidad = float(raw_cantidad)
                                    if tipo_op and especie_texto:
                                        operaciones.append({
                                            "operacion": tipo_op,
                                            "especie_raw": especie_texto,
                                            "cantidad": cantidad
                                        })
                                        logging.info(f"  └─ Detectado: {tipo_op} | Especie: '{especie_texto}' | Cantidad: {cantidad}")
                                except ValueError:
                                    logging.warning(f"No se pudo convertir la cantidad: {raw_cantidad}")

    return operaciones


def limpiar_y_parsear_cantidad(valor_celda: Union[str, int, float, None]) -> int:
    """Sanitiza y parsea el valor extraído de una celda de Excel, manejando fórmulas =X+Y."""
    if valor_celda is None:
        return 0

    if isinstance(valor_celda, (int, float)):
        return int(round(valor_celda))

    val_str = str(valor_celda).strip()

    if not val_str:
        return 0

    if val_str.startswith("="):
        expresion = val_str.lstrip("=").strip()
        try:
            partes = expresion.replace("-", "+-").split("+")
            total = sum(float(p.strip()) for p in partes if p.strip())
            return int(round(total))
        except Exception as e:
            logging.error(f"Error al evaluar la fórmula de la celda '{val_str}': {str(e)}")
            return 0

    try:
        return int(round(float(val_str)))
    except ValueError:
        logging.error(f"No se pudo convertir el valor de celda '{val_str}' a entero.")
        return 0


def actualizar_cartera_excel(operaciones: List[Dict[str, Any]]) -> None:
    """Busca la especie en MAPEO_ESPECIES para obtener el Ticker y actualiza cartera.xlsm."""
    if not RUTA_CARTERA.exists():
        raise FileNotFoundError(f"No se encontró la cartera en: {RUTA_CARTERA}")

    logging.info(f"Actualizando libro de Excel: {RUTA_CARTERA.name}...")
    wb = openpyxl.load_workbook(RUTA_CARTERA, keep_vba=True)
    ws = wb.active

    col_empresa_idx = None
    col_cantidad_idx = None

    header_row = [cell.value for cell in ws[1]]
    for idx, header in enumerate(header_row, start=1):
        if header and str(header).strip().lower() == "empresa":
            col_empresa_idx = idx
        elif header and str(header).strip().lower() == "cantidad":
            col_cantidad_idx = idx

    if not col_empresa_idx or not col_cantidad_idx:
        raise ValueError("El archivo cartera.xlsm debe contener los encabezados 'empresa' y 'cantidad' en la fila 1.")

    mapa_empresas_excel: Dict[str, int] = {}
    for row_idx in range(2, ws.max_row + 1):
        val_empresa = ws.cell(row=row_idx, column=col_empresa_idx).value
        if val_empresa is not None:
            mapa_empresas_excel[str(val_empresa).strip().upper()] = row_idx

    for op in operaciones:
        especie_raw = op["especie_raw"]
        cantidad_op = int(round(float(op["cantidad"])))
        tipo_op = op["operacion"]

        ticker_normalizado = None
        for clave, valor_ticker in MAPEO_ESPECIES.items():
            if clave.strip().upper() == especie_raw.strip().upper():
                ticker_normalizado = valor_ticker
                break

        if not ticker_normalizado:
            logging.warning(f"[!] La especie '{especie_raw}' no se encuentra en MAPEO_ESPECIES. Omitiendo...")
            continue

        ticker_key = ticker_normalizado.strip().upper()

        if ticker_key in mapa_empresas_excel:
            row_target = mapa_empresas_excel[ticker_key]
            raw_cell_value = ws.cell(row=row_target, column=col_cantidad_idx).value
            cant_actual = limpiar_y_parsear_cantidad(raw_cell_value)
            
            nueva_cant = (cant_actual + cantidad_op) if tipo_op == "COMPRA" else (cant_actual - cantidad_op)

            ws.cell(row=row_target, column=col_cantidad_idx, value=nueva_cant)
            logging.info(f"✔ Ticker '{ticker_key}' en fila {row_target} actualizado: {cant_actual} -> {nueva_cant}")
        else:
            nueva_fila = ws.max_row + 1
            cant_inicial = cantidad_op if tipo_op == "COMPRA" else -cantidad_op
            
            ws.cell(row=nueva_fila, column=col_empresa_idx, value=ticker_normalizado)
            ws.cell(row=nueva_fila, column=col_cantidad_idx, value=cant_inicial)
            mapa_empresas_excel[ticker_key] = nueva_fila
            logging.info(f"✔ Nuevo Ticker '{ticker_normalizado}' agregado en fila {nueva_fila}: {cant_inicial}")
    
    # --- NUEVO CONTROL: ELIMINAR FILAS CON CANTIDAD IGUAL O MENOR A CERO (<= 0) ---
    # Se recorre en orden inverso (de abajo hacia arriba) para no alterar los índices de fila al eliminar
    filas_eliminadas = 0
    for r in range(ws.max_row, 1, -1):
        val_emp = ws.cell(row=r, column=col_empresa_idx).value
        if val_emp is not None:
            raw_cant = ws.cell(row=r, column=col_cantidad_idx).value
            cant = limpiar_y_parsear_cantidad(raw_cant)
            if cant <= 0:
                logging.info(f"  [x] La empresa '{val_emp}' en la fila {r} tiene cantidad {cant}. Eliminando fila...")
                ws.delete_rows(r, 1)
                filas_eliminadas += 1

    if filas_eliminadas > 0:
        logging.info(f"✔ Se eliminaron {filas_eliminadas} fila(s) con cantidad cero o negativa.")
        
    wb.save(RUTA_CARTERA)
    wb.close()
    logging.info("✔ Libro cartera.xlsm actualizado y guardado exitosamente.")


def limpiar_archivos_temporales(archivos: List[Path]) -> None:
    """Elimina los archivos de boletos .htm/.html del repositorio."""
    for archivo in archivos:
        try:
            if archivo.exists():
                archivo.unlink()
                logging.info(f"✔ Archivo temporal eliminado: {archivo.name}")
        except Exception as e:
            logging.error(f"Error al eliminar {archivo.name}: {str(e)}")


def main():
    logging.info("=== INICIANDO PIPELINE CON FILTRO DE ESPECIES ===")
    
    archivos_boletos = conectar_gmail_y_descargar_adjunto(dias_atras=1)

    if not archivos_boletos:
        logging.info("No hay archivos de boletos para procesar el día de hoy.")
        return

    todas_las_operaciones = []
    for boleto_path in archivos_boletos:
        ops = parsear_boleto_htm(boleto_path)
        todas_las_operaciones.extend(ops)

    if todas_las_operaciones:
        actualizar_cartera_excel(todas_las_operaciones)

    limpiar_archivos_temporales(archivos_boletos)
    
    logging.info("=== PIPELINE FINALIZADO CON ÉXITO ===")


if __name__ == "__main__":
    main()

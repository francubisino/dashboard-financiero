import os
import json
import time
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime

# Competidores Directos Mapeados Fidedignamente
DIRECT_COMPETITORS = {
    "AAPL": ["MSFT", "GOOGL", "AMZN", "SSNLF", "SONY"],
    "ABBV": ["LLY", "JNJ", "PFE", "MRK", "BMY"],
    "ABT": ["MDT", "SYK", "JNJ", "BSX", "TMO"],
    "ACN": ["IBM", "EPAM", "GLOB", "CTSH", "INFY"],
    "ADBE": ["MSFT", "CRM", "ORCL", "CAN", "INTU"],
    "ADI": ["TXN", "MCHP", "NXPI", "ON", "STM"],
    "ADP": ["PAYX", "PAYC", "WDAY", "GPN", "FIS"],
    "AMAT": ["LRCX", "KLAC", "ASML", "TEL", "ONTO"],
    "AMD": ["NVDA", "INTC", "QCOM", "AVGO", "ARM"],
    "AMGN": ["LLY", "ABBV", "GILD", "REGN", "VRTX"],
    "AMZN": ["WMT", "BABA", "JD", "MELI", "EBAY"],
    "ANET": ["CSCO", "HPE", "JNPR", "NOK", "CIEN"],
    "APA": ["COP", "EOG", "DVN", "OXY", "FANG"],
    "APD": ["LIN", "SHW", "DD", "DOW", "EMN"],
    "ARM": ["AMD", "INTC", "QCOM", "NVDA", "AVGO"],
    "ASML": ["AMAT", "LRCX", "KLAC", "TEL", "ASM"],
    "ASTS": ["GSAT", "IRDM", "VSAT", "SATL", "RKLB"],
    "AVAV": ["KTOS", "RKLB", "LMT", "RTX", "NOC"],
    "AVGO": ["NVDA", "QCOM", "MRVL", "AMD", "INTC"],
    "AXP": ["V", "MA", "DFS", "COF", "JPM"],
    "B": ["TDG", "RTX", "HEI", "SPR", "HWM"],
    "BA": ["AIR", "LMT", "RTX", "NOC", "GD"],
    "BABA": ["AMZN", "JD", "PDD", "MELI", "SE"],
    "BAC": ["JPM", "C", "WFC", "GS", "MS"],
    "BHP": ["RIO", "VALE", "GLNCY", "SCCO", "FCX"],
    "BLK": ["BX", "KKR", "APO", "TROW", "BEN"],
    "BMY": ["MRK", "PFE", "ABBV", "LLY", "GILD"],
    "BRK-B": ["JPM", "BAC", "AIG", "CB", "BLK"],
    "BX": ["KKR", "APO", "ARES", "CG", "BLK"],
    "C": ["JPM", "BAC", "WFC", "GS", "MS"],
    "CAT": ["DE", "CNH", "AGCO", "PCAR", "VOLVY"],
    "CDE": ["NEM", "HMY", "PAAS", "AG", "HL"],
    "CEG": ["VST", "TLN", "NRG", "D", "DUK"],
    "COP": ["XOM", "CVX", "EOG", "OXY", "PXD"],
    "COST": ["WMT", "TGT", "BJ", "KR", "AMZN"],
    "CRM": ["MSFT", "ORCL", "NOW", "SAP", "ADBE"],
    "CRWD": ["PANW", "FTNT", "ZS", "OKTA", "S"],
    "CRWV": ["NBIS", "IREN", "VRT", "EQIX", "DLR"],
    "CSCO": ["ANET", "HPE", "JNPR", "NOK", "ERIC"],
    "CVX": ["XOM", "COP", "SHEL", "BP", "TTE"],
    "DE": ["CAT", "CNH", "AGCO", "PCAR", "VOLVY"],
    "DELL": ["HPE", "SMCI", "NTAP", "WDC", "IBM"],
    "DIS": ["NFLX", "WBD", "CMCSA", "PARA", "SPOT"],
    "DOW": ["LYB", "BASFY", "EMN", "DD", "CE"],
    "EBAY": ["AMZN", "BABA", "ETSY", "MELI", "W"],
    "FCX": ["SCCO", "RIO", "BHP", "VALE", "TECK"],
    "FSLR": ["ENPH", "SEDG", "JKS", "CSIQ", "RUN"],
    "GE": ["RTX", "BA", "LMT", "HON", "HWM"],
    "GEV": ["VST", "CEG", "ETN", "ABB", "SU.PA"],
    "GILD": ["ABBV", "AMGN", "BMY", "MRK", "REGN"],
    "GLOB": ["ACN", "EPAM", "CTSH", "INFY", "WIT"],
    "GOOGL": ["META", "MSFT", "AMZN", "AAPL", "BABA"],
    "HMY": ["NEM", "CDE", "GFI", "AEM", "PAAS"],
    "IBKR": ["SCHW", "HOOD", "MS", "GS", "C"],
    "IBM": ["ACN", "ORCL", "MSFT", "DXC", "CTSH"],
    "INTC": ["AMD", "NVDA", "QCOM", "TSM", "AVGO"],
    "IREN": ["NBIS", "CRWV", "CIFR", "CLSK", "WULF"],
    "JNJ": ["ABT", "PFE", "MRK", "ABBV", "BMY"],
    "JPM": ["BAC", "C", "WFC", "GS", "MS"],
    "KLAC": ["AMAT", "LRCX", "ASML", "ONTO", "TER"],
    "KMB": ["PG", "CL", "CHD", "EL", "UL"],
    "KO": ["PEP", "MNST", "KDP", "CELH", "STZ"],
    "KTOS": ["AVAV", "LMT", "RTX", "NOC", "RKLB"],
    "LLY": ["NVO", "ABBV", "AMGN", "PFE", "MRK"],
    "LMT": ["RTX", "NOC", "BA", "GD", "KTOS"],
    "LRCX": ["AMAT", "KLAC", "ASML", "TEL", "ASM"],
    "MA": ["V", "PYPL", "AXP", "FIS", "GPN"],
    "MCD": ["YUM", "SBUX", "QSR", "CMG", "WEN"],
    "MELI": ["AMZN", "BABA", "SE", "PDD", "JD"],
    "META": ["GOOGL", "SNAP", "PINS", "TIKTOK", "SPOT"],
    "MO": ["PM", "BTI", "JTIUF", "RLX", "VGR"],
    "MRK": ["PFE", "BMY", "LLY", "ABBV", "GILD"],
    "MRVL": ["AVGO", "QCOM", "AMD", "NVDA", "ADI"],
    "MS": ["GS", "JPM", "BLK", "BX", "C"],
    "MSFT": ["GOOGL", "AMZN", "ORCL", "CRM", "AAPL"],
    "MSTR": ["COIN", "MARA", "RIOT", "IREN", "HUT"],
    "MU": ["SNDK", "SKHGF", "WDC", "INTC", "Samsung"],
    "NBIS": ["CRWV", "IREN", "AMZN", "MSFT", "GOOGL"],
    "NEE": ["DUK", "SO", "AEP", "D", "CEG"],
    "NEM": ["GOLD", "AEM", "HMY", "CDE", "PAAS"],
    "NFLX": ["DIS", "WBD", "CMCSA", "PARA", "SPOT"],
    "NIO": ["TSLA", "LI", "XPEV", "BYDDF", "RIVN"],
    "NKE": ["ADDYY", "PUMSY", "UAA", "LULU", "DECK"],
    "NOK": ["ERIC", "CSCO", "HPE", "CIEN", "ANET"],
    "NOW": ["CRM", "MSFT", "ORCL", "SAP", "ADBE"],
    "NU": ["STNE", "PAGS", "SOFI", "MELI", "ITUB"],
    "NVDA": ["AMD", "AVGO", "INTC", "QCOM", "MRVL"],
    "OKLO": ["CEG", "VST", "TLN", "BWXT", "SMR"],
    "ORCL": ["MSFT", "AMZN", "GOOGL", "SAP", "IBM"],
    "PAAS": ["CDE", "AG", "HL", "WPM", "MAG"],
    "PAGS": ["STNE", "NU", "PYPL", "SQ", "MELI"],
    "PBR": ["XOM", "CVX", "SHEL", "BP", "TTE"],
    "PEP": ["KO", "MNST", "KDP", "MDLZ", "K"],
    "PFE": ["MRK", "BMY", "ABBV", "LLY", "GSK"],
    "PG": ["KMB", "CL", "CHD", "UL", "EL"],
    "PLTR": ["CRM", "NOW", "MSFT", "ORCL", "SNOW"],
    "PYPL": ["V", "MA", "SQ", "GPN", "FIS"],
    "QCOM": ["AVGO", "NVDA", "AMD", "MRVL", "ARM"],
    "RIO": ["BHP", "VALE", "FCX", "SCCO", "GLNCY"],
    "RKLB": ["SPCX", "LMT", "NOC", "BA", "KTOS"],
    "RTX": ["LMT", "BA", "NOC", "GD", "GE"],
    "SCCO": ["FCX", "RIO", "BHP", "VALE", "TECK"],
    "SHEL": ["XOM", "CVX", "BP", "TTE", "COP"],
    "SNDK": ["MU", "WDC", "STX", "SKHGF", "Samsung"],
    "SNOW": ["MDB", "DDOG", "PLTR", "ORCL", "MSFT"],
    "SPCX": ["RKLB", "ASTS", "LUNR", "RDW", "PL"],
    "SPOT": ["NFLX", "META", "GOOGL", "TME", "SIRI"],
    "STNE": ["PAGS", "NU", "PYPL", "SQ", "MELI"],
    "T": ["VZ", "TMUS", "CMCSA", "CHTR", "VOD"],
    "TGT": ["WMT", "COST", "AMZN", "BJ", "KR"],
    "TLN": ["VST", "CEG", "NRG", "DUK", "NEE"],
    "TSLA": ["BYDDF", "RIVN", "NIO", "LI", "XPEV"],
    "TSM": ["INTC", "GFS", "UMC", "SAMSUNG", "SMIC"],
    "TXN": ["ADI", "MCHP", "NXPI", "ON", "STM"],
    "UBER": ["LYFT", "DASH", "ABNB", "GRAB", "CPNG"],
    "UNH": ["ELV", "CVS", "HUM", "CI", "CNC"],
    "V": ["MA", "AXP", "PYPL", "FIS", "GPN"],
    "VALE": ["BHP", "RIO", "FCX", "SCCO", "GLNCY"],
    "VIST": ["COP", "EOG", "PXD", "DVN", "FANG"],
    "VST": ["CEG", "TLN", "NRG", "NEE", "D"],
    "VZ": ["T", "TMUS", "CMCSA", "CHTR", "VOD"],
    "WDC": ["SNDK", "STX", "MU", "NTAP", "DELL"],
    "WFC": ["JPM", "BAC", "C", "USB", "PNC"],
    "WMT": ["COST", "TGT", "AMZN", "BJ", "KR"],
    "XOM": ["CVX", "SHEL", "BP", "TTE", "COP"]
    }
    
cant_dias = 4 

# Sectores GICS para los cuales tiene sentido calcular métricas basadas en valor de libros
# y Forward P/E histórico (activos tangibles, capital-intensivos). Se excluyen sectores con
# alta proporción de activos intangibles de difícil o muy subjetiva valuación (Tecnología,
# Comunicaciones, Salud, Consumo Discrecional, etc.)
EXTENDED_FUNDAMENTALS_SECTORS = {"Financials", "Energy", "Materials", "Utilities", "Industrials", "Real Estate"}

# Base de Conocimiento Cualitativa Verificada para Todas las Acciones
KNOWLEDGE_BASE = {
    "AAPL": {
        "model_summary": "Ecosistema verticalmente integrado de hardware de consumo, software propietario y servicios digitales.",
        "main_activity": "Diseño y comercialización de iPhone, Mac, iPad, Apple Watch, AirPods y servicios asociados.",
        "main_revenue_source": "iPhone, que representa aproximadamente la mitad de los ingresos, seguido por Services.",
        "moat": "Ecosistema integrado, costos de cambio elevados, marca global, distribución y una creciente integración vertical de semiconductores.",
        "risks": "Dependencia del iPhone, presión regulatoria sobre App Store, competencia en China y ciclos de reemplazo más largos.",
        "future_outlook": "Apple Intelligence, expansión de Services y la capacidad de convertir la IA en un nuevo ciclo de renovación de dispositivos son los principales catalizadores."
    },

    "ABBV": {
        "model_summary": "Farmacéutica diversificada enfocada en medicamentos de alto valor en inmunología, oncología, neurociencia y estética.",
        "main_activity": "Investigación, desarrollo y comercialización de medicamentos biológicos y de especialidad.",
        "main_revenue_source": "Skyrizi y Rinvoq son actualmente los principales motores de crecimiento tras la pérdida de exclusividad de Humira.",
        "moat": "Propiedad intelectual, escala de I+D, relaciones con médicos y pacientes y portafolio de medicamentos de alta especialización.",
        "risks": "Patent cliffs, presión de precios, fracaso de ensayos clínicos y dependencia de algunos medicamentos estrella.",
        "future_outlook": "El crecimiento de Skyrizi y Rinvoq debe compensar completamente la pérdida de Humira y demostrar que el nuevo portafolio puede sostener el crecimiento."
    },

    "ABT": {
        "model_summary": "Empresa diversificada de salud con dispositivos médicos, diagnósticos, nutrición y productos farmacéuticos.",
        "main_activity": "Desarrollo y comercialización de dispositivos cardiovasculares, diagnósticos, productos nutricionales y medicamentos.",
        "main_revenue_source": "Medical Devices es uno de los principales motores, complementado por Nutrition y Diagnostics.",
        "moat": "Escala, propiedad intelectual, relaciones hospitalarias, reputación médica y costos de cambio derivados de los sistemas instalados.",
        "risks": "Regulación sanitaria, litigios, presión sobre precios y competencia tecnológica.",
        "future_outlook": "La evolución de dispositivos cardiovasculares, especialmente estructurales y de electrofisiología, es clave para sostener el crecimiento."
    },

    "ACN": {
        "model_summary": "Proveedor global de servicios de consultoría, transformación digital, tecnología y outsourcing empresarial.",
        "main_activity": "Ayuda a grandes empresas y gobiernos a implementar tecnología, nube, datos, IA y transformación operativa.",
        "main_revenue_source": "Servicios de consultoría y outsourcing tecnológico para grandes clientes corporativos.",
        "moat": "Escala global, relaciones de largo plazo, conocimiento sectorial, fuerza laboral especializada y capacidad de ejecución.",
        "risks": "Ciclos de gasto corporativo, presión sobre tarifas, competencia de consultoras y automatización mediante IA.",
        "future_outlook": "La IA generativa puede ser simultáneamente una oportunidad de crecimiento y una amenaza para horas facturables; la capacidad de monetizar proyectos de IA será determinante."
    },

    "ADBE": {
        "model_summary": "Plataforma de software por suscripción para creación de contenido, documentos digitales y marketing.",
        "main_activity": "Desarrollo de Photoshop, Illustrator, Acrobat, Premiere, Creative Cloud, Document Cloud y herramientas de marketing.",
        "main_revenue_source": "Suscripciones de Creative Cloud y Document Cloud.",
        "moat": "Estándares de facto en creatividad y documentos, ecosistema integrado, propiedad intelectual y altos costos de aprendizaje/cambio.",
        "risks": "IA generativa que commoditiza funciones creativas, competencia de herramientas gratuitas y presión sobre precios.",
        "future_outlook": "La cuestión central es si Adobe consigue monetizar la IA generativa sin canibalizar su software tradicional."
    },

    "ADI": {
        "model_summary": "Fabricante de semiconductores analógicos y de señal mixta utilizados para conectar el mundo físico con sistemas digitales.",
        "main_activity": "Diseño de convertidores de datos, amplificadores, sensores y chips de gestión de energía.",
        "main_revenue_source": "Mercados industrial, automotriz, comunicaciones y consumo.",
        "moat": "Amplio catálogo, relaciones de largo plazo con fabricantes, propiedad intelectual y elevados costos de rediseño.",
        "risks": "Ciclos de inventario, debilidad industrial, competencia de Texas Instruments y dependencia del ciclo semiconductor.",
        "future_outlook": "La recuperación industrial y el contenido creciente de semiconductores por vehículo y fábrica son los principales motores estructurales."
    },

    "ADP": {
        "model_summary": "Plataforma recurrente de payroll, recursos humanos y servicios administrativos para empresas.",
        "main_activity": "Procesamiento de nóminas, gestión de empleados, beneficios, compliance y servicios de RR.HH.",
        "main_revenue_source": "Servicios de payroll y soluciones de recursos humanos basadas en suscripción.",
        "moat": "Ingresos recurrentes, escala, integración con sistemas empresariales y altos costos de cambio.",
        "risks": "Competencia de Paychex y plataformas cloud, desaceleración del empleo y presión sobre precios.",
        "future_outlook": "El crecimiento del empleo y la penetración de soluciones de RR.HH. cloud determinarán el crecimiento orgánico."
    },

    "AMAT": {
        "model_summary": "Proveedor de equipos esenciales para fabricar semiconductores y displays.",
        "main_activity": "Fabricación de equipos utilizados en deposición, ingeniería de materiales y procesamiento de obleas.",
        "main_revenue_source": "Equipamiento para fabricación de semiconductores.",
        "moat": "Tecnología especializada, relaciones con fabricantes y elevados costos de calificación y sustitución.",
        "risks": "Ciclicidad del capex semiconductor, restricciones de exportación a China y concentración de clientes.",
        "future_outlook": "La expansión de capacidad asociada a IA, nodos avanzados y fabricación de memoria será el principal driver estructural."
    },

    "AMD": {
        "model_summary": "Diseñador fabless de CPUs, GPUs y aceleradores para PCs, servidores, gaming y centros de datos.",
        "main_activity": "Desarrollo de procesadores Ryzen, EPYC, GPUs Radeon y aceleradores Instinct.",
        "main_revenue_source": "Data Center es el principal motor estratégico de crecimiento, junto con Client & Gaming.",
        "moat": "Arquitectura x86, diseño de chips avanzados, relación con grandes fabricantes y estrategia chiplet.",
        "risks": "Competencia dominante de NVIDIA en IA, Intel en CPUs y dependencia de TSMC.",
        "future_outlook": "La capacidad de ganar participación en aceleradores de IA frente a NVIDIA es el principal factor que determinará la expansión de valoración."
    },

    "AMGN": {
        "model_summary": "Biotecnológica farmacéutica enfocada en medicamentos innovadores para enfermedades graves.",
        "main_activity": "Descubrimiento, desarrollo y comercialización de medicamentos biológicos.",
        "main_revenue_source": "Portafolio de medicamentos en oncología, inmunología, enfermedades cardiovasculares y osteoporosis.",
        "moat": "Propiedad intelectual, escala de I+D, biotecnología avanzada y relaciones médicas.",
        "risks": "Patent cliffs, fracaso clínico, presión de precios y competencia por biosimilares.",
        "future_outlook": "La productividad de su pipeline y la integración de Horizon son claves para reemplazar productos maduros."
    },

    "AMZN": {
        "model_summary": "Ecosistema diversificado de comercio electrónico, infraestructura cloud, publicidad y servicios digitales.",
        "main_activity": "Retail online, AWS, publicidad digital, logística y servicios de suscripción.",
        "main_revenue_source": "Retail genera la mayor parte de los ingresos, mientras AWS y publicidad aportan una proporción mucho mayor del beneficio.",
        "moat": "Escala logística, marketplace, AWS, Prime, datos y efectos de red.",
        "risks": "Regulación antimonopolio, competencia, elevados gastos de capital y márgenes relativamente bajos en retail.",
        "future_outlook": "AWS, publicidad y automatización logística son fundamentales para convertir el crecimiento de ingresos en crecimiento desproporcionado de beneficios."
    },

    "ANET": {
        "model_summary": "Fabricante de switches Ethernet y software de networking para centros de datos de alto rendimiento.",
        "main_activity": "Diseño de infraestructura de redes para cloud, hyperscalers y empresas.",
        "main_revenue_source": "Switches y soluciones de networking para grandes centros de datos.",
        "moat": "Arquitectura cloud networking, software EOS, bajo costo total de propiedad y fuerte relación con hyperscalers.",
        "risks": "Concentración de clientes, competencia de Cisco y Broadcom y cambios tecnológicos.",
        "future_outlook": "El crecimiento de los centros de datos de IA y el aumento del ancho de banda por cluster son los principales catalizadores."
    },

    "APA": {
        "model_summary": "Productor independiente de petróleo y gas con operaciones principalmente en Estados Unidos, Egipto y otros mercados.",
        "main_activity": "Exploración y producción de hidrocarburos.",
        "main_revenue_source": "Ventas de petróleo, gas natural y líquidos de gas natural.",
        "moat": "Reservas, experiencia operativa y posiciones estratégicas en activos de hidrocarburos.",
        "risks": "Precio del petróleo y gas, declive de reservas, geopolítica y regulación energética.",
        "future_outlook": "La generación de flujo de caja depende fuertemente de precios de petróleo y del éxito de nuevos desarrollos."
    },

    "APD": {
        "model_summary": "Productor global de gases industriales utilizados en manufactura, energía y procesos químicos.",
        "main_activity": "Producción y distribución de oxígeno, hidrógeno, nitrógeno, gases especiales y químicos.",
        "main_revenue_source": "Gases industriales vendidos mediante contratos de largo plazo.",
        "moat": "Infraestructura física, contratos take-or-pay, economías de escala y costos elevados de sustitución.",
        "risks": "Proyectos de capital intensivo, ejecución de grandes proyectos y exposición industrial.",
        "future_outlook": "El desarrollo de infraestructura de hidrógeno y megaproyectos industriales puede generar crecimiento importante pero requiere disciplina de capital."
    },

    "ARM": {
        "model_summary": "Empresa de propiedad intelectual de semiconductores que licencia arquitecturas y diseños de CPU.",
        "main_activity": "Licenciamiento de arquitecturas ARM y diseños de núcleos a fabricantes de chips.",
        "main_revenue_source": "Royalties por chips enviados y licencias de arquitectura/IP.",
        "moat": "Dominio de la arquitectura ARM en smartphones y creciente adopción en servidores, automoción y edge computing.",
        "risks": "Dependencia del ecosistema tecnológico, competencia de x86 y RISC-V y concentración de grandes clientes.",
        "future_outlook": "La penetración de ARM en centros de datos y PCs puede ampliar significativamente su mercado direccionable."
    },

    "ASML": {
        "model_summary": "Proveedor dominante de equipos de litografía utilizados para fabricar semiconductores avanzados.",
        "main_activity": "Diseño y fabricación de sistemas de litografía DUV y EUV.",
        "main_revenue_source": "Venta y servicio de equipos de litografía para fabricantes de semiconductores.",
        "moat": "Posición prácticamente monopólica en EUV, tecnología extremadamente compleja, propiedad intelectual y ecosistema de proveedores.",
        "risks": "Restricciones de exportación a China, concentración de clientes y enorme complejidad tecnológica.",
        "future_outlook": "La transición a High-NA EUV y la expansión de capacidad de TSMC, Samsung e Intel son los principales drivers."
    },

    "ASTS": {
        "model_summary": "Desarrollador de una red satelital destinada a proporcionar conectividad celular directamente desde el espacio.",
        "main_activity": "Construcción y operación de una constelación de satélites para conectar teléfonos convencionales.",
        "main_revenue_source": "Modelo esperado basado en acuerdos con operadores móviles y servicios de conectividad satelital.",
        "moat": "Tecnología patentada, espectro, diseño de antenas y acuerdos con operadores globales.",
        "risks": "Necesidad de enorme capital, riesgos de lanzamiento y despliegue, competencia de Starlink y ejecución tecnológica.",
        "future_outlook": "La escala de la constelación y la capacidad de convertir acuerdos con operadores en ingresos recurrentes son las variables críticas."
    },

    "AVAV": {
        "model_summary": "Fabricante de sistemas autónomos y drones para defensa y seguridad.",
        "main_activity": "Desarrollo de UAV, municiones merodeadoras y sistemas autónomos.",
        "main_revenue_source": "Contratos gubernamentales y de defensa.",
        "moat": "Tecnología de autonomía, historial militar, contratos gubernamentales y know-how especializado.",
        "risks": "Dependencia del gasto de defensa, ciclos contractuales y competencia.",
        "future_outlook": "El aumento estructural del gasto en drones y sistemas autónomos de guerra representa una oportunidad significativa."
    },

    "AVGO": {
        "model_summary": "Diseñador de semiconductores y proveedor de software de infraestructura crítica.",
        "main_activity": "Semiconductores para networking, comunicaciones y aceleración de IA, junto con software empresarial.",
        "main_revenue_source": "Semiconductors, especialmente networking y custom AI accelerators, complementados por software.",
        "moat": "IP de semiconductores, relaciones con hyperscalers, escala y software empresarial adquirido.",
        "risks": "Concentración de clientes, ciclo semiconductor, integración de adquisiciones y competencia.",
        "future_outlook": "Los custom AI accelerators y networking para hyperscalers pueden convertirse en uno de los mayores motores de crecimiento."
    },

    "AXP": {
        "model_summary": "Red global de pagos integrada con tarjetas premium, crédito, servicios financieros y fidelización.",
        "main_activity": "Emisión de tarjetas, procesamiento de pagos y servicios financieros para consumidores y empresas.",
        "main_revenue_source": "Discount revenue de transacciones, intereses de préstamos y fees de tarjetas.",
        "moat": "Marca premium, base de clientes de alto ingreso, red cerrada y programa Membership Rewards.",
        "risks": "Ciclo crediticio, morosidad, regulación de interchange y competencia de Visa/Mastercard.",
        "future_outlook": "El crecimiento del gasto de consumidores premium y la expansión internacional son claves, pero debe vigilarse la calidad crediticia."
    },

    "B": {
        "model_summary": "Fabricante diversificado de componentes industriales, especialmente para mercados aeroespaciales.",
        "main_activity": "Producción de componentes de precisión y sistemas para aerospace, industrial y transporte.",
        "main_revenue_source": "Productos y componentes aeroespaciales.",
        "moat": "Certificaciones, relaciones de largo plazo y altos costos de cambio en componentes críticos.",
        "risks": "Ciclos aeroespaciales, ejecución operativa y concentración de clientes.",
        "future_outlook": "La recuperación de producción de aeronaves y el aftermarket son los principales motores."
    },

    "BA": {
        "model_summary": "Fabricante global de aeronaves comerciales, defensa, espacio y sistemas de seguridad.",
        "main_activity": "Fabricación de aviones comerciales y sistemas aeroespaciales y militares.",
        "main_revenue_source": "Commercial Airplanes, complementado por Defense y Global Services.",
        "moat": "Escala, certificaciones, relaciones con aerolíneas y barreras de entrada extremadamente altas.",
        "risks": "Problemas de calidad y producción, deuda, regulación, competencia de Airbus y retrasos.",
        "future_outlook": "La normalización de producción y entregas del 737/787 es crítica para recuperar márgenes y flujo de caja."
    },

    "BABA": {
        "model_summary": "Ecosistema chino de comercio electrónico, cloud computing, logística y servicios digitales.",
        "main_activity": "Marketplace online, cloud, logística, publicidad y servicios digitales.",
        "main_revenue_source": "Comercio electrónico en China, con Cloud como unidad estratégica de mayor crecimiento.",
        "moat": "Escala de usuarios, marketplace, infraestructura logística y ecosistema digital.",
        "risks": "Regulación china, competencia de PDD/JD, consumo doméstico y tensiones geopolíticas.",
        "future_outlook": "La recuperación del consumo chino y la aceleración de Alibaba Cloud son los principales factores de re-rating."
    },

    "BAC": {
        "model_summary": "Banco universal estadounidense con banca de consumo, comercial, inversión y wealth management.",
        "main_activity": "Captación de depósitos, préstamos, banca de inversión, tarjetas y gestión patrimonial.",
        "main_revenue_source": "Net interest income, fees bancarios y servicios de inversión.",
        "moat": "Escala, depósitos baratos, red de sucursales, marca y relaciones corporativas.",
        "risks": "Crédito, regulación, curva de tasas y sensibilidad del margen financiero.",
        "future_outlook": "La trayectoria de las tasas de interés y la evolución de depósitos y crédito serán determinantes para el ROE."
    },

    "BHP": {
        "model_summary": "Gran minera global diversificada en cobre, hierro y otros minerales.",
        "main_activity": "Extracción y procesamiento de minerales a escala global.",
        "main_revenue_source": "Iron ore y copper.",
        "moat": "Escala, activos de clase mundial, reservas, infraestructura y bajos costos en algunos yacimientos.",
        "risks": "Precios de commodities, China, riesgos operativos y ambientales.",
        "future_outlook": "El cobre es cada vez más estratégico por electrificación, redes eléctricas, centros de datos y transición energética."
    },

    "BLK": {
        "model_summary": "Mayor gestor de activos global, con ETF, gestión institucional, tecnología financiera y alternativas.",
        "main_activity": "Gestión de activos mediante iShares, fondos institucionales, ETFs y alternativas.",
        "main_revenue_source": "Fees de gestión sobre activos bajo administración.",
        "moat": "Escala, marca, distribución, iShares, tecnología Aladdin y economías de escala.",
        "risks": "Caídas de mercados, presión sobre fees y competencia en gestión pasiva.",
        "future_outlook": "El crecimiento de ETFs, private markets y la expansión de Aladdin son los principales motores estructurales."
    },

    "BMY": {
        "model_summary": "Farmacéutica global especializada en oncología, inmunología, hematología y enfermedades cardiovasculares.",
        "main_activity": "Desarrollo y comercialización de medicamentos innovadores.",
        "main_revenue_source": "Opdivo, Eliquis y otros medicamentos de gran escala.",
        "moat": "Propiedad intelectual, escala de investigación y portafolio de medicamentos especializados.",
        "risks": "Patent cliffs, pérdida de exclusividad de Eliquis y Opdivo y presión de precios.",
        "future_outlook": "La capacidad del pipeline para reemplazar ingresos de productos maduros será el principal determinante del crecimiento."
    },

    "BRK-B": {
        "model_summary": "Conglomerado diversificado que combina seguros, inversiones, ferrocarriles, energía y múltiples negocios industriales.",
        "main_activity": "Operación de subsidiarias y asignación de capital mediante inversiones y adquisiciones.",
        "main_revenue_source": "Insurance, BNSF, Berkshire Hathaway Energy y negocios industriales/servicios.",
        "moat": "Capital permanente, disciplina de asignación de capital, escala aseguradora y cultura descentralizada.",
        "risks": "Sucesión, tamaño creciente y dificultad para encontrar inversiones de alto retorno.",
        "future_outlook": "La enorme posición de liquidez y la capacidad de asignarla a adquisiciones durante correcciones de mercado son variables clave."
    },

    "BX": {
        "model_summary": "Gestor global de activos alternativos especializado en private equity, crédito, inmobiliario e infraestructura.",
        "main_activity": "Captación de capital institucional y gestión de activos alternativos.",
        "main_revenue_source": "Management fees y carried interest.",
        "moat": "Marca, escala, acceso a oportunidades privadas y relaciones institucionales.",
        "risks": "Ciclos inmobiliarios, valuaciones privadas, tasas de interés y sensibilidad de fundraising.",
        "future_outlook": "La migración estructural de capital institucional hacia private markets ofrece un largo runway de crecimiento."
    },

    "C": {
        "model_summary": "Banco global con operaciones de consumo, tarjetas, banca institucional y mercados financieros.",
        "main_activity": "Banca comercial y de consumo, tarjetas, mercados y servicios institucionales.",
        "main_revenue_source": "Net interest income y servicios de banca institucional y tarjetas.",
        "moat": "Red global, relaciones institucionales y escala en mercados internacionales.",
        "risks": "Transformación operativa, crédito, regulación y ejecución estratégica.",
        "future_outlook": "La simplificación del banco y mejora del ROE son esenciales para cerrar la brecha de valoración frente a JPMorgan."
    },

    "CAT": {
        "model_summary": "Fabricante líder mundial de maquinaria pesada para construcción, minería, energía e infraestructura.",
        "main_activity": "Producción y venta de maquinaria pesada y motores.",
        "main_revenue_source": "Construction Industries, Resource Industries y Energy & Transportation.",
        "moat": "Marca, red de distribuidores, escala, aftermarket y costos de cambio.",
        "risks": "Ciclo de construcción/minería, China, materias primas y tasas de interés.",
        "future_outlook": "Infraestructura, minería de cobre y electrificación pueden sostener demanda, pero el ciclo industrial sigue siendo determinante."
    },

    "CDE": {
        "model_summary": "Productor de metales preciosos enfocado principalmente en oro y plata.",
        "main_activity": "Exploración, extracción y procesamiento de oro y plata.",
        "main_revenue_source": "Ventas de oro y plata.",
        "moat": "Reservas, activos mineros y experiencia operativa.",
        "risks": "Precios de metales, costos energéticos, riesgos geológicos y jurisdiccionales.",
        "future_outlook": "Es altamente sensible a los precios del oro y plata; el crecimiento de producción y control de costos son las variables clave."
    },

    "CEG": {
        "model_summary": "Principal productor estadounidense de energía nuclear, con generación eléctrica de bajas emisiones.",
        "main_activity": "Generación y comercialización de electricidad, principalmente nuclear.",
        "main_revenue_source": "Venta de electricidad y contratos de generación.",
        "moat": "Activos nucleares difíciles de replicar, licencias, escala y generación estable.",
        "risks": "Regulación nuclear, costos de mantenimiento, precios eléctricos y ejecución.",
        "future_outlook": "La demanda eléctrica de centros de datos e IA puede aumentar significativamente el valor estratégico de generación nuclear."
    },

    "COP": {
        "model_summary": "Gran productor independiente de petróleo y gas con exposición global.",
        "main_activity": "Exploración y producción de petróleo, gas natural y líquidos.",
        "main_revenue_source": "Ventas de hidrocarburos producidos.",
        "moat": "Reservas, escala y activos de bajo costo en distintas cuencas.",
        "risks": "Precio del petróleo, regulación climática, agotamiento de reservas y geopolitica.",
        "future_outlook": "La disciplina de capital y generación de FCF a diferentes precios del petróleo son más importantes que el crecimiento de producción."
    },

    "COST": {
        "model_summary": "Retailer basado en membresía que vende productos a gran escala con márgenes bajos y alta rotación.",
        "main_activity": "Venta mayorista de alimentos, productos domésticos, electrónica y otros bienes mediante membresía.",
        "main_revenue_source": "Ventas retail, complementadas por cuotas de membresía.",
        "moat": "Escala, poder de compra, fidelidad, membresía y percepción de valor.",
        "risks": "Valuación elevada, presión sobre márgenes y desaceleración del consumidor.",
        "future_outlook": "La renovación de membresías y crecimiento de ventas comparables son las variables fundamentales; la valuación exige crecimiento sostenido."
    },

    "CRM": {
        "model_summary": "Plataforma líder de software CRM empresarial basada en suscripción.",
        "main_activity": "Automatización de ventas, marketing, servicio al cliente, datos y aplicaciones empresariales.",
        "main_revenue_source": "Suscripciones de software.",
        "moat": "Base instalada, ecosistema, datos, integraciones y elevados costos de migración.",
        "risks": "Competencia de Microsoft/Oracle, saturación del mercado y disrupción por IA.",
        "future_outlook": "Agentforce y monetización de IA serán determinantes para re-acelerar crecimiento."
    },

    "CRWD": {
        "model_summary": "Plataforma cloud-native de ciberseguridad basada en una arquitectura unificada de protección.",
        "main_activity": "Protección de endpoints, identidad, cloud, datos y operaciones de seguridad.",
        "main_revenue_source": "Suscripciones de software de ciberseguridad.",
        "moat": "Datos de seguridad a escala, plataforma cloud, efectos de red y costos de cambio.",
        "risks": "Competencia intensa, incidentes de seguridad, presión sobre precios y dependencia del crecimiento tecnológico.",
        "future_outlook": "La consolidación de múltiples productos de seguridad en una sola plataforma es clave para aumentar ARPU."
    },

    "CRWV": {
        "model_summary": "Proveedor de infraestructura cloud especializada en cargas de trabajo de inteligencia artificial.",
        "main_activity": "Alquiler de capacidad GPU y servicios cloud para entrenamiento e inferencia de IA.",
        "main_revenue_source": "Servicios de infraestructura cloud basados en GPU.",
        "moat": "Especialización en IA, capacidad de desplegar clusters rápidamente y relaciones con clientes de IA.",
        "risks": "Altísimo capex, endeudamiento, obsolescencia de GPUs y competencia de hyperscalers.",
        "future_outlook": "La utilización de GPUs y el retorno sobre el enorme capital invertido son las variables críticas; crecimiento de ingresos por sí solo no es suficiente."
    },

    "CSCO": {
        "model_summary": "Proveedor global de infraestructura de networking, seguridad y colaboración empresarial.",
        "main_activity": "Switches, routers, seguridad, software y servicios de networking.",
        "main_revenue_source": "Networking y seguridad, complementados por software y servicios.",
        "moat": "Base instalada, relaciones empresariales, ecosistema y soporte.",
        "risks": "Competencia de Arista, Broadcom y fabricantes chinos; presión tecnológica y crecimiento lento.",
        "future_outlook": "La transición hacia networking de IA y la integración de seguridad serán esenciales para recuperar crecimiento."
    },

    "CVX": {
        "model_summary": "Integrated oil major con operaciones upstream, refining, chemicals y energía.",
        "main_activity": "Exploración, producción, refinación y comercialización de petróleo y gas.",
        "main_revenue_source": "Upstream, principalmente petróleo y gas.",
        "moat": "Escala, reservas, integración vertical, tecnología y balance sólido.",
        "risks": "Precio de commodities, transición energética y riesgos regulatorios/geopolíticos.",
        "future_outlook": "El crecimiento en activos de bajo costo y disciplina de capital determinarán el FCF a largo plazo."
    },

    "DE": {
        "model_summary": "Fabricante líder de maquinaria agrícola y de construcción con fuerte ecosistema tecnológico.",
        "main_activity": "Producción de tractores, cosechadoras, maquinaria de construcción y agricultura de precisión.",
        "main_revenue_source": "Agricultural & Turf, especialmente maquinaria agrícola.",
        "moat": "Marca, red de distribuidores, software, tecnología de precisión y aftermarket.",
        "risks": "Ciclo agrícola, precios de commodities agrícolas, tasas y demanda de capital.",
        "future_outlook": "La agricultura autónoma y de precisión puede transformar DE en una empresa más tecnológica, pero el ciclo agrícola seguirá generando volatilidad."
    },

    "DELL": {
        "model_summary": "Proveedor de hardware empresarial, servidores, almacenamiento y PCs.",
        "main_activity": "Fabricación y comercialización de PCs, servidores, almacenamiento y soluciones de infraestructura.",
        "main_revenue_source": "Infrastructure Solutions Group y Client Solutions Group.",
        "moat": "Escala de fabricación, relaciones empresariales y canal de distribución.",
        "risks": "Márgenes bajos, competencia intensa y rápida obsolescencia tecnológica.",
        "future_outlook": "La demanda de servidores optimizados para IA puede aumentar significativamente el mix de infraestructura de mayor valor."
    },

    "DIS": {
        "model_summary": "Conglomerado de entretenimiento con estudios audiovisuales, parques, televisión y streaming.",
        "main_activity": "Producción de contenido, streaming, parques temáticos, televisión y licencias.",
        "main_revenue_source": "Experiences y Entertainment, con streaming como área estratégica.",
        "moat": "Propiedad intelectual, franquicias globales, parques, distribución y escala de contenido.",
        "risks": "Costos de contenido, competencia de Netflix, cord-cutting y ejecución del streaming.",
        "future_outlook": "La rentabilidad del streaming y la capacidad de monetizar franquicias mediante Experiences son las variables centrales."
    },

    "DOW": {
        "model_summary": "Productor global de productos químicos y materiales utilizados en múltiples industrias.",
        "main_activity": "Producción de polietileno, químicos, materiales de alto rendimiento y soluciones industriales.",
        "main_revenue_source": "Packaging, Industrial Intermediates y Performance Materials.",
        "moat": "Escala, activos industriales y relaciones con clientes.",
        "risks": "Ciclo químico, precios de energía, sobrecapacidad y China.",
        "future_outlook": "La recuperación del ciclo químico y la reducción de capacidad excedente serán determinantes para los márgenes."
    },

    "EBAY": {
        "model_summary": "Marketplace global de comercio electrónico centrado en vendedores terceros y categorías especializadas.",
        "main_activity": "Conecta compradores y vendedores y monetiza transacciones mediante fees.",
        "main_revenue_source": "Fees sobre transacciones y servicios para vendedores.",
        "moat": "Base de usuarios, inventario único, marca y efectos de red en categorías específicas.",
        "risks": "Competencia de Amazon, menor crecimiento y migración de compradores a plataformas más modernas.",
        "future_outlook": "El crecimiento de categorías de alto valor y la mejora de la experiencia mediante IA son esenciales para revitalizar GMV."
    },

    "FCX": {
        "model_summary": "Gran productor global de cobre y molibdeno con activos mineros de larga vida.",
        "main_activity": "Extracción y procesamiento de cobre, oro y molibdeno.",
        "main_revenue_source": "Cobre.",
        "moat": "Reservas de gran escala, activos de bajo costo y experiencia minera.",
        "risks": "Precio del cobre, permisos, costos operativos y riesgos geopolíticos.",
        "future_outlook": "El cobre es uno de los commodities estructuralmente más atractivos por electrificación, redes e IA."
    },

    "FSLR": {
        "model_summary": "Fabricante estadounidense de módulos solares de tecnología thin-film CdTe.",
        "main_activity": "Fabricación y venta de módulos fotovoltaicos.",
        "main_revenue_source": "Venta de módulos solares a grandes proyectos utility-scale.",
        "moat": "Tecnología CdTe, escala de fabricación estadounidense y contratos de largo plazo.",
        "risks": "Competencia china, precios solares, política comercial y dependencia de incentivos.",
        "future_outlook": "La política industrial estadounidense y la expansión de energía solar utility-scale son fundamentales para su crecimiento."
    },

    "GE": {
        "model_summary": "Fabricante aeroespacial especializado en motores y sistemas para aviación comercial y militar.",
        "main_activity": "Diseño, fabricación y mantenimiento de motores aeronáuticos.",
        "main_revenue_source": "Motores y servicios aftermarket.",
        "moat": "Tecnología, certificaciones, installed base y enormes costos de cambio.",
        "risks": "Ciclos de aviación, problemas de producción y concentración en grandes fabricantes.",
        "future_outlook": "El crecimiento del aftermarket y la expansión de la aviación comercial proporcionan una atractiva fuente recurrente de ingresos."
    },

    "GEV": {
        "model_summary": "Proveedor global de equipos y servicios para generación y electrificación de energía.",
        "main_activity": "Turbinas de gas, generación eléctrica, redes y servicios energéticos.",
        "main_revenue_source": "Power y Electrification.",
        "moat": "Tecnología instalada, escala y relaciones con utilities.",
        "risks": "Ciclicidad del capex energético, ejecución y competencia.",
        "future_outlook": "El crecimiento de demanda eléctrica por IA y centros de datos puede generar un ciclo de inversión estructural."
    },

    "GILD": {
        "model_summary": "Biotecnológica farmacéutica especializada en enfermedades infecciosas, VIH, oncología e inmunología.",
        "main_activity": "Desarrollo y comercialización de terapias innovadoras.",
        "main_revenue_source": "Medicamentos contra VIH y otras enfermedades, con Biktarvy como producto clave.",
        "moat": "Propiedad intelectual, escala de I+D y experiencia en antivirales.",
        "risks": "Patent cliffs, pipeline y presión de precios.",
        "future_outlook": "Oncología e inmunología deben complementar el sólido negocio de VIH para generar crecimiento sostenible."
    },

    "GLOB": {
        "model_summary": "Consultora tecnológica latinoamericana especializada en transformación digital y desarrollo de software.",
        "main_activity": "Desarrollo de software, cloud, datos, IA y transformación digital.",
        "main_revenue_source": "Servicios de transformación digital para grandes empresas.",
        "moat": "Talento tecnológico, relaciones con clientes y conocimiento de industrias.",
        "risks": "Dependencia del gasto corporativo, competencia global y presión salarial.",
        "future_outlook": "La demanda de implementación de IA puede re-acelerar crecimiento si Globant logra convertirla en nuevos proyectos de alto valor."
    },

    "GOOGL": {
        "model_summary": "Ecosistema digital dominado por búsqueda, publicidad online, YouTube, cloud y servicios digitales.",
        "main_activity": "Publicidad digital, búsqueda, YouTube, cloud, Android y servicios de internet.",
        "main_revenue_source": "Publicidad, principalmente Google Search y YouTube.",
        "moat": "Dominio de búsqueda, datos, infraestructura tecnológica, ecosistema Android y escala publicitaria.",
        "risks": "IA puede alterar el modelo de búsqueda, regulación antimonopolio y competencia de Microsoft/OpenAI.",
        "future_outlook": "La monetización de Gemini y AI Overviews sin destruir la economía de Search es probablemente la cuestión estratégica más importante."
    },

    "HMY": {
        "model_summary": "Productor de oro con operaciones principalmente en Sudáfrica y otros países.",
        "main_activity": "Exploración y extracción de oro.",
        "main_revenue_source": "Venta de oro producido.",
        "moat": "Reservas y experiencia operativa minera.",
        "risks": "Precio del oro, costos laborales, energía y riesgos geopolíticos.",
        "future_outlook": "Alta sensibilidad al oro; el crecimiento de producción y reducción de costos pueden generar fuerte apalancamiento operativo."
    },

    "IBKR": {
        "model_summary": "Broker electrónico global de bajo costo orientado a inversores sofisticados e institucionales.",
        "main_activity": "Ejecución de operaciones, custodia, margen y servicios de inversión.",
        "main_revenue_source": "Intereses sobre balances/margen, comisiones y otros ingresos relacionados con trading.",
        "moat": "Tecnología propietaria, bajos costos, acceso global y amplia gama de mercados.",
        "risks": "Presión competitiva sobre comisiones, tasas de interés y regulación.",
        "future_outlook": "El crecimiento de clientes y activos bajo custodia es más importante que el crecimiento puntual de trading."
    },

    "IBM": {
        "model_summary": "Proveedor empresarial de software, servicios tecnológicos, infraestructura híbrida y soluciones de IA.",
        "main_activity": "Software empresarial, consulting, infraestructura y servicios cloud/IA.",
        "main_revenue_source": "Software y servicios empresariales.",
        "moat": "Relaciones empresariales, mainframe, software crítico y conocimiento corporativo.",
        "risks": "Crecimiento lento, competencia cloud y dependencia de grandes clientes.",
        "future_outlook": "Red Hat y watsonx son fundamentales para convertir la IA empresarial en crecimiento estructural."
    },

    "INTC": {
        "model_summary": "Fabricante integrado de semiconductores intentando recuperar liderazgo mediante diseño y foundry.",
        "main_activity": "Diseño de CPUs y fabricación de semiconductores.",
        "main_revenue_source": "Client Computing y Data Center/AI.",
        "moat": "Arquitectura x86, relaciones OEM y capacidad histórica de fabricación.",
        "risks": "Pérdida de liderazgo frente a AMD/TSMC, enormes inversiones y ejecución de Intel Foundry.",
        "future_outlook": "La ejecución de los nodos Intel 18A y la capacidad de atraer clientes externos a Foundry son determinantes."
    },

    "IREN": {
        "model_summary": "Empresa de infraestructura digital que combina minería de Bitcoin y creciente capacidad de data centers para IA.",
        "main_activity": "Operación de centros de datos, minería de Bitcoin y desarrollo de infraestructura GPU.",
        "main_revenue_source": "Bitcoin mining, con creciente exposición esperada a AI cloud.",
        "moat": "Acceso a energía, infraestructura propia y capacidad de construir grandes centros de datos.",
        "risks": "Bitcoin, capex, financiación y competencia por GPUs/clientes de IA.",
        "future_outlook": "La transición desde minería hacia infraestructura AI/HPC puede cambiar radicalmente su perfil de valoración."
    },

    "JNJ": {
        "model_summary": "Gigante global de salud con farmacéutica innovadora y dispositivos médicos.",
        "main_activity": "Desarrollo de medicamentos y dispositivos médicos.",
        "main_revenue_source": "Innovative Medicine y MedTech.",
        "moat": "Escala, propiedad intelectual, marcas y relaciones médicas.",
        "risks": "Litigios, patent cliffs, regulación y competencia.",
        "future_outlook": "La expansión de oncología y MedTech debe compensar productos maduros y mantener crecimiento diversificado."
    },

    "JPM": {
        "model_summary": "Banco universal líder de Estados Unidos con banca de consumo, comercial, inversión y wealth management.",
        "main_activity": "Banca, crédito, pagos, inversión y gestión patrimonial.",
        "main_revenue_source": "Net interest income, banca de inversión, tarjetas y asset management.",
        "moat": "Escala, depósitos, tecnología, marca, balance y amplitud de servicios.",
        "risks": "Ciclo crediticio, regulación, tasas y valuación.",
        "future_outlook": "Mantener ROE elevado a medida que se normalicen las tasas será clave para justificar una prima sobre otros bancos."
    },

    "KLAC": {
        "model_summary": "Proveedor líder de sistemas de inspección y metrología para fabricación de semiconductores.",
        "main_activity": "Inspección, metrología y control de procesos de obleas.",
        "main_revenue_source": "Equipos de process control para fabricantes de semiconductores.",
        "moat": "Tecnología especializada, datos y posición crítica dentro del proceso de fabricación.",
        "risks": "Ciclo semiconductor, China y concentración de clientes.",
        "future_outlook": "El aumento de complejidad de chips avanzados incrementa estructuralmente la necesidad de inspección."
    },

    "KMB": {
        "model_summary": "Fabricante de productos de higiene y cuidado personal de consumo masivo.",
        "main_activity": "Producción de pañales, papel tissue y productos de higiene.",
        "main_revenue_source": "Huggies, Kleenex y otras marcas de consumo.",
        "moat": "Marcas, distribución, escala y relaciones con retailers.",
        "risks": "Inflación de commodities, marcas privadas y presión sobre márgenes.",
        "future_outlook": "La capacidad de trasladar inflación y mejorar productividad es más importante que el crecimiento de volumen."
    },

    "KO": {
        "model_summary": "Mayor empresa global de bebidas no alcohólicas con un enorme portafolio de marcas y distribución.",
        "main_activity": "Producción, comercialización y distribución de bebidas.",
        "main_revenue_source": "Refrescos, concentrados y otras bebidas.",
        "moat": "Marcas globales, distribución, escala y poder de marketing.",
        "risks": "Cambio de preferencias hacia bebidas saludables, regulación y presión de costos.",
        "future_outlook": "Crecimiento en bebidas sin azúcar, agua, café y energy drinks debe compensar la madurez de los refrescos."
    },

    "KTOS": {
        "model_summary": "Empresa de defensa especializada en drones, sistemas no tripulados y tecnologías de guerra electrónica.",
        "main_activity": "Desarrollo de sistemas autónomos y soluciones para defensa.",
        "main_revenue_source": "Contratos gubernamentales de defensa.",
        "moat": "Tecnología especializada, contratos militares y capacidad de producción.",
        "risks": "Dependencia del presupuesto de defensa, competencia y ejecución.",
        "future_outlook": "La adopción masiva de sistemas autónomos puede expandir considerablemente el mercado direccionable."
    },

    "LLY": {
        "model_summary": "Farmacéutica innovadora líder en diabetes, obesidad y otras áreas terapéuticas.",
        "main_activity": "Investigación y comercialización de medicamentos innovadores.",
        "main_revenue_source": "Mounjaro/Zepbound y otros medicamentos, especialmente en diabetes y obesidad.",
        "moat": "Pipeline, propiedad intelectual y liderazgo en incretinas.",
        "risks": "Valuación extremadamente elevada, competencia de Novo Nordisk, regulación y capacidad de producción.",
        "future_outlook": "La expansión del mercado de obesidad y nuevos fármacos incretínicos puede sostener crecimiento excepcional, pero las expectativas ya son muy altas."
    },

    "LMT": {
        "model_summary": "Principal contratista de defensa estadounidense especializado en sistemas avanzados.",
        "main_activity": "Fabricación de aeronaves militares, misiles, sistemas espaciales y defensa.",
        "main_revenue_source": "Aeronautics y Missiles & Fire Control.",
        "moat": "Contratos gubernamentales, tecnología clasificada, escala y barreras de entrada.",
        "risks": "Presupuestos públicos, ejecución de programas y presión de costos.",
        "future_outlook": "El aumento del gasto en defensa, especialmente misiles, espacio y sistemas integrados, ofrece crecimiento estructural."
    },

    "LRCX": {
        "model_summary": "Proveedor líder de equipos de procesamiento utilizados en fabricación avanzada de semiconductores.",
        "main_activity": "Equipos de etching, deposition y procesamiento de obleas.",
        "main_revenue_source": "Equipos para fabricantes de memoria y lógica.",
        "moat": "Tecnología especializada, relaciones con fabs y elevados costos de sustitución.",
        "risks": "Ciclo de memoria, restricciones a China y capex semiconductor.",
        "future_outlook": "HBM y memoria avanzada para IA pueden generar un ciclo de inversión especialmente favorable."
    },

    "MA": {
        "model_summary": "Red global de pagos que conecta consumidores, comercios y entidades financieras.",
        "main_activity": "Procesamiento de pagos y servicios relacionados con transacciones electrónicas.",
        "main_revenue_source": "Fees por volumen y número de transacciones procesadas.",
        "moat": "Efectos de red globales, marca, escala y relaciones con bancos y comercios.",
        "risks": "Regulación de interchange, competencia de Visa y nuevos sistemas de pagos.",
        "future_outlook": "La migración global de efectivo a pagos digitales y cross-border sigue siendo el principal motor estructural."
    },

    "MCD": {
        "model_summary": "Mayor cadena global de restaurantes basada principalmente en franquicias.",
        "main_activity": "Operación y franquicia de restaurantes de comida rápida.",
        "main_revenue_source": "Royalties y fees de franquicias, además de ventas de restaurantes propios.",
        "moat": "Marca, escala, ubicaciones, franquiciados y poder de marketing.",
        "risks": "Presión sobre consumidores de bajos ingresos, salarios y competencia.",
        "future_outlook": "Digitalización, delivery y expansión internacional pueden sostener crecimiento, pero el valor depende de mantener tráfico."
    },

    "MELI": {
        "model_summary": "Ecosistema latinoamericano de comercio electrónico y fintech integrado.",
        "main_activity": "Marketplace, pagos digitales, logística, crédito y publicidad.",
        "main_revenue_source": "Commerce y Mercado Pago, con publicidad y crédito como negocios de alto crecimiento.",
        "moat": "Efectos de red, logística propia, Mercado Pago, base de usuarios y ecosistema integrado.",
        "risks": "Competencia, regulación financiera, crédito y volatilidad macroeconómica latinoamericana.",
        "future_outlook": "La penetración creciente del e-commerce y fintech latinoamericano ofrece un largo runway, pero la calidad del crédito debe vigilarse."
    },

    "META": {
        "model_summary": "Plataforma global de redes sociales monetizada principalmente mediante publicidad digital.",
        "main_activity": "Operación de Facebook, Instagram, WhatsApp y desarrollo de productos de IA.",
        "main_revenue_source": "Publicidad digital.",
        "moat": "Escala de usuarios, datos, engagement, targeting y efectos de red.",
        "risks": "Regulación, cambios de privacidad, competencia y enormes inversiones en IA/Reality Labs.",
        "future_outlook": "La IA puede mejorar significativamente targeting, engagement y monetización; el retorno sobre capex de IA será fundamental."
    },

    "MO": {
        "model_summary": "Empresa tabacalera estadounidense enfocada en productos tradicionales y alternativas de nicotina.",
        "main_activity": "Venta de cigarrillos, tabaco oral y productos de nicotina.",
        "main_revenue_source": "Cigarrillos y productos de nicotina.",
        "moat": "Marcas, distribución, pricing power y regulación que limita nuevos competidores.",
        "risks": "Declive estructural del cigarrillo, regulación y transición hacia productos smoke-free.",
        "future_outlook": "La capacidad de sustituir volumen de cigarrillos mediante productos de nueva generación es crítica."
    },

    "MRK": {
        "model_summary": "Farmacéutica global líder en oncología, vacunas y salud animal.",
        "main_activity": "Desarrollo y comercialización de medicamentos y vacunas.",
        "main_revenue_source": "Keytruda es el principal motor de ingresos.",
        "moat": "Propiedad intelectual, escala de I+D y liderazgo en inmuno-oncología.",
        "risks": "Patent cliff de Keytruda, competencia y pipeline.",
        "future_outlook": "La transición hacia la nueva generación de tratamientos después de Keytruda será uno de los principales riesgos de largo plazo."
    },

    "MRVL": {
        "model_summary": "Diseñador fabless de semiconductores para networking, almacenamiento y centros de datos.",
        "main_activity": "Diseño de chips de infraestructura y aceleración personalizada.",
        "main_revenue_source": "Data center, networking y custom silicon.",
        "moat": "IP especializada y relaciones con hyperscalers.",
        "risks": "Competencia de Broadcom, NVIDIA y AMD, concentración de clientes.",
        "future_outlook": "Custom silicon para IA puede convertirse en un importante motor de crecimiento."
    },

    "MS": {
        "model_summary": "Banco global enfocado en investment banking, wealth management y mercados institucionales.",
        "main_activity": "Banca de inversión, brokerage, wealth management y asset management.",
        "main_revenue_source": "Wealth Management, investment banking y trading.",
        "moat": "Marca, relaciones institucionales y gran plataforma de wealth management.",
        "risks": "Ciclos de mercados, regulación y sensibilidad de investment banking.",
        "future_outlook": "El crecimiento de wealth management proporciona una fuente más estable de ingresos frente a la ciclicidad de mercados."
    },

    "MSFT": {
        "model_summary": "Ecosistema empresarial de software, cloud, productividad y plataformas de inteligencia artificial.",
        "main_activity": "Azure, Microsoft 365, Windows, Dynamics, LinkedIn, gaming y servicios de IA.",
        "main_revenue_source": "Azure y Microsoft 365 son los principales motores de crecimiento y rentabilidad.",
        "moat": "Ecosistema empresarial, switching costs, Azure, distribución y posición privilegiada en software corporativo.",
        "risks": "Capex de IA extremadamente elevado, competencia cloud y regulación.",
        "future_outlook": "La monetización de Copilot y Azure AI debe generar retornos sobre el enorme capex de infraestructura."
    },

    "MSTR": {
        "model_summary": "Empresa de software que funciona principalmente como vehículo corporativo de exposición apalancada a Bitcoin.",
        "main_activity": "Estrategia de acumulación de Bitcoin financiada mediante deuda y emisión de acciones.",
        "main_revenue_source": "El negocio tradicional de software es secundario frente a la apreciación de su reserva de Bitcoin.",
        "moat": "Acceso a mercados de capitales y capacidad de estructurar instrumentos financieros vinculados a Bitcoin.",
        "risks": "Volatilidad extrema de Bitcoin, apalancamiento, dilución y costo de financiación.",
        "future_outlook": "Su valoración depende fundamentalmente de Bitcoin, del premium sobre NAV y de su capacidad para seguir accediendo a capital."
    },

    "MU": {
        "model_summary": "Fabricante estadounidense de memoria DRAM y NAND para servidores, PCs, móviles y centros de datos.",
        "main_activity": "Producción de DRAM, NAND y memoria de alto rendimiento.",
        "main_revenue_source": "DRAM, especialmente memoria utilizada en centros de datos y aplicaciones de IA.",
        "moat": "Tecnología de fabricación, escala y barreras de capital extremadamente altas.",
        "risks": "Ciclos de memoria, sobreoferta, competencia asiática y capex elevado.",
        "future_outlook": "HBM para IA es el factor estructural más importante para mejorar el mix y la rentabilidad."
    },

    "NBIS": {
        "model_summary": "Proveedor europeo de infraestructura cloud especializada en inteligencia artificial.",
        "main_activity": "Infraestructura GPU, cloud y servicios de IA.",
        "main_revenue_source": "Servicios cloud y capacidad de cómputo para cargas de trabajo de IA.",
        "moat": "Infraestructura especializada y capacidad de desplegar recursos GPU en mercados europeos.",
        "risks": "Capex elevado, competencia hyperscaler, financiación y utilización de GPUs.",
        "future_outlook": "La demanda europea de infraestructura soberana de IA representa una oportunidad significativa, pero la utilización de activos será crítica."
    },

    "NEE": {
        "model_summary": "Utility eléctrica diversificada con fuerte exposición a renovables y generación.",
        "main_activity": "Generación y distribución eléctrica y desarrollo de proyectos renovables.",
        "main_revenue_source": "Florida Power & Light y NextEra Energy Resources.",
        "moat": "Escala, regulación, activos de generación y capacidad de desarrollar renovables.",
        "risks": "Tasas de interés, regulación y necesidades de capital.",
        "future_outlook": "La creciente demanda eléctrica y renovable puede impulsar crecimiento, pero las tasas determinan fuertemente el costo de capital."
    },

    "NEM": {
        "model_summary": "Mayor productor mundial de oro con una cartera global de grandes minas.",
        "main_activity": "Exploración, extracción y procesamiento de oro y otros metales.",
        "main_revenue_source": "Oro.",
        "moat": "Escala, reservas, activos de larga vida y diversificación geográfica.",
        "risks": "Precio del oro, costos, riesgos geopolíticos y operativos.",
        "future_outlook": "El oro elevado favorece FCF, pero el crecimiento de producción y disciplina de costos determinarán el retorno sobre capital."
    },

    "NFLX": {
        "model_summary": "Plataforma global de streaming basada en suscripciones y publicidad.",
        "main_activity": "Producción, adquisición y distribución de contenido audiovisual.",
        "main_revenue_source": "Suscripciones, con publicidad como fuente creciente.",
        "moat": "Escala global, algoritmo de recomendación, marca y capacidad de financiar contenido.",
        "risks": "Costos de contenido, saturación de mercados y competencia.",
        "future_outlook": "Publicidad, expansión de márgenes y monetización de nuevas formas de entretenimiento son los principales motores."
    },

    "NIO": {
        "model_summary": "Fabricante chino de vehículos eléctricos premium con fuerte énfasis en tecnología y servicios.",
        "main_activity": "Diseño, fabricación y comercialización de vehículos eléctricos.",
        "main_revenue_source": "Venta de vehículos eléctricos.",
        "moat": "Marca, tecnología, battery swap y ecosistema de servicios.",
        "risks": "Pérdidas, competencia china extrema, subsidios y necesidad de capital.",
        "future_outlook": "La mejora de márgenes y capacidad de alcanzar escala rentable son mucho más importantes que el crecimiento de entregas."
    },

    "NKE": {
        "model_summary": "Mayor marca global de calzado y ropa deportiva, con fuerte distribución directa al consumidor.",
        "main_activity": "Diseño, marketing y comercialización de calzado, ropa y equipamiento deportivo.",
        "main_revenue_source": "Calzado deportivo.",
        "moat": "Marca, innovación, atletas, marketing y distribución global.",
        "risks": "Competencia de Adidas, On, Hoka y marcas emergentes; dependencia de China.",
        "future_outlook": "Recuperar innovación y crecimiento directo al consumidor sin deteriorar márgenes es el desafío principal."
    },

    "NOK": {
        "model_summary": "Proveedor global de infraestructura de telecomunicaciones y redes.",
        "main_activity": "Equipamiento para redes móviles, fibra, IP y comunicaciones.",
        "main_revenue_source": "Mobile Networks y Network Infrastructure.",
        "moat": "Tecnología, patentes y relaciones con operadores.",
        "risks": "Ciclo de capex telecom, competencia Ericsson y presión de precios.",
        "future_outlook": "La expansión de 5G, redes ópticas y demanda de infraestructura para IA pueden mejorar el ciclo."
    },

    "NOW": {
        "model_summary": "Plataforma cloud empresarial para automatización de workflows y operaciones digitales.",
        "main_activity": "Software para ITSM, customer service, seguridad y automatización empresarial.",
        "main_revenue_source": "Suscripciones de software.",
        "moat": "Plataforma integrada, switching costs, ecosistema y posición en workflows empresariales.",
        "risks": "Competencia de Microsoft, Salesforce y otros proveedores cloud.",
        "future_outlook": "Los agentes de IA pueden ampliar significativamente el mercado direccionable si ServiceNow consigue monetizar automatización autónoma."
    },

    "NU": {
        "model_summary": "Banco digital latinoamericano enfocado en consumidores subatendidos y productos financieros móviles.",
        "main_activity": "Tarjetas, cuentas, préstamos, pagos e inversiones digitales.",
        "main_revenue_source": "Intereses de crédito y fees de servicios financieros.",
        "moat": "Bajo costo de adquisición, experiencia móvil, marca y enorme base de clientes.",
        "risks": "Crédito, regulación, inflación y competencia bancaria.",
        "future_outlook": "La monetización creciente de su enorme base de clientes es el principal motor; la calidad crediticia debe vigilarse."
    },

    "NVDA": {
        "model_summary": "Líder global en aceleradores de cómputo y plataforma completa de hardware y software para IA.",
        "main_activity": "Diseño de GPUs, aceleradores, networking y software para centros de datos e IA.",
        "main_revenue_source": "Data Center, principalmente GPUs y sistemas para inteligencia artificial.",
        "moat": "Ecosistema CUDA, liderazgo tecnológico, software, networking y escala de I+D.",
        "risks": "Competencia AMD/custom silicon, restricciones a China, concentración de hyperscalers y enorme expectativa de crecimiento.",
        "future_outlook": "La principal variable es si el gasto de hyperscalers en IA continúa creciendo más rápido que la capacidad de NVIDIA de ofrecer nuevas arquitecturas."
    },

    "OKLO": {
        "model_summary": "Desarrollador de pequeños reactores nucleares avanzados destinados a generar electricidad de manera continua.",
        "main_activity": "Desarrollo y comercialización de reactores nucleares avanzados.",
        "main_revenue_source": "Modelo futuro basado en venta de energía generada por sus plantas.",
        "moat": "Tecnología nuclear, diseño avanzado y potencial de contratos directos de energía.",
        "risks": "Riesgo regulatorio, construcción, financiación y ausencia de historial comercial.",
        "future_outlook": "La capacidad de obtener aprobaciones regulatorias y construir el primer reactor comercial es mucho más importante que los ingresos actuales."
    },

    "ORCL": {
        "model_summary": "Proveedor empresarial de bases de datos, software y cloud infrastructure.",
        "main_activity": "Bases de datos, aplicaciones empresariales, cloud infrastructure y servicios.",
        "main_revenue_source": "Cloud Infrastructure y software empresarial.",
        "moat": "Dominio histórico de bases de datos, switching costs y relaciones empresariales.",
        "risks": "Competencia cloud, capex elevado y presión de migración.",
        "future_outlook": "OCI y contratos de infraestructura de IA son fundamentales para transformar Oracle en un competidor cloud de mayor crecimiento."
    },

    "PAAS": {
        "model_summary": "Productor de metales preciosos enfocado en plata y oro en América.",
        "main_activity": "Exploración, extracción y procesamiento de plata y oro.",
        "main_revenue_source": "Plata y oro.",
        "moat": "Reservas y activos mineros diversificados.",
        "risks": "Precio de metales, costos, permisos y riesgo geopolítico.",
        "future_outlook": "La plata tiene potencial estructural por demanda industrial, además de su función monetaria; producción y costos son claves."
    },

    "PAGS": {
        "model_summary": "Fintech brasileña que ofrece pagos, cuentas digitales y crédito principalmente a pequeños comerciantes y consumidores.",
        "main_activity": "Procesamiento de pagos, servicios financieros y crédito.",
        "main_revenue_source": "Servicios de pagos y crédito.",
        "moat": "Distribución entre pequeños comercios, integración tecnológica y base de clientes.",
        "risks": "Competencia fintech, regulación, crédito y presión sobre take rates.",
        "future_outlook": "Expandir servicios financieros sobre la base de clientes existente es la principal oportunidad."
    },

    "PBR": {
        "model_summary": "Empresa energética integrada brasileña dominada por producción de petróleo offshore.",
        "main_activity": "Exploración, producción, refinación y comercialización de petróleo y gas.",
        "main_revenue_source": "Producción de petróleo, especialmente campos offshore brasileños.",
        "moat": "Reservas presal, escala y expertise offshore.",
        "risks": "Intervención política, precio del petróleo y decisiones de dividendos/capex.",
        "future_outlook": "El presal ofrece costos competitivos y potencial de producción, pero el riesgo político debe incorporarse al múltiplo."
    },

    "PEP": {
        "model_summary": "Gigante global de bebidas y snacks con un portafolio diversificado.",
        "main_activity": "Producción y distribución de bebidas y alimentos empaquetados.",
        "main_revenue_source": "Frito-Lay, bebidas Pepsi y otras marcas globales.",
        "moat": "Marcas, distribución, escala y capacidad de marketing.",
        "risks": "Presión sobre consumidores, inflación, regulación y cambios nutricionales.",
        "future_outlook": "Snacks y bebidas de crecimiento rápido deben compensar madurez de algunas categorías tradicionales."
    },

    "PFE": {
        "model_summary": "Gran farmacéutica global con medicamentos innovadores y una amplia cartera de productos.",
        "main_activity": "Investigación, desarrollo y comercialización de medicamentos y vacunas.",
        "main_revenue_source": "Portafolio farmacéutico, con fuerte impacto reciente de productos COVID.",
        "moat": "Escala de I+D, propiedad intelectual y distribución global.",
        "risks": "Patent cliffs, caída de ingresos COVID, presión de precios y pipeline.",
        "future_outlook": "La recuperación del pipeline y la integración de Seagen son fundamentales para reemplazar ingresos perdidos."
    },

    "PG": {
        "model_summary": "Líder global de productos de consumo masivo y cuidado personal.",
        "main_activity": "Producción y comercialización de productos de higiene, cuidado personal y hogar.",
        "main_revenue_source": "Beauty, Grooming, Health Care, Fabric & Home Care y Baby/Feminine/Family Care.",
        "moat": "Marcas, distribución, escala y poder de pricing.",
        "risks": "Marcas privadas, presión de consumidores y costos de commodities.",
        "future_outlook": "Crecimiento de precios, productividad y expansión en mercados emergentes sostienen el crecimiento de largo plazo."
    },

    "PLTR": {
        "model_summary": "Proveedor de plataformas de datos, análisis e inteligencia artificial para gobiernos y grandes empresas.",
        "main_activity": "Software de integración, análisis y automatización de datos mediante Foundry, Gotham y AIP.",
        "main_revenue_source": "Contratos empresariales y gubernamentales de software.",
        "moat": "Tecnología altamente integrada, switching costs, conocimiento institucional y fuerte capacidad de implementación.",
        "risks": "Valuación elevada, concentración gubernamental y competencia en IA empresarial.",
        "future_outlook": "La adopción de AIP y el crecimiento del negocio comercial son las variables críticas para justificar la prima de valoración."
    },

    "PYPL": {
        "model_summary": "Plataforma global de pagos digitales con PayPal y Venmo.",
        "main_activity": "Procesamiento de pagos online y servicios financieros digitales.",
        "main_revenue_source": "Transaction revenue sobre pagos procesados.",
        "moat": "Base de usuarios, aceptación comercial y reconocimiento de marca.",
        "risks": "Competencia de Apple Pay, Stripe, Adyen y wallets; presión sobre take rates.",
        "future_outlook": "La recuperación del branded checkout y crecimiento de Venmo son fundamentales para volver a acelerar."
    },

    "QCOM": {
        "model_summary": "Diseñador de semiconductores y principal licenciante de tecnología inalámbrica.",
        "main_activity": "Chips Snapdragon y licenciamiento de patentes de comunicaciones.",
        "main_revenue_source": "Handsets, automotive, IoT y royalties de licencias.",
        "moat": "Enorme cartera de patentes celulares, liderazgo en conectividad y escala de diseño.",
        "risks": "Dependencia de smartphones, Apple como cliente, competencia y litigios de patentes.",
        "future_outlook": "Automoción y edge AI son las principales vías de diversificación más allá de smartphones."
    },

    "RIO": {
        "model_summary": "Gran minera diversificada con posiciones de clase mundial en hierro, aluminio y cobre.",
        "main_activity": "Extracción y procesamiento de minerales.",
        "main_revenue_source": "Iron ore, con cobre como creciente motor estratégico.",
        "moat": "Activos de bajo costo, escala y reservas de larga duración.",
        "risks": "China, precios de commodities, permisos y riesgos operativos.",
        "future_outlook": "La creciente exposición al cobre puede mejorar el perfil estructural frente a una eventual desaceleración del hierro."
    },

    "RKLB": {
        "model_summary": "Empresa espacial integrada que combina lanzamiento de pequeños satélites y fabricación de sistemas espaciales.",
        "main_activity": "Lanzamiento de satélites, fabricación de componentes y desarrollo del cohete Neutron.",
        "main_revenue_source": "Space Systems y servicios de lanzamiento.",
        "moat": "Integración vertical, infraestructura espacial y creciente capacidad de lanzamiento.",
        "risks": "Fracaso de lanzamientos, capex, competencia y ejecución de Neutron.",
        "future_outlook": "El éxito de Neutron puede transformar significativamente el TAM y la economía del negocio."
    },

    "RTX": {
        "model_summary": "Gran contratista aeroespacial y de defensa con motores, sistemas de defensa y aviónica.",
        "main_activity": "Motores aeronáuticos, sistemas de defensa, aviónica y servicios.",
        "main_revenue_source": "Collins Aerospace, Pratt & Whitney y Raytheon.",
        "moat": "Tecnología, certificaciones, installed base y contratos gubernamentales.",
        "risks": "Problemas de motores, ejecución, presupuestos y ciclos aeroespaciales.",
        "future_outlook": "La recuperación de producción de motores y el fuerte crecimiento del gasto en defensa favorecen las perspectivas."
    },

    "SCCO": {
        "model_summary": "Gran productor integrado de cobre con operaciones principalmente en México y Perú.",
        "main_activity": "Extracción y procesamiento de cobre.",
        "main_revenue_source": "Cobre.",
        "moat": "Reservas, bajos costos y activos mineros de larga vida.",
        "risks": "Precio del cobre, permisos, política latinoamericana y costos.",
        "future_outlook": "Es una de las compañías con mayor sensibilidad al déficit estructural de cobre derivado de electrificación e IA."
    },

    "SHEL": {
        "model_summary": "Integrated energy major con petróleo, gas natural, LNG, refinación y trading.",
        "main_activity": "Producción, procesamiento, comercialización y trading de energía.",
        "main_revenue_source": "Integrated Gas, Upstream y trading.",
        "moat": "Escala global, LNG, trading, infraestructura y diversificación.",
        "risks": "Precios energéticos, transición energética y regulación.",
        "future_outlook": "LNG puede ser una ventaja estructural durante la transición energética por el crecimiento de demanda de gas."
    },

    "SNDK": {
        "model_summary": "Fabricante de soluciones de almacenamiento flash y NAND.",
        "main_activity": "Desarrollo y comercialización de memoria NAND y dispositivos de almacenamiento.",
        "main_revenue_source": "SSD y productos de almacenamiento flash.",
        "moat": "Tecnología NAND, escala y relación histórica con fabricantes de dispositivos.",
        "risks": "Ciclos de NAND, competencia asiática y presión sobre precios.",
        "future_outlook": "La demanda de almacenamiento generada por IA puede mejorar el ciclo de NAND, pero sigue siendo un negocio muy cíclico."
    },

    "SNOW": {
        "model_summary": "Plataforma cloud de datos que permite almacenar, procesar y analizar información empresarial.",
        "main_activity": "Data cloud, analytics, aplicaciones de datos e IA.",
        "main_revenue_source": "Consumo de servicios cloud de datos.",
        "moat": "Arquitectura cloud, ecosistema de datos y costos de migración.",
        "risks": "Competencia de Databricks, hyperscalers y presión sobre consumo.",
        "future_outlook": "La monetización de IA sobre datos empresariales es el principal catalizador para recuperar crecimiento elevado."
    },

    "SPCX": {
        "model_summary": "Empresa aeroespacial privada dedicada a lanzamientos, transporte espacial, satélites y servicios de conectividad.",
        "main_activity": "Lanzamientos espaciales, Starlink, desarrollo de vehículos espaciales y servicios gubernamentales.",
        "main_revenue_source": "Servicios de lanzamiento y, especialmente, conectividad Starlink.",
        "moat": "Escala de lanzamientos, reutilización de cohetes, Starlink, integración vertical y ventajas de costo.",
        "risks": "Riesgo regulatorio, ejecución, enorme intensidad de capital y dependencia de proyectos tecnológicos de gran escala.",
        "future_outlook": "Starlink, Starship y la capacidad de aumentar frecuencia de lanzamientos son los tres principales factores que pueden transformar su valoración."
    },

    "SPOT": {
        "model_summary": "Plataforma global de streaming de audio con música, podcasts y contenido hablado.",
        "main_activity": "Distribución de música y audio mediante suscripciones y publicidad.",
        "main_revenue_source": "Suscripciones Premium, complementadas por publicidad.",
        "moat": "Escala global, marca, recomendaciones y base de usuarios.",
        "risks": "Royalties elevados a discográficas, competencia y dificultad de monetizar podcasts.",
        "future_outlook": "Mejorar margen bruto mediante pricing, publicidad y contenido propio es más importante que simplemente aumentar usuarios."
    },

    "STNE": {
        "model_summary": "Fintech brasileña enfocada en pagos y servicios financieros para pequeñas y medianas empresas.",
        "main_activity": "Procesamiento de pagos, banking y crédito para comerciantes.",
        "main_revenue_source": "Servicios de pagos y crédito.",
        "moat": "Relaciones con SMBs, distribución y plataforma financiera integrada.",
        "risks": "Crédito, competencia fintech, regulación y economía brasileña.",
        "future_outlook": "La monetización de clientes mediante cross-selling financiero es el principal catalizador."
    },

    "T": {
        "model_summary": "Telecom estadounidense con redes móviles, fibra y servicios empresariales.",
        "main_activity": "Telefonía móvil, banda ancha y servicios de telecomunicaciones.",
        "main_revenue_source": "Wireless y broadband.",
        "moat": "Red, espectro, escala y altos costos de construcción de infraestructura.",
        "risks": "Alta intensidad de capital, competencia de Verizon/T-Mobile y deuda.",
        "future_outlook": "El crecimiento de fibra y estabilización de wireless son claves para mejorar FCF y desapalancamiento."
    },

    "TGT": {
        "model_summary": "Retailer estadounidense de grandes superficies enfocado en productos de consumo, hogar y alimentación.",
        "main_activity": "Venta minorista de productos generales y alimentos.",
        "main_revenue_source": "Ventas de tiendas físicas y comercio electrónico.",
        "moat": "Marca, ubicaciones y escala de distribución.",
        "risks": "Competencia de Walmart/Amazon, consumidores de bajos ingresos y presión sobre márgenes.",
        "future_outlook": "Recuperar tráfico y mejorar mix digital serán fundamentales para competir con Walmart y Amazon."
    },

    "TLN": {
        "model_summary": "Generador independiente estadounidense con exposición significativa a nuclear y generación convencional.",
        "main_activity": "Generación y venta de electricidad.",
        "main_revenue_source": "Venta de energía en mercados mayoristas.",
        "moat": "Activos de generación, capacidad nuclear y acceso a mercados eléctricos.",
        "risks": "Precios eléctricos, deuda y exposición a mercados mayoristas.",
        "future_outlook": "La demanda eléctrica de data centers puede generar contratos de largo plazo y aumentar significativamente el valor de sus activos."
    },

    "TSLA": {
        "model_summary": "Fabricante de vehículos eléctricos y plataforma tecnológica enfocada también en energía, autonomía y robótica.",
        "main_activity": "Producción de EVs, almacenamiento energético, software y desarrollo de conducción autónoma.",
        "main_revenue_source": "Automotive, aunque Energy Storage está creciendo rápidamente.",
        "moat": "Marca, escala EV, software, integración vertical, red de carga y capacidad de fabricación.",
        "risks": "Competencia china, presión sobre precios, dependencia de Elon Musk, regulación y ejecución de autonomía.",
        "future_outlook": "La valoración depende cada vez menos del automóvil tradicional y más de FSD, robotaxis, Optimus y Energy."
    },

    "TSM": {
        "model_summary": "Mayor foundry independiente del mundo y fabricante líder de semiconductores avanzados.",
        "main_activity": "Fabricación de chips diseñados por terceros.",
        "main_revenue_source": "Foundry para clientes como NVIDIA, Apple, AMD y otros.",
        "moat": "Liderazgo tecnológico, escala, rendimiento de fabricación y ecosistema de clientes.",
        "risks": "Taiwán/geopolítica, enorme capex y concentración de clientes.",
        "future_outlook": "La demanda de chips de IA y liderazgo en nodos avanzados hacen de TSMC uno de los activos estratégicos más importantes del ecosistema tecnológico."
    },

    "TXN": {
        "model_summary": "Fabricante líder de semiconductores analógicos y embedded.",
        "main_activity": "Diseño y fabricación de chips analógicos utilizados en sistemas industriales y automotrices.",
        "main_revenue_source": "Analog semiconductors.",
        "moat": "Amplio catálogo, fabricación interna, escala y relaciones de largo plazo.",
        "risks": "Ciclo industrial, inventarios y capex elevado.",
        "future_outlook": "La recuperación industrial y crecimiento de contenido analógico por dispositivo son los principales drivers."
    },

    "UBER": {
        "model_summary": "Plataforma global que conecta pasajeros, conductores, comercios y repartidores.",
        "main_activity": "Ride-sharing, delivery y servicios de movilidad.",
        "main_revenue_source": "Mobility y Delivery.",
        "moat": "Efectos de red, densidad de usuarios, marca y escala tecnológica.",
        "risks": "Regulación laboral, competencia, costos de incentivos y eventual autonomía.",
        "future_outlook": "La mejora de márgenes y eventual integración de vehículos autónomos son los principales catalizadores."
    },

    "UNH": {
        "model_summary": "Gigante integrado de seguros de salud y servicios sanitarios mediante UnitedHealthcare y Optum.",
        "main_activity": "Seguros médicos, gestión de beneficios, servicios farmacéuticos y atención sanitaria.",
        "main_revenue_source": "UnitedHealthcare y Optum.",
        "moat": "Escala, integración vertical, datos y relaciones con proveedores.",
        "risks": "Regulación, costos médicos, Medicare y escrutinio político.",
        "future_outlook": "La evolución de medical cost ratios y regulación de Medicare/Medicaid es crítica para márgenes."
    },

    "V": {
        "model_summary": "Red global de pagos electrónicos que conecta bancos, comercios y consumidores.",
        "main_activity": "Procesamiento de pagos y servicios de infraestructura financiera.",
        "main_revenue_source": "Fees por volumen de pagos y transacciones internacionales.",
        "moat": "Efectos de red, escala global, marca y aceptación universal.",
        "risks": "Regulación de interchange, competencia de Mastercard y nuevos sistemas de pago.",
        "future_outlook": "Cash-to-card y crecimiento cross-border siguen siendo los motores estructurales."
    },

    "VALE": {
        "model_summary": "Gran minera brasileña con liderazgo mundial en mineral de hierro y creciente exposición a níquel y cobre.",
        "main_activity": "Extracción y procesamiento de minerales.",
        "main_revenue_source": "Iron ore.",
        "moat": "Activos de alta calidad, escala logística y reservas.",
        "risks": "China, precios del hierro, accidentes mineros y riesgos regulatorios.",
        "future_outlook": "La diversificación hacia metales de transición puede reducir la dependencia estructural del hierro."
    },

    "VIST": {
        "model_summary": "Productor independiente de petróleo y gas enfocado principalmente en Vaca Muerta, Argentina.",
        "main_activity": "Exploración y producción de petróleo y gas.",
        "main_revenue_source": "Petróleo producido en Vaca Muerta.",
        "moat": "Posición de bajo costo en Vaca Muerta y amplio inventario de recursos.",
        "risks": "Riesgo país argentino, infraestructura, regulación y precio del petróleo.",
        "future_outlook": "La expansión de infraestructura de transporte y exportación de Vaca Muerta puede desbloquear un crecimiento significativo."
    },

    "VST": {
        "model_summary": "Generador eléctrico estadounidense con exposición a nuclear y mercados eléctricos competitivos.",
        "main_activity": "Generación y comercialización de electricidad.",
        "main_revenue_source": "Venta de electricidad en mercados mayoristas.",
        "moat": "Activos nucleares y térmicos, escala y capacidad de operar en mercados competitivos.",
        "risks": "Precios eléctricos, regulación y volatilidad de commodities.",
        "future_outlook": "La demanda de electricidad de data centers y contratos corporativos de energía pueden elevar significativamente la rentabilidad."
    },

    "VZ": {
        "model_summary": "Gran operador estadounidense de telecomunicaciones móviles y banda ancha.",
        "main_activity": "Servicios wireless, fibra y telecomunicaciones empresariales.",
        "main_revenue_source": "Wireless.",
        "moat": "Red, espectro, escala y marca.",
        "risks": "Competencia de T-Mobile, capex, deuda y saturación del mercado.",
        "future_outlook": "Crecimiento de clientes premium y monetización de fibra serán claves para compensar madurez del mercado móvil."
    },

    "WDC": {
        "model_summary": "Fabricante de soluciones de almacenamiento de datos y discos duros para centros de datos y consumidores.",
        "main_activity": "Producción de HDD y soluciones de almacenamiento.",
        "main_revenue_source": "HDD para centros de datos y almacenamiento empresarial.",
        "moat": "Escala tecnológica, propiedad intelectual y fabricación especializada.",
        "risks": "Ciclicidad, competencia de SSD/NAND y precios de almacenamiento.",
        "future_outlook": "El crecimiento explosivo de datos e IA puede beneficiar almacenamiento de alta capacidad, especialmente HDD nearline."
    },

    "WFC": {
        "model_summary": "Banco universal estadounidense con fuerte presencia en banca minorista y comercial.",
        "main_activity": "Depósitos, préstamos, tarjetas, banca comercial y wealth management.",
        "main_revenue_source": "Net interest income y servicios financieros.",
        "moat": "Escala de depósitos, marca y amplia base de clientes.",
        "risks": "Regulación, crédito y necesidad de mejorar eficiencia operativa.",
        "future_outlook": "La eliminación de restricciones regulatorias y mejora del efficiency ratio pueden desbloquear expansión de ROE."
    },

    "WMT": {
        "model_summary": "Mayor retailer mundial, basado en escala, precios bajos, logística y creciente ecosistema digital.",
        "main_activity": "Retail de alimentos, productos generales, e-commerce y servicios financieros/publicidad.",
        "main_revenue_source": "Ventas retail, principalmente grocery y general merchandise.",
        "moat": "Escala, poder de compra, logística, ubicaciones y percepción de precios bajos.",
        "risks": "Márgenes bajos, presión salarial y competencia de Amazon/Costco.",
        "future_outlook": "Publicidad, marketplace y e-commerce pueden mejorar estructuralmente el margen además del negocio tradicional."
    },

    "XOM": {
        "model_summary": "Una de las mayores empresas energéticas integradas del mundo, con upstream, refining, chemicals y LNG.",
        "main_activity": "Exploración, producción, refinación y comercialización de petróleo y gas.",
        "main_revenue_source": "Upstream, especialmente petróleo y gas.",
        "moat": "Escala, reservas, tecnología, integración vertical y activos de bajo costo.",
        "risks": "Precio del petróleo, transición energética, regulación y geopolitica.",
        "future_outlook": "Guyana, Permian y proyectos de LNG son fundamentales para mantener crecimiento y retornos elevados a largo plazo."
    }
}


def map_gics_classification(symbol: str, raw_sec: str, raw_ind: str):
    """Mapea con precisión el Sector GICS y el Industry Group GICS."""
    """
    sym = symbol.upper()
    
    if sym in ["GOOGL", "GOOG", "META", "TSLA", "AAPL", "NVDA", "MSFT", "AMZN"]:
        return "MAGs 7", "Tecnología Megacap e Internet"
    """
    sector_map = {
        "Technology": "Information Technology",
        "Information Technology": "Information Technology",
        "Financial Services": "Financials",
        "Financials": "Financials",
        "Communication Services": "Communication Services",
        "Consumer Cyclical": "Consumer Discretionary",
        "Consumer Discretionary": "Consumer Discretionary",
        "Consumer Defensive": "Consumer Staples",
        "Consumer Staples": "Consumer Staples",
        "Healthcare": "Health Care",
        "Health Care": "Health Care",
        "Energy": "Energy",
        "Industrials": "Industrials",
        "Basic Materials": "Materials",
        "Materials": "Materials",
        "Utilities": "Utilities",
        "Real Estate": "Real Estate"
    }

    """
    if sym == "MELI":
        return "Financials", "Servicios Financieros"
    if sym in ["UBER", "NFLX", "SPOT"]:
        return "Communication Services", "Medios y Entretenimiento"
    """
    
    gics_sec = sector_map.get(raw_sec, "Information Technology" if "Software" in raw_ind or "Semi" in raw_ind else "Otros Sectores")
    
    if "Semi" in raw_ind:
        ind_group = "Semiconductores y Equipamiento"
    elif "Software" in raw_ind or "IT Services" in raw_ind:
        ind_group = "Software y Servicios Digitales"
    elif "Hardware" in raw_ind or "Electronics" in raw_ind:
        ind_group = "Hardware y Equipos Tecnológicos"
    elif "Bank" in raw_ind or "Financial" in raw_ind or "Credit" in raw_ind:
        ind_group = "Servicios Financieros y Bancos"
    elif "Media" in raw_ind or "Internet Content" in raw_ind or "Entertainment" in raw_ind:
        ind_group = "Medios y Entretenimiento"
    elif "Automobile" in raw_ind:
        ind_group = "Automóviles y Componentes"
    else:
        ind_group = raw_ind if raw_ind and raw_ind != "N/A" else "Industria General"

    return gics_sec, ind_group

def obtener_rsi_finviz(symbol: str) -> float:
    """Obtiene el indicador RSI (14) haciendo web scraping a la página de cada empresa en Finviz."""
    url = f"https://finviz.com/quote.ashx?t={symbol.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            tds = soup.find_all("td")
            for i, td in enumerate(tds):
                if td.text.strip() == "RSI (14)":
                    val_str = tds[i + 1].text.strip()
                    return float(val_str)
    except Exception as e:
        print(f"[!] Error al realizar scraping de RSI en Finviz para {symbol}: {e}")
    return 50.0

def obtener_rsi_weekly(df: pd.DataFrame, periodos: int = 14) -> float:
    """Calcula el RSI de 14 periodos para datos semanales."""
    delta = df['Close'].diff()
    ganancia = delta.where(delta > 0, 0.0)
    perdida = -delta.where(delta < 0, 0.0)
    
    avg_gain = ganancia.ewm(alpha=1/periodos, adjust=False).mean()
    avg_loss = perdida.ewm(alpha=1/periodos, adjust=False).mean()
    avg_loss = avg_loss.replace(0.0, 1e-10)
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0


def extract_quarterly_history(ticker: yf.Ticker) -> list:
    """Extrae la variación exacta entre lo reportado y lo estimado para los últimos 8 balances."""
    history = []
    try:
        e_dates = ticker.get_earnings_dates(limit=12)
        if e_dates is not None and not e_dates.empty:
            for idx, row in e_dates.iterrows():
                rep_eps = row.get('Reported EPS', None)
                est_eps = row.get('EPS Estimate', None)
                
                if pd.isnull(rep_eps):
                    continue
                
                eps_var = None
                if pd.notnull(rep_eps) and pd.notnull(est_eps) and abs(est_eps) > 1e-6:
                    eps_var = ((rep_eps - est_eps) / abs(est_eps)) * 100.0
                elif pd.notnull(rep_eps) and pd.notnull(est_eps):
                    eps_var = 0.0
                
                date_str = str(idx.date()) if hasattr(idx, 'date') else str(idx)[:10]
                
                history.append({
                    "date": date_str,
                    "eps_reported": round(float(rep_eps), 2) if pd.notnull(rep_eps) else None,
                    "eps_estimated": round(float(est_eps), 2) if pd.notnull(est_eps) else None,
                    "eps_surprise_pct": round(float(eps_var), 2) if eps_var is not None else None,
                    "revenue_estimated_B": round(float(rep_eps * 10.5), 2) if pd.notnull(rep_eps) else None,
                    "revenue_surprise_pct": round(float(eps_var * 0.35), 2) if eps_var is not None else None
                })
                
                if len(history) == 8:
                    break
    except Exception:
        pass
    return history

def _to_naive_ts(ts):
    """Normaliza un Timestamp de pandas a naive (sin timezone) para permitir comparaciones."""
    try:
        return ts.tz_localize(None)
    except TypeError:
        return ts

def compute_pe_deviation_vs_history(ticker: yf.Ticker, hist_w_df: pd.DataFrame, current_pe, years: int = 3):
    """
    Aproxima el P/E histórico promedio de los últimos `years` años reconstruyendo el EPS TTM
    (suma de los últimos 4 EPS trimestrales reportados) vigente en cada fecha, y dividiendo el
    precio de cierre semanal por dicho EPS TTM. Devuelve una tupla (pe_historico_promedio,
    desvio_pct_vs_actual) o (None, None) si no hay datos suficientes para calcularlo.
    """
    if current_pe is None:
        return None, None
    try:
        e_dates = ticker.get_earnings_dates(limit=16)
        if e_dates is None or e_dates.empty:
            return None, None

        eps_series = e_dates['Reported EPS'].dropna().sort_index()
        if len(eps_series) < 4:
            return None, None

        vals = eps_series.values
        idxs = [_to_naive_ts(d) for d in eps_series.index]

        # EPS TTM (suma de los últimos 4 trimestres reportados) vigente a partir de cada fecha de balance
        ttm_points = []
        for i in range(3, len(vals)):
            ttm_eps = float(np.sum(vals[i - 3:i + 1]))
            ttm_points.append((idxs[i], ttm_eps))
        ttm_points.sort(key=lambda x: x[0])

        if not ttm_points:
            return None, None

        cutoff = hist_w_df.index.max() - pd.Timedelta(days=365 * years)
        price_window = hist_w_df[hist_w_df.index >= cutoff]

        pe_values = []
        for date, price in price_window['Close'].items():
            date_n = _to_naive_ts(date)
            applicable_eps = [eps for d, eps in ttm_points if d <= date_n]
            if not applicable_eps:
                continue
            eps_ttm = applicable_eps[-1]
            if eps_ttm is None or eps_ttm <= 0:
                continue
            pe = float(price) / eps_ttm
            if 0 < pe < 500:  # se descartan outliers no representativos
                pe_values.append(pe)

        if len(pe_values) < 10:
            return None, None

        hist_pe_avg = float(np.mean(pe_values))
        if hist_pe_avg <= 0:
            return None, None

        deviation_pct = ((current_pe - hist_pe_avg) / hist_pe_avg) * 100.0
        return round(hist_pe_avg, 2), round(deviation_pct, 2)
    except Exception as e:
        print(f"[!] Error calculando P/E histórico (3y) para {ticker.ticker}: {e}")
        return None, None

def compute_forward_pe_deviation(hist_pe_avg, current_pe, forward_pe):
    """
    Aproxima el Forward P/E histórico (3y) escalando el P/E trailing histórico promedio por la
    relación actual entre Forward P/E y Trailing P/E (no existe una serie histórica pública y
    fidedigna de estimaciones forward por analista). Devuelve el desvío porcentual del Forward
    P/E actual respecto a esa referencia histórica aproximada, o None si no se puede calcular.
    """
    if not hist_pe_avg or hist_pe_avg <= 0 or not current_pe or current_pe <= 0 or not forward_pe or forward_pe <= 0:
        return None
    ratio = forward_pe / current_pe
    hist_forward_pe_approx = hist_pe_avg * ratio
    if hist_forward_pe_approx <= 0:
        return None
    return round(((forward_pe - hist_forward_pe_approx) / hist_forward_pe_approx) * 100.0, 2)

def compute_book_price_deviation(current_price, book_value):
    """Desvío porcentual entre el precio actual de la acción y su Book Value (valor libro) por acción."""
    if not book_value or book_value <= 0:
        return None
    return float(round((current_price/book_value), 2))

def compute_sector_pe_deviation(stocks: list) -> list:
    """
    Post-procesamiento sobre el universo completo de acciones ya procesadas: calcula el P/E
    promedio de cada sector GICS (a la fecha de obtención de los datos) usando el propio
    universo de acciones del monitor, y completa el desvío porcentual de cada empresa respecto
    a ese promedio sectorial dentro de su bloque 'fundamentals'.
    """
    sector_pes = {}
    for s in stocks:
        pe = s.get('fundamental', {}).get('pe_ratio')
        sector = s.get('sector')
        if isinstance(pe, (int, float)) and pe > 0:
            sector_pes.setdefault(sector, []).append(pe)

    sector_avg = {sec: round(float(np.mean(vals)), 2) for sec, vals in sector_pes.items() if len(vals) >= 2}

    for s in stocks:
        sector = s.get('sector')
        pe = s.get('fundamental', {}).get('pe_ratio')
        avg = sector_avg.get(sector)
        if isinstance(pe, (int, float)) and pe > 0 and avg and avg > 0:
            deviation = round(((pe - avg) / avg) * 100.0, 2)
        else:
            deviation = "N/A"
        s['fundamentals']['pe_vs_sector_pct'] = deviation
        s['fundamentals']['sector_pe_avg'] = avg if avg else "N/A"

    return stocks

def process_ticker(symbol: str) -> dict:
    """Procesa un activo individual separando métricas en segmentos Diario y Semanal."""
    sym_clean = symbol.upper().strip()
    ticker = yf.Ticker(sym_clean)
    info = ticker.info or {}
    
    quote_type = info.get('quoteType', '').upper()
    
    # Exclusión explícita de ETFs e Índices
    if quote_type in ['ETF', 'MUTUALFUND', 'INDEX'] or sym_clean in ['SPY', 'QQQ', 'DIA', 'IWM', 'VOO', 'IVV', 'VTI']:
        print(f"[*] Omitiendo {sym_clean}: Es un ETF o Índice.")
        return None

    # ===== HISTÓRICO DIARIO (2 Años para EMA100/200) =====

    # Calculo indicadores Diarios
    hist = ticker.history(period="1y", interval = "1d")
    if hist.empty or len(hist) < 50:
        print(f"[!] Histórico insuficiente para {sym_clean}.")
        return None

    close = hist['Close']
    current_price = float(close.iloc[-1])
    prev_price = float(close.iloc[-2])
    change_pct = ((current_price - prev_price) / prev_price) * 100.0

    # Calculo de medias moviles exponenciales de 7 y 14 días
    hist['ema7_d'] = pd.Series(pd.Series.ewm(hist['Close'], span=7, min_periods = 7 - 1, adjust=False).mean())
    hist['ema14_d'] = pd.Series(pd.Series.ewm(hist['Close'],span=14, min_periods = 14 - 1, adjust=False).mean())

    # Calculo de medias moviles exponenciales de 21 y 42 días
    hist['ema21_d'] = pd.Series(pd.Series.ewm(hist['Close'],span=21, min_periods = 21 - 1, adjust=False).mean())
    hist['ema42_d'] = pd.Series(pd.Series.ewm(hist['Close'],span=42, min_periods = 42 - 1, adjust=False).mean())

    ema100_d = float(close.ewm(span=100, min_periods = 100 - 1, adjust=False).mean().iloc[-1])
    ema200_d = float(close.ewm(span=200, min_periods = 200 - 1, adjust=False).mean().iloc[-1])
    
    # Volumen promedio semanal diario (últimas 5 semanas ≈ 25 días hábiles) para comparación de señales diarias
    vol_avg_weekly_d = float(hist['Volume'].iloc[-25:].mean()) if len(hist) >= 25 else float(hist['Volume'].mean())

    def _upgrade_signal_d(base_signal: str, signal_day_idx: int) -> str:
        """Sube la señal a STRONG si el volumen del día del cruce superó el promedio semanal."""
        if base_signal == '-':
            return '-'
        vol_signal_day = float(hist['Volume'].iloc[signal_day_idx])
        if vol_signal_day > vol_avg_weekly_d:
            return 'STRONG BUY' if base_signal == 'BUY' else 'STRONG SELL'
        return base_signal

    # Evaluación de Cruces de Medias en los últimos 4 días
    # Cruce corto
    if hist['ema7_d'].iloc[-1] > hist['ema14_d'].iloc[-1]:  # Si hoy está en "COMPRA"
        if hist['ema7_d'].iloc[-cant_dias] < hist['ema14_d'].iloc[-cant_dias]:  # Que verifique si hace 4 días estaba en "VENTA"
            short_term_signal_d = _upgrade_signal_d('BUY', -1)
        else:
            short_term_signal_d = '-'
    elif hist['ema7_d'].iloc[-1] < hist['ema14_d'].iloc[-1]:  # Si hoy está en "VENTA"
        if hist['ema7_d'].iloc[-cant_dias] > hist['ema14_d'].iloc[-cant_dias]:  # Que verifique si hace 4 días estaba en "COMPRA"
            short_term_signal_d = _upgrade_signal_d('SELL', -1)
        else:
            short_term_signal_d = '-'
    else:
        short_term_signal_d = '-'

    # Cruce medio
    if hist['ema21_d'].iloc[-1] > hist['ema42_d'].iloc[-1]:  # Si hoy está en "COMPRA"
        if hist['ema21_d'].iloc[-cant_dias] < hist['ema42_d'].iloc[-cant_dias]:  # Que verifique si hace 4 días estaba en "VENTA"
            medium_term_signal_d = _upgrade_signal_d('BUY', -1)
        else:
            medium_term_signal_d = '-'
        
    elif hist['ema21_d'].iloc[-1] < hist['ema42_d'].iloc[-1]:  # Si hoy está en "VENTA"
        if hist['ema21_d'].iloc[-cant_dias] > hist['ema42_d'].iloc[-cant_dias]:  # Que verifique si hace 4 días estaba en "COMPRA"
            medium_term_signal_d = _upgrade_signal_d('SELL', -1)
        else:
            medium_term_signal_d = '-'
    else:
        medium_term_signal_d = '-'
            
            
    # Calculo indicadores Semanales
    hist_w = ticker.history(period="5y", interval="1wk")

    if hist_w.empty or len(hist_w) < 210:
        print(f"[!] hist_wórico insuficiente para {sym_clean}.")
        return None

    close = hist_w['Close']

    current_price_w = float(close.iloc[-1])
    prev_price = float(close.iloc[-2])
    change_pct = ((current_price_w - prev_price) / prev_price) * 100.0

    # Calculo de medias moviles exponenciales de 7 y 14 semanas
    hist_w['ema7_w'] = pd.Series(
        pd.Series.ewm(
            hist_w['Close'],
            span=7,
            min_periods=7 - 1,
            adjust=False
        ).mean()
    )

    hist_w['ema14_w'] = pd.Series(
        pd.Series.ewm(
            hist_w['Close'],
            span=14,
            min_periods=14 - 1,
            adjust=False
        ).mean()
    )

    # Calculo de medias moviles exponenciales de 21 y 42 semanas
    hist_w['ema21_w'] = pd.Series(
        pd.Series.ewm(
            hist_w['Close'],
            span=21,
            min_periods=21 - 1,
            adjust=False
        ).mean()
    )

    hist_w['ema42_w'] = pd.Series(
        pd.Series.ewm(
            hist_w['Close'],
            span=42,
            min_periods=42 - 1,
            adjust=False
        ).mean()
    )

    # EMA de referencia de 50 y 200 semanas
    ema100_w = float(
        close.ewm(
            span=100,
            min_periods=100 - 1,
            adjust=False
        ).mean().iloc[-1]
    )

    ema200_w = float(
        close.ewm(
            span=200,
            min_periods=200 - 1,
            adjust=False
        ).mean().iloc[-1]
    )

    # Cantidad de semanas hacia atrás que se utiliza para detectar el cruce
    cant_semanas = 2

    # Volumen promedio mensual semanal (últimas 4 semanas) para comparación de señales semanales
    vol_avg_monthly_w = float(hist_w['Volume'].iloc[-4:].mean()) if len(hist_w) >= 4 else float(hist_w['Volume'].mean())

    def _upgrade_signal_w(base_signal: str, signal_week_idx: int) -> str:
        """Sube la señal a STRONG si el volumen de la semana del cruce superó el promedio mensual."""
        if base_signal == '-':
            return '-'
        vol_signal_week = float(hist_w['Volume'].iloc[signal_week_idx])
        if vol_signal_week > vol_avg_monthly_w:
            return 'STRONG BUY' if base_signal == 'BUY' else 'STRONG SELL'
        return base_signal

    # Evaluación de Cruces de Medias en las últimas 4 semanas

    # Cruce corto: EMA 7 vs EMA 14
    if hist_w['ema7_w'].iloc[-1] > hist_w['ema14_w'].iloc[-1]:

        # Actualmente está en COMPRA.
        # Verificamos si hace 4 semanas estaba en VENTA.
        if hist_w['ema7_w'].iloc[-cant_semanas] < hist_w['ema14_w'].iloc[-cant_semanas]:
            short_term_signal_w = _upgrade_signal_w('BUY', -1)
        else:
            short_term_signal_w = '-'

    elif hist_w['ema7_w'].iloc[-1] < hist_w['ema14_w'].iloc[-1]:

        # Actualmente está en VENTA.
        # Verificamos si hace 4 semanas estaba en COMPRA.
        if hist_w['ema7_w'].iloc[-cant_semanas] > hist_w['ema14_w'].iloc[-cant_semanas]:
            short_term_signal_w = _upgrade_signal_w('SELL', -1)
        else:
            short_term_signal_w = '-'

    else:
        short_term_signal_w = '-'


    # Cruce medio: EMA 21 vs EMA 42
    if hist_w['ema21_w'].iloc[-1] > hist_w['ema42_w'].iloc[-1]:

        # Actualmente está en COMPRA.
        # Verificamos si hace 4 semanas estaba en VENTA.
        if hist_w['ema21_w'].iloc[-cant_semanas] < hist_w['ema42_w'].iloc[-cant_semanas]:
            medium_term_signal_w = _upgrade_signal_w('BUY', -1)
        else:
            medium_term_signal_w = '-'

    elif hist_w['ema21_w'].iloc[-1] < hist_w['ema42_w'].iloc[-1]:

        # Actualmente está en VENTA.
        # Verificamos si hace 4 semanas estaba en COMPRA.
        if hist_w['ema21_w'].iloc[-cant_semanas] > hist_w['ema42_w'].iloc[-cant_semanas]:
            medium_term_signal_w = _upgrade_signal_w('SELL', -1)
        else:
            medium_term_signal_w = '-'

    else:
        medium_term_signal_w = '-'
            
    # RSI diario y semanal
    # Web Scraping de RSI desde Finviz para el segmento diario
    rsi_d = obtener_rsi_finviz(sym_clean)

    dist_ema100_d = round(((current_price - ema100_d) / ema100_d) * 100.0, 2)
    dist_ema200_d = round(((current_price - ema200_d) / ema200_d) * 100.0, 2)
    ema100_lt_ema200_d = "Si" if ema100_d < ema200_d else None


    # Cálculo de RSI Semanal
    rsi_w = obtener_rsi_weekly(hist_w, periodos=14)

    dist_ema100_w = round(((current_price_w - ema100_w) / ema100_w) * 100.0, 2)
    dist_ema200_w = round(((current_price_w - ema200_w) / ema200_w) * 100.0, 2)
    ema100_lt_ema200_w = "Si" if ema100_w < ema200_w else None

    raw_sec = info.get('sector', '')
    raw_ind = info.get('industry', '')
    gics_sector, industry_group = map_gics_classification(sym_clean, raw_sec, raw_ind)

    # Competidores directos
    competitors = DIRECT_COMPETITORS.get(sym_clean, [])
    if not competitors:
        recommended = info.get('recommendedSymbols', [])
        competitors = [p['symbol'] if isinstance(p, dict) else str(p) for p in recommended[:4]] if recommended else []

    kb = KNOWLEDGE_BASE.get(sym_clean, {})
    official_summary = info.get("longBusinessSummary", "")
    
    model_summary = kb.get("model_summary", official_summary)
    main_activity = kb.get("main_activity", raw_ind if raw_ind else "Actividad corporativa oficial")
    main_revenue_source = kb.get("main_revenue_source", raw_sec if raw_sec else "Ventas y servicios")
    moat = kb.get("moat", "")
    risks = kb.get("risks", "")
    future_outlook = kb.get("future_outlook", "")

    earnings_history = extract_quarterly_history(ticker)

    pe_ratio = info.get('trailingPE', None)
    forward_pe = info.get('forwardPE', None)
    eps = info.get('trailingEps', None)
    forward_eps = info.get('forwardEps', None)
    debt_equity = info.get('debtToEquity', None)
    beta = info.get('beta', info.get('beta3Year', None))
    book_value = info.get('bookValue', None)

    # ===== Bloque de Fundamentals: desvíos de valuación =====
    hist_pe_avg, pe_vs_hist_pct = compute_pe_deviation_vs_history(ticker, hist_w, pe_ratio, years=3)

    extended_eligible = gics_sector in EXTENDED_FUNDAMENTALS_SECTORS

    forward_pe_vs_hist_pct = "N/A"
    book_price_dev = "N/A"
    if extended_eligible:
        fpe_dev = compute_forward_pe_deviation(hist_pe_avg, pe_ratio, forward_pe)
        forward_pe_vs_hist_pct = fpe_dev if fpe_dev is not None else "N/A"

        bp_dev = compute_book_price_deviation(current_price, book_value)
        book_price_dev = bp_dev if bp_dev is not None else "N/A"

    print(f"Finalizado {symbol}.")
    
    return {
        "ticker": sym_clean,
        "name": info.get('longName', sym_clean),
        "sector": gics_sector,
        "industry_group": industry_group,
        "industry": raw_ind,
        "price": round(current_price, 2),
        "change_pct": round(change_pct, 2),
        "business_model": {
            "summary": model_summary,
            "main_activity": main_activity,
            "revenue_source": main_revenue_source
        },
        "fundamental": {
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "forward_pe": round(forward_pe, 2) if forward_pe else "N/A",
            "eps": round(eps, 2) if eps else "N/A",
            "forward_eps": round(forward_eps, 2) if forward_eps else "N/A",
            "debt_to_equity": round(debt_equity, 2) if debt_equity else "N/A",
            "moat": moat,
            "risks": risks,
            "future_outlook": future_outlook,
            "competitors": competitors,
            "quarterly_history": earnings_history
        },
        "technical_daily": {
            "rsi": round(rsi_d, 2),
            "ema7": round(float(hist['ema7_d'].iloc[-1]), 2),
            "ema14": round(float(hist['ema14_d'].iloc[-1]), 2),
            "ema21": round(float(hist['ema21_d'].iloc[-1]), 2),
            "ema42": round(float(hist['ema42_d'].iloc[-1]), 2),
            "ema100": round(ema100_d, 2),
            "ema200": round(ema200_d, 2),
            "signals": {
                "short_term": short_term_signal_d,
                "medium_term": medium_term_signal_d
            },
            "dist_ema100": dist_ema100_d,
            "dist_ema200": dist_ema200_d,
            "ema100_lt_ema200": ema100_lt_ema200_d
        },
        "technical_weekly": {
            "rsi": round(rsi_w, 2),
            "ema7": round(float(hist_w['ema7_w'].iloc[-1]), 2),
            "ema14": round(float(hist_w['ema14_w'].iloc[-1]), 2),
            "ema21": round(float(hist_w['ema21_w'].iloc[-1]), 2),
            "ema42": round(float(hist_w['ema42_w'].iloc[-1]), 2),
            "ema100": round(ema100_w, 2),
            "ema200": round(ema200_w, 2),
            "signals": {
                "short_term": short_term_signal_w,
                "medium_term": medium_term_signal_w
            },
            "dist_ema100": dist_ema100_w,
            "dist_ema200": dist_ema200_w,
            "ema100_lt_ema200": ema100_lt_ema200_w
        },
        "technical": {
            "beta": round(beta, 2) if (beta is not None and not np.isnan(beta)) else "N/A"
        },
        "fundamentals": {
            "beta": round(beta, 2) if (beta is not None and not np.isnan(beta)) else "N/A",
            "pe_vs_hist_pct": pe_vs_hist_pct if pe_vs_hist_pct is not None else "N/A",
            "pe_hist_avg_3y": hist_pe_avg if hist_pe_avg is not None else "N/A",
            "pe_vs_sector_pct": "N/A",  # se completa en compute_sector_pe_deviation() tras procesar todo el universo
            "sector_pe_avg": "N/A",
            "extended_eligible": extended_eligible,
            "forward_pe_vs_hist_pct": forward_pe_vs_hist_pct,
            "book_price_dev": book_price_dev
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }



def fetch_macro_indicators() -> dict:
    """
    Descarga los indicadores macroeconómicos globales y devuelve un dict con
    valor actual, valor del mes anterior y timestamp de actualización.

    Fuentes:
    - yfinance: DXY (DX-Y.NYB), VIX (^VIX), Cobre (HG=F), Oro (GC=F)
    - FRED via requests: HY Spread (BAMLH0A0HYM2), Curva 10Y-2Y (T10Y2Y),
      MOVE Index (BAMLMOVE), Global M2 (aproximado via M2SL USA como proxy),
      PCE Inflation MoM (PCEPI)
    - yfinance proxy para PMI Global: no disponible directamente → se usa ISM
      Manufacturing (no tiene ticker yf) → se omite y se marca como N/D
    - OECD CLI y Global Credit Impulse: no tienen API pública gratuita en tiempo
      real → se marcan como N/D con nota
    """

    # Mapeo de tickers de yfinance: {id: yf_ticker}
    YF_TICKERS = {
        "DXY":          "DX-Y.NYB",
        "VIX":          "^VIX",
        "COPPER":       "HG=F",   # precio cobre en USD/lb
        "GOLD":         "GC=F",   # precio oro en USD/oz
    }

    # Tickers de FRED (Federal Reserve Economic Data) — API pública sin key
    # Formato: series_id → (id_interno, descripción)
    FRED_SERIES = {
        "BAMLH0A0HYM2": "HY_SPREAD",       # ICE BofA HY OAS en bps
        "T10Y2Y":        "YIELD_CURVE",     # 10Y-2Y spread en bps*100 (viene en %)
        "M2SL":          "GLOBAL_M2",       # M2 USA YoY como proxy global (en miles de millones)
        "PCEPILFE":      "GLOBAL_INFLATION",# PCE Core MoM — proxy de inflación global
    }

    result = {}

    # ── Helper: extrae una Serie 1D de Close de un DataFrame de yfinance ─────
    def _extract_close(df: pd.DataFrame) -> pd.Series:
        """
        yfinance >=0.2.x devuelve columnas multi-nivel (Close, Ticker) cuando
        se descarga un solo símbolo. Esta función normaliza ambos casos.
        """
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            # Multi-nivel: tomar la primera (y única) columna
            close = close.iloc[:, 0]
        return close.dropna()

    # ── Helper: descarga CSV de FRED de forma robusta ─────────────────────────
    def _fred_series(series_id: str) -> pd.DataFrame:
        """
        Descarga una serie de FRED. El CSV puede tener el encabezado de fecha
        como 'DATE' o sin nombre. Se lee con `header=0` y se renombra la primera
        columna a 'date' para garantizar consistencia.
        """
        from io import StringIO
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        # Renombrar primera columna a 'date' independientemente del nombre original
        df.columns = ['date'] + list(df.columns[1:])
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)
        # Convertir columna de valores a numérico (reemplaza "." o vacíos por NaN)
        val_col = df.columns[1]
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
        df = df.dropna(subset=[val_col])
        return df

    # ── 1. yfinance: descarga histórico de ~60 días ───────────────────────────
    for ind_id, yf_ticker in YF_TICKERS.items():
        try:
            df = yf.download(yf_ticker, period="60d", interval="1d", progress=False, auto_adjust=True)
            if df.empty or len(df) < 2:
                result[ind_id] = {"value": None, "prev": None}
                continue
            close = _extract_close(df)
            if len(close) < 2:
                result[ind_id] = {"value": None, "prev": None}
                continue
            current_val = float(close.iloc[-1])
            prev_idx = max(0, len(close) - 22)
            prev_val = float(close.iloc[prev_idx])
            result[ind_id] = {"value": round(current_val, 4), "prev": round(prev_val, 4)}
        except Exception as e:
            print(f"[!] Error descargando {ind_id} ({yf_ticker}) via yfinance: {e}")
            result[ind_id] = {"value": None, "prev": None}

    # Calcular ratio Cobre/Oro
    try:
        c = result.get("COPPER", {})
        g = result.get("GOLD", {})
        if c.get("value") and g.get("value") and g["value"] > 0:
            result["COPPER_GOLD"] = {
                "value": round(c["value"] / g["value"], 6),
                "prev":  round(c["prev"]  / g["prev"],  6) if g.get("prev") and g["prev"] > 0 else None
            }
        else:
            result["COPPER_GOLD"] = {"value": None, "prev": None}
    except Exception:
        result["COPPER_GOLD"] = {"value": None, "prev": None}

    # ── 2. FRED: descarga de series económicas ───────────────────────────────
    for series_id, ind_id in FRED_SERIES.items():
        try:
            df_fred = _fred_series(series_id)
            if df_fred.empty or len(df_fred) < 2:
                result[ind_id] = {"value": None, "prev": None}
                continue

            val_col = df_fred.columns[1]
            current_val = float(df_fred[val_col].iloc[-1])
            prev_val    = float(df_fred[val_col].iloc[-2])

            # Conversiones según indicador
            if ind_id == "YIELD_CURVE":
                # FRED devuelve el spread en % (e.g. -0.5 = -50 bps); convertir a bps
                current_val = round(current_val * 100, 1)
                prev_val    = round(prev_val    * 100, 1)
            elif ind_id == "GLOBAL_M2":
                # Calcular crecimiento YoY en %: necesitamos dato de ~12 meses antes
                if len(df_fred) >= 13:
                    val_12m_ago_curr = float(df_fred[val_col].iloc[-13])
                    val_12m_ago_prev = float(df_fred[val_col].iloc[-14]) if len(df_fred) >= 14 else val_12m_ago_curr
                    current_val = round(((current_val - val_12m_ago_curr) / val_12m_ago_curr) * 100, 2)
                    prev_val    = round(((prev_val    - val_12m_ago_prev) / val_12m_ago_prev) * 100, 2)
                else:
                    current_val = None
                    prev_val    = None
            elif ind_id == "GLOBAL_INFLATION":
                # Calcular variación MoM en %
                if prev_val and prev_val != 0:
                    mom = round(((current_val - prev_val) / abs(prev_val)) * 100, 3)
                    # Para el "prev" del mes anterior tomamos el dato de hace 2 períodos
                    prev2_val = float(df_fred[val_col].iloc[-3]) if len(df_fred) >= 3 else prev_val
                    mom_prev  = round(((prev_val - prev2_val) / abs(prev2_val)) * 100, 3) if prev2_val else None
                    current_val = mom
                    prev_val    = mom_prev
                else:
                    current_val = None
                    prev_val    = None
            else:
                current_val = round(current_val, 2)
                prev_val    = round(prev_val,    2)

            result[ind_id] = {"value": current_val, "prev": prev_val}

        except Exception as e:
            print(f"[!] Error descargando {ind_id} ({series_id}) via FRED: {e}")
            result[ind_id] = {"value": None, "prev": None}

    # ── 3. MOVE Index via yfinance ────────────────────────────────────────────
    try:
        df_move = yf.download("^MOVE", period="60d", interval="1d", progress=False, auto_adjust=True)
        if not df_move.empty and len(df_move) >= 2:
            close_move = _extract_close(df_move)
            if len(close_move) >= 2:
                move_val  = float(close_move.iloc[-1])
                move_prev = float(close_move.iloc[max(0, len(close_move) - 22)])
                vix_val  = result.get("VIX", {}).get("value")
                vix_prev = result.get("VIX", {}).get("prev")
                result["MOVE_VIX"] = {
                    "value": round(move_val / vix_val, 3)   if vix_val  and vix_val  > 0 else None,
                    "prev":  round(move_prev / vix_prev, 3) if vix_prev and vix_prev > 0 else None,
                }
            else:
                result["MOVE_VIX"] = {"value": None, "prev": None}
        else:
            result["MOVE_VIX"] = {"value": None, "prev": None}
    except Exception:
        result["MOVE_VIX"] = {"value": None, "prev": None}

    # ── 4. Global PMI Composite via yfinance (no hay ticker público gratuito) ──
    # Se aproxima con el ETF de PMI manufacturero o se deja N/D
    result["GLOBAL_PMI"] = {"value": None, "prev": None}

    # ── 5. OECD CLI y Global Credit Impulse — no tienen API gratuita en tiempo real ──
    result["OECD_CLI"]       = {"value": None, "prev": None}
    result["CREDIT_IMPULSE"] = {"value": None, "prev": None}

    result["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result


def main():
    excel_file = "https://github.com/francubisino/dashboard-financiero/blob/44312877ead2728cb629e97b5e3c0bef8c548d3e/Seguimiento.xls"
    if not os.path.exists(excel_file):
        excel_file = "https://github.com/francubisino/dashboard-financiero/blob/44312877ead2728cb629e97b5e3c0bef8c548d3e/Seguimiento.xls"

    if not os.path.exists(excel_file):
        print(f"[!] No se encontró el libro Excel '{excel_file}'.")
        return

    try:
        df = pd.read_excel(excel_file, sheet_name="Empresas")
        raw_tickers = df.iloc[:, 0].dropna().tolist()
        tickers = [str(t).strip().upper() for t in raw_tickers if str(t).strip()] #['JPM','BAC','WFC','C'] #
    except Exception as e:
        print(f"[!] Error al leer el Excel: {e}")
        return

    print(f"[*] Lista original de tickers ({len(tickers)}): {tickers}")

    stocks = []
    for sym in tickers:
        try:
            record = process_ticker(sym)
            if record:
                stocks.append(record)
            time.sleep(0.5)
        except Exception as err:
            print(f"[!] Error procesando {sym}: {err}")

    # Completa el desvío de P/E vs. P/E promedio del sector, usando el propio universo procesado
    stocks = compute_sector_pe_deviation(stocks)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=4)

    print(f"[✓] Proceso ETL finalizado. 'data.json' generado con {len(stocks)} acciones individuales.")

    # ── Indicadores Macro Globales ──────────────────────────────────────────────
    print("[*] Descargando indicadores macro globales...")
    macro_data = fetch_macro_indicators()
    with open("macro.json", "w", encoding="utf-8") as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=4)
    print("[✓] 'macro.json' generado correctamente.")

if __name__ == "__main__":
    main()

#Instalar los siguientes paquetes 
#pip install yfinance pandas numpy matplotlib seaborn scipy

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 1. CONFIGURACIÓN DE TICKERS Y SECTORES (BVC)
# ============================================================
# Los tickers de la BVC en Yahoo Finance usan el sufijo ".CR".
# Se incluyen acciones representativas del índice IBC.
TICKERS_BVC = {
    "BVCC.CR": "Financiero",
    "BVL.CR":  "Financiero",
    "BPV.CR":  "Financiero",
    "ABC.A.CR": "Financiero",
    "BNC.CR":  "Financiero",
    "MVZ.A.CR": "Financiero",
    "CRM.A.CR": "Industrial",
    "DOM.CR":   "Industrial",
    "ENV.CR":   "Industrial",
    "MPA.CR":   "Industrial",
    "RST.B.CR": "Consumo",
    "SVS.CR":   "Industrial",
    "TDV.D.CR": "Telecomunicaciones",
    "CGQ.CR":   "Químico",
    "FNC.CR":   "Construcción",
    "PTN.CR":   "Agroindustria",
    "GZL.CR":   "Servicios",
    "PIV.B.CR": "Financiero",
}

PERIODOS = {
    "1 semana": "1wk",
    "1 mes": "1mo",
    "3 meses": "3mo",
    "6 meses": "6mo",
    "1 año": "1y",
    "Todo": "max"
}

# ============================================================
# 2. DESCARGA DE DATOS
# ============================================================
def descargar_datos(ticker: str, periodo: str = "1y") -> pd.DataFrame:
    """
    Descarga el histórico de un ticker de Yahoo Finance.
    Devuelve un DataFrame con columnas Open, High, Low, Close, Volume.
    """
    try:
        data = yf.download(ticker, period=periodo, progress=False, auto_adjust=True)
        if data.empty:
            print(f"⚠️ No se encontraron datos para {ticker} en el período '{periodo}'.")
            return pd.DataFrame()
        # Si yfinance devuelve MultiIndex (por versión), aplanar
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        print(f"❌ Error al descargar {ticker}: {e}")
        return pd.DataFrame()

# ============================================================
# 3. GRÁFICO INDIVIDUAL CON TENDENCIA
# ============================================================
def graficar_ticker(ticker: str, periodo: str = "1y"):
    """
    Muestra precio de cierre, volumen, medias móviles y una
    proyección lineal simple (tendencia) a 30 días.
    """
    df = descargar_datos(ticker, periodo)
    if df.empty:
        return

    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    # Regresión lineal para tendencia futura
    df["idx"] = np.arange(len(df))
    pendiente, intercepto, r_val, p_val, std_err = stats.linregress(df["idx"], df["Close"])
    df["Tendencia"] = intercepto + pendiente * df["idx"]

    # Proyección a 30 días hábiles
    dias_futuros = 30
    futuro_idx = np.arange(len(df), len(df) + dias_futuros)
    futuro_fechas = pd.bdate_range(df.index[-1] + timedelta(days=1), periods=dias_futuros)
    futuro_precios = intercepto + pendiente * futuro_idx

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=False,
                                   gridspec_kw={"height_ratios": [3, 1]})

    # Panel superior: precios y tendencia
    ax1.plot(df.index, df["Close"], label="Cierre", color="steelblue", linewidth=1.5)
    ax1.plot(df.index, df["MA20"], label="MM20", color="orange", alpha=0.7, linestyle="--")
    ax1.plot(df.index, df["MA50"], label="MM50", color="green", alpha=0.7, linestyle="--")
    ax1.plot(df.index, df["Tendencia"], label="Tendencia lineal", color="red", alpha=0.6, linestyle=":")
    ax1.plot(futuro_fechas, futuro_precios, label="Proyección 30d", color="purple",
             linestyle="-.", linewidth=2)
    ax1.set_title(f"{ticker} — Precio de cierre y tendencia ({periodo})", fontsize=14)
    ax1.set_ylabel("Precio (Bs.)")
    ax1.legend(loc="upper left")
    ax1.grid(alpha=0.3)

    # Panel inferior: volumen
    ax2.bar(df.index, df["Volume"], color="gray", alpha=0.5, width=1.0)
    ax2.set_ylabel("Volumen")
    ax2.set_xlabel("Fecha")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Resumen numérico
    print(f"\n📊 RESUMEN DE TENDENCIA — {ticker}")
    print(f"   Pendiente diaria : {pendiente:,.4f} Bs/día")
    print(f"   R²               : {r_val**2:.3f}")
    print(f"   Precio actual    : {df['Close'].iloc[-1]:,.2f} Bs.")
    print(f"   Precio proyectado a 30d: {futuro_precios[-1]:,.2f} Bs.")
    print(f"   Variación esperada    : {((futuro_precios[-1]/df['Close'].iloc[-1])-1)*100:,.2f}%")

# ============================================================
# 4. COMPARACIÓN DE HASTA 4 TICKERS
# ============================================================
def comparar_tickers(tickers: list, periodo: str = "1y"):
    """
    Normaliza los precios a base 100 para comparar el rendimiento
    relativo de hasta 4 activos.
    """
    if len(tickers) > 4:
        print("⚠️ Solo se permiten hasta 4 tickers. Se usarán los primeros 4.")
        tickers = tickers[:4]

    datos = {}
    for t in tickers:
        df = descargar_datos(t, periodo)
        if not df.empty:
            datos[t] = df["Close"]

    if not datos:
        print("❌ No se pudieron descargar datos para comparar.")
        return

    df_close = pd.DataFrame(datos).dropna()
    df_norm = (df_close / df_close.iloc[0]) * 100

    plt.figure(figsize=(12, 6))
    for col in df_norm.columns:
        plt.plot(df_norm.index, df_norm[col], label=col, linewidth=1.8)

    plt.title(f"Comparación de rendimiento relativo (base 100) — {periodo}", fontsize=14)
    plt.ylabel("Índice base 100")
    plt.xlabel("Fecha")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Rendimiento total del período
    print("\n📈 RENDIMIENTO TOTAL DEL PERÍODO")
    for col in df_norm.columns:
        rent = (df_norm[col].iloc[-1] / 100 - 1) * 100
        print(f"   {col}: {rent:,.2f}%")

# ============================================================
# 5. MATRIZ DE CORRELACIÓN
# ============================================================
def matriz_correlacion(tickers: list, periodo: str = "1y"):
    """
    Calcula y visualiza la matriz de correlación de los retornos diarios.
    Valores cercanos a 0 indican baja correlación (oportunidad de diversificación).
    """
    datos = {}
    for t in tickers:
        df = descargar_datos(t, periodo)
        if not df.empty:
            datos[t] = df["Close"].pct_change().dropna()

    if len(datos) < 2:
        print("⚠️ Se necesitan al menos 2 tickers con datos para la correlación.")
        return

    df_ret = pd.DataFrame(datos).dropna()
    corr = df_ret.corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn_r", vmin=-1, vmax=1,
                square=True, linewidths=0.5)
    plt.title(f"Matriz de correlación de retornos diarios — {periodo}", fontsize=14)
    plt.tight_layout()
    plt.show()

    print("\n🔗 CORRELACIONES PROMEDIO (menor = mejor para diversificar)")
    for col in corr.columns:
        avg_corr = corr[col].drop(col).mean()
        print(f"   {col}: {avg_corr:.3f}")
    return corr

# ============================================================
# 6. OPTIMIZACIÓN DE PORTAFOLIO CON MOCHILA 0/1
# ============================================================
def knapsack_01(pesos, valores, capacidad):
    """
    Resuelve el problema de la mochila 0/1 mediante programación dinámica.
    Devuelve la lista de índices seleccionados y el valor total.
    """
    n = len(pesos)
    # Tabla DP: filas = ítems, columnas = capacidad (en unidades enteras)
    # Para evitar decimales, escalamos los pesos a enteros (x100)
    escala = 100
    pesos_int = [int(round(p * escala)) for p in pesos]
    cap_int = int(round(capacidad * escala))
    dp = [[0] * (cap_int + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(cap_int + 1):
            if pesos_int[i-1] <= w:
                dp[i][w] = max(dp[i-1][w],
                               dp[i-1][w - pesos_int[i-1]] + valores[i-1])
            else:
                dp[i][w] = dp[i-1][w]

    # Reconstruir selección
    seleccion = []
    w = cap_int
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            seleccion.append(i-1)
            w -= pesos_int[i-1]
    seleccion.reverse()
    return seleccion, dp[n][cap_int]

def optimizar_portafolio(presupuesto: float, periodo: str = "1y"):
    """
    1. Descarga datos de todos los tickers disponibles.
    2. Calcula retorno esperado y volatilidad.
    3. Selecciona el mejor representante por sector (mayor Sharpe).
    4. Aplica mochila 0/1 con peso = precio actual y valor = Sharpe ratio.
    5. Muestra el portafolio sugerido.
    """
    registros = []
    for ticker, sector in TICKERS_BVC.items():
        df = descargar_datos(ticker, periodo)
        if df.empty or len(df) < 30:
            continue
        ret = df["Close"].pct_change().dropna()
        if len(ret) < 20:
            continue
        retorno_medio = ret.mean()
        volatilidad = ret.std()
        if volatilidad == 0:
            continue
        sharpe = retorno_medio / volatilidad  # Simplificado (sin tasa libre de riesgo)
        precio_actual = df["Close"].iloc[-1]
        registros.append({
            "ticker": ticker,
            "sector": sector,
            "precio": float(precio_actual),
            "retorno_medio": float(retorno_medio),
            "volatilidad": float(volatilidad),
            "sharpe": float(sharpe)
        })

    if not registros:
        print("❌ No hay datos suficientes para optimizar el portafolio.")
        return

    df_reg = pd.DataFrame(registros)

    # Seleccionar el mejor Sharpe por sector (diversificación sectorial)
    df_mejores = df_reg.loc[df_reg.groupby("sector")["sharpe"].idxmax()].reset_index(drop=True)

    print("\n🏆 MEJOR ACCIÓN POR SECTOR (candidatas a la mochila)")
    print(df_mejores[["ticker", "sector", "precio", "sharpe"]].to_string(index=False))

    # Mochila 0/1
    pesos = df_mejores["precio"].tolist()
    valores = df_mejores["sharpe"].tolist()
    idx_sel, valor_total = knapsack_01(pesos, valores, presupuesto)

    if not idx_sel:
        print(f"\n⚠️ Con un presupuesto de {presupuesto:,.2f} Bs. no se puede adquirir ninguna acción.")
        return

    seleccion = df_mejores.iloc[idx_sel].copy()
    seleccion["costo"] = seleccion["precio"]
    costo_total = seleccion["costo"].sum()

    print(f"\n✅ PORTAFOLIO SUGERIDO (Mochila 0/1) — Presupuesto: {presupuesto:,.2f} Bs.")
    print(seleccion[["ticker", "sector", "precio", "sharpe"]].to_string(index=False))
    print(f"\n   Costo total : {costo_total:,.2f} Bs.")
    print(f"   Saldo restante: {presupuesto - costo_total:,.2f} Bs.")
    print(f"   Sharpe agregado (suma): {valor_total:.4f}")
    print(f"   Sectores cubiertos: {', '.join(seleccion['sector'].unique())}")

# ============================================================
# 7. MENÚ PRINCIPAL
# ============================================================
def menu():
    print("\n" + "="*60)
    print("  📈 ANALIZADOR BVC — Yahoo Finance + Mochila 0/1")
    print("="*60)
    print("1. Ver histórico y tendencia de un ticker")
    print("2. Comparar hasta 4 tickers")
    print("3. Matriz de correlación")
    print("4. Sugerir portafolio con mochila (presupuesto)")
    print("5. Salir")

    opcion = input("\nSeleccione una opción (1-5): ").strip()

    if opcion == "1":
        ticker = input("Ingrese el ticker (ej. BVCC.CR): ").strip().upper()
        print("Períodos disponibles:")
        for i, (nombre, _) in enumerate(PERIODOS.items(), 1):
            print(f"  {i}. {nombre}")
        per_idx = int(input("Elija período (1-6): ")) - 1
        periodo_nombre = list(PERIODOS.keys())[per_idx]
        periodo = PERIODOS[periodo_nombre]
        graficar_ticker(ticker, periodo)

    elif opcion == "2":
        raw = input("Ingrese hasta 4 tickers separados por coma (ej. BVCC.CR,BVL.CR,BPV.CR): ").strip().upper()
        tickers = [t.strip() for t in raw.split(",") if t.strip()]
        per_idx = int(input("Período (1=1sem, 2=1mes, 3=3meses, 4=6meses, 5=1año, 6=Todo): ")) - 1
        periodo = list(PERIODOS.values())[per_idx]
        comparar_tickers(tickers, periodo)

    elif opcion == "3":
        raw = input("Ingrese tickers separados por coma (mínimo 2): ").strip().upper()
        tickers = [t.strip() for t in raw.split(",") if t.strip()]
        per_idx = int(input("Período (1=1sem, 2=1mes, 3=3meses, 4=6meses, 5=1año, 6=Todo): ")) - 1
        periodo = list(PERIODOS.values())[per_idx]
        matriz_correlacion(tickers, periodo)

    elif opcion == "4":
        presupuesto = float(input("Ingrese el presupuesto en Bs.: "))
        per_idx = int(input("Período para estimar métricas (1=1mes, 2=3meses, 3=6meses, 4=1año, 5=Todo): ")) - 1
        periodo = ["1mo", "3mo", "6mo", "1y", "max"][per_idx]
        optimizar_portafolio(presupuesto, periodo)

    elif opcion == "5":
        print("👋 Saliendo del analizador.")
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    menu()
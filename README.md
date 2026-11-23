# analisisfinancierobolsadevaloresdecaracas

Análisis financiero de la bolsa de valores de Caracas 


📌 Notas sobre el funcionamiento y la lógica financiera

1. Tickers de la BVC en Yahoo Finance:
      La BVC no tiene una cobertura tan amplia como otros mercados, pero acciones como BVCC.CR (Bolsa de Valores de Caracas), BVL.CR (Banco de Venezuela) o BPV.CR (Banco Provincial) sí están disponibles con el sufijo .CR. El programa incluye un diccionario con 18 tickers representativos del índice IBC.
2. Períodos seleccionables:
      Se usa directamente el parámetro period de yfinance (1wk, 1mo, 3mo, 6mo, 1y, max), por lo que no hay que calcular fechas manualmente.
3. Análisis de tendencia futura:
      Se ajusta una regresión lineal simple sobre el precio de cierre y se proyectan 30 días hábiles. Se muestra la pendiente diaria, el coeficiente de determinación R^2 y el precio proyectado. Es una aproximación educativa, no una predicción financiera profesional.
4. Comparación de hasta 4 tickers:
      Los precios se normalizan a base 100 para comparar el rendimiento relativo sin que las diferencias de escala (por ejemplo, Bs. vs. USD) distorsionen la gráfica.
5. Matriz de correlación:
      Se calcula sobre los retornos diarios (pct_change). Un valor cercano a 0 indica baja correlación (buen candidato para diversificar); cercano a 1 indica que se mueven juntos (malo para diversificar). Se muestra un heatmap con anotaciones.
6. Mochila 0/1 aplicada al portafolio:
   · Peso: precio actual de la acción (Bs.).
   · Valor: Sharpe ratio simplificado (retorno medio / volatilidad).
   · Capacidad: presupuesto ingresado por el usuario.
        Antes de la mochila, se elige la acción con mejor Sharpe de cada sector para garantizar que el portafolio esté diversificado sectorialmente. Luego la mochila selecciona el subconjunto que maximiza el Sharpe total sin exceder el presupuesto.
   · Si el presupuesto no alcanza para ninguna acción, se informa.
   · Es una adaptación del problema clásico de la mochila 0/1, ampliamente usado en selección de portafolios bajo restricción de capital.
7. Advertencia:
      Este programa es una herramienta educativa de análisis cuantitativo. No constituye asesoría financiera. Los datos de Yahoo Finance para la BVC pueden tener retrasos o interrupciones, y los precios en bolívares pueden estar sujetos a alta volatilidad cambiaria.

Incorporación de interfaz gráfica con Tkinder ajustable 

A continuación te presento una versión completamente rediseñada del analizador, ahora con interfaz gráfica Tkinter que se adapta automáticamente a la resolución de pantalla del sistema, junto con un conjunto de recomendaciones para obtener tendencias más realistas y una guía para incorporar el análisis de noticias financieras.

---

🖥️ Interfaz Tkinter adaptativa

Estrategia de adaptación a la resolución

El problema de las interfaces Tkinter que “no caben” en pantallas pequeñas se debe a tres prácticas comunes: usar geometry("1440x900") fijo, emplear place() con coordenadas absolutas y no consultar el tamaño real del monitor. La solución consiste en:

1. Obtener la resolución real con winfo_screenwidth() y winfo_screenheight() al iniciar la aplicación.
2. Calcular un factor de escala respecto a una resolución de referencia (por ejemplo, 1920×1080) y aplicarlo a fuentes, paddings y tamaños mínimos.
3. Usar grid() o pack() en lugar de place(), ya que los gestores geométricos relativos permiten que los widgets se redimensionen con la ventana.
4. Definir un tamaño mínimo de ventana (minsize) basado en el espacio disponible, para evitar que los controles se oculten.

Puntos clave de la adaptación:

· El factor self.factor se calcula una sola vez y se reutiliza en todas las fuentes y paddings.
· La ventana ocupa el 88% de la pantalla, dejando márgenes para la barra de tareas.
· Se usa grid/pack en todos los paneles; ningún widget depende de coordenadas fijas.
· El Treeview y las áreas de gráficos se expanden con fill="both", expand=True.


📊 Análisis adicionales para tendencias más realistas

La regresión lineal simple es un punto de partida, pero para tendencias realistas conviene incorporar:


Categoría Indicadores / Técnicas Por qué mejora la señal
Momentum RSI, MACD, Estocástico, Williams %R Detectan sobrecompra/sobreventa y cambios de impulso antes que el precio.
Tendencia SMA/EMA de 20, 50 y 200, ADX, Ichimoku, Parabolic SAR Confirman la dirección y fuerza de la tendencia, filtrando falsas rupturas.
Volatilidad Bandas de Bollinger, ATR, Keltner, Donchian Ajustan los niveles de entrada/salida al régimen de volatilidad actual.
Patrones Fibonacci, VCP (Volatility Contraction Pattern), wedges, flags Identifican zonas de soporte/resistencia y continuaciones probables.
Volumen OBV, VWAP, volumen relativo Confirman si el movimiento tiene respaldo real o es especulativo.
Riesgo Volatilidad anualizada, drawdown máximo, beta vs. IBC Permiten dimensionar posiciones y comparar contra el índice.


Recomendación práctica: en lugar de una sola recta de tendencia, calcula una señal compuesta que combine al menos 3–4 indicadores no redundantes (por ejemplo, EMA50 + RSI + MACD + ATR). Si la mayoría coincide en dirección, la proyección gana robustez; si divergen, es señal de rango o incertidumbre, y la proyección lineal debe tomarse con cautela.


📰 Análisis de noticias financieras para dar exactitud

El análisis técnico por sí solo no captura shocks informativos (resultados, regulaciones, eventos macro). Para incorporar noticias necesitas dos piezas: fuente de titulares y motor de sentimiento.

Fuentes de noticias accesibles desde Python

1. yfinance ya expone noticias por ticker mediante yf.Ticker(ticker).news. Devuelve una lista de diccionarios con title, publisher, link y providerPublishTime. Es la opción más directa si ya usas Yahoo Finance.
2. NewsAPI (newsapi-python) permite búsquedas por palabra clave o ticker, pero requiere clave API y en el plan gratuito tiene límites de peticiones.
3. SentiSense ofrece un SDK oficial con noticias y sentimiento agregado por ticker (get_documents_by_ticker).
4. Apify tiene actores específicos para Yahoo Finance, Google News y Finviz que devuelven titulares ya puntuados con VADER.


Enfoque Herramienta Ventaja Limitación
Léxico general VADER (vaderSentiment) Rápido, sin entrenamiento, funciona bien en titulares cortos No entiende jerga financiera (“guidance”, “downgrade”)
Modelo financiero FinBERT (ProsusAI/finbert en Hugging Face) Entrenado en texto financiero, clasifica positivo/negativo/neutral con mayor precisión Requiere transformers y más recursos de cómputo
API externa SentiSense / FinBrain Devuelve score agregado listo para usar Depende de clave y cuota


Cómo integrarlo en el analizador

1. Añade una pestaña “📰 Noticias y sentimiento”.
2. Al seleccionar un ticker, llama a yf.Ticker(ticker).news y muestra los 5–10 titulares más recientes.
3. Pasa cada titular por VADER (o FinBERT si tienes GPU) y calcula un sentimiento promedio en una ventana móvil de 7 días.
4. Superpón ese score de sentimiento como una línea secundaria en el gráfico de precios o como un heatmap temporal debajo del volumen.
5. Cuando el sentimiento promedio sea muy negativo y el precio esté en zona de sobrecompra (RSI > 70), el sistema puede marcar una alerta de divergencia negativa; si el sentimiento es positivo y el RSI está en sobreventa, una divergencia positiva.

Advertencia importante: el sentimiento de noticias es ruidoso y tiene sesgos (los medios sobrerreaccionan, hay clickbait). Úsalo como capa de confirmación, no como señal única. Además, para la BVC la cobertura de noticias en inglés es limitada; muchas informaciones clave llegan en español y no siempre están indexadas en Yahoo Finance. En ese caso, combinar yfinance con búsquedas en Google News (vía feedparser o NewsAPI) suele dar mejor cobertura.


⚠️ Limitaciones y buenas prácticas

· Datos de la BVC en Yahoo Finance: la cobertura es irregular; algunos tickers del diccionario pueden devolver series cortas o vacías. El programa ya maneja estos casos con messagebox y omite el ticker.
· Proyección lineal: no es una predicción financiera. Es una extrapolación de tendencia que debe validarse con los indicadores adicionales y el contexto de noticias.
· Mochila 0/1: asume que puedes comprar fracciones o que el precio es el costo unitario. En la práctica, las acciones de la BVC se negocian en lotes; para un uso real habría que redondear a múltiplos enteros y considerar comisiones.
· Claves API: si integras NewsAPI o SentiSense, nunca las escribas en el código; usa variables de entorno (os.getenv("NEWS_API_KEY")) como en los ejemplos de referencia.

Con esta versión tienes una base funcional y adaptable. Los siguientes pasos naturales son: (1) añadir la pestaña de noticias con VADER/FinBERT, (2) incorporar los indicadores técnicos como columnas calculadas y (3) convertir la proyección lineal en una señal compuesta que pondere tendencia, momentum, volatilidad y sentimiento.



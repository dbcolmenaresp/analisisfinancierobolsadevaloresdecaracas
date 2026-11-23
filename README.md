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
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# CONFIGURACIÓN
# ============================================================
TICKERS_BVC = {
    "BVCC.CR": "Financiero", "BVL.CR": "Financiero", "BPV.CR": "Financiero",
    "ABC.A.CR": "Financiero", "BNC.CR": "Financiero", "MVZ.A.CR": "Financiero",
    "CRM.A.CR": "Industrial", "DOM.CR": "Industrial", "ENV.CR": "Industrial",
    "MPA.CR": "Industrial", "RST.B.CR": "Consumo", "SVS.CR": "Industrial",
    "TDV.D.CR": "Telecomunicaciones", "CGQ.CR": "Químico",
    "FNC.CR": "Construcción", "PTN.CR": "Agroindustria",
    "GZL.CR": "Servicios", "PIV.B.CR": "Financiero",
}
PERIODOS = {"1 semana": "1wk", "1 mes": "1mo", "3 meses": "3mo",
            "6 meses": "6mo", "1 año": "1y", "Todo": "max"}

# ============================================================
# CLASE PRINCIPAL
# ============================================================
class AnalizadorBVC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📈 Analizador BVC — Yahoo Finance + Mochila 0/1")
        self.configure(bg="#f0f0f0")

        # ---- Adaptación automática a la resolución ----
        self._configurar_resolucion()

        # ---- Estilos y fuentes escaladas ----
        self._configurar_estilos()

        # ---- Construcción de la UI ----
        self._construir_ui()

    def _configurar_resolucion(self):
        """Calcula factor de escala y tamaño de ventana según la pantalla."""
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()

        # Referencia de diseño: 1920x1080
        self.factor = min(ancho_pantalla / 1920, alto_pantalla / 1080)
        self.factor = max(0.7, min(self.factor, 1.6))  # límites

        ancho_ventana = int(ancho_pantalla * 0.88)
        alto_ventana = int(alto_pantalla * 0.88)
        self.geometry(f"{ancho_ventana}x{alto_ventana}+{int(ancho_pantalla*0.06)}+{int(alto_pantalla*0.06)}")
        self.minsize(int(900 * self.factor), int(600 * self.factor))

    def _configurar_estilos(self):
        """Aplica factor de escala a fuentes y paddings."""
        f = self.factor
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("TLabel", font=("Segoe UI", int(10 * f)))
        estilo.configure("TButton", font=("Segoe UI", int(10 * f)), padding=int(6 * f))
        estilo.configure("TNotebook.Tab", font=("Segoe UI", int(10 * f)), padding=(int(10*f), int(4*f)))
        estilo.configure("TCombobox", font=("Segoe UI", int(10 * f)))
        estilo.configure("TEntry", font=("Segoe UI", int(10 * f)))
        estilo.configure("Treeview", font=("Segoe UI", int(9 * f)), rowheight=int(24 * f))
        estilo.configure("Treeview.Heading", font=("Segoe UI", int(10 * f), "bold"))

    def _construir_ui(self):
        """Crea las pestañas y los paneles de la aplicación."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=int(8*self.factor), pady=int(8*self.factor))

        # Pestaña 1: Ticker individual
        self.tab_ticker = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ticker, text="📊 Ticker individual")
        self._construir_tab_ticker(self.tab_ticker)

        # Pestaña 2: Comparación
        self.tab_comparar = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_comparar, text="🔄 Comparar (≤4)")
        self._construir_tab_comparar(self.tab_comparar)

        # Pestaña 3: Correlación
        self.tab_corr = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_corr, text="🔗 Correlación")
        self._construir_tab_corr(self.tab_corr)

        # Pestaña 4: Mochila / Portafolio
        self.tab_mochila = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_mochila, text="🎒 Portafolio (Mochila)")
        self._construir_tab_mochila(self.tab_mochila)

    # ----------------------------------------------------------
    # PESTAÑA 1: TICKER INDIVIDUAL
    # ----------------------------------------------------------
    def _construir_tab_ticker(self, parent):
        f = self.factor
        frame_ctrl = ttk.Frame(parent)
        frame_ctrl.pack(fill="x", padx=int(10*f), pady=int(8*f))

        ttk.Label(frame_ctrl, text="Ticker:").pack(side="left", padx=(0, int(4*f)))
        self.entry_ticker = ttk.Entry(frame_ctrl, width=int(12*f))
        self.entry_ticker.pack(side="left", padx=(0, int(10*f)))
        self.entry_ticker.insert(0, "BVCC.CR")

        ttk.Label(frame_ctrl, text="Período:").pack(side="left", padx=(0, int(4*f)))
        self.combo_periodo_ticker = ttk.Combobox(
            frame_ctrl, values=list(PERIODOS.keys()), state="readonly", width=int(12*f))
        self.combo_periodo_ticker.pack(side="left", padx=(0, int(10*f)))
        self.combo_periodo_ticker.set("1 año")

        btn_graficar = ttk.Button(frame_ctrl, text="Graficar y analizar",
                                  command=self._graficar_ticker)
        btn_graficar.pack(side="left")

        # Área de gráfico
        self.frame_grafico_ticker = ttk.Frame(parent)
        self.frame_grafico_ticker.pack(fill="both", expand=True, padx=int(10*f), pady=int(4*f))

        # Texto de resumen
        self.text_resumen_ticker = tk.Text(parent, height=int(6*f), wrap="word",
                                           font=("Consolas", int(9*f)))
        self.text_resumen_ticker.pack(fill="x", padx=int(10*f), pady=(0, int(8*f)))

    def _graficar_ticker(self):
        ticker = self.entry_ticker.get().strip().upper()
        periodo_nombre = self.combo_periodo_ticker.get()
        periodo = PERIODOS.get(periodo_nombre, "1y")

        df = self._descargar(ticker, periodo)
        if df.empty:
            return

        df = df.copy()
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        df["idx"] = np.arange(len(df))

        pendiente, intercepto, r_val, _, _ = stats.linregress(df["idx"], df["Close"])
        df["Tendencia"] = intercepto + pendiente * df["idx"]

        dias_futuros = 30
        futuro_idx = np.arange(len(df), len(df) + dias_futuros)
        futuro_fechas = pd.bdate_range(df.index[-1] + timedelta(days=1), periods=dias_futuros)
        futuro_precios = intercepto + pendiente * futuro_idx

        fig = Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=None)

        ax1.plot(df.index, df["Close"], label="Cierre", color="steelblue", lw=1.4)
        ax1.plot(df.index, df["MA20"], label="MM20", color="orange", ls="--", alpha=0.8)
        ax1.plot(df.index, df["MA50"], label="MM50", color="green", ls="--", alpha=0.8)
        ax1.plot(df.index, df["Tendencia"], label="Tendencia", color="red", ls=":", alpha=0.7)
        ax1.plot(futuro_fechas, futuro_precios, label="Proyección 30d",
                 color="purple", ls="-.", lw=2)
        ax1.set_title(f"{ticker} — Cierre y tendencia ({periodo_nombre})", fontsize=11)
        ax1.legend(loc="upper left", fontsize=8)
        ax1.grid(alpha=0.25)

        ax2.bar(df.index, df["Volume"], color="gray", alpha=0.5, width=1.0)
        ax2.set_ylabel("Volumen")
        ax2.grid(alpha=0.25)
        fig.tight_layout()

        self._mostrar_figura(fig, self.frame_grafico_ticker)

        precio_act = df["Close"].iloc[-1]
        var_esp = ((futuro_precios[-1] / precio_act) - 1) * 100
        resumen = (
            f"Pendiente diaria : {pendiente:,.4f} Bs/día\n"
            f"R²               : {r_val**2:.3f}\n"
            f"Precio actual    : {precio_act:,.2f} Bs.\n"
            f"Proyección 30d   : {futuro_precios[-1]:,.2f} Bs.\n"
            f"Variación esperada: {var_esp:,.2f}%"
        )
        self.text_resumen_ticker.delete("1.0", "end")
        self.text_resumen_ticker.insert("1.0", resumen)

    # ----------------------------------------------------------
    # PESTAÑA 2: COMPARACIÓN
    # ----------------------------------------------------------
    def _construir_tab_comparar(self, parent):
        f = self.factor
        frame_ctrl = ttk.Frame(parent)
        frame_ctrl.pack(fill="x", padx=int(10*f), pady=int(8*f))

        ttk.Label(frame_ctrl, text="Tickers (separados por coma, máx. 4):").pack(side="left")
        self.entry_tickers_comp = ttk.Entry(frame_ctrl, width=int(50*f))
        self.entry_tickers_comp.pack(side="left", padx=int(6*f))
        self.entry_tickers_comp.insert(0, "BVCC.CR,BVL.CR,BPV.CR,CRM.A.CR")

        ttk.Label(frame_ctrl, text="Período:").pack(side="left", padx=(int(10*f), int(4*f)))
        self.combo_periodo_comp = ttk.Combobox(frame_ctrl, values=list(PERIODOS.keys()),
                                               state="readonly", width=int(12*f))
        self.combo_periodo_comp.pack(side="left")
        self.combo_periodo_comp.set("1 año")

        btn_comp = ttk.Button(frame_ctrl, text="Comparar", command=self._comparar)
        btn_comp.pack(side="left", padx=int(6*f))

        self.frame_grafico_comp = ttk.Frame(parent)
        self.frame_grafico_comp.pack(fill="both", expand=True, padx=int(10*f), pady=int(4*f))

    def _comparar(self):
        raw = self.entry_tickers_comp.get().strip().upper()
        tickers = [t.strip() for t in raw.split(",") if t.strip()][:4]
        periodo = PERIODOS.get(self.combo_periodo_comp.get(), "1y")

        datos = {}
        for t in tickers:
            df = self._descargar(t, periodo)
            if not df.empty:
                datos[t] = df["Close"]

        if len(datos) < 1:
            messagebox.showwarning("Sin datos", "No se pudieron descargar datos.")
            return

        df_close = pd.DataFrame(datos).dropna()
        df_norm = (df_close / df_close.iloc[0]) * 100

        fig = Figure(figsize=(10, 5), dpi=100)
        ax = fig.add_subplot(111)
        for col in df_norm.columns:
            ax.plot(df_norm.index, df_norm[col], label=col, lw=1.6)
        ax.set_title("Comparación de rendimiento relativo (base 100)", fontsize=11)
        ax.set_ylabel("Índice base 100")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.25)
        fig.tight_layout()

        self._mostrar_figura(fig, self.frame_grafico_comp)

    # ----------------------------------------------------------
    # PESTAÑA 3: CORRELACIÓN
    # ----------------------------------------------------------
    def _construir_tab_corr(self, parent):
        f = self.factor
        frame_ctrl = ttk.Frame(parent)
        frame_ctrl.pack(fill="x", padx=int(10*f), pady=int(8*f))

        ttk.Label(frame_ctrl, text="Tickers (separados por coma, mín. 2):").pack(side="left")
        self.entry_tickers_corr = ttk.Entry(frame_ctrl, width=int(50*f))
        self.entry_tickers_corr.pack(side="left", padx=int(6*f))
        self.entry_tickers_corr.insert(0, "BVCC.CR,BVL.CR,BPV.CR,CRM.A.CR")

        btn_corr = ttk.Button(frame_ctrl, text="Calcular correlación",
                              command=self._calcular_correlacion)
        btn_corr.pack(side="left", padx=int(6*f))

        self.frame_grafico_corr = ttk.Frame(parent)
        self.frame_grafico_corr.pack(fill="both", expand=True, padx=int(10*f), pady=int(4*f))

    def _calcular_correlacion(self):
        raw = self.entry_tickers_corr.get().strip().upper()
        tickers = [t.strip() for t in raw.split(",") if t.strip()]

        datos = {}
        for t in tickers:
            df = self._descargar(t, "1y")
            if not df.empty:
                datos[t] = df["Close"].pct_change().dropna()

        if len(datos) < 2:
            messagebox.showwarning("Datos insuficientes",
                                   "Se necesitan al menos 2 tickers con datos.")
            return

        df_ret = pd.DataFrame(datos).dropna()
        corr = df_ret.corr()

        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn_r",
                    vmin=-1, vmax=1, square=True, linewidths=0.5, ax=ax,
                    annot_kws={"size": 8})
        ax.set_title("Matriz de correlación de retornos diarios", fontsize=11)
        fig.tight_layout()

        self._mostrar_figura(fig, self.frame_grafico_corr)

    # ----------------------------------------------------------
    # PESTAÑA 4: MOCHILA / PORTAFOLIO
    # ----------------------------------------------------------
    def _construir_tab_mochila(self, parent):
        f = self.factor
        frame_ctrl = ttk.Frame(parent)
        frame_ctrl.pack(fill="x", padx=int(10*f), pady=int(8*f))

        ttk.Label(frame_ctrl, text="Presupuesto (Bs.):").pack(side="left")
        self.entry_presupuesto = ttk.Entry(frame_ctrl, width=int(15*f))
        self.entry_presupuesto.pack(side="left", padx=int(6*f))
        self.entry_presupuesto.insert(0, "100000")

        ttk.Label(frame_ctrl, text="Período de estimación:").pack(side="left", padx=(int(10*f), int(4*f)))
        self.combo_periodo_mochila = ttk.Combobox(
            frame_ctrl, values=["1 mes", "3 meses", "6 meses", "1 año", "Todo"],
            state="readonly", width=int(12*f))
        self.combo_periodo_mochila.pack(side="left")
        self.combo_periodo_mochila.set("1 año")

        btn_opt = ttk.Button(frame_ctrl, text="Optimizar portafolio",
                             command=self._optimizar_mochila)
        btn_opt.pack(side="left", padx=int(6*f))

        self.frame_resultado_mochila = ttk.Frame(parent)
        self.frame_resultado_mochila.pack(fill="both", expand=True, padx=int(10*f), pady=int(4*f))

        self.tree_mochila = ttk.Treeview(self.frame_resultado_mochila,
                                         columns=("ticker", "sector", "precio", "sharpe"),
                                         show="headings", height=int(8*f))
        for col, txt in zip(("ticker", "sector", "precio", "sharpe"),
                            ("Ticker", "Sector", "Precio (Bs.)", "Sharpe")):
            self.tree_mochila.heading(col, text=txt)
            self.tree_mochila.column(col, width=int(120*f), anchor="center")
        self.tree_mochila.pack(fill="both", expand=True)

    def _optimizar_mochila(self):
        try:
            presupuesto = float(self.entry_presupuesto.get().replace(",", ""))
        except ValueError:
            messagebox.showerror("Error", "Ingrese un presupuesto numérico válido.")
            return

        periodo_nombre = self.combo_periodo_mochila.get()
        periodo_map = {"1 mes": "1mo", "3 meses": "3mo", "6 meses": "6mo",
                       "1 año": "1y", "Todo": "max"}
        periodo = periodo_map.get(periodo_nombre, "1y")

        registros = []
        for ticker, sector in TICKERS_BVC.items():
            df = self._descargar(ticker, periodo)
            if df.empty or len(df) < 30:
                continue
            ret = df["Close"].pct_change().dropna()
            if len(ret) < 20 or ret.std() == 0:
                continue
            registros.append({
                "ticker": ticker, "sector": sector,
                "precio": float(df["Close"].iloc[-1]),
                "sharpe": float(ret.mean() / ret.std())
            })

        if not registros:
            messagebox.showwarning("Sin datos", "No hay datos suficientes.")
            return

        df_reg = pd.DataFrame(registros)
        df_mejores = df_reg.loc[df_reg.groupby("sector")["sharpe"].idxmax()].reset_index(drop=True)

        pesos = df_mejores["precio"].tolist()
        valores = df_mejores["sharpe"].tolist()
        idx_sel, _ = self._knapsack_01(pesos, valores, presupuesto)

        # Limpiar tabla
        for row in self.tree_mochila.get_children():
            self.tree_mochila.delete(row)

        if not idx_sel:
            messagebox.showinfo("Sin selección",
                                f"Con {presupuesto:,.2f} Bs. no se puede adquirir ninguna acción.")
            return

        seleccion = df_mejores.iloc[idx_sel]
        for _, row in seleccion.iterrows():
            self.tree_mochila.insert("", "end", values=(
                row["ticker"], row["sector"],
                f"{row['precio']:,.2f}", f"{row['sharpe']:.4f}"
            ))

        costo_total = seleccion["precio"].sum()
        messagebox.showinfo(
            "Portafolio sugerido",
            f"Costo total: {costo_total:,.2f} Bs.\n"
            f"Saldo restante: {presupuesto - costo_total:,.2f} Bs.\n"
            f"Sectores: {', '.join(seleccion['sector'].unique())}"
        )

    @staticmethod
    def _knapsack_01(pesos, valores, capacidad):
        escala = 100
        pesos_int = [int(round(p * escala)) for p in pesos]
        cap_int = int(round(capacidad * escala))
        n = len(pesos)
        dp = [[0] * (cap_int + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for w in range(cap_int + 1):
                if pesos_int[i-1] <= w:
                    dp[i][w] = max(dp[i-1][w],
                                   dp[i-1][w - pesos_int[i-1]] + valores[i-1])
                else:
                    dp[i][w] = dp[i-1][w]
        sel, w = [], cap_int
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                sel.append(i-1)
                w -= pesos_int[i-1]
        sel.reverse()
        return sel, dp[n][cap_int]

    # ----------------------------------------------------------
    # UTILIDADES
    # ----------------------------------------------------------
    def _descargar(self, ticker, periodo):
        try:
            data = yf.download(ticker, period=periodo, progress=False, auto_adjust=True)
            if data.empty:
                messagebox.showwarning("Sin datos",
                                       f"No se encontraron datos para {ticker}.")
                return pd.DataFrame()
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            return data
        except Exception as e:
            messagebox.showerror("Error de descarga", f"{ticker}: {e}")
            return pd.DataFrame()

    def _mostrar_figura(self, fig, frame_destino):
        for w in frame_destino.winfo_children():
            w.destroy()
        canvas = FigureCanvasTkAgg(fig, master=frame_destino)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, frame_destino)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    app = AnalizadorBVC()
    app.mainloop()
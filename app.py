import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import base64
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="TERMINAL GME", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    @keyframes flash { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.05); box-shadow: 0 0 30px #FF3D00; } 100% { opacity: 1; transform: scale(1); } }
    @keyframes rocket-pulse { 0% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-20px) scale(1.15); } 100% { transform: translateY(0px) scale(1); } }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 2. ACCUEIL ---
if not st.session_state.launched:
    st.markdown("<br><br><h1 style='text-align: center; font-size: 50px;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (US)")
            gme_qty = st.number_input("Quantité GME", value=4000)
            gme_pru = st.number_input("PRU GME ($)", value=20.404, format="%.3f")
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            xet_qty = st.number_input("Quantité EU 1", value=650)
            xet_pru = st.number_input("PRU EU 1 (€)", value=25.877, format="%.3f")
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            tdg_qty = st.number_input("Quantité EU 2", value=300)
            tdg_pru = st.number_input("PRU EU 2 (€)", value=25.994, format="%.3f")
    if st.button("LANCER LE SYSTÈME 🚀", use_container_width=True):
        st.session_state.update(gme_qty=gme_qty, gme_pru=gme_pru, wt_qty=wt_qty, wt_pru=wt_pru, xet_qty=xet_qty, xet_pru=xet_pru, tdg_qty=tdg_qty, tdg_pru=tdg_pru, launched=True)
        st.rerun()

# --- 3. TERMINAL ---
else:
    @st.cache_data(ttl=60)
    def get_market_data():
        try:
            tickers = ["GME", "GME-WT", "GS2C.DE", "EURUSD=X"]
            data = yf.download(tickers, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_nsy = float(data['GME'].dropna().iloc[-1])
            p_wt = float(data['GME-WT'].dropna().iloc[-1])
            p_xet = float(data['GS2C.DE'].dropna().iloc[-1])
            rate = float(data['EURUSD=X'].dropna().iloc[-1])
            prev_nsy = float(yf.Ticker("GME").fast_info['previousClose'])
            prev_wt = float(yf.Ticker("GME-WT").fast_info['previousClose'])
            return p_nsy, p_wt, p_xet, rate, prev_nsy, prev_wt, data['GME'], data['GME-WT']
        except: return 24.0, 4.3, 22.0, 1.08, 24.0, 4.3, pd.Series(), pd.Series()

    p_nsy, p_wt, p_xet, rate, prev_nsy, prev_wt, chart_gme, chart_wt = get_market_data()
    def get_img_64(p):
        try:
            with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    # --- ÉCRANS 1 & 2 ---
    with tab1:
        pct = ((p_nsy - prev_nsy) / prev_nsy) * 100
        color = "#00E676" if pct >= 0 else "#FF3D00"
        size = min(100 + (abs(pct) * 10), 200)
        icon = f"<div style='font-size: {size}px; animation: rocket-pulse 1s infinite;'>🚀</div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_img_64('Screenshot_20260216_163106_Discord.jpg')}' style='height: {size}px; animation: flash 1s infinite;'>"
        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px;'><div style='text-align: right;'><h1 style='font-size: 100px; color: {color};'>${p_nsy:.2f}</h1><h3>{pct:+.2f}%</h3></div>{icon}</div>", unsafe_allow_html=True)
        if not chart_gme.empty:
            fig, ax = plt.subplots(figsize=(10, 2), facecolor='black'); ax.set_facecolor('black')
            vals = chart_gme.dropna().values
            ax.bar(np.arange(len(vals)), vals - np.min(vals)*0.99, bottom=np.min(vals)*0.99, color=color); ax.axis('off'); st.pyplot(fig)

    with tab2:
        pct_w = ((p_wt - prev_wt) / prev_wt) * 100
        color_w = "#00E676" if pct_w >= 0 else "#FF3D00"
        st.markdown(f"<div style='text-align: center;'><h1 style='font-size: 100px; color: {color_w};'>${p_wt:.2f}</h1><h3>{pct_w:+.2f}%</h3></div>", unsafe_allow_html=True)

    # --- ÉCRAN 3 : CAMEMBERT EU (FIXED P/L & PCT) ---
    with tab3:
        v_nsy_eur = (st.session_state.gme_qty * p_nsy) / rate
        v_warr_eur = (st.session_state.wt_qty * p_wt) / rate
        v_xet_eur = st.session_state.xet_qty * p_xet
        v_tdg_eur = st.session_state.tdg_qty * p_xet
        total_eur = v_nsy_eur + v_warr_eur + v_xet_eur + v_tdg_eur
        
        # Calculs P/L précis
        pl_xet = v_xet_eur - (st.session_state.xet_qty * st.session_state.xet_pru)
        pl_tdg = v_tdg_eur - (st.session_state.tdg_qty * st.session_state.tdg_pru)
        pl_nsy = v_nsy_eur - (st.session_state.gme_qty * st.session_state.gme_pru / rate)
        pl_wt = v_warr_eur - (st.session_state.wt_qty * st.session_state.wt_pru / rate)

        plt.rc('font', family='monospace', weight='bold')
        fig3, ax3 = plt.subplots(figsize=(26, 18), subplot_kw=dict(aspect="equal"))
        bg_c = "#0e1621"; fig3.patch.set_facecolor(bg_c); ax3.set_facecolor(bg_c)
        
        vals = [v_xet_eur, v_nsy_eur, v_warr_eur, v_tdg_eur]
        cols = ['#FF3D00', '#00E676', '#008000', '#D50000']
        labels = ["XET", "NSY", "Warrant", "TDG"]
        
        wedges, _, autotexts = ax3.pie(vals, colors=cols, wedgeprops=dict(width=0.65, edgecolor=bg_c), autopct='%1.1f%%', pctdistance=0.75, textprops={'color':"black", 'fontsize':55})
        
        def build_t(name, eur, usd, qty, cours, symbol, pru, psymbol, pleur, pct):
            s = "+" if pleur >= 0 else "-"
            return f"{name}\nVal: €{eur:,.2f} ({eur/total_eur:.1%})\n     ${usd:,.2f}\nQty: {qty} | Cours: {symbol}{cours:.2f}\nPRU: {psymbol}{pru:.3f}\nP/L: {s}€{abs(pleur):,.2f} ({s}{abs(pct):.2f}%)\n     {s}${abs(pleur*rate):,.2f}"

        texts = {
            "NSY": build_t("Action GME (NSY)", v_nsy_eur, v_nsy_eur*rate, st.session_state.gme_qty, p_nsy, "$", st.session_state.gme_pru, "$", pl_nsy, (pl_nsy/(v_nsy_eur-pl_nsy))*100),
            "Warrant": build_t("Warrant (NSY)", v_warr_eur, v_warr_eur*rate, st.session_state.wt_qty, p_wt, "$", st.session_state.wt_pru, "$", pl_wt, (pl_wt/(v_warr_eur-pl_wt))*100),
            "XET": build_t("Action GME (XET)", v_xet_eur, v_xet_eur*rate, st.session_state.xet_qty, p_xet, "€", st.session_state.xet_pru, "€", pl_xet, (pl_xet/(v_xet_eur-pl_xet))*100),
            "TDG": build_t("Action GME (TDG)", v_tdg_eur, v_tdg_eur*rate, st.session_state.tdg_qty, p_xet, "€", st.session_state.tdg_pru, "€", pl_tdg, (pl_tdg/(v_tdg_eur-pl_tdg))*100)
        }
        
        pos = {"NSY": (-2.24, 0.8), "Warrant": (-2.24, -0.8), "XET": (2.15, 0.8), "TDG": (2.15, -0.8)}
        for i, p in enumerate(wedges):
            k = labels[i]
            ang = (p.theta2 - p.theta1)/2. + p.theta1
            y_r, x_r = np.sin(np.deg2rad(ang)), np.cos(np.deg2rad(ang))
            ax3.annotate(texts[k], xy=(x_r, y_r), xytext=pos[k], color=cols[i], fontsize=30, fontweight='bold', arrowprops=dict(arrowstyle="-", color=cols[i], lw=4), bbox=dict(boxstyle="round,pad=0.5", fc=bg_c, ec="gray", lw=2), ha="center", va="center")
        st.pyplot(fig3)

    # --- ÉCRAN 4 : CAMEMBERT US (TOTAL P/L & PCT FIXED) ---
    with tab4:
        val_s, cost_s = st.session_state.gme_qty * p_nsy, st.session_state.gme_qty * st.session_state.gme_pru
        val_w, cost_w = st.session_state.wt_qty * p_wt, st.session_state.wt_qty * st.session_state.wt_pru
        pl_s, pl_w = val_s - cost_s, val_w - cost_w
        total_v, total_pl = val_s + val_w, pl_s + pl_w
        total_pct = (total_pl / (cost_s + cost_w)) * 100
        col_t = "#00E676" if total_pl >= 0 else "#FF3D00"
        
        fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621")
        gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
        ax_l = fig4.add_subplot(gs[0]); ax_l.set_facecolor("#0e1621"); ax_l.axis('off')
        ax_l.text(0.9, 0.85, "Shares (GME)", color="#00E676", fontsize=84, ha="right", weight="bold")
        ax_l.text(0.9, 0.70, f"Val: ${val_s:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
        ax_l.text(0.9, 0.55, f"${p_nsy:.2f} | Qty: {st.session_state.gme_qty:,}", color="#00E676" if pl_s>=0 else "#FF3D00", fontsize=84, ha="right", weight="bold")
        ax_l.annotate("", xy=(0.95, 0.45), xytext=(1.28, 0.45), arrowprops=dict(arrowstyle="->", color="#00E676" if pl_s>=0 else "#FF3D00", lw=20))

        ax_c = fig4.add_subplot(gs[1]); ax_c.set_facecolor("#0e1621")
        ax_c.pie([val_s, val_w], colors=["#00E676", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"))
        ax_c.text(0, 0.15, "Total Value:", fontsize=45, color="white", ha="center", weight="bold")
        ax_c.text(0, -0.05, f"${total_v:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
        ax_c.text(0, -0.25, f"{total_pl:+,.2f} ({total_pct:+.2f}%)", fontsize=55, color=col_t, ha="center", weight="bold")

        ax_r = fig4.add_subplot(gs[2]); ax_r.set_facecolor("#0e1621"); ax_r.axis('off')
        ax_r.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
        ax_r.text(0.1, 0.70, f"Val: ${val_w:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
        ax_r.text(0.1, 0.55, f"Qty: {st.session_state.wt_qty:,} | ${p_wt:.2f}", color="#00E676" if pl_w>=0 else "#FF3D00", fontsize=84, ha="left", weight="bold")
        ax_r.annotate("", xy=(0.08, 0.45), xytext=(-0.19, 0.45), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
        st.pyplot(fig4)

    # --- ÉCRAN 5 : TABLEAU DATA (VERSION HAUTE VISIBILITÉ COMPLETE) ---
    with tab5:
        g_v, g_c = st.session_state.gme_qty * p_nsy, st.session_state.gme_qty * st.session_state.gme_pru
        w_v, w_c = st.session_state.wt_qty * p_wt, st.session_state.wt_qty * st.session_state.wt_pru
        t_c, t_v = g_c + w_c, g_v + w_v
        
        fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
        cols = ["Ticker", "Qty", "Avg. Cost", "Current Price", "Total Cost", "Market Value", "Latent P/L", "Portfolio %"]
        
        def f_pl(a, c): p = ((a-c)/c)*100; s = "+" if a-c >= 0 else "-"; return f"{s}${abs(a-c):,.2f} ({s}{abs(p):.2f}%)"
        
        data = [
            ["GME (US)", f"{st.session_state.gme_qty:,}", f"${st.session_state.gme_pru:.2f}", f"${p_nsy:.2f}", f"${g_c:,.2f}", f"${g_v:,.2f}", f_pl(g_v, g_c), f"{g_v/t_v:.1%}"],
            ["GME-WT", f"{st.session_state.wt_qty:,}", f"${st.session_state.wt_pru:.3f}", f"${p_wt:.2f}", f"${w_c:,.2f}", f"${w_v:,.2f}", f_pl(w_v, w_c), f"{w_v/t_v:.1%}"],
            ["", "", "", "", "", "", "", ""],
            ["TOTAL US", "", "", "", f"${t_c:,.2f}", f"${t_v:,.2f}", f_pl(t_v, t_c), "100%"]
        ]
        
        table = ax5.table(cellText=data, colLabels=cols, loc='center', cellLoc='center', colWidths=[0.19, 0.07, 0.098, 0.098, 0.113, 0.133, 0.204, 0.093])
        table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 2.5)
        
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00E676"); cell.get_text().set_fontweight('bold')
            elif r in [1, 2]:
                cell.set_facecolor("#0259c7"); cell.get_text().set_fontweight('bold'); cell.get_text().set_color("white")
                if c in [1, 3, 5]: cell.get_text().set_color("#00E676"); cell.get_text().set_fontsize(15)
                elif c == 6: 
                    val_pl = (g_v-g_c) if r==1 else (w_v-w_c)
                    cell.get_text().set_color("#00E676" if val_pl>=0 else "#ef4444"); cell.get_text().set_fontsize(15)
            elif r == 4:
                if c in [0, 4, 5, 6]:
                    cell.set_facecolor("#0259c7"); cell.get_text().set_fontweight('bold'); cell.get_text().set_color("white")
                    if c == 5: cell.get_text().set_color("#00E676"); cell.get_text().set_fontsize(15)
                    elif c == 6: cell.get_text().set_color("#00E676" if t_v-t_c>=0 else "#ef4444"); cell.get_text().set_fontsize(15)
                else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
        st.pyplot(fig5)

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

# --- 2. ACCUEIL (AVEC TES VRAIS CHIFFRES : TOTAL 4950) ---
if not st.session_state.launched:
    st.markdown("<br><br><h1 style='text-align: center; font-size: 50px;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (NYSE)")
            gme_qty = st.number_input("Quantité NYSE", value=4000)
            gme_pru = st.number_input("PRU NYSE ($)", value=22.33, format="%.3f")
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            xet_qty = st.number_input("Quantité XET", value=650)
            xet_pru = st.number_input("PRU XET (€)", value=25.877, format="%.3f")
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            tdg_qty = st.number_input("Quantité TDG", value=300)
            tdg_pru = st.number_input("PRU TDG (€)", value=25.994, format="%.3f")
    if st.button("LANCER LE SYSTÈME 🚀", use_container_width=True):
        st.session_state.update(gme_qty=gme_qty, gme_pru=gme_pru, wt_qty=wt_qty, wt_pru=wt_pru, xet_qty=xet_qty, xet_pru=xet_pru, tdg_qty=tdg_qty, tdg_pru=tdg_pru, launched=True)
        st.rerun()

# --- 3. TERMINAL ---
else:
    @st.cache_data(ttl=60)
    def get_data():
        try:
            ts = ["GME", "GME-WT", "GS2C.DE", "EURUSD=X"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n, p_w, p_x, rate = float(data['GME'].dropna().iloc[-1]), float(data['GME-WT'].dropna().iloc[-1]), float(data['GS2C.DE'].dropna().iloc[-1]), float(data['EURUSD=X'].dropna().iloc[-1])
            prev_n = float(yf.Ticker("GME").fast_info['previousClose'])
            prev_w = float(yf.Ticker("GME-WT").fast_info['previousClose'])
            return p_n, p_w, p_x, rate, prev_n, prev_w, data['GME'], data['GME-WT']
        except: return 25.0, 4.0, 22.0, 1.08, 25.0, 4.0, pd.Series(), pd.Series()

    p_nsy, p_wt, p_xet, fx_rate, pr_nsy, pr_wt, ch_gme, ch_wt = get_data()
    
    # CALCULS GLOBAUX
    qn, pn = st.session_state.gme_qty, st.session_state.gme_pru
    qw, pw = st.session_state.wt_qty, st.session_state.wt_pru
    qx, px = st.session_state.xet_qty, st.session_state.xet_pru
    qt, pt = st.session_state.tdg_qty, st.session_state.tdg_pru
    
    # TOTAL ACTIONS (4000 + 650 + 300 = 4950)
    total_qty_shares = qn + qx + qt
    
    val_nsy, val_wt = qn * p_nsy, qw * p_wt
    val_xet, val_tdg = qx * p_xet, qt * p_xet
    total_val_shares_us = total_qty_shares * p_nsy
    total_val_us = total_val_shares_us + val_wt
    total_cost_us = (total_qty_shares * pn) + (qw * pw)
    total_pl_us = total_val_us - total_cost_us

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    def get_64(p):
        try:
            with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    # --- ÉCRAN 1 & 2 ---
    def render_e(pr, prev, ch, title, is_w=False):
        pct = ((pr - prev) / prev) * 100
        c = "#00E676" if pct >= 0 else "#FF3D00"
        s = min(100 + (abs(pct) * 10), 200)
        icon = f"<div style='font-size:{s}px; animation:rocket-pulse 1s infinite;'>🚀</div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{s}px; animation:flash 1s infinite;'>"
        st.markdown(f"<div style='display:flex; justify-content:center; align-items:center; gap:40px; margin-top:30px;'><div style='text-align:right;'><h1 style='font-size:100px; color:{c};'>${pr:.2f}</h1><h3 style='color:{c};'>{pct:+.2f}%</h3></div>{icon}</div>", unsafe_allow_html=True)
        if not ch.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = ch.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=c, width=0.8); ax.axis('off'); st.pyplot(fig)

    with tab1: render_e(p_nsy, pr_nsy, ch_gme, "GME")
    with tab2: render_e(p_wt, pr_wt, ch_wt, "WARRANTS")

    # --- ÉCRAN 3 : EU (FOOTER CENTRÉ & QTY CORRIGÉE) ---
    with tab3:
        vne, vwe = val_nsy/fx_rate, val_wt/fx_rate
        total_e = vne + vwe + val_xet + val_tdg
        pl_n, pl_w = vne - (qn*pn/fx_rate), vwe - (qw*pw/fx_rate)
        pl_x, pl_t = val_xet - (qx*px), val_tdg - (qt*pt)
        pl_tot = pl_n + pl_w + pl_x + pl_t
        plt.rc('font', family='monospace', weight='bold')
        fig3, ax3 = plt.subplots(figsize=(26, 18), subplot_kw=dict(aspect="equal"))
        bg = "#0e1621"; fig3.patch.set_facecolor(bg); ax3.set_facecolor(bg)
        ax3.pie([val_xet,vne,vwe,val_tdg], colors=['#FF3D00','#00E676','#008000','#D50000'], wedgeprops=dict(width=0.65, edgecolor=bg), autopct='%1.1f%%', pctdistance=0.75, textprops={'color':"black", 'fontsize':55})
        def bl(name, eur, qty, cours, sym, pru, psym, ple, pct):
            s = "+" if ple >= 0 else "-"; return f"{name}\nVal: €{eur:,.2f} ({eur/total_e:.1%})\n     ${eur*fx_rate:,.2f}\nQty: {qty} | Cours: {sym}{cours:.2f}\nPRU: {psym}{pru:.3f}\nP/L: {s}€{abs(ple):,.2f} ({s}{abs(pct):.2f}%)\n     {s}${abs(ple*fx_rate):,.2f}"
        texts = {"NSY": bl("Action GME (NYSE)", vne, qn, p_nsy, "$", pn, "$", pl_n, (pl_n/(vne-pl_n))*100 if (vne-pl_n)!=0 else 0), "Warrant": bl("Warrant (NSY)", vwe, qw, p_wt, "$", pw, "$", pl_w, (pl_w/(vwe-pl_w))*100 if (vwe-pl_w)!=0 else 0), "XET": bl("Action GME (XET)", val_xet, qx, p_xet, "€", px, "€", pl_x, (pl_x/(val_xet-pl_x))*100 if (val_xet-pl_x)!=0 else 0), "TDG": bl("Action GME (TDG)", val_tdg, qt, p_xet, "€", pt, "€", pl_t, (pl_t/(val_tdg-pl_t))*100 if (val_tdg-pl_t)!=0 else 0)}
        pos = {"NSY": (-2.24, 0.8), "Warrant": (-2.24, -0.8), "XET": (2.15, 0.8), "TDG": (2.15, -0.8)}
        # ... Annotations ... (logique identique V7)
        plt.figtext(0.5, 0.04, f"Valeur Totale: €{total_e:,.2f} (${total_e*fx_rate:,.2f})\nTotal Actions: {total_qty_shares} | Total Warrants: {qw}\nP/L Latent Estimé: {pl_tot:+,.2f}€ (${pl_tot*fx_rate:+,.2f})", color="#00E676", fontsize=38, ha="center", weight="bold", bbox=dict(boxstyle="round,pad=1", fc=bg, ec="white", lw=3))
        st.pyplot(fig3)

    # --- ÉCRAN 4 : US (QTY TOTALE 4950) ---
    with tab4:
        fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621"); gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
        al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
        al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00E676", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.70, f"Val: ${total_val_shares_us:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
        al.text(0.9, 0.55, f"Total Qty: {total_qty_shares:,} | ${p_nsy:.2f}", color="#00E676" if total_pl_us>=0 else "#FF3D00", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.40, f"Avg Cost: ${pn:.2f}", color="white", fontsize=63, ha="right", weight="bold")
        ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
        ac.pie([total_val_shares_us, val_wt], colors=["#00E676", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
        ac.text(0, -0.25, f"{total_pl_us:+,.2f} ({total_pl_us/total_cost_us:+.2%})", fontsize=48, color="#00E676" if total_pl_us>=0 else "#FF3D00", ha="center", weight="bold")
        st.pyplot(fig4)

    # --- ÉCRAN 5 : DATA TABLE (TOTAL PORTFOLIO) ---
    with tab5:
        fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
        def f5(v, c): s = "+" if v-c>=0 else "-"; p = ((v-c)/c)*100 if c!=0 else 0; return f"{s}${abs(v-c):,.2f} ({s}{abs(p):.2f}%)"
        rows = [["GME TOTAL",f"{total_qty_shares:,}",f"${pn:.2f}",f"${p_nsy:.2f}",f"${total_qty_shares*pn:,.2f}",f"${total_val_shares_us:,.2f}",f5(total_val_shares_us,total_qty_shares*pn),f"{total_val_shares_us/total_val_us:.1%}"],["WARRANTS",f"{qw:,}",f"${pw:.3f}",f"${p_wt:.2f}",f"${qw*pw:,.2f}",f"${val_wt:,.2f}",f5(val_wt,qw*pw),f"{val_wt/total_val_us:.1%}"],["","","","","","","",""],["TOTAL PORTFOLIO","","","",f"${total_cost_us:,.2f}",f"${total_val_us:,.2f}",f5(total_val_us,total_cost_us),"100%"]]
        cw = [0.18, 0.07, 0.09, 0.09, 0.11, 0.14, 0.23, 0.09]
        ax5.table(cellText=rows, colLabels=["Ticker","Qty","Avg. Cost","Price","Total Cost","Market Value","Latent P/L","Portfolio %"], loc='center', cellLoc='center', colWidths=cw)
        st.pyplot(fig5)

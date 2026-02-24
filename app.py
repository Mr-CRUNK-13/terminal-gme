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
            st.markdown("### 🇺🇸 Actions GME (NYSE)")
            gme_ny_qty = st.number_input("Quantité NYSE", value=4000)
            gme_pru = st.number_input("PRU Moyen ($)", value=22.33, format="%.3f")
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
        st.session_state.update(gme_ny_qty=gme_ny_qty, gme_pru=gme_pru, wt_qty=wt_qty, wt_pru=wt_pru, xet_qty=xet_qty, xet_pru=xet_pru, tdg_qty=tdg_qty, tdg_pru=tdg_pru, launched=True)
        st.rerun()

# --- 3. TERMINAL ---
else:
    @st.cache_data(ttl=60)
    def fetch_master_data():
        try:
            ts = ["GME", "GME-WT", "GS2C.DE", "EURUSD=X"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n, p_w, p_x, rate = float(data['GME'].dropna().iloc[-1]), float(data['GME-WT'].dropna().iloc[-1]), float(data['GS2C.DE'].dropna().iloc[-1]), float(data['EURUSD=X'].dropna().iloc[-1])
            prev_n = float(yf.Ticker("GME").fast_info['previousClose'])
            prev_w = float(yf.Ticker("GME-WT").fast_info['previousClose'])
            return p_n, p_w, p_x, rate, prev_n, prev_w, data['GME'], data['GME-WT']
        except: return 25.0, 4.3, 22.0, 1.08, 25.0, 4.3, pd.Series(), pd.Series()

    # --- TOUS LES CALCULS CENTRALISÉS (SÉCURITÉ ANTI-BUG) ---
    p_nsy, p_wt, p_xet, fx, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_master_data()
    qn, pn, qw, pw = st.session_state.gme_ny_qty, st.session_state.gme_pru, st.session_state.wt_qty, st.session_state.wt_pru
    qx, px, qt, pt = st.session_state.xet_qty, st.session_state.xet_pru, st.session_state.tdg_qty, st.session_state.tdg_pru
    
    total_q_shares = qn + qx + qt
    v_nsy_u = total_q_shares * p_nsy
    v_wt_u = qw * p_wt
    total_val_u = v_nsy_u + v_wt_u
    total_cost_u = (total_q_shares * pn) + (qw * pw)
    total_pl_u = total_val_u - total_cost_u
    total_pct_u = (total_pl_u / total_cost_u) * 100 if total_cost_u != 0 else 0

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    def get_img(p):
        try:
            with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    # --- ÉCRAN 1 & 2 : GME & WARRANTS ---
    def render_live(price, prev, chart, title):
        pct = ((price - prev) / prev) * 100
        color = "#00FF00" if pct >= 0 else "#FF3D00"
        s = min(100 + (abs(pct) * 10), 200)
        icon = f"<div style='font-size:{s}px; animation:rocket-pulse 1s infinite;'>🚀</div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_img('Screenshot_20260216_163106_Discord.jpg')}' style='height:{s}px; animation:flash 1s infinite;'>"
        st.markdown(f"<div style='display:flex; justify-content:center; align-items:center; gap:40px; margin-top:30px;'><div style='text-align:right;'><h2 style='color:#888;'>{title}</h2><h1 style='font-size:100px; color:{color}; text-shadow:0 0 20px {color}; margin:0;'>${price:.2f}</h1><h3 style='color:{color};'>{pct:+.2f}%</h3></div>{icon}</div>", unsafe_allow_html=True)
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=color, width=0.8); ax.axis('off'); st.pyplot(fig)

    with tab1: render_live(p_nsy, pr_nsy, ch_gme, "GAMESTOP CORP. (GME)")
    with tab2: render_live(p_wt, pr_wt, ch_wt, "WARRANTS (GME-WT)")

    # --- ÉCRAN 3 : EU (CENTRAGE & DONNÉES PARFAITES) ---
    with tab3:
        v_nsy_e, v_wt_e = (qn * p_nsy)/fx, (qw * p_wt)/fx
        v_x_e, v_t_e = qx*p_xet, qt*p_xet
        total_e = v_nsy_e + v_wt_e + v_x_e + v_t_e
        pl_n, pl_w, pl_x, pl_t = v_nsy_e-(qn*pn/fx), v_wt_e-(qw*pw/fx), v_x_e-(qx*px), v_t_e-(qt*pt)
        pl_tot_e = pl_n + pl_w + pl_x + pl_t

        plt.rc('font', family='monospace', weight='bold')
        fig3, ax3 = plt.subplots(figsize=(26, 18), subplot_kw=dict(aspect="equal"))
        fig3.patch.set_facecolor("#0e1621"); ax3.set_facecolor("#0e1621")
        
        # Centrage forcé
        plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
        
        wedges, _, autotexts = ax3.pie([v_x_e, v_nsy_e, v_wt_e, v_t_e], colors=['#FF3D00','#00FF00','#008000','#D50000'], wedgeprops=dict(width=0.65, edgecolor="#0e1621"), autopct='%1.1f%%', pctdistance=0.75, textprops={'color':"black", 'fontsize':55})
        
        def build_l(name, eur, qty, crs, sym, pru, psym, ple, pct):
            s = "+" if ple >= 0 else "-"
            return f"{name}\nVal: €{eur:,.2f} ({eur/total_e:.1%})\n     ${eur*fx:,.2f}\nQty: {qty} | Cours: {sym}{crs:.2f}\nPRU: {psym}{pru:.3f}\nP/L: {s}€{abs(ple):,.2f} ({s}{abs(pct):.2f}%)\n     {s}${abs(ple*fx):,.2f}"

        texts = {"NSY": build_l("Action GME (NYSE)", v_nsy_e, qn, p_nsy, "$", pn, "$", pl_n, (pl_n/(v_nsy_e-pl_n))*100 if (v_nsy_e-pl_n)!=0 else 0), 
                 "Warrant": build_l("Warrant (NSY)", v_wt_e, qw, p_wt, "$", pw, "$", pl_w, (pl_w/(v_wt_e-pl_w))*100 if (v_wt_e-pl_w)!=0 else 0), 
                 "XET": build_l("Action GME (XET)", v_x_e, qx, p_xet, "€", px, "€", pl_x, (pl_x/(v_x_e-pl_x))*100 if (v_x_e-pl_x)!=0 else 0), 
                 "TDG": build_l("Action GME (TDG)", v_t_e, qt, p_xet, "€", pt, "€", pl_t, (pl_t/(v_t_e-pl_t))*100 if (v_t_e-pl_t)!=0 else 0)}
        
        pos = {"NSY": (-2.24, 0.8), "Warrant": (-2.24, -0.8), "XET": (2.15, 0.8), "TDG": (2.15, -0.8)}
        for i, k in enumerate(["XET", "NSY", "Warrant", "TDG"]):
            p = wedges[i]; ang = (p.theta2 - p.theta1)/2. + p.theta1
            ax3.annotate(texts[k], xy=(np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))), xytext=pos[k], color=['#FF3D00','#00FF00','#008000','#D50000'][i], fontsize=30, weight='bold', arrowprops=dict(arrowstyle="-", color=['#FF3D00','#00FF00','#008000','#D50000'][i], lw=4), bbox=dict(boxstyle="round,pad=0.5", fc="#0e1621", ec="gray", lw=2), ha="center", va="center")

        footer = f"Valeur Totale: €{total_e:,.2f} (${total_e*fx:,.2f})\nTotal Actions: {total_q_shares} | Total Warrants: {qw}\nP/L Latent Estimé: {pl_tot_e:+,.2f}€ (${pl_tot_e*fx:+,.2f})"
        plt.figtext(0.5, 0.05, footer, color="#00FF00", fontsize=38, ha="center", weight="bold", bbox=dict(boxstyle="round,pad=1", fc="#0e1621", ec="white", lw=3))
        st.pyplot(fig3)

    # --- ÉCRAN 4 : US (CENTRAGE DONUT) ---
    with tab4:
        fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621"); gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        # Gauche
        al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
        al.text(0.9, 0.85, "GME Shares (US)", color="#00FF00", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.55, f"Qty: {total_q_shares:,} | ${p_nsy:.2f}", color="#00FF00" if (v_nsy_u-total_q_shares*pn)>=0 else "#FF3D00", fontsize=84, ha="right")
        al.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00FF00", lw=20))
        # Centre
        ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
        ac.pie([v_nsy_u, v_wt_u], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
        ac.text(0, -0.05, f"${total_val_u:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
        ac.text(0, -0.25, f"{total_pl_u:+,.2f} ({total_pct_u:+.2f}%)", fontsize=48, color="#00FF00" if total_pl_u>=0 else "#FF3D00", ha="center", weight="bold")
        # Droite
        ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
        ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
        ar.text(0.1, 0.55, f"Price: ${p_wt:.2f}", color="#00FF00" if (v_wt_u-qw*pw)>=0 else "#FF3D00", fontsize=84, ha="left")
        ar.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
        st.pyplot(fig4)

    # --- ÉCRAN 5 : DATA (TABLE BLEUE & BLANCHE) ---
    with tab5:
        fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
        def f5(v, c): s = "+" if v-c>=0 else "-"; p = ((v-c)/c)*100 if c!=0 else 0; return f"{s}${abs(v-c):,.2f} ({s}{abs(p):.2f}%)"
        rows = [["GME TOTAL",f"{total_q_shares:,}",f"${pn:.2f}",f"${p_nsy:.2f}",f"${total_q_shares*pn:,.2f}",f"${v_nsy_u:,.2f}",f5(v_nsy_u,total_q_shares*pn),f"{v_nsy_u/total_val_u:.1%}"],["WARRANTS",f"{qw:,}",f"${pw:.3f}",f"${p_wt:.2f}",f"${qw*pw:,.2f}",f"${v_wt_u:,.2f}",f5(v_wt_u,qw*pw),f"{v_wt_u/total_val_u:.1%}"],["","","","","","","",""],["TOTAL PORTFOLIO","","","",f"${total_cost_u:,.2f}",f"${total_val_u:,.2f}",f5(total_val_u,total_cost_u),"100%"]]
        cw = [0.18, 0.07, 0.09, 0.09, 0.11, 0.14, 0.23, 0.09]
        table = ax5.table(cellText=rows, colLabels=["Ticker","Qty","Avg. Cost","Price","Total Cost","Market Value","Latent P/L","Portfolio %"], loc='center', cellLoc='center', colWidths=cw)
        table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 2.5)
        for (r, c), cell in table.get_celld().items():
            if r == 0: cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00FF00"); cell.get_text().set_fontweight('bold')
            elif r in [1, 2, 4]:
                if r == 4 and c not in [0, 4, 5, 6]: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a"); continue
                cell.set_facecolor("#0259c7"); cell.get_text().set_color("white"); cell.get_text().set_fontweight('bold')
                if c in [1, 3, 5]: cell.get_text().set_color("#00FF00"); cell.get_text().set_fontsize(14)
                elif c == 6: cell.get_text().set_color("#00FF00" if (total_val_u-total_cost_u if r==4 else v_nsy_u-total_q_shares*pn if r==1 else v_wt_u-qw*pw)>=0 else "#ef4444"); cell.get_text().set_fontsize(14)
            else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
        st.pyplot(fig5)

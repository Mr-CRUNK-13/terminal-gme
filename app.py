import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import base64
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="TERMINAL GME", 
    page_icon="Screenshot_20260216_163106_Discord.jpg", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Style CSS pour le fond noir, les animations et la suppression des menus Streamlit
st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    
    @keyframes flash {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.05); box-shadow: 0 0 30px #FF3D00; }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes rocket-pulse {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-20px) scale(1.15); } 
        100% { transform: translateY(0px) scale(1); }
    }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 2. ACCUEIL (CONFIGURATION) ---
if not st.session_state.launched:
    st.markdown("<br><br><h1 style='text-align: center; font-size: 50px;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (US)")
            gme_qty = st.number_input("Quantité GME", value=4950)
            gme_pru = st.number_input("PRU GME ($)", value=22.33, format="%.3f")
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
            
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            xet_qty = st.number_input("Quantité EU 1 (XET)", value=650)
            xet_pru = st.number_input("PRU EU 1 (€)", value=25.877, format="%.3f")
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            tdg_qty = st.number_input("Quantité EU 2 (TDG)", value=300)
            tdg_pru = st.number_input("PRU EU 2 (€)", value=25.994, format="%.3f")

    if st.button("LANCER LE SYSTÈME 🚀", use_container_width=True):
        st.session_state.update(
            gme_qty=gme_qty, gme_pru=gme_pru, 
            wt_qty=wt_qty, wt_pru=wt_pru, 
            xet_qty=xet_qty, xet_pru=xet_pru, 
            tdg_qty=tdg_qty, tdg_pru=tdg_pru, 
            launched=True
        )
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
            
            # Récupération des clôtures précédentes pour le calcul du % du jour
            t_gme = yf.Ticker("GME")
            prev_nsy = float(t_gme.fast_info['previousClose'])
            t_wt = yf.Ticker("GME-WT")
            prev_wt = float(t_wt.fast_info['previousClose'])
            
            return p_nsy, p_wt, p_xet, rate, prev_nsy, prev_wt, data['GME'], data['GME-WT']
        except:
            return 25.80, 4.23, 21.96, 1.08, 25.0, 4.0, pd.Series(), pd.Series()

    p_nsy, p_wt, p_xet, rate, prev_nsy, prev_wt, chart_gme, chart_wt = get_market_data()

    def get_img_64(p):
        try:
            with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    # --- ÉCRAN 1 : GME ---
    with tab1:
        pct = ((p_nsy - prev_nsy) / prev_nsy) * 100
        color = "#00E676" if pct >= 0 else "#FF3D00"
        size = min(100 + (abs(pct) * 10), 200)
        icon = f"<div style='font-size: {size}px; animation: rocket-pulse 1s ease-in-out infinite;'>🚀</div>" if pct >= 0 else f"<img src='data:image/jpeg;base64,{get_img_64('Screenshot_20260216_163106_Discord.jpg')}' style='height: {size}px; animation: flash 1s infinite;'>"
        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px;'><div style='text-align: right;'><h1 style='font-size: 100px; color: {color}; text-shadow: 0 0 20px {color}; margin: 0;'>${p_nsy:.2f}</h1><h3>{pct:+.2f}%</h3></div>{icon}</div>", unsafe_allow_html=True)
        if not chart_gme.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            vals = chart_gme.dropna().values
            ax.bar(np.arange(len(vals)), vals - np.min(vals)*0.99, bottom=np.min(vals)*0.99, color=color, width=0.8); ax.axis('off'); st.pyplot(fig)

    # --- ÉCRAN 2 : WARRANTS ---
    with tab2:
        pct_w = ((p_wt - prev_wt) / prev_wt) * 100
        col_w = "#00E676" if pct_w >= 0 else "#FF3D00"
        size_w = min(100 + (abs(pct_w) * 10), 200)
        icon_w = f"<div style='font-size: {size_w}px; animation: rocket-pulse 1s ease-in-out infinite;'>🚀</div>" if pct_w >= 0 else f"<img src='data:image/jpeg;base64,{get_img_64('Screenshot_20260216_163106_Discord.jpg')}' style='height: {size_w}px; animation: flash 1s infinite;'>"
        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px;'><div style='text-align: right;'><h1 style='font-size: 100px; color: {col_w}; text-shadow: 0 0 20px {col_w}; margin: 0;'>${p_wt:.2f}</h1><h3>{pct_w:+.2f}%</h3></div>{icon_w}</div>", unsafe_allow_html=True)
        if not chart_wt.empty:
            fig2, ax2 = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax2.set_facecolor('black')
            vals2 = chart_wt.dropna().values
            ax2.bar(np.arange(len(vals2)), vals2 - np.min(vals2)*0.99, bottom=np.min(vals2)*0.99, color=col_w, width=0.8); ax2.axis('off'); st.pyplot(fig2)

    # --- ÉCRAN 3 : CAMEMBERT EU (VERSION ULTIME AVEC FOOTER) ---
    with tab3:
        # Données dynamiques
        q_x, q_t, q_n, q_w = st.session_state.xet_qty, st.session_state.tdg_qty, st.session_state.gme_qty, st.session_state.wt_qty
        pru_x, pru_t, pru_n, pru_w = st.session_state.xet_pru, st.session_state.tdg_pru, st.session_state.gme_pru, st.session_state.wt_pru
        
        v_x_e = q_x * p_xet
        v_t_e = q_t * p_xet
        v_n_e = (q_n * p_nsy) / rate
        v_w_e = (q_w * p_wt) / rate
        tot_e = v_x_e + v_t_e + v_n_e + v_w_e
        
        pl_x = v_x_e - (q_x * pru_x)
        pl_t = v_t_e - (q_t * pru_t)
        pl_n = v_n_e - (q_n * pru_n / rate)
        pl_w = v_w_e - (q_w * pru_w / rate)
        pl_tot = pl_x + pl_t + pl_n + pl_w

        plt.rc('font', family='monospace', weight='bold')
        fig3, ax3 = plt.subplots(figsize=(26, 18), subplot_kw=dict(aspect="equal"))
        bg = "#0e1621"; fig3.patch.set_facecolor(bg); ax3.set_facecolor(bg)
        
        vals_pie = [v_x_e, v_n_e, v_w_e, v_t_e]
        cols_pie = ['#FF3D00', '#00E676', '#008000', '#D50000']
        labels_pie = ["XET", "NSY", "Warrant", "TDG"]
        
        wedges, _, autotexts = ax3.pie(vals_pie, startangle=0, colors=cols_pie, wedgeprops=dict(width=0.65, edgecolor=bg), autopct='%1.1f%%', pctdistance=0.75, textprops={'color':"black", 'fontsize':55})
        
        def build_label(name, eur, qty, cours, symbol, pru, psymbol, pleur, pct):
            s = "+" if pleur >= 0 else "-"
            return f"{name}\nVal: €{eur:,.2f} ({eur/tot_e:.1%})\n     ${eur*rate:,.2f}\nQty: {qty} | Cours: {symbol}{cours:.2f}\nPRU: {psymbol}{pru:.3f}\nP/L: {s}€{abs(pleur):,.2f} ({s}{abs(pct):.2f}%)\n     {s}${abs(pleur*rate):,.2f}"

        texts = {
            "NSY": build_label("Action GME Class A (NSY)", v_n_e, q_n, p_nsy, "$", pru_n, "$", pl_n, (pl_n/(v_n_e-pl_n))*100 if (v_n_e-pl_n)!=0 else 0),
            "Warrant": build_label("Warrant GameStop (NSY)", v_w_e, q_w, p_wt, "$", pru_w, "$", pl_w, (pl_w/(v_w_e-pl_w))*100 if (v_w_e-pl_w)!=0 else 0),
            "XET": build_label("Action GME Class A (XET)", v_x_e, q_x, p_xet, "€", pru_x, "€", pl_x, (pl_x/(v_x_e-pl_x))*100 if (v_x_e-pl_x)!=0 else 0),
            "TDG": build_label("Action GME Class A (TDG)", v_t_e, q_t, p_xet, "€", pru_t, "€", pl_t, (pl_t/(v_t_e-pl_t))*100 if (v_t_e-pl_t)!=0 else 0)
        }
        
        pos_dict = {"NSY": (-2.24, 0.8), "Warrant": (-2.24, -0.8), "XET": (2.15, 0.8), "TDG": (2.15, -0.8)}
        for i, p in enumerate(wedges):
            k = labels_pie[i]; ang = (p.theta2 - p.theta1)/2. + p.theta1
            y_r, x_r = np.sin(np.deg2rad(ang)), np.cos(np.deg2rad(ang))
            ax3.annotate(texts[k], xy=(x_r, y_r), xytext=pos_dict[k], color=cols_pie[i], fontsize=30, fontweight='bold', arrowprops=dict(arrowstyle="-", color=cols_pie[i], lw=4), bbox=dict(boxstyle="round,pad=0.5", fc=bg, ec="gray", lw=2), ha="center", va="center")

        # --- FOOTER ---
        plt.figtext(0.42, 0.08, "Valeur Totale: ", color="white", fontsize=38, ha="right", weight="bold")
        plt.figtext(0.42, 0.08, f"€{tot_e:,.2f} (${tot_e*rate:,.2f})", color="#00E676", fontsize=38, ha="left", weight="bold")
        plt.figtext(0.42, 0.04, "Total Actions: ", color="white", fontsize=38, ha="right", weight="bold")
        plt.figtext(0.42, 0.04, f"{q_x+q_t+q_n} | Total Warrants: {q_w}", color="#00E676", fontsize=38, ha="left", weight="bold")
        plt.figtext(0.44, 0.00, "P/L Latent Estimé: ", color="white", fontsize=38, ha="right", weight="bold")
        plt.figtext(0.44, 0.00, f"{pl_tot:+,.2f}€ (${pl_tot*rate:+,.2f})", color="#00E676", fontsize=38, ha="left", weight="bold")
        fig3.add_artist(plt.Rectangle((0.18, -0.04), 0.64, 0.17, transform=fig3.transFigure, facecolor=bg, edgecolor="white", lw=3, zorder=-1))
        st.pyplot(fig3)

    # --- ÉCRAN 4 : US ALLOCATION (VERSION 3 PANNEAUX EXACTE) ---
    with tab4:
        v_s, c_s = q_n * p_nsy, q_n * pru_n
        v_w, c_w = q_w * p_wt, q_w * pru_w
        pl_s, pl_w = v_s - c_s, v_w - c_w
        t_v_us, t_pl_us = v_s + v_w, pl_s + pl_w
        t_pct_us = (t_pl_us / (c_s + c_w)) * 100
        
        fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621")
        gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
        
        # Panneau Gauche (Shares)
        al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
        al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00E676", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.70, f"Val: ${v_s:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
        al.text(0.9, 0.55, f"${p_nsy:.2f} | Qty: {q_n:,}", color="#00E676" if pl_s>=0 else "#FF3D00", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.40, f"Avg Cost: ${pru_n:.2f}", color="white", fontsize=63, ha="right", weight="bold")
        al.text(0.9, 0.25, f"P/L: {pl_s:+,.2f} ({pl_s/c_s:+.2%})", color="#00E676" if pl_s>=0 else "#FF3D00", fontsize=84, ha="right", weight="bold")
        al.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00E676" if pl_s>=0 else "#FF3D00", lw=20))

        # Panneau Centre (Donut)
        ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
        ac.pie([v_s, v_w], colors=["#00E676", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
        ac.text(-1.125, 0, f"{(v_s/t_v_us)*100:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
        ac.text(1.125, 0, f"{(v_w/t_v_us)*100:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
        ac.text(0, 0.15, "Total Value:", fontsize=45, color="white", ha="center", weight="bold")
        ac.text(0, -0.05, f"${t_v_us:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
        ac.text(0, -0.25, f"{t_pl_us:+,.2f} ({t_pct_us:+.2f}%)", fontsize=55, color="#00E676" if t_pl_us>=0 else "#FF3D00", ha="center", weight="bold")

        # Panneau Droit (Warrants)
        ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
        ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
        ar.text(0.1, 0.70, f"Val: ${v_w:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
        ar.text(0.1, 0.55, f"Qty: {q_w:,} | Price: ${p_wt:.2f}", color="#00E676" if pl_w>=0 else "#FF3D00", fontsize=84, ha="left", weight="bold")
        ar.text(0.1, 0.40, f"Avg Cost: ${pru_w:.3f}", color="white", fontsize=63, ha="left", weight="bold")
        ar.text(0.1, 0.25, f"P/L: {pl_w:+,.2f} ({pl_w/c_w:+.2%})", color="#00E676" if pl_w>=0 else "#FF3D00", fontsize=84, ha="left", weight="bold")
        ar.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
        
        st.pyplot(fig4)

    # --- ÉCRAN 5 : DATA TABLE (VERSION HAUTE VISIBILITÉ SANS DÉBORDEMENT) ---
    with tab5:
        fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
        cols = ["Ticker", "Qty", "Avg. Cost", "Current Price", "Total Cost", "Market Value", "Latent P/L", "Portfolio %"]
        
        def f_data(val, cost): 
            p = ((val-cost)/cost)*100 if cost!=0 else 0
            s = "+" if val-cost>=0 else "-"
            return f"{s}${abs(val-cost):,.2f} ({s}{abs(p):.2f}%)"
        
        rows = [
            ["GME (US)", f"{q_n:,}", f"${pru_n:.2f}", f"${p_nsy:.2f}", f"${c_s:,.2f}", f"${v_s:,.2f}", f_data(v_s, c_s), f"{v_s/t_v_us:.1%}"],
            ["GME-WT", f"{q_w:,}", f"${pru_w:.3f}", f"${p_wt:.2f}", f"${c_w:,.2f}", f"${v_w:,.2f}", f_data(v_w, c_w), f"{v_w/t_v_us:.1%}"],
            ["", "", "", "", "", "", "", ""],
            ["TOTAL US", "", "", "", f"${c_s+c_w:,.2f}", f"${t_v_us:,.2f}", f_data(t_v_us, c_s+c_w), "100%"]
        ]
        
        # Largeurs de colonnes identiques au code Colab
        cw = [0.19, 0.07, 0.098, 0.098, 0.113, 0.133, 0.204, 0.093]
        table = ax5.table(cellText=rows, colLabels=cols, loc='center', cellLoc='center', colWidths=cw)
        table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 2.5)
        
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00E676"); cell.get_text().set_fontweight('bold')
            elif r in [1, 2]:
                cell.set_facecolor("#0259c7"); cell.get_text().set_color("white"); cell.get_text().set_fontweight('bold')
                if c in [1, 3, 5]: cell.get_text().set_color("#00E676"); cell.get_text().set_fontsize(15)
                elif c == 6: 
                    pl_val = (v_s-c_s) if r==1 else (v_w-c_w)
                    cell.get_text().set_color("#00E676" if pl_val>=0 else "#ef4444"); cell.get_text().set_fontsize(15)
            elif r == 4:
                if c in [0, 4, 5, 6]:
                    cell.set_facecolor("#0259c7"); cell.get_text().set_fontweight('bold')
                    if c == 5: cell.get_text().set_color("#00E676"); cell.get_text().set_fontsize(15)
                    elif c == 6: cell.get_text().set_color("#00E676" if t_pl_us>=0 else "#ef4444"); cell.get_text().set_fontsize(15)
                    else: cell.get_text().set_color("white")
                else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
        st.pyplot(fig5)

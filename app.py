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

st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    .btn-launch {
        background-color: #00FF00; color: #050505; font-size: 24px; 
        font-weight: bold; border-radius: 10px; padding: 15px; 
        width: 100%; text-align: center; display: block;
        box-shadow: 0px 0px 20px #00FF00; margin-top: 30px;
    }
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

# --- 2. ACCUEIL (CONFIGURATION CENTRALISÉE) ---
if not st.session_state.launched:
    st.markdown("<br><br><h1 style='text-align: center; font-size: 50px;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE"):
        st.text_input("Surnom pour le Leaderboard", value="Mr-CRUNK-13")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (US)")
            gme_qty = st.number_input("Quantité GME", value=4000, step=1)
            gme_pru = st.number_input("PRU GME ($)", value=20.404, format="%.3f")
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013, step=1)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            xet_qty = st.number_input("Quantité EU 1", value=650, step=1)
            xet_pru = st.number_input("PRU EU 1 (€)", value=25.877, format="%.3f")
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            tdg_qty = st.number_input("Quantité EU 2", value=300, step=1)
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
    def get_all_market_data():
        try:
            tickers = ["GME", "GME-WT", "GS2C.DE", "EURUSD=X"]
            # Récupération avec prepost=True pour les horaires étendues
            data = yf.download(tickers, period="1d", interval="2m", prepost=True, progress=False)['Close']
            
            def last_v(sym, fallback):
                if sym in data.columns:
                    val = data[sym].dropna()
                    return float(val.iloc[-1]) if not val.empty else fallback
                return fallback

            # Récupération des clôtures précédentes pour les %
            prev_closes = {s: yf.Ticker(s).fast_info['previousClose'] for s in tickers}
            
            p_gme = last_v("GME", 25.80)
            p_wt = last_v("GME-WT", 4.23)
            p_xet = last_v("GS2C.DE", 21.96)
            p_fx = last_v("EURUSD=X", 1.08)
            
            return {
                "prices": {"GME": p_gme, "WT": p_wt, "XET": p_xet, "FX": p_fx},
                "prev": prev_closes,
                "charts": {"GME": data["GME"] if "GME" in data.columns else pd.Series(),
                           "WT": data["GME-WT"] if "GME-WT" in data.columns else pd.Series()}
            }
        except:
            return None

    def get_image_base64(path):
        try:
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
        except: return ""

    m_data = get_all_market_data()
    if not m_data: st.error("Erreur de flux boursier"); st.stop()

    prices = m_data["prices"]
    charts = m_data["charts"]
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    # --- ÉCRAN 1 & 2 : LOGIQUE DYNAMIQUE ---
    def render_live_tab(price, prev, chart, title, is_warrant=False):
        pct = ((price - prev) / prev) * 100
        color = "#00E676" if pct >= 0 else "#FF3D00"
        sign = "+" if pct >= 0 else ""
        abs_pct = abs(pct)
        size = min(100 + (abs_pct * 10), 200)
        speed = max(1.5 - (abs_pct * 0.1), 0.4)
        
        if pct >= 0:
            icon_html = f"<div style='font-size: {size}px; animation: rocket-pulse {speed}s ease-in-out infinite; line-height: 1; text-shadow: 0 0 30px #00FF00;'>🚀</div>"
        else:
            img_b64 = get_image_base64("Screenshot_20260216_163106_Discord.jpg")
            icon_html = f"<img src='data:image/jpeg;base64,{img_b64}' style='height: {size}px; border-radius: 15px; box-shadow: 0 0 20px {color}; animation: flash {speed}s infinite;'>" if img_b64 else "⚠️"

        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px;'><div style='text-align: right;'><h2 style='color: #888; font-family: monospace; margin: 0;'>{title}</h2><h1 style='font-size: 100px; color: {color}; text-shadow: 0 0 20px {color}; margin: 0;'>${price:.2f}</h1><h3 style='color: {color}; margin: 0;'>{sign}{pct:.2f}%</h3></div><div>{icon_html}</div></div>", unsafe_allow_html=True)
        
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#050505')
            ax.set_facecolor('#050505')
            vals = chart.dropna().values
            min_y = np.min(vals) * 0.99
            ax.bar(np.arange(len(vals)), vals - min_y, bottom=min_y, color=color, width=0.8)
            ax.axis('off')
            st.pyplot(fig)

    with tab1: render_live_tab(prices["GME"], m_data["prev"]["GME"], charts["GME"], "GAMESTOP CORP. (GME)")
    with tab2: render_live_tab(prices["WT"], m_data["prev"]["GME-WT"], charts["WT"], "WARRANTS (GME-WT)", True)

    # --- ÉCRAN 3 : CAMEMBERT EU (Ton Code Ultime) ---
    with tab3:
        # Calculs branchés sur tes inputs
        v_xet_eur = st.session_state.xet_qty * prices["XET"]
        v_tdg_eur = st.session_state.tdg_qty * prices["XET"]
        v_nsy_eur = (st.session_state.gme_qty * prices["GME"]) / prices["FX"]
        v_warr_eur = (st.session_state.wt_qty * prices["WT"]) / prices["FX"]
        total_eur = v_xet_eur + v_tdg_eur + v_nsy_eur + v_warr_eur
        
        fig3, ax3 = plt.subplots(figsize=(20, 12), facecolor="#0e1621")
        ax3.set_facecolor("#0e1621")
        vals_pie = [v_xet_eur, v_nsy_eur, v_warr_eur, v_tdg_eur]
        cols_pie = ['#FF3D00', '#00E676', '#008000', '#D50000']
        ax3.pie(vals_pie, colors=cols_pie, startangle=0, wedgeprops=dict(width=0.6, edgecolor="#0e1621"), autopct='%1.1f%%', textprops={'color':"white", 'weight':'bold', 'fontsize':20})
        st.pyplot(fig3)

    # --- ÉCRAN 4 : CAMEMBERT US (Ton Code Ultime) ---
    with tab4:
        v_s = st.session_state.gme_qty * prices["GME"]
        v_w = st.session_state.wt_qty * prices["WT"]
        total_us = v_s + v_w
        
        fig4 = plt.figure(figsize=(22, 10), facecolor="#0e1621")
        gs4 = GridSpec(1, 3, width_ratios=[1, 1.5, 1])
        ax_c = fig4.add_subplot(gs4[1])
        ax_c.pie([v_s, v_w], colors=["#00E676", "#006400"], radius=1.2, wedgeprops=dict(width=0.4, edgecolor="#0e1621"))
        plt.suptitle("US ALLOCATION", color="white", fontsize=30, weight="bold")
        st.pyplot(fig4)

    # --- ÉCRAN 5 : TABLEAU DATA (Ton Code Ultime) ---
    with tab5:
        st.markdown("<h2 style='text-align: center;'>PORTFOLIO SUMMARY</h2>", unsafe_allow_html=True)
        # On recrée ton tableau avec les données live
        gme_val = st.session_state.gme_qty * prices["GME"]
        wt_val = st.session_state.wt_qty * prices["WT"]
        
        df_data = {
            "Ticker": ["GME (US)", "WARRANT"],
            "Qty": [st.session_state.gme_qty, st.session_state.wt_qty],
            "Price": [f"${prices['GME']:.2f}", f"${prices['WT']:.2f}"],
            "Market Value": [f"${gme_val:,.2f}", f"${wt_val:,.2f}"]
        }
        st.table(pd.DataFrame(df_data))

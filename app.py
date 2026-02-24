import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="TERMINAL GME", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

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

# --- 2. ACCUEIL ---
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
        st.session_state.update(gme_qty=gme_qty, gme_pru=gme_pru, wt_qty=wt_qty, wt_pru=wt_pru, 
                                xet_qty=xet_qty, xet_pru=xet_pru, tdg_qty=tdg_qty, tdg_pru=tdg_pru, launched=True)
        st.rerun()

# --- 3. TERMINAL ---
else:
    # NOUVEAU MOTEUR UNIVERSEL : Il accepte n'importe quel symbole boursier !
    @st.cache_data(ttl=60)
    def get_live_data(ticker_symbol):
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="1d", interval="2m", prepost=True)
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(ticker.fast_info['previousClose'])
            else:
                current_price = float(ticker.fast_info['lastPrice'])
                prev_close = float(ticker.fast_info['previousClose'])
                
            change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
            return current_price, change_pct, hist['Close']
        except Exception:
            # En cas d'erreur de Yahoo Finance sur le symbole
            return 0.0, 0.0, pd.Series()
            
    def get_image_base64(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return ""
            
    # --- RÉCUPÉRATION DES DONNÉES DES 2 ACTIFS ---
    gme_price, gme_pct, gme_chart = get_live_data("GME")
    # Note : Le symbole des warrants varie souvent sur YF (GME-WT, GMEW, etc.). On tente GME-WT.
    wt_price, wt_pct, wt_chart = get_live_data("GME-WT") 
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])
    
    # ==========================================
    # ONGLETS 1 : GME (L'Original)
    # ==========================================
    with tab1:
        gme_color = "#00FF00" if gme_pct >= 0 else "#FF3D00"
        gme_sign = "+" if gme_pct >= 0 else ""
        gme_abs_pct = abs(gme_pct)
        gme_icon_size = min(100 + (gme_abs_pct * 10), 200)
        gme_anim_speed = max(1.5 - (gme_abs_pct * 0.1), 0.4)
        
        if gme_pct >= 0:
            icon_html = f"<div style='font-size: {gme_icon_size}px; animation: rocket-pulse {gme_anim_speed}s ease-in-out infinite; line-height: 1; text-shadow: 0 0 30px #00FF00;'>🚀</div>"
        else:
            img_b64 = get_image_base64("Screenshot_20260216_163106_Discord.jpg")
            if img_b64:
                icon_html = f"<img src='data:image/jpeg;base64,{img_b64}' style='height: {gme_icon_size}px; border-radius: 15px; box-shadow: 0 0 20px {gme_color}; animation: flash {gme_anim_speed}s infinite;'>"
            else:
                icon_html = f"<div style='font-size: 80px; color: {gme_color};'>⚠️ Image INTROUVABLE</div>"

        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px; margin-bottom: 20px;'><div style='text-align: right;'><h2 style='color: #888; font-family: monospace; margin: 0;'>GAMESTOP CORP. (GME)</h2><h1 style='font-size: 110px; color: {gme_color}; text-shadow: 0 0 20px {gme_color}; margin: 0; line-height: 1;'>${gme_price:.2f}</h1><h3 style='color: {gme_color}; margin: 0;'>{gme_sign}{gme_pct:.2f}%</h3></div><div>{icon_html}</div></div>", unsafe_allow_html=True)
        
        if not gme_chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#050505')
            ax.set_facecolor('#050505')
            prices = gme_chart.values
            x_pos = np.arange(len(prices))
            min_y = np.min(prices) * 0.99
            ax.bar(x_pos, prices - min_y, bottom=min_y, color=gme_color, width=0.8, edgecolor='none')
            ax.axis('off')
            ax.set_xlim(-1, len(prices))
            ax.set_ylim(min_y, np.max(prices) * 1.01)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            st.pyplot(fig)

    # ==========================================
    # ONGLETS 2 : WARRANTS (Le Jumeau)
    # ==========================================
    with tab2:
        # Sécurité : Si Yahoo Finance ne trouve pas le symbole exact du Warrant, on évite le crash
        if wt_price == 0.0:
            st.warning("⚠️ Connexion au marché des Warrants en cours... (Symbole YF à vérifier)")
            wt_price = st.session_state.wt_pru # Affiche le PRU en attendant
            
        wt_color = "#00FF00" if wt_pct >= 0 else "#FF3D00"
        wt_sign = "+" if wt_pct >= 0 else ""
        wt_abs_pct = abs(wt_pct)
        wt_icon_size = min(100 + (wt_abs_pct * 10), 200)
        wt_anim_speed = max(1.5 - (wt_abs_pct * 0.1), 0.4)
        
        if wt_pct >= 0:
            icon_wt_html = f"<div style='font-size: {wt_icon_size}px; animation: rocket-pulse {wt_anim_speed}s ease-in-out infinite; line-height: 1; text-shadow: 0 0 30px #00FF00;'>🚀</div>"
        else:
            img_b64 = get_image_base64("Screenshot_20260216_163106_Discord.jpg")
            if img_b64:
                icon_wt_html = f"<img src='data:image/jpeg;base64,{img_b64}' style='height: {wt_icon_size}px; border-radius: 15px; box-shadow: 0 0 20px {wt_color}; animation: flash {wt_anim_speed}s infinite;'>"
            else:
                icon_wt_html = f"<div style='font-size: 80px; color: {wt_color};'>⚠️ Image INTROUVABLE</div>"

        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px; margin-bottom: 20px;'><div style='text-align: right;'><h2 style='color: #888; font-family: monospace; margin: 0;'>WARRANTS (GME-WT)</h2><h1 style='font-size: 110px; color: {wt_color}; text-shadow: 0 0 20px {wt_color}; margin: 0; line-height: 1;'>${wt_price:.3f}</h1><h3 style='color: {wt_color}; margin: 0;'>{wt_sign}{wt_pct:.2f}%</h3></div><div>{icon_wt_html}</div></div>", unsafe_allow_html=True)
        
        if not wt_chart.empty:
            fig_wt, ax_wt = plt.subplots(figsize=(10, 2.5), facecolor='#050505')
            ax_wt.set_facecolor('#050505')
            prices_wt = wt_chart.values
            x_pos_wt = np.arange(len(prices_wt))
            min_y_wt = np.min(prices_wt) * 0.99
            ax_wt.bar(x_pos_wt, prices_wt - min_y_wt, bottom=min_y_wt, color=wt_color, width=0.8, edgecolor='none')
            ax_wt.axis('off')
            ax_wt.set_xlim(-1, len(prices_wt))
            ax_wt.set_ylim(min_y_wt, np.max(prices_wt) * 1.01)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            st.pyplot(fig_wt)

    with tab3:
        st.markdown("<h2 style='text-align: center;'>Écran 3 : Camembert EU</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center;'>Écran 4 : Camembert US</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center;'>Écran 5 : Tableau Détaillé</h2>", unsafe_allow_html=True)

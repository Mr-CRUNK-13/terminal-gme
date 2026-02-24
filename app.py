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
    
    /* Animation Image WEN Moon (Clignote en rouge) */
    @keyframes flash {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(1.05); box-shadow: 0 0 30px #FF3D00; }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* NOUVELLE Animation Fusée (Pulsation de décollage) */
    @keyframes rocket-pulse {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-20px) scale(1.15); } /* Monte et grossit fortement */
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
    @st.cache_data(ttl=60)
    def get_live_data():
        try:
            ticker = yf.Ticker("GME")
            hist = ticker.history(period="1d", interval="2m", prepost=True)
            if not hist.empty:
                current_gme_price = float(hist['Close'].iloc[-1])
                prev_close = float(ticker.fast_info['previousClose'])
            else:
                current_gme_price = float(ticker.fast_info['lastPrice'])
                prev_close = float(ticker.fast_info['previousClose'])
                
            gme_change_pct = ((current_gme_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
            return current_gme_price, gme_change_pct, hist['Close']
        except Exception:
            return 25.00, 0.0, pd.Series()
            
    def get_image_base64(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return ""
    
    current_gme_price, gme_change_pct, chart_data = get_live_data()
    ticker_color = "#00FF00" if gme_change_pct >= 0 else "#FF3D00"
    sign = "+" if gme_change_pct >= 0 else ""
    
    # MOTEUR DYNAMIQUE SIMPLIFIÉ ET ROBUSTE
    abs_pct = abs(gme_change_pct)
    # Taille de base 100px, augmente avec la volatilité
    icon_size = min(100 + (abs_pct * 10), 200)
    # Vitesse : plus le % est haut, plus anim_speed est petit (donc rapide)
    anim_speed = max(1.5 - (abs_pct * 0.1), 0.4)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])
    
    with tab1:
        # Affichage propre sur une seule ligne de code
        if gme_change_pct >= 0:
            # Une seule fusée qui pulse puissamment
            icon_html = f"<div style='font-size: {icon_size}px; animation: rocket-pulse {anim_speed}s ease-in-out infinite; line-height: 1; text-shadow: 0 0 30px #00FF00;'>🚀</div>"
        else:
            img_b64 = get_image_base64("Screenshot_20260216_163106_Discord.jpg")
            if img_b64:
                icon_html = f"<img src='data:image/jpeg;base64,{img_b64}' style='height: {icon_size}px; border-radius: 15px; box-shadow: 0 0 20px {ticker_color}; animation: flash {anim_speed}s infinite;'>"
            else:
                icon_html = f"<div style='font-size: 80px; color: {ticker_color};'>⚠️ Image INTROUVABLE</div>"

        st.markdown(f"<div style='display: flex; justify-content: center; align-items: center; gap: 40px; margin-top: 30px; margin-bottom: 20px;'><div style='text-align: right;'><h2 style='color: #888; font-family: monospace; margin: 0;'>GAMESTOP CORP. (GME)</h2><h1 style='font-size: 110px; color: {ticker_color}; text-shadow: 0 0 20px {ticker_color}; margin: 0; line-height: 1;'>${current_gme_price:.2f}</h1><h3 style='color: {ticker_color}; margin: 0;'>{sign}{gme_change_pct:.2f}%</h3></div><div>{icon_html}</div></div>", unsafe_allow_html=True)
        
        if not chart_data.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#050505')
            ax.set_facecolor('#050505')
            prices = chart_data.values
            x_pos = np.arange(len(prices))
            min_y = np.min(prices) * 0.99
            ax.bar(x_pos, prices - min_y, bottom=min_y, color=ticker_color, width=0.8, edgecolor='none')
            ax.axis('off')
            ax.set_xlim(-1, len(prices))
            ax.set_ylim(min_y, np.max(prices) * 1.01)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            st.pyplot(fig)

    with tab2:
        st.markdown("<h2 style='text-align: center;'>Écran 2 : Warrants GME-WT</h2>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<h2 style='text-align: center;'>Écran 3 : Camembert EU</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center;'>Écran 4 : Camembert US</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center;'>Écran 5 : Tableau Détaillé</h2>", unsafe_allow_html=True)

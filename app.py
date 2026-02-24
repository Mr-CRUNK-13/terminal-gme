import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="TERMINAL GME", layout="wide", initial_sidebar_state="collapsed")

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
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .rocket { animation: pulse 2s infinite; font-size: 150px; text-align: center; margin-bottom: 30px; }
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
            gme_qty = st.number_input("Quantité GME (US)", value=4000, step=1)
            gme_pru = st.number_input("PRU GME ($)", value=20.404, format="%.3f")
            wt_qty = st.number_input("Quantité Warrants", value=4013, step=1)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
        with col2:
            xet_qty = st.number_input("Quantité XET (EU)", value=650, step=1)
            xet_pru = st.number_input("PRU XET (€)", value=25.877, format="%.3f")
            tdg_qty = st.number_input("Quantité TDG (EU)", value=300, step=1)
            tdg_pru = st.number_input("PRU TDG (€)", value=25.994, format="%.3f")

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
            # NOUVEAU RÉGLAGE : Uniquement le jour actuel (1d), toutes les 2 minutes, avec le pre/post market
            hist = ticker.history(period="1d", interval="2m", prepost=True)
            
            if not hist.empty:
                current_gme_price = float(hist['Close'].iloc[-1])
                # On récupère le prix de clôture de la veille pour avoir le VRAI pourcentage journalier
                prev_close = float(ticker.fast_info['previousClose'])
            else:
                # Filet de sécurité si Yahoo Finance met du temps à charger le graphique
                current_gme_price = float(ticker.fast_info['lastPrice'])
                prev_close = float(ticker.fast_info['previousClose'])
                
            gme_change_pct = ((current_gme_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
            
            return current_gme_price, gme_change_pct, hist['Close']
            
        except Exception as e:
            return 25.00, 0.0, pd.Series()
    
    current_gme_price, gme_change_pct, chart_data = get_live_data()
    ticker_color = "#00FF00" if gme_change_pct >= 0 else "#FF3D00"
    sign = "+" if gme_change_pct >= 0 else ""
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])
    
    with tab1:
        # PRIX EN DIRECT
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <h2 style="color: #888; font-family: monospace;">GAMESTOP CORP. (GME)</h2>
            <h1 style="font-size: 100px; color: {ticker_color}; text-shadow: 0 0 20px {ticker_color};">${current_gme_price:.2f}</h1>
            <h3 style="color: {ticker_color};">{sign}{gme_change_pct:.2f}%</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # VRAI GRAPHIQUE LED JOURNALIER
        if not chart_data.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='#050505')
            ax.set_facecolor('#050505')
            
            prices = chart_data.values
            x_pos = np.arange(len(prices))
            
            # On coupe le bas du graphique au plus proche du prix pour accentuer visuellement les variations
            min_y = np.min(prices) * 0.99
            
            # Dessin des barres denses avec la couleur du jour (Vert ou Rouge)
            ax.bar(x_pos, prices - min_y, bottom=min_y, color=ticker_color, width=0.8, edgecolor='none')
            
            ax.axis('off')
            ax.set_xlim(-1, len(prices))
            ax.set_ylim(min_y, np.max(prices) * 1.01)
            
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            st.pyplot(fig)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # LOGIQUE D'AFFICHAGE : FUSÉE OU TON IMAGE WEN MOON
        if gme_change_pct >= 0:
            st.markdown("<div class='rocket'>🚀</div>", unsafe_allow_html=True)
        else:
            try:
                st.image("Screenshot_20260216_163106_Discord.jpg", use_container_width=True)
            except:
                st.warning("⚠️ Image introuvable dans le coffre GitHub.")

    with tab2:
        st.markdown("<h2 style='text-align: center;'>Écran 2 : Warrants GME-WT</h2>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<h2 style='text-align: center;'>Écran 3 : Camembert EU</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center;'>Écran 4 : Camembert US</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center;'>Écran 5 : Tableau Détaillé</h2>", unsafe_allow_html=True)

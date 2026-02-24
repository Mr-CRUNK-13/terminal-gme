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
    .rocket { animation: pulse 2s infinite; font-size: 150px; text-align: center; }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 2. ACCUEIL (Avec tes VRAIES données figées) ---
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
            data = yf.download("GME", period="5d", interval="1d", progress=False)
            current_gme_price = float(data['Close'].iloc[-1])
            prev_gme_price = float(data['Close'].iloc[-2])
            gme_change_pct = ((current_gme_price - prev_gme_price) / prev_gme_price) * 100
        except Exception as e:
            return 25.00, 0.0
        return current_gme_price, gme_change_pct
    
    current_gme_price, gme_change_pct = get_live_data()
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # LOGIQUE : FUSÉE si Vert, TON IMAGE si Rouge
        if gme_change_pct >= 0:
            st.markdown("<div class='rocket'>🚀</div>", unsafe_allow_html=True)
        else:
            try:
                # Ton image exacte intégrée ici !
                st.image("Screenshot_20260216_163106_Discord.jpg", use_container_width=True)
            except:
                st.warning("⚠️ Image introuvable. Assure-toi que Screenshot_20260216_163106_Discord.jpg est bien dans ton GitHub.")

        st.markdown("<br><br>", unsafe_allow_html=True)

        # GRAPHIQUE BARRES LED 
        quantities = [st.session_state.gme_qty, st.session_state.wt_qty, st.session_state.xet_qty + st.session_state.tdg_qty]
        labels = ['US Shares', 'Warrants', 'EU Shares']
        
        fig, ax = plt.subplots(figsize=(10, 3))
        fig.patch.set_facecolor('#050505')
        ax.set_facecolor('#050505')
        
        bars = ax.barh(labels, quantities, color='#00FF00', edgecolor='#00FF00', height=0.4)
        
        for bar in bars:
            bar.set_linewidth(2)
            
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_color('#00FF00')
        ax.tick_params(axis='x', colors='#050505')
        ax.tick_params(axis='y', colors='white', labelsize=12)
        
        for i, v in enumerate(quantities):
            ax.text(v + (max(quantities)*0.02), i, f"{v:,.0f}", color='white', va='center', fontsize=14, fontweight='bold')
            
        st.pyplot(fig)

    with tab2:
        st.markdown("<h2 style='text-align: center;'>Écran 2 : Warrants GME-WT</h2>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<h2 style='text-align: center;'>Écran 3 : Camembert EU</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center;'>Écran 4 : Camembert US</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center;'>Écran 5 : Tableau Détaillé</h2>", unsafe_allow_html=True)

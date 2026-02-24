import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import base64
import os

# --- 1. CONFIGURATION DE LA PAGE (Mode App Mobile) ---
st.set_page_config(page_title="TERMINAL GME", layout="wide", initial_sidebar_state="collapsed")

# --- 2. PROTECTION OLED & STYLE CSS ---
# Le Pixel Shifter décale l'écran de 1 pixel toutes les minutes pour protéger ta tablette
st.markdown("""
<style>
    @keyframes pixelShift {
        0% { transform: translate(0px, 0px); }
        25% { transform: translate(1px, 1px); }
        50% { transform: translate(0px, 1px); }
        75% { transform: translate(1px, 0px); }
        100% { transform: translate(0px, 0px); }
    }
    body, .stApp {
        background-color: #050505 !important;
        color: white;
        animation: pixelShift 60s infinite; 
    }
    /* Masquer l'interface par défaut de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Bouton Lancement */
    .btn-launch {
        background-color: #00FF00; color: #050505; font-size: 24px; 
        font-weight: bold; border-radius: 10px; padding: 15px; 
        width: 100%; text-align: center; text-decoration: none; display: block;
        box-shadow: 0px 0px 20px #00FF00; margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTION DE LA MÉMOIRE (Configuration) ---
if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 4. ÉCRAN D'ACCUEIL & CONFIGURATION ---
if not st.session_state.launched:
    st.markdown("<h1 style='text-align: center; font-size: 50px; color: #fff; text-shadow: 0 0 10px #fff;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Prêt pour le décollage</p>", unsafe_allow_html=True)
    
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE (Clique pour ouvrir)"):
        st.text_input("Surnom pour le Leaderboard WEN MOON", value="", placeholder="Ex: DiamondHands (Laisser vide pour Anonyme)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (US)")
            gme_qty = st.number_input("Quantité GME", value=4950, step=1)
            gme_pru = st.number_input("PRU GME ($)", value=22.33, step=0.01)
            
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013, step=1)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, step=0.001)
            
        with col2:
            st.markdown("### 🇪🇺 Actions GME (Europe 1)")
            eu1_qty = st.number_input("Quantité EU 1", value=0, step=1)
            eu1_pru = st.number_input("PRU EU 1 (€)", value=0.0, step=0.01)
            
            st.markdown("### 🇪🇺 Actions GME (Europe 2)")
            eu2_qty = st.number_input("Quantité EU 2", value=0, step=1)
            eu2_pru = st.number_input("PRU EU 2 (€)", value=0.0, step=0.01)

    # Bouton magique de lancement
    if st.button("LANCER LE SYSTÈME WEN MOON 🚀", use_container_width=True):
        # Sauvegarde des données dans la mémoire
        st.session_state.gme_qty = gme_qty
        st.session_state.gme_pru = gme_pru
        st.session_state.wt_qty = wt_qty
        st.session_state.wt_pru = wt_pru
        st.session_state.launched = True
        st.rerun()
        
    st.markdown("<p style='text-align: right; color: #333; margin-top: 50px;'>By Mr-CRUNK-13</p>", unsafe_allow_html=True)

# --- 5. LE TERMINAL (Les 5 Écrans) ---
else:
    # Récupération des données en direct
    @st.cache_data(ttl=60) # Met à jour toutes les 60 secondes
    def get_live_data():
        gme = yf.Ticker("GME").history(period="1d", prepost=True)
        wt = yf.Ticker("GME-WT").history(period="1d", prepost=True)
        return gme, wt
    
    gme_data, wt_data = get_live_data()
    current_gme_price = gme_data['Close'].iloc[-1] if not gme_data.empty else 25.00
    
    # Création de la navigation façon application mobile (Onglets)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])
    
    with tab1:
        # ÉCRAN 1 : Ticker Géant GME
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <h2 style="color: #888; font-family: monospace;">GAMESTOP CORP. (GME)</h2>
            <h1 style="font-size: 120px; color: #00FF00; font-family: monospace; text-shadow: 0 0 20px #00FF00;">${current_gme_price:.2f}</h1>
            <h3 style="color: #00FF00; font-family: monospace;">+5.2% 🚀 <span style="font-size: 20px; color: #888;">(Démo Animation)</span></h3>
        </div>
        """, unsafe_allow_html=True)
        # Ici viendra s'insérer le graphique Matplotlib parfait
        
    with tab2:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 2 : Warrants GME-WT (En construction)</h2>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 3 : Camembert EU (En construction)</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 4 : Camembert US (En construction)</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 5 : Tableau Détaillé (En construction)</h2>", unsafe_allow_html=True)


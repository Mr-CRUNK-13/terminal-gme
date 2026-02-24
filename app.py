import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="TERMINAL GME", layout="wide", initial_sidebar_state="collapsed")

# --- 2. STYLE CSS ---
st.markdown("""
<style>
    body, .stApp {
        background-color: #050505 !important;
        color: white;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .btn-launch {
        background-color: #00FF00; color: #050505; font-size: 24px; 
        font-weight: bold; border-radius: 10px; padding: 15px; 
        width: 100%; text-align: center; text-decoration: none; display: block;
        box-shadow: 0px 0px 20px #00FF00; margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GESTION DE LA MÉMOIRE ---
if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 4. ÉCRAN D'ACCUEIL ---
if not st.session_state.launched:
    st.markdown("<br><br><h1 style='text-align: center; font-size: 50px; color: #fff; text-shadow: 0 0 10px #fff;'>TERMINAL GME</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Prêt pour le décollage</p>", unsafe_allow_html=True)
    
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE (Clique pour ouvrir)"):
        st.text_input("Surnom pour le Leaderboard", value="", placeholder="Ex: DiamondHands")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (US)")
            # Remplace ces "value" par tes vraies données pour qu'elles restent par défaut !
            gme_qty = st.number_input("Quantité GME", value=4950, step=1)
            gme_pru = st.number_input("PRU GME ($)", value=22.33, step=0.01)
            
            st.markdown("### 📜 Warrants GME-WT")
            wt_qty = st.number_input("Quantité Warrants", value=4013, step=1)
            wt_pru = st.number_input("PRU Warrants ($)", value=3.243, step=0.001)
            
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            xet_qty = st.number_input("Quantité XET", value=0, step=1)
            xet_pru = st.number_input("PRU XET (€)", value=0.0, step=0.01)
            
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            tdg_qty = st.number_input("Quantité TDG", value=0, step=1)
            tdg_pru = st.number_input("PRU TDG (€)", value=0.0, step=0.01)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("LANCER LE SYSTÈME WEN MOON 🚀", use_container_width=True):
        st.session_state.gme_qty = gme_qty
        st.session_state.gme_pru = gme_pru
        st.session_state.wt_qty = wt_qty
        st.session_state.wt_pru = wt_pru
        st.session_state.xet_qty = xet_qty
        st.session_state.xet_pru = xet_pru
        st.session_state.tdg_qty = tdg_qty
        st.session_state.tdg_pru = tdg_pru
        st.session_state.launched = True
        st.rerun()
        
    st.markdown("<p style='text-align: right; color: #333; margin-top: 50px;'>By Mr-CRUNK-13</p>", unsafe_allow_html=True)

# --- 5. LE TERMINAL ---
else:
    @st.cache_data(ttl=60)
    def get_live_data():
        try:
            gme = yf.Ticker("GME").history(period="5d")
            current_gme_price = round(gme['Close'].iloc[-1], 2)
            prev_gme_price = round(gme['Close'].iloc[-2], 2)
            gme_change_pct = ((current_gme_price - prev_gme_price) / prev_gme_price) * 100
        except:
            current_gme_price = 25.80
            gme_change_pct = 0.0
        return current_gme_price, gme_change_pct
    
    current_gme_price, gme_change_pct = get_live_data()
    ticker_color = "#00FF00" if gme_change_pct >= 0 else "#FF3D00"
    sign = "+" if gme_change_pct >= 0 else ""
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])
    
    with tab1:
        # VRAI TICKER LIVE
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <h2 style="color: #888; font-family: monospace;">GAMESTOP CORP. (GME)</h2>
            <h1 style="font-size: 100px; color: {ticker_color}; font-family: monospace; text-shadow: 0 0 20px {ticker_color};">${current_gme_price:.2f}</h1>
            <h3 style="color: {ticker_color}; font-family: monospace;">{sign}{gme_change_pct:.2f}% 🚀</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # IMAGE WEN MOON (S'assure qu'elle s'affiche au dessus ou en dessous du graphe)
        # Remplace 'nom_de_ton_image.jpg' par le vrai nom de ton image dans le coffre GitHub
        try:
            # st.image("nom_de_ton_image.jpg", use_container_width=True) 
            pass # Retire le '#' de la ligne du dessus quand on connectera l'image exacte
        except:
            pass

        # GRAPHIQUE PARFAIT
        qty_s = st.session_state.gme_qty
        cost_s_avg = st.session_state.gme_pru
        qty_w = st.session_state.wt_qty
        cost_w_avg = st.session_state.wt_pru
        
        price_shares = current_gme_price
        price_warrants = 4.23 # Warrants fixes temporairement
        
        val_s = qty_s * price_shares
        cost_s = qty_s * cost_s_avg
        pl_s = val_s - cost_s
        
        val_w = qty_w * price_warrants
        cost_w = qty_w * cost_w_avg
        pl_w = val_w - cost_w

        total_val = val_s + val_w
        total_pl = pl_s + pl_w
        total_cost = cost_s + cost_w
        total_pct = (total_pl / total_cost) * 100 if total_cost > 0 else 0

        pct_s = (val_s / total_val) * 100 if total_val > 0 else 0
        pct_w = (val_w / total_val) * 100 if total_val > 0 else 0

        G, DG, R = "#00E676", "#006400", "#FF3D00"
        col_s = G if pl_s >= 0 else R
        col_w = G if pl_w >= 0 else R
        col_t = G if total_pl >= 0 else R

        sz_w, sz_c = 40, 55 

        plt.rc('font', family='monospace', weight='bold')
        fig = plt.figure(figsize=(24, 12))
        bg_color = "#050505"
        fig.patch.set_facecolor(bg_color)
        gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])

        # LEFT PANEL (Shares)
        ax_left = fig.add_subplot(gs[0]); ax_left.set_facecolor(bg_color); ax_left.axis('off')
        y_start, y_step = 0.85, 0.15
        ax_left.text(0.9, y_start, "GameStop Shares", color=G, fontsize=sz_c, ha="right", va="center")
        ax_left.text(0.9, y_start - y_step, f"Val: ${val_s:,.2f}", color="white", fontsize=sz_w, ha="right", va="center")
        ax_left.text(0.9, y_start - 2*y_step, f"${price_shares:.2f}", color=col_s, fontsize=sz_c, ha="right", va="center")
        ax_left.text(0.9, y_start - 3*y_step, f"Avg Cost: ${cost_s_avg:.2f}", color="white", fontsize=sz_w, ha="right", va="center")
        pl_s_pct = (pl_s/cost_s) if cost_s > 0 else 0
        ax_left.text(0.9, y_start - 4*y_step, f"{pl_s:+,.2f} ({pl_s_pct:+.2%})", color=col_s, fontsize=sz_c, ha="right", va="center")

        # CENTER PANEL (Donut)
        ax_center = fig.add_subplot(gs[1]); ax_center.set_facecolor(bg_color)
        if val_s > 0 or val_w > 0:
            ax_center.pie([val_s, val_w], startangle=21.6, colors=[G, DG], radius=1.35, wedgeprops=dict(width=0.45, edgecolor=bg_color))
            ax_center.text(-1.125, 0, f"{pct_s:.0f}%", fontsize=60, color="white", ha="center", va="center")
            ax_center.text(1.125, 0, f"{pct_w:.0f}%", fontsize=60, color="white", ha="center", va="center")
        ax_center.text(0, -0.05, f"${total_val:,.2f}", fontsize=70, color="white", ha="center", va="center")
        ax_center.text(0, -0.25, f"{total_pl:+,.2f} ({total_pct:+.2f}%)", fontsize=45, color=col_t, ha="center", va="center")

        # RIGHT PANEL (Warrants)
        ax_right = fig.add_subplot(gs[2]); ax_right.set_facecolor(bg_color); ax_right.axis('off')
        ax_right.text(0.1, y_start, "Warrants (GME-WT)", color=DG, fontsize=sz_c, ha="left", va="center")
        ax_right.text(0.1, y_start - y_step, f"Val: ${val_w:,.2f}", color="white", fontsize=sz_w, ha="left", va="center")
        ax_right.text(0.1, y_start - 2*y_step, f"${price_warrants:.2f}", color=col_w, fontsize=sz_c, ha="left", va="center")
        ax_right.text(0.1, y_start - 3*y_step, f"Avg Cost: ${cost_w_avg:.3f}", color="white", fontsize=sz_w, ha="left", va="center")
        pl_w_pct = (pl_w/cost_w) if cost_w > 0 else 0
        ax_right.text(0.1, y_start - 4*y_step, f"{pl_w:+,.2f} ({pl_w_pct:+.2%})", color=col_w, fontsize=sz_c, ha="left", va="center")

        plt.subplots_adjust(left=0.02, right=0.98, wspace=0.02)
        st.pyplot(fig)

    with tab2:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 2 : Warrants GME-WT (En construction)</h2>", unsafe_allow_html=True)
    with tab3:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 3 : Camembert EU (En construction)</h2>", unsafe_allow_html=True)
    with tab4:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 4 : Camembert US (En construction)</h2>", unsafe_allow_html=True)
    with tab5:
        st.markdown("<h2 style='text-align: center; color: white;'>Écran 5 : Tableau Détaillé (En construction)</h2>", unsafe_allow_html=True)

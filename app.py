import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import base64
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="TERMINAL GME", page_icon="Screenshot_20260216_163106_Discord.jpg", layout="wide", initial_sidebar_state="collapsed")

# --- INJECTION DU MANIFESTE & BOUTON PLEIN ÉCRAN FLOTTANT ---
components.html(
    """
    <script>
    const parent = window.parent.document;
    const head = parent.querySelector('head');
    
    if (!parent.querySelector('#pwa-manifest')) {
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-capable" content="yes">');
        head.insertAdjacentHTML('beforeend', '<meta name="mobile-web-app-capable" content="yes">');
        head.insertAdjacentHTML('beforeend', '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">');
        const manifest = {
            "name": "TERMINAL GME", "short_name": "GME",
            "start_url": window.parent.location.href,
            "display": "fullscreen",
            "background_color": "#050505", "theme_color": "#050505"
        };
        const blob = new Blob([JSON.stringify(manifest)], {type: 'application/json'});
        head.insertAdjacentHTML('beforeend', '<link id="pwa-manifest" rel="manifest" href="' + URL.createObjectURL(blob) + '">');
    }

    // Traqueur d'état Plein Écran infaillible via une classe sur le BODY
    const handleFsChange = () => {
        if (parent.fullscreenElement || parent.webkitFullscreenElement || parent.msFullscreenElement) {
            parent.body.classList.add('is-fullscreen');
        } else {
            parent.body.classList.remove('is-fullscreen');
        }
    };
    parent.addEventListener('fullscreenchange', handleFsChange);
    parent.addEventListener('webkitfullscreenchange', handleFsChange);
    parent.addEventListener('msfullscreenchange', handleFsChange);

    if (!parent.getElementById('btn-fullscreen')) {
        const btn = parent.createElement('button');
        btn.id = 'btn-fullscreen';
        btn.innerText = '⛶';
        // Styles par défaut (Mode Normal : Bas Droite, Grand)
        btn.style.position = 'fixed';
        btn.style.bottom = '70px';
        btn.style.right = '20px';
        btn.style.zIndex = '99999';
        btn.style.background = '#050505';
        btn.style.color = '#00FF00';
        btn.style.border = '2px solid #00FF00';
        btn.style.borderRadius = '10px';
        btn.style.width = '55px';
        btn.style.height = '55px';
        btn.style.fontSize = '30px';
        btn.style.cursor = 'pointer';
        btn.style.boxShadow = '0 0 15px #00FF00';
        
        btn.onclick = function() {
            const docEl = parent.documentElement;
            if (!parent.fullscreenElement && !parent.webkitFullscreenElement) {
                if (docEl.requestFullscreen) docEl.requestFullscreen();
                else if (docEl.webkitRequestFullscreen) docEl.webkitRequestFullscreen();
                else if (docEl.msRequestFullscreen) docEl.msRequestFullscreen();
                parent.body.classList.add('is-fullscreen');
            } else {
                if (parent.exitFullscreen) parent.exitFullscreen();
                else if (parent.webkitExitFullscreen) parent.webkitExitFullscreen();
                else if (parent.msExitFullscreen) parent.msExitFullscreen();
                parent.body.classList.remove('is-fullscreen');
            }
        };
        parent.body.appendChild(btn);
    }
    </script>
    """,
    height=0,
    width=0,
)

# --- FORCE FAVICON CHROME (HACK ANTI-CACHE) ---
wen_ico = get_b64("Screenshot_20260216_163106_Discord.jpg")
if wen_ico:
    components.html(f"""<script>
        const link = window.parent.document.querySelector("link[rel~='icon']") || window.parent.document.createElement('link');
        link.rel = 'icon';
        link.href = "data:image/jpeg;base64,{wen_ico}";
        window.parent.document.head.appendChild(link);
    </script>""", height=0, width=0)

st.markdown("""
<style>
    body, .stApp { background-color: #050505 !important; color: white; }
    #MainMenu, footer, header {visibility: hidden;}
    @keyframes flash { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.05); box-shadow: 0 0 30px #FF0000; } 100% { opacity: 1; transform: scale(1); } }
    @keyframes rocket-pulse { 0% { transform: translateY(0px) scale(1); } 50% { transform: translateY(-20px) scale(1.15); } 100% { transform: translateY(0px) scale(1); } }
    @keyframes neon-text { 0%, 100% { color: white; text-shadow: none; } 50% { color: #00FF00; text-shadow: 0 0 15px #00FF00, 0 0 45px #00FF00, 0 0 90px #00FF00; } }
    @keyframes nuclear-neon { 0%, 100% { filter: drop-shadow(0 0 0 transparent); } 50% { filter: drop-shadow(0 0 20px #00FF00) drop-shadow(0 0 60px #00FF00) drop-shadow(0 0 150px #00FF00); } }
    @keyframes nuclear-red-img { 0%, 100% { filter: drop-shadow(0 0 0 transparent); } 50% { filter: drop-shadow(0 0 20px #FF0000) drop-shadow(0 0 70px #FF0000) drop-shadow(0 0 150px #FF0000); } }
    @keyframes neon-img { 0%, 100% { filter: drop-shadow(0 0 0px transparent); } 50% { filter: drop-shadow(0 0 25px #00FF00); } }

    /* PAR DÉFAUT (Protège le mode normal et paysage) */
    .mobile-break { display: none; }
    .desktop-space { display: inline; }

    /* CIBLAGE DU BOUTON EN MODE PLEIN ÉCRAN (Parfait) */
    body.is-fullscreen #btn-fullscreen {
        bottom: 20px !important;
        left: 20px !important;
        right: auto !important;
        width: 38px !important;
        height: 38px !important;
        font-size: 21px !important;
        border-radius: 8px !important;
    }

    /* --- BOUCLIER V44 : MODIFICATIONS UNIQUEMENT EN PORTRAIT PLEIN ÉCRAN --- */
    @media screen and (orientation: portrait) {
        body.is-fullscreen .gme-title {
            font-size: 35px !important;
            white-space: normal !important;
            padding-top: 0px !important; 
            line-height: 1.1 !important;
        }
        body.is-fullscreen .desktop-space { display: none !important; }
        
        /* LA CORRECTION ULTIME EST ICI : ESPACEMENT GARANTI */
        body.is-fullscreen .mobile-break { display: none !important; } /* On cache l'ancien <br> inutile */
        
        /* On injecte un bloc invisible de 30px juste après le mot TERMINAL */
        body.is-fullscreen .terminal-word::after {
            content: "" !important;
            display: block !important; /* Force le retour à la ligne */
            height: 30px !important;   /* Force l'espace vertical exact */
        }
        
        /* ASPIRATION DES MARGES (Parfait, ne pas toucher) */
        body.is-fullscreen .main .block-container,
        body.is-fullscreen [data-testid="stAppViewBlockContainer"] {
            padding-top: 0px !important; 
            padding-bottom: 0px !important; 
            margin-top: -80px !important; 
        }
        body.is-fullscreen div[style*='margin-bottom: 40px'] {
            margin-bottom: 10px !important; 
        }
        body.is-fullscreen h4 {
            margin-top: 0px !important; 
        }
    }
</style>
""", unsafe_allow_html=True)

if 'launched' not in st.session_state:
    st.session_state.launched = False

# --- 2. ACCUEIL ---
if not st.session_state.launched:
    wen_b64 = get_b64('Screenshot_20260216_163106_Discord.jpg')
    # AJOUT DU SPAN 'terminal-word' POUR LE CIBLAGE CSS V44
    st.markdown(f"""
    <br>
    <div style='display:flex; justify-content:center; align-items:center; width: 100%; margin-bottom: 40px;'>
        <div style='flex: 0 0 180px; display: flex; justify-content: center; align-items: center;'>
            <img src='data:image/jpeg;base64,{wen_b64}' style='height:130px; animation: neon-img 1.5s infinite;'>
        </div>
        <div style='flex: 1; text-align: center; white-space: nowrap; padding: 0 10px; display: flex; justify-content: center; align-items: center;'>
            <h1 class='gme-title' style='font-size: 70px; margin: 0; line-height: 1; padding-top: 25px; animation: neon-text 1.5s infinite;'><span class='terminal-word'>TERMINAL</span><span class='desktop-space'> </span><br class='mobile-break'>GME</h1>
        </div>
        <div style='flex: 0 0 180px; display: flex; justify-content: center; align-items: center;'>
            <div style='animation: rocket-pulse 1s ease-in-out infinite;'>
                <div style='font-size: 90px; animation: nuclear-neon 1.5s infinite;'>🚀</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ CONFIGURATION DU PORTEFEUILLE"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🇺🇸 Actions GME (NYSE)")
            g_n_q = st.number_input("Quantité NYSE", value=4000)
            g_n_p = st.number_input("PRU NYSE ($)", value=20.404, format="%.3f")
            st.markdown("### 📜 Warrants GME-WT")
            w_q = st.number_input("Quantité Warrants", value=4013)
            w_p = st.number_input("PRU Warrants ($)", value=3.243, format="%.3f")
        with col2:
            st.markdown("### 🇪🇺 Actions GME (XET)")
            x_q = st.number_input("Quantité XET", value=650)
            x_p = st.number_input("PRU XET (€)", value=25.877, format="%.3f")
            st.markdown("### 🇪🇺 Actions GME (TDG)")
            t_q = st.number_input("Quantité TDG", value=300)
            t_p = st.number_input("PRU TDG (€)", value=25.994, format="%.3f")
            st.markdown("### ⚓ PRU Global Actions US")
            g_p = st.number_input("PRU Moyen Global (Data & US Tab) ($)", value=22.33, format="%.3f")

    if st.button("LANCER LE SYSTÈME WEN MOON 🚀🌘!", use_container_width=True):
        st.session_state.update(qn=g_n_q, pn=g_n_p, qw=w_q, pw=w_p, qx=x_q, px=x_p, qt=t_q, pt=t_p, gp=g_p, launched=True)
        st.rerun()
    st.markdown("<h4 style='text-align: right; margin-top: 30px; font-family: monospace; animation: neon-text 1.5s infinite;'>By Mr-CRUNK-13</h4>", unsafe_allow_html=True)

# --- 3. TERMINAL ---
else:
    @st.cache_data(ttl=60)
    def fetch_terminal_data():
        try:
            ts = ["GME", "GME-WT", "GS2C.DE", "EURUSD=X"]
            data = yf.download(ts, period="1d", interval="2m", prepost=True, progress=False)['Close']
            p_n, p_w, p_x, rate = float(data['GME'].dropna().iloc[-1]), float(data['GME-WT'].dropna().iloc[-1]), float(data['GS2C.DE'].dropna().iloc[-1]), float(data['EURUSD=X'].dropna().iloc[-1])
            prev_n = float(yf.Ticker("GME").fast_info['previousClose'])
            prev_w = float(yf.Ticker("GME-WT").fast_info['previousClose'])
            return p_n, p_w, p_x, rate, prev_n, prev_w, data['GME'], data['GME-WT']
        except: return 24.50, 4.30, 22.10, 1.08, 24.0, 4.0, pd.Series(), pd.Series()

    p_nsy, p_wt, p_xet, fx, pr_nsy, pr_wt, ch_gme, ch_wt = fetch_terminal_data()
    qn, pn, qw, pw, qx, px, qt, pt, gp = st.session_state.qn, st.session_state.pn, st.session_state.qw, st.session_state.pw, st.session_state.qx, st.session_state.px, st.session_state.qt, st.session_state.pt, st.session_state.gp

    total_shares = qn + qx + qt
    v_s_u, v_w_u = total_shares * p_nsy, qw * p_wt
    t_v_u, t_c_u = v_s_u + v_w_u, (total_shares * gp) + (qw * pw)
    t_pl_u = t_v_u - t_c_u

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 GME", "📜 WARRANTS", "🇪🇺 EU", "🇺🇸 US", "📋 DATA"])

    def draw_live(price, prev, chart):
        pct = ((price - prev) / prev) * 100
        diff = price - prev
        clr = "#00FF00" if pct >= 0 else "#FF0000"
        sz = min(100 + (abs(pct) * 10), 200)
        
        if pct >= 0:
            icn = f"<div style='animation: rocket-pulse 1s ease-in-out infinite;'><div style='font-size:{sz}px; animation: nuclear-neon 1.5s infinite;'>🚀</div></div>"
        else:
            icn = f"<img src='data:image/jpeg;base64,{get_b64('Screenshot_20260216_163106_Discord.jpg')}' style='height:{sz}px; animation:flash 1s infinite, nuclear-red-img 1.5s infinite;'>"
            
        st.markdown(f"<div style='display:flex; justify-content:center; align-items:center; gap:40px; margin-top:30px;'><div style='text-align:right;'><h1 style='font-size:100px; color:{clr}; text-shadow:0 0 20px {clr}; margin:0;'>${price:.2f}</h1><h3 style='color:{clr}; margin:0;'>${diff:+.2f} {pct:+.2f}%</h3></div>{icn}</div>", unsafe_allow_html=True)
        if not chart.empty:
            fig, ax = plt.subplots(figsize=(10, 2.5), facecolor='black'); ax.set_facecolor('black')
            v = chart.dropna().values
            ax.bar(np.arange(len(v)), v - np.min(v)*0.99, bottom=np.min(v)*0.99, color=clr, width=0.8); ax.axis('off'); st.pyplot(fig)

    with tab1: draw_live(p_nsy, pr_nsy, ch_gme)
    with tab2: draw_live(p_wt, pr_wt, ch_wt)

    with tab3:
        vne, vwe = (qn*p_nsy)/fx, (qw*p_wt)/fx
        vxe, vte = qx*p_xet, qt*p_xet
        total_e = vne+vwe+vxe+vte
        pl_n, pl_w, pl_x, pl_t = vne-(qn*pn/fx), vwe-(qw*pw/fx), vxe-(qx*px), vte-(qt*pt)
        pl_tot_e = pl_n+pl_w+pl_x+pl_t
        plt.rc('font', family='monospace', weight='bold')
        fig3, ax3 = plt.subplots(figsize=(26, 18), subplot_kw=dict(aspect="equal"))
        fig3.patch.set_facecolor("#0e1621"); ax3.set_facecolor("#0e1621")
        plt.subplots_adjust(left=0.1, right=0.9, top=0.85, bottom=0.15)
        wedges, _, autotexts = ax3.pie([vxe, vne, vwe, vte], colors=['#FF0000','#00FF00','#008000','#D50000'], wedgeprops=dict(width=0.65, edgecolor="#0e1621"), autopct='%1.1f%%', pctdistance=0.75, textprops={'color':"black", 'fontsize':55})
        def build_l(name, eur, qty, crs, sym, pru, psym, ple, pct):
            s = "+" if ple >= 0 else "-"
            return f"{name}\nVal: €{eur:,.2f} ({eur/total_e:.1%})\n     ${eur*fx:,.2f}\nQty: {qty} | Cours: {sym}{crs:.2f}\nPRU: {psym}{pru:.3f}\nP/L: {s}€{abs(ple):,.2f} ({s}{abs(pct):.2f}%)\n     {s}${abs(ple*fx):,.2f}"
        txts = {"NSY": build_l("Action GME (NYSE)",vne,qn,p_nsy,"$",pn,"$",pl_n,(pl_n/(vne-pl_n))*100 if (vne-pl_n)!=0 else 0), "Warrant": build_l("Warrant (NSY)",vwe,qw,p_wt,"$",pw,"$",pl_w,(pl_w/(vwe-pl_w))*100 if (vwe-pl_w)!=0 else 0), "XET": build_l("Action GME (XET)",vxe,qx,p_xet,"€",px,"€",pl_x,(pl_x/(vxe-pl_x))*100 if (vxe-pl_x)!=0 else 0), "TDG": build_l("Action GME (TDG)",vte,qt,p_xet,"€",pt,"€",pl_t,(pl_t/(vte-pl_t))*100 if (vte-pl_t)!=0 else 0)}
        pos = {"NSY": (-2.24, 0.8), "Warrant": (-2.24, -0.8), "XET": (2.15, 0.8), "TDG": (2.15, -0.8)}
        for i, k in enumerate(["XET", "NSY", "Warrant", "TDG"]):
            p = wedges[i]; ang = (p.theta2 - p.theta1)/2. + p.theta1
            ax3.annotate(txts[k], xy=(np.cos(np.deg2rad(ang)), np.sin(np.deg2rad(ang))), xytext=pos[k], color=['#FF0000','#00FF00','#008000','#D50000'][i], fontsize=30, weight='bold', arrowprops=dict(arrowstyle="-", color=['#FF0000','#00FF00','#008000','#D50000'][i], lw=4), bbox=dict(boxstyle="round,pad=0.5", fc="#0e1621", ec="gray", lw=2), ha="center", va="center")
        footer = f"Valeur Totale: €{total_e:,.2f} (${total_e*fx:,.2f})\nP/L Latent Estimé: {pl_tot_e:+,.2f}€ (${pl_tot_e*fx:+,.2f})"
        plt.figtext(0.5, 0.05, footer, color="#00FF00", fontsize=38, ha="center", weight="bold", bbox=dict(boxstyle="round,pad=1", fc="#0e1621", ec="white", lw=3))
        st.pyplot(fig3)

    with tab4:
        pl_s_u, pl_w_u = v_s_u - (total_shares * gp), v_w_u - (qw * pw)
        fig4 = plt.figure(figsize=(32, 18)); fig4.patch.set_facecolor("#0e1621"); gs = GridSpec(1, 3, width_ratios=[1, 2.5, 1])
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.1)
        al = fig4.add_subplot(gs[0]); al.set_facecolor("#0e1621"); al.axis('off')
        al.text(0.9, 0.85, "GameStop Shares (GME)", color="#00FF00", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.70, f"Val: ${v_s_u:,.2f}", color="white", fontsize=63, ha="right", weight="bold")
        al.text(0.9, 0.55, f"Qty: {total_shares:,} | Price: ${p_nsy:.2f}", color="#00FF00" if pl_s_u>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
        al.text(0.9, 0.40, f"Avg Cost: ${gp:.2f}", color="white", fontsize=63, ha="right", weight="bold")
        al.text(0.9, 0.25, f"P/L: ${pl_s_u:+,.2f} ({pl_s_u/(total_shares*gp):+.2%})", color="#00FF00" if pl_s_u>=0 else "#FF0000", fontsize=84, ha="right", weight="bold")
        al.annotate("", xy=(0.95, 0.5), xytext=(1.28, 0.5), arrowprops=dict(arrowstyle="->", color="#00FF00" if pl_s_u>=0 else "#FF0000", lw=20))
        ac = fig4.add_subplot(gs[1]); ac.set_facecolor("#0e1621")
        ac.pie([v_s_u, v_w_u], colors=["#00FF00", "#006400"], radius=1.35, wedgeprops=dict(width=0.45, edgecolor="#0e1621"), startangle=21.6)
        ac.text(-1.1, 0, f"{(v_s_u/t_v_u)*100:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
        ac.text(1.1, 0, f"{(v_w_u/t_v_u)*100:.0f}%", fontsize=75, color="black", ha="center", weight="bold")
        ac.text(0, 0.15, "Total Value:", fontsize=45, color="white", ha="center", weight="bold")
        ac.text(0, -0.05, f"${t_v_u:,.2f}", fontsize=85, color="white", ha="center", weight="bold")
        ac.text(0, -0.25, f"${t_pl_u:+,.2f} ({t_pl_u/t_c_u:+.2%})", fontsize=48, color="#00FF00" if t_pl_u>=0 else "#FF0000", ha="center", weight="bold")
        ar = fig4.add_subplot(gs[2]); ar.set_facecolor("#0e1621"); ar.axis('off')
        ar.text(0.1, 0.85, "Warrants (GME-WT)", color="#006400", fontsize=84, ha="left", weight="bold")
        ar.text(0.1, 0.70, f"Val: ${v_w_u:,.2f}", color="white", fontsize=63, ha="left", weight="bold")
        ar.text(0.1, 0.55, f"Qty: {qw:,} | Price: ${p_wt:.2f}", color="#00FF00" if pl_w_u>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
        ar.text(0.1, 0.40, f"Avg Cost: ${pw:.3f}", color="white", fontsize=63, ha="left", weight="bold")
        ar.text(0.1, 0.25, f"P/L: ${pl_w_u:+,.2f} ({pl_w_u/(qw*pw):+.2%})", color="#00FF00" if pl_w_u>=0 else "#FF0000", fontsize=84, ha="left", weight="bold")
        ar.annotate("", xy=(0.08, 0.5), xytext=(-0.19, 0.5), arrowprops=dict(arrowstyle="->", color="#006400", lw=20))
        st.pyplot(fig4)

    with tab5:
        fig5, ax5 = plt.subplots(figsize=(14, 6)); fig5.patch.set_facecolor("#0f172a"); ax5.axis('off')
        def f5(v, c): s = "+" if v-c>=0 else "-"; p = ((v-c)/c)*100 if c!=0 else 0; return f"{s}${abs(v-c):,.2f} ({s}{abs(p):.2f}%)"
        rows = [["GME TOTAL",f"{total_shares:,}",f"${gp:.2f}",f"${p_nsy:.2f}",f"${total_shares*gp:,.2f}",f"${v_s_u:,.2f}",f5(v_s_u,total_shares*gp),f"{v_s_u/t_v_u:.1%}"],["WARRANTS",f"{qw:,}",f"${pw:.3f}",f"${p_wt:.2f}",f"${qw*pw:,.2f}",f"${v_w_u:,.2f}",f5(v_w_u,qw*pw),f"{v_w_u/t_v_u:.1%}"],["","","","","","","",""],["TOTAL PORTFOLIO","","","",f"${t_c_u:,.2f}",f"${t_v_u:,.2f}",f5(t_v_u,t_c_u),"100%"]]
        cw = [0.18, 0.07, 0.09, 0.09, 0.11, 0.14, 0.23, 0.09]
        table = ax5.table(cellText=rows, colLabels=["Ticker","Qty","Avg. Cost","Price","Total Cost","Market Value","Latent P/L","Portfolio %"], loc='center', cellLoc='center', colWidths=cw)
        table.auto_set_font_size(False); table.set_fontsize(12); table.scale(1, 2.5)
        for (r, c), cell in table.get_celld().items():
            if r == 0: cell.set_facecolor("#001f3f"); cell.get_text().set_color("#00FF00"); cell.get_text().set_fontweight('bold')
            elif r in [1, 2, 4]:
                if r == 4 and c not in [0, 4, 5, 6]: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a"); continue
                cell.set_facecolor("#0259c7"); cell.get_text().set_color("white"); cell.get_text().set_fontweight('bold')
                if c in [1, 3, 5]: cell.get_text().set_color("#00FF00"); cell.get_text().set_fontsize(14)
                elif c == 6: cell.get_text().set_color("#00FF00" if (v_s_u-total_shares*gp if r==1 else v_w_u-qw*pw if r==2 else t_pl_u)>=0 else "#ef4444"); cell.get_text().set_fontsize(14)
            else: cell.set_facecolor("#0f172a"); cell.set_edgecolor("#0f172a")
        st.pyplot(fig5)

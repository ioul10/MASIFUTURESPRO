# =============================================================================
# MASI Futures Pro - Version Finale
# =============================================================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions
import time

# Configuration de la page (DOIT ÊTRE EN PREMIER)
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# GESTION DU SPLASH SCREEN
# =============================================================================

def show_splash_screen():
    """Affiche l'écran de chargement"""
    
    # CSS pour l'animation
    st.markdown("""
        <style>
            @keyframes pulse {
                0%, 100% { opacity: 0.6; }
                50% { opacity: 1; }
            }
            .splash-container {
                text-align: center;
                padding: 80px 20px;
                background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
                max-width: 600px;
                margin: 100px auto;
            }
            .splash-title {
                color: white;
                font-size: 2.5em;
                margin: 30px 0 10px 0;
                font-weight: 700;
                text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            .splash-version {
                color: rgba(255,255,255,0.9);
                font-size: 1.2em;
                margin: 10px 0 30px 0;
            }
            .splash-loading {
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                color: rgba(255,255,255,0.8);
                font-size: 0.9em;
                animation: pulse 1.5s infinite;
            }
            .splash-footer {
                color: rgba(255,255,255,0.6);
                margin-top: 20px;
                font-size: 0.8em;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Layout centré
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
            <div class='splash-container'>
        """, unsafe_allow_html=True)
        
        # Logo
        try:
            st.image("logo.png", width=250, use_container_width=False)
        except:
            st.markdown("<div style='font-size: 5em; margin: 20px 0;'>📈</div>", unsafe_allow_html=True)
        
        # Titre et version
        st.markdown(f"""
            <h1 class='splash-title'>{config.APP_NAME}</h1>
            <p class='splash-version'>v{config.APP_VERSION}</p>
        """, unsafe_allow_html=True)
        
        # Message de chargement
        st.markdown("""
            <div class='splash-loading'>
                🔍 Initialisation des connexions...<br>
                📊 Chargement des données de marché...<br>
                ✅ Prêt !
            </div>
            <p class='splash-footer'>
                Développé par OULMADANI Ilyas & ATANANE Oussama<br>
                Conforme Instruction BAM N° IN-2026-01
            </p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE PRINCIPALE
# =============================================================================

# Initialiser le session state pour le splash screen
if 'splash_shown' not in st.session_state:
    st.session_state['splash_shown'] = False

# Afficher le splash screen une seule fois
if not st.session_state['splash_shown']:
    show_splash_screen()
    st.session_state['splash_shown'] = True
    time.sleep(3)  # Attendre 3 secondes
    st.rerun()  # Recharger la page pour afficher le contenu principal

# =============================================================================
# CONTENU PRINCIPAL DE L'APPLICATION
# =============================================================================

update_statut_connexions()
render_sidebar()
render_header()

# Titre de la page d'accueil
st.title(f"Bienvenue sur {config.APP_NAME}")

st.markdown(f"""
    <div style='padding: 30px; background: linear-gradient(135deg, {config.COLORS["card"]} 0%, #f8fafc 100%); 
                border-radius: 16px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
        <h2 style='color: {config.COLORS["primary"]}; margin-top: 0;'>🎯 Objectif de l'Application</h2>
        <p style='font-size: 1.1em; line-height: 1.8;'>
            {config.APP_NAME} est une plateforme professionnelle de pricing des contrats futures 
            sur les indices <strong>MASI</strong> et <strong>MASI20</strong> de la Bourse de Casablanca.
        </p>
        <p style='font-size: 1.1em; line-height: 1.8;'>
            Conforme à l'**Instruction BAM N° IN-2026-01**, cette application 
            vous permet de calculer le prix théorique des futures en temps réel, d'analyser les 
            opportunités d'arbitrage et de visualiser la structure par terme des prix.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Actions rapides
st.markdown("### 🚀 Actions Rapides")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["primary"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>🧮</h3>
            <h4 style='margin: 10px 0;'>Pricing</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Calculez le prix théorique F₀ avec sensibilités
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["success"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>📊</h3>
            <h4 style='margin: 10px 0;'>Indices</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Niveaux MASI & MASI20 en temps réel
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["warning"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>📰</h3>
            <h4 style='margin: 10px 0;'>Actualités</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                News du marché marocain
            </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Guide d'utilisation
with st.expander("📘 Guide d'Utilisation Rapide"):
    st.markdown("""
        ### Comment utiliser MASI Futures Pro ?
        
        **1. Pricing d'un Future :**
        - Cliquez sur "🧮 Pricing" dans le menu de navigation
        - Le niveau spot est récupéré automatiquement
        - Ajustez les paramètres (r, d, maturité)
        - Visualisez F₀, la base et les sensibilités
        
        **2. Analyse d'Arbitrage :**
        - Comparez le prix théorique avec le prix marché
        - Identifiez les opportunités d'arbitrage
        - Consultez la stratégie recommandée
        
        **3. Couverture (N*) :**
        - Calculez le Beta de votre portefeuille
        - Déterminez le nombre optimal de contrats
        - Visualisez la corrélation avec le MASI20
        
        **4. Données en Temps Réel :**
        - Les niveaux MASI/MASI20 sont mis à jour automatiquement
        - Le taux sans risque provient de BKAM
        - Les dividendes sont calculés selon la formule BAM
    """)

# Footer
render_footer()


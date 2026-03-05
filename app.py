# ============================================
# MASI Futures Pro - Version Alpha
# ============================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from components.guide_bam import render_guide_bam  # ← NOUVEL IMPORT
from utils.scraping import update_statut_connexions

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

update_statut_connexions()

# ────────────────────────────────────────────
# NAVIGATION PRINCIPALE
# ────────────────────────────────────────────
page = st.sidebar.radio(
    "🧭 Navigation",
    ["🏠 Accueil", "📰 News", "🧮 Pricing", "📚 Guide BAM"],
    label_visibility="collapsed"
)

render_header()

# ────────────────────────────────────────────
# ROUTING VERS LES PAGES
# ────────────────────────────────────────────
if page == "🏠 Accueil":
    # ────────────────────────────────────────
    # CONTENU DE LA PAGE D'ACCUEIL
    # ────────────────────────────────────────
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
                Basée sur l'**Instruction BAM N° IN-2026-01**, cette application 
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

elif page == "📰 News":
    # Redirection vers la page News
    st.switch_page("pages/01_📰_News.py")

elif page == "🧮 Pricing":
    # Redirection vers la page Pricing
    st.switch_page("pages/02_🧮_Pricing.py")

elif page == "📚 Guide BAM":
    # Affichage du guide BAM
    render_guide_bam()

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
render_footer()

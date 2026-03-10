# =============================================================================
# MASI Futures Pro — Page d'Accueil
# Version 0.3 — Pages Séparées
# =============================================================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions
from datetime import datetime

# Configuration (TOUJOURS EN PREMIER)
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personnalisé
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #d4dce6 100%);
    }
    .stApp > header {
        background: linear-gradient(90deg, #1E3A5F 0%, #2E5C8A 100%);
        box-shadow: 0 2px 8px rgba(30, 58, 95, 0.3);
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(30, 58, 95, 0.15);
        transition: all 0.3s ease;
    }
    .stButton>button {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%);
        color: white !important;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2E5C8A 0%, #3E7CAD 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Initialisation
update_statut_connexions()
render_sidebar()
render_header()

# Horloge Dynamique
st.components.v1.html("""
    <div style='padding: 15px; background: #f8fafc; border-radius: 8px; 
                margin-bottom: 20px; border-left: 4px solid #1E3A5F;'>
        <div style='display: flex; justify-content: space-between;'>
            <div>
                <p id='time' style='margin: 0; font-size: 1.5em; font-weight: bold; color: #1E3A5F;'></p>
                <p id='date' style='margin: 5px 0 0 0; color: #6B7280;'></p>
            </div>
            <div style='text-align: right;'>
                <p id='status' style='margin: 0; color: #10B981; font-weight: 600;'>Marché Ouvert</p>
            </div>
        </div>
    </div>
    <script>
    function update() {
        const now = new Date();
        document.getElementById('time').textContent = now.toLocaleTimeString('fr-FR');
        document.getElementById('date').textContent = now.toLocaleDateString('fr-FR', 
            {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'});
        const hour = now.getHours();
        const day = now.getDay();
        const statusEl = document.getElementById('status');
        if (day >= 1 && day <= 5 && hour >= 10 && hour < 15) {
            statusEl.textContent = '● Marché Ouvert';
            statusEl.style.color = '#10B981';
        } else {
            statusEl.textContent = '○ Marché Fermé';
            statusEl.style.color = '#6B7280';
        }
    }
    update();
    setInterval(update, 60000);
    </script>
""", height=100)

# Titre
st.title(f"Bienvenue sur {config.APP_NAME}")

# Objectif
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

# Actions Rapides
st.markdown("### 🚀 Accès Rapide aux Pages")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["primary"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>🧮</h3>
            <h4 style='margin: 10px 0;'>Pricing</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Prix théorique F₀ avec Term Structure
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["success"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>🛡️</h3>
            <h4 style='margin: 10px 0;'>Couverture</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Calcul N* pour hedging de portefeuille
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["warning"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>📊</h3>
            <h4 style='margin: 10px 0;'>Risques</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                VaR, P&L, marges et alertes
            </p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Guide BAM
with st.expander("📚 Instruction BAM N° IN-2026-01 — Résumé"):
    st.markdown("""
        ### 📐 Formule du Cours Théorique
        
        **F₀ = S × e^((r - d) × t)**
        
        | Variable | Signification | Source |
        |----------|---------------|--------|
        | **S** | Prix spot de l'indice | Bourse de Casablanca |
        | **r** | Taux sans risque | BKAM (fichier Excel) |
        | **d** | Taux de dividende | Calculé selon échéance |
        | **t** | Temps (jours/360) | Selon maturité du future |
        
        ### 📋 Hiérarchie des Cours de Clôture
        
        1. **Cours du fixing** (priorité)
        2. **Dernier cours traité** (si pas de fixing)
        3. **Cours théorique** (si pas de cours)
        
        *Conforme à l'Instruction Bank Al-Maghrib N° IN-2026-01*
    """)

# Footer
render_footer()

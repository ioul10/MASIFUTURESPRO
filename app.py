# =============================================================================
# MASI Futures Pro - Version Finale Corrigée
# Conforme Instruction BAM N° IN-2026-01
# Développeurs: OULMADANI Ilyas & ATANANE Oussama | v0.2 Beta
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS (TOUJOURS EN PREMIER)
# ─────────────────────────────────────────────────────────────────────────────
import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION DE LA PAGE (DOIT ÊTRE LA PREMIÈRE COMMANDE STREAMLIT)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS PERSONNALISÉ - DESIGN PROFESSIONNEL CDG
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    /* Arrière-plan global avec dégradé CDG Capital */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 50%, #d4dce6 100%);
    }
    
    /* Header personnalisé */
    .stApp > header {
        background: linear-gradient(90deg, #1E3A5F 0%, #2E5C8A 100%);
        box-shadow: 0 2px 8px rgba(30, 58, 95, 0.3);
    }
    
    /* Cards avec effet de survol */
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(30, 58, 95, 0.15);
        transition: all 0.3s ease;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 2px solid #e2e8f0;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%);
        color: white !important;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #2E5C8A 0%, #3E7CAD 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
update_statut_connexions()
render_sidebar()
render_header()

# ─────────────────────────────────────────────────────────────────────────────
# HORLOGE DYNAMIQUE (JavaScript - Mise à jour automatique)
# ─────────────────────────────────────────────────────────────────────────────
st.components.v1.html("""
    <div id='clock-container' style='padding: 15px 20px; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                                     border-radius: 12px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                                     border-left: 5px solid #1E3A5F;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <p id='current-date' style='margin: 0; font-size: 0.9em; color: #6B7280;'></p>
                <p id='current-time' style='margin: 5px 0 0 0; font-size: 1.5em; font-weight: 700; color: #1E3A5F;'></p>
            </div>
            <div style='text-align: right;'>
                <p id='market-status' style='margin: 0; font-size: 1.1em; font-weight: 700; color: #10B981;'>● Marché Ouvert</p>
                <p id='market-info' style='margin: 5px 0 0 0; font-size: 0.85em; color: #6B7280;'>Cotation en cours</p>
            </div>
        </div>
    </div>
    
    <script>
    function updateClock() {
        const now = new Date();
        
        // Date en français
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('current-date').textContent = now.toLocaleDateString('fr-FR', options);
        
        // Heure en français
        document.getElementById('current-time').textContent = now.toLocaleTimeString('fr-FR');
        
        // Statut du marché (Lundi-Vendredi, 10h-15h30)
        const day = now.getDay();
        const hour = now.getHours();
        const minute = now.getMinutes();
        const currentTime = hour + minute/60;
        
        let statusEl = document.getElementById('market-status');
        let infoEl = document.getElementById('market-info');
        
        if (day >= 1 && day <= 5 && currentTime >= 10 && currentTime < 15.5) {
            statusEl.innerHTML = '● Marché Ouvert';
            statusEl.style.color = '#10B981';
            infoEl.textContent = 'Cotation en cours';
        } else {
            statusEl.innerHTML = '○ Marché Fermé';
            statusEl.style.color = '#6B7280';
            
            // Calcul prochaine ouverture
            let nextOpen = new Date(now);
            if (day === 6 || day === 0 || currentTime >= 15.5) {
                nextOpen.setDate(now.getDate() + (1 - now.getDay() + 7) % 7 || 7);
                nextOpen.setHours(10, 0, 0, 0);
            } else {
                nextOpen.setHours(10, 0, 0, 0);
            }
            
            const optionsNext = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
            infoEl.textContent = 'Prochaine ouverture: ' + nextOpen.toLocaleDateString('fr-FR', optionsNext);
        }
    }
    
    updateClock();
    setInterval(updateClock, 1000);
    </script>
""", height=120)

# ─────────────────────────────────────────────────────────────────────────────
# CONTENU DE LA PAGE D'ACCUEIL
# ─────────────────────────────────────────────────────────────────────────────
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
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
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
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
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
        <div class='metric-card' style='padding: 25px; background: {config.COLORS["card"]}; 
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

# Guide BAM complet
with st.expander("📚 Instruction BAM N° IN-2026-01 — Modalités de détermination des cours de clôture"):
    st.markdown("""
        ### 📐 Formule du Cours Théorique (Article 2)
        
        **Cours théorique = S × e^((r-d)t)**
        
        | Variable | Signification | Source |
        |----------|---------------|--------|
        | **S** | Prix spot (cash) de l'indice | Bourse de Casablanca |
        | **r** | Taux d'intérêt sans risque | BKAM (Bons du Trésor) |
        | **d** | Taux de dividende de l'indice | Calculé : Σ(Pi × Di/Ci) |
        | **t** | Temps jusqu'à l'échéance (jours/360) | Tous jours inclus |
        
        ---
        
        ### 📋 Hiérarchie des Cours de Clôture (Article 1)
        
        1. **Cours du fixing de clôture** (priorité absolue)
        2. **Dernier cours traité** (si absence de fixing)
        3. **Cours théorique** (si absence de cours traité)
        
        ---
        
        ### 💰 Calcul du Taux de Dividende (Article 2)
        
        **Formule : d = Σ (Pi × Di / Ci)**
        
        | Symbole | Signification |
        |---------|---------------|
        | **i** | Les actions qui constituent l'indice |
        | **Di** | Dividende par action i |
        | **Ci** | Cours de l'action i |
        | **Pi** | Poids du titre i dans l'indice |
        
        ---
        
        ### 🎓 Fondement Théorique
        
        > **Principe d'absence d'opportunité d'arbitrage**  
        > À l'équilibre, aucun trader ne peut réaliser un profit sans risque 
        > en exploitant la différence entre le future et le spot.
        
        ---
        
        ### 🔢 Exemple Numérique
        
        S = 1 876.54, r = 3.5%, d = 2.8%, t = 90/360 = 0.25
        
        F₀ = 1 876.54 × e^((0.035-0.028)×0.25) = **1 879.82 points**
        
        Base = +3.28 points (+0.17%) → Contango léger
        
        ---
        
        *Conforme à l'Instruction Bank Al-Maghrib N° IN-2026-01*
    """)

# Footer
render_footer()

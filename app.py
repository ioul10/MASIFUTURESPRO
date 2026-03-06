# ============================================
# MASI Futures Pro - Version Finale
# Conforme Instruction BAM N° IN-2026-01
# ============================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions
from datetime import datetime

def show_splash_screen():
    """Affiche l'écran de chargement avec logo PNG"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style='
                text-align: center;
                padding: 60px 20px;
                background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(30, 58, 95, 0.3);
            '>
        """, unsafe_allow_html=True)
        
        # Afficher le logo PNG
        try:
            st.image("logo.png", width=250, use_container_width=False)
        except:
            st.markdown("<div style='font-size: 5em;'>📈</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <h1 style='
                color: white;
                font-size: 2.5em;
                margin: 30px 0 10px 0;
                font-weight: 700;
                text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            '>
                {config.APP_NAME}
            </h1>
            
            <p style='
                color: rgba(255,255,255,0.9);
                font-size: 1.2em;
                margin: 10px 0 30px 0;
            '>
                v{config.APP_VERSION}
            </p>
            
            <div style='
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            '>
                <p style='
                    color: rgba(255,255,255,0.8);
                    font-size: 0.9em;
                    animation: pulse 1.5s infinite;
                '>
                    🔍 Initialisation des connexions...<br>
                    📊 Chargement des données de marché...<br>
                    ✅ Prêt !
                </p>
            </div>
            
            <p style='
                color: rgba(255,255,255,0.6);
                margin-top: 20px;
                font-size: 0.8em;
            '>
                Développé par OULMADANI Ilyas & ATANANE Oussama
            </p>
            
            </div>
            
            <style>
                @keyframes pulse {
                    0%, 100% { opacity: 0.6; }
                    50% { opacity: 1; }
                }
            </style>
        """, unsafe_allow_html=True)

# =============================================================================
# INITIALISATION DE L'APPLICATION
# =============================================================================

# Afficher l'écran de chargement
show_splash_screen()

# Attendre 3 secondes (simulation de chargement)
import time
time.sleep(3)

# Maintenant afficher le vrai contenu
st.empty()  # Effacer l'écran de chargement

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────
# CSS PERSONNALISÉ - DESIGN PROFESSIONNEL CDG
# ────────────────────────────────────────────
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

update_statut_connexions()

render_sidebar()

# ────────────────────────────────────────────
# HORLOGE DYNAMIQUE (Auto-refresh JavaScript)
# ────────────────────────────────────────────
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
        
        // Date
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('current-date').textContent = now.toLocaleDateString('fr-FR', options);
        
        // Heure
        document.getElementById('current-time').textContent = now.toLocaleTimeString('fr-FR');
        
        // Statut du marché (Lundi-Vendredi, 10h-15h30)
        const day = now.getDay(); // 0=Dimanche, 1=Lundi, ..., 6=Samedi
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
                // Weekend ou après 15h30 → Lundi prochain
                nextOpen.setDate(now.getDate() + (1 - now.getDay() + 7) % 7 || 7);
                nextOpen.setHours(10, 0, 0, 0);
            } else {
                // Avant 10h → Aujourd'hui
                nextOpen.setHours(10, 0, 0, 0);
            }
            
            const optionsNext = { weekday: 'long', hour: '2-digit', minute: '2-digit' };
            infoEl.textContent = 'Prochaine ouverture: ' + nextOpen.toLocaleDateString('fr-FR', optionsNext);
        }
    }
    
    updateClock();
    setInterval(updateClock, 1000); // Mise à jour chaque seconde
    </script>
""", height=120)

# ────────────────────────────────────────────
# CONTENU DE LA PAGE D'ACCUEIL
# ────────────────────────────────────────────
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

# ────────────────────────────────────────────
# GUIDE COMPLET - INSTRUCTION BAM N° IN-2026-01
# ────────────────────────────────────────────
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
        
        Le cours de clôture est déterminé selon la hiérarchie suivante :
        
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
        
        **Exemple pratique :**
        - Pour le MASI20 : somme sur les 20 constituants
        - Utiliser les poids officiels de l'indice
        - Dividendes annuels attendus
        
        ---
        
        ### 🎓 Fondement Théorique
        
        > **Principe d'absence d'opportunité d'arbitrage**  
        > À l'équilibre du marché, aucun trader ne peut réaliser un profit sans risque 
        > en exploitant la différence entre le future et le spot.
        
        **Stratégies d'arbitrage :**
        
        - **Si Prix Marché > Cours Théorique** : Vendre Future + Acheter Spot
        - **Si Prix Marché < Cours Théorique** : Acheter Future + Vendre Spot
        - **À l'équilibre** : Prix Marché = Cours Théorique
        
        ---
        
        ### 🔢 Exemple Numérique Complet
        
        **Données MASI20 :**
        - S = 1 876.54 points (spot)
        - r = 3.5% = 0.035 (taux BKAM)
        - d = 2.8% = 0.028 (dividend yield)
        - Jours restants = 90
        - t = 90/360 = 0.25
        
        **Calcul :**
        ```
        F₀ = 1 876.54 × e^((0.035 - 0.028) × 0.25)
           = 1 876.54 × e^(0.00175)
           = 1 876.54 × 1.001751
           = 1 879.82 points
        ```
        
        **Base :** 1 879.82 - 1 876.54 = **+3.28 points (+0.17%)**
        
        ---
        
        ### 📖 Références Réglementaires
        
        - **Dahir N°1-14-96** du 20 Rejeb 1435 (20 Mai 2014)  
          Loi n°42-12 relative au marché à terme d'instruments financiers (Article 9)
          
        - **Règlement Général** de la société gestionnaire du marché à terme  
          Approuvé par l'arrêté n°2582-22 du 27 septembre 2022 (Article 58)
        
        ---
        
        *Conforme à l'Instruction Bank Al-Maghrib N° IN-2026-01*  
        *Application à usage professionnel et éducatif*
    """)

# Footer
render_footer()



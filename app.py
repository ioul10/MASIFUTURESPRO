import streamlit.components.v1 as components 
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

# Horloge Dynamique — Version Corrigée
horloge_html = """
<div style='padding: 20px; background: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%); 
            border-radius: 12px; margin-bottom: 25px; 
            border-left: 5px solid #1E3A5F;
            box-shadow: 0 4px 12px rgba(30,58,95,0.1);'>
    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
        <div style='flex: 1; min-width: 200px;'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                📅 Date Actuelle
            </p>
            <p id='date' style='margin: 5px 0 0 0; font-size: 1.3em; font-weight: 600; color: #1E3A5F;'>
                --/--/----
            </p>
        </div>
        
        <div style='flex: 1; min-width: 200px; text-align: center;'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                🕐 Heure
            </p>
            <p id='time' style='margin: 5px 0 0 0; font-size: 2.5em; font-weight: 700; 
                               color: #1E3A5F; font-family: monospace; letter-spacing: 2px;'>
                --:--:--
            </p>
        </div>
        
        <div style='flex: 1; min-width: 200px; text-align: right;'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280; text-transform: uppercase; letter-spacing: 1px;'>
                📊 État du Marché
            </p>
            <p id='status' style='margin: 10px 0 0 0; font-size: 1.2em; font-weight: 600; color: #6B7280;'>
                ○ Vérification...
            </p>
            <p id='next-session' style='margin: 5px 0 0 0; font-size: 0.85em; color: #9CA3AF;'>
                --
            </p>
        </div>
    </div>
    
    <div style='margin-top: 15px; background: #e5e7eb; border-radius: 10px; height: 8px; overflow: hidden;'>
        <div id='progress-bar' style='width: 0%; height: 100%; 
                                      background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
                                      transition: width 1s ease;'></div>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    
    const dateOptions = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    document.getElementById('date').textContent = now.toLocaleDateString('fr-FR', dateOptions);
    
    const timeString = now.toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    document.getElementById('time').textContent = timeString;
    
    const day = now.getDay();
    const hour = now.getHours();
    const minute = now.getMinutes();
    const currentTime = hour + minute / 60;
    
    const statusEl = document.getElementById('status');
    const nextSessionEl = document.getElementById('next-session');
    const progressBar = document.getElementById('progress-bar');
    
    if (day >= 1 && day <= 5) {
        const marketOpen = 10.0;
        const marketClose = 15.5;
        
        if (currentTime >= marketOpen && currentTime < marketClose) {
            statusEl.innerHTML = '● Marché Ouvert';
            statusEl.style.color = '#10B981';
            
            const progress = ((currentTime - marketOpen) / (marketClose - marketOpen)) * 100;
            progressBar.style.width = progress + '%';
            progressBar.style.background = 'linear-gradient(90deg, #10B981 0%, #34D399 100%)';
            
            nextSessionEl.textContent = 'Fermeture dans ' + Math.ceil(marketClose - currentTime) + 'h';
        } else if (currentTime < marketOpen) {
            statusEl.innerHTML = '○ Marché Fermé';
            statusEl.style.color = '#F59E0B';
            progressBar.style.width = '0%';
            
            const hoursUntilOpen = marketOpen - currentTime;
            nextSessionEl.textContent = 'Ouverture dans ' + hoursUntilOpen.toFixed(1) + 'h';
        } else {
            statusEl.innerHTML = '○ Marché Fermé';
            statusEl.style.color = '#6B7280';
            progressBar.style.width = '100%';
            progressBar.style.background = 'linear-gradient(90deg, #6B7280 0%, #9CA3AF 100%)';
            
            const nextOpen = new Date(now);
            nextOpen.setDate(now.getDate() + 1);
            if (nextOpen.getDay() === 6) nextOpen.setDate(nextOpen.getDate() + 1);
            if (nextOpen.getDay() === 0) nextOpen.setDate(nextOpen.getDate() + 1);
            nextSessionEl.textContent = 'Prochaine séance: ' + nextOpen.toLocaleDateString('fr-FR', {weekday: 'long', day: 'numeric', month: 'short'});
        }
    } else {
        statusEl.innerHTML = '○ Week-end';
        statusEl.style.color = '#6B7280';
        progressBar.style.width = '0%';
        
        const nextOpen = new Date(now);
        nextOpen.setDate(now.getDate() + (1 - now.getDay() + 7) % 7 || 7);
        nextSessionEl.textContent = 'Reprise: ' + nextOpen.toLocaleDateString('fr-FR', {weekday: 'long', day: 'numeric', month: 'short'}) + ' à 10h00';
    }
}

updateClock();
setInterval(updateClock, 1000);
</script>
"""

st.components.v1.html(horloge_html, height=180)

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

# =============================================================================
# BANDEAU DÉVELOPPEMENT EN COURS
# =============================================================================
st.markdown("""
    <div class='dev-banner'>
        <div style='display: flex; align-items: center; gap: 15px; flex-wrap: wrap;'>
            <div style='font-size: 2.5em;'>🚧</div>
            <div style='flex: 1;'>
                <h3 style='margin: 0; color: #92400e;'>⚠️ Application en Développement</h3>
                <p style='margin: 10px 0 0 0; color: #78350f; line-height: 1.6;'>
                    Cette application est actuellement en <strong>phase de test et développement</strong>. 
                    Certaines fonctionnalités peuvent être incomplètes ou en cours d'amélioration.
                </p>
                <p style='margin: 10px 0 0 0; color: #78350f; font-size: 0.9em;'>
                    📅 <strong>Version actuelle :</strong> v0.4 Beta &nbsp;|&nbsp; 
                    🎯 <strong>Statut :</strong> Module de Pricing Opérationnel
                </p>
            </div>
            <div style='text-align: right; min-width: 150px;'>
                <p style='margin: 0; font-size: 0.85em; color: #92400e;'>Prochaine mise à jour</p>
                <p style='margin: 5px 0 0 0; font-weight: bold; color: #78350f;'>Semaine 1</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Footer
render_footer()     








# ============================================
# SIDEBAR - MASI Futures Pro
# Version Professionnelle avec Animation
# ============================================

import streamlit as st
import config
import time
from datetime import datetime

def render_sidebar():
    """Affiche la sidebar avec animation de chargement"""
    
    with st.sidebar:
        # ────────────────────────────────────────
        # ANIMATION DE CHARGEMENT (Première ouverture)
        # ────────────────────────────────────────
        if 'sidebar_initialized' not in st.session_state:
            # Étape 1: Vérification des données
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Vérification des connexions...")
            time.sleep(0.5)
            progress_bar.progress(33)
            
            status_text.text("📊 Connexion à BKAM...")
            time.sleep(0.5)
            progress_bar.progress(66)
            
            status_text.text("🏦 Connexion à la Bourse de Casablanca...")
            time.sleep(0.5)
            progress_bar.progress(100)
            
            status_text.text("✅ Prêt !")
            time.sleep(0.3)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state['sidebar_initialized'] = True
        
        # ────────────────────────────────────────
        # LOGO & TITRE (Style CDG Capital)
        # ────────────────────────────────────────
        st.markdown(f"""
            <div style='
                text-align: center;
                padding: 25px 15px;
                background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
            '>
                <!-- Logo CDG Capital (Emoji stylisé) -->
                <div style='
                    font-size: 3em;
                    margin-bottom: 10px;
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
                '>
                    📊
                </div>
                
                <h1 style='
                    font-size: 1.6em;
                    margin: 0;
                    color: white;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                '>
                    {config.APP_NAME}
                </h1>
                
                <p style='
                    color: rgba(255,255,255,0.9);
                    margin: 8px 0 0 0;
                    font-size: 0.9em;
                    font-weight: 500;
                '>
                    v{config.APP_VERSION}
                </p>
                
                <div style='
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid rgba(255,255,255,0.3);
                    font-size: 0.75em;
                    color: rgba(255,255,255,0.8);
                '>
                    Conforme BAM IN-2026-01
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # ────────────────────────────────────────
        # STATUT DES DONNÉES (Avec animation)
        # ────────────────────────────────────────
        st.markdown("### 🔗 Statut des Données")
        
        statut_bkam = st.session_state.get('statut_bkam', '🟢')
        statut_bourse = st.session_state.get('statut_bourse', '🟢')
        statut_news = st.session_state.get('statut_news', '🟢')
        
        # Style amélioré pour le statut
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid {config.COLORS["primary"]};
                margin-bottom: 20px;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-size: 1.2em; margin-right: 8px;'>{statut_bkam}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f;'>BKAM (Taux)</span>
                </div>
                <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                    <span style='font-size: 1.2em; margin-right: 8px;'>{statut_bourse}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f;'>Bourse de Casablanca</span>
                </div>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 1.2em; margin-right: 8px;'>{statut_news}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f;'>News (Ilboursa)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # ────────────────────────────────────────
        # NAVIGATION
        # ────────────────────────────────────────
        st.markdown("### 🧭 Navigation")
        
        # Sélecteur d'indice
        indice_defaut = st.selectbox(
            "🇲🇦 Indice de Référence",
            config.INDICES,
            index=0,
            help="Sélectionnez l'indice pour le calcul"
        )
        st.session_state['indice_defaut'] = indice_defaut
        
        # Info multiplicateur
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                margin: 15px 0;
                border-left: 4px solid {config.COLORS["warning"]};
            '>
                <p style='margin: 0; font-size: 0.9em; color: #92400e;'>
                    <strong>Multiplicateur:</strong><br>
                    <span style='font-size: 1.3em; color: #78350f;'>
                        {config.MULTIPLICATEUR} MAD/point
                    </span>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # ────────────────────────────────────────
        # LIENS RAPIDES
        # ────────────────────────────────────────
        st.markdown("### 📚 Ressources")
        
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                padding: 12px;
                border-radius: 8px;
                margin: 10px 0;
            '>
                <a href='#' style='
                    display: block;
                    padding: 8px 12px;
                    color: {config.COLORS["primary"]};
                    text-decoration: none;
                    border-radius: 6px;
                    margin-bottom: 5px;
                    transition: all 0.2s;
                ' onmouseover="this.style.background='#e0f2fe'" onmouseout="this.style.background='transparent'">
                    📘 Guide BAM IN-2026-01
                </a>
                <a href='#' style='
                    display: block;
                    padding: 8px 12px;
                    color: {config.COLORS["primary"]};
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.2s;
                ' onmouseover="this.style.background='#e0f2fe'" onmouseout="this.style.background='transparent'">
                    📖 Formules de Pricing
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        # ────────────────────────────────────────
        # INFO APPLICATION
        # ────────────────────────────────────────
        st.divider()
        
        st.markdown(f"""
            <div style='
                text-align: center;
                padding: 15px;
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                border-radius: 8px;
                margin: 10px 0;
            '>
                <p style='
                    margin: 0;
                    font-size: 0.8em;
                    color: #166534;
                    line-height: 1.6;
                '>
                    <strong>Basé sur:</strong><br>
                    Document CDG Capital<br>
                    Marché à Terme Marocain
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Footer sidebar
        st.markdown(f"""
            <div style='
                text-align: center;
                font-size: 0.75em;
                color: {config.COLORS["text_muted"]};
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
            '>
                © 2026 MASI Futures Pro<br>
                <span style='color: {config.COLORS["primary"]}; font-weight: 600;'>
                    Conforme Instruction BAM
                </span>
            </div>
        """, unsafe_allow_html=True)

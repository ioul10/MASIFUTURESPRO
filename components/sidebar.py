# ============================================
# SIDEBAR - MASI Futures Pro
# Version Professionnelle V.0.2 Beta
# Développeurs: OULMADANI Ilyas & ATANANE Oussama
# ============================================

import streamlit as st
import config
import time
from datetime import datetime

def render_sidebar():
    """Affiche la sidebar avec animation de chargement"""
    
    with st.sidebar:
        # ────────────────────────────────────────
        # ANIMATION DE CHARGEMENT
        # ────────────────────────────────────────
        if 'sidebar_initialized' not in st.session_state:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Vérification des connexions...")
            time.sleep(0.4)
            progress_bar.progress(25)
            
            status_text.text("📊 Connexion à BKAM (Taux)...")
            time.sleep(0.4)
            progress_bar.progress(50)
            
            status_text.text("🏦 Connexion Bourse de Casablanca...")
            time.sleep(0.4)
            progress_bar.progress(75)
            
            status_text.text("✅ Application prête !")
            time.sleep(0.3)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state['sidebar_initialized'] = True
        
        # ────────────────────────────────────────
        # EN-TÊTE DE L'APPLICATION (Correction ici)
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
                <div style='font-size: 3em; margin-bottom: 10px;'>📈</div>
                
                <h1 style='
                    font-size: 1.5em;
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
                    font-size: 0.95em;
                    font-weight: 600;
                    background: rgba(255,255,255,0.15);
                    padding: 4px 12px;
                    border-radius: 20px;
                    display: inline-block;
                '>
                    v0.2 Beta
                </p>
                
                <div style='
                    margin-top: 12px;
                    padding-top: 12px;
                    border-top: 1px solid rgba(255,255,255,0.3);
                    font-size: 0.75em;
                    color: rgba(255,255,255,0.85);
                '>
                    Conforme BAM IN-2026-01
                </div>
            </div>
        """, unsafe_allow_html=True)  # ← CE PARAMÈTRE EST ESSENTIEL !
        
        # Le reste du code...
        st.divider()
        
        st.markdown("### 🔗 Statut des Données")
        
        statut_bkam = st.session_state.get('statut_bkam', '🟢')
        statut_bourse = st.session_state.get('statut_bourse', '🟢')
        statut_news = st.session_state.get('statut_news', '🟢')
        
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid {config.COLORS["primary"]};
                margin-bottom: 20px;
            '>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 1.3em; margin-right: 10px;'>{statut_bkam}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f; font-weight: 500;'>BKAM (Taux)</span>
                </div>
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <span style='font-size: 1.3em; margin-right: 10px;'>{statut_bourse}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f; font-weight: 500;'>Bourse de Casablanca</span>
                </div>
                <div style='display: flex; align-items: center;'>
                    <span style='font-size: 1.3em; margin-right: 10px;'>{statut_news}</span>
                    <span style='font-size: 0.9em; color: #1e3a5f; font-weight: 500;'>News (Ilboursa)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 🧭 Navigation")
        
        indice_defaut = st.selectbox(
            "🇲🇦 Indice de Référence",
            config.INDICES,
            index=0
        )
        st.session_state['indice_defaut'] = indice_defaut
        
        st.info(f"💰 Multiplicateur: **{config.MULTIPLICATEUR} MAD/point**")
        
        st.divider()
        st.markdown("### 👥 Développeurs")
        
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                border-left: 4px solid {config.COLORS["success"]};
            '>
                <div style='margin-bottom: 10px;'>
                    <span style='font-size: 1.2em;'>👤</span>
                    <span style='margin-left: 8px; color: #1e3a5f; font-weight: 600;'>
                        OULMADANI Ilyas
                    </span>
                </div>
                <div>
                    <span style='font-size: 1.2em;'>👤</span>
                    <span style='margin-left: 8px; color: #1e3a5f; font-weight: 600;'>
                        ATANANE Oussama
                    </span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📚 Ressources")
        
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                padding: 12px;
                border-radius: 8px;
                margin: 10px 0;
                border-left: 4px solid {config.COLORS["warning"]};
            '>
                <p style='margin: 0; font-size: 0.85em; color: #92400e; line-height: 1.6;'>
                    <strong>📖 Basé sur:</strong><br>
                    Document CDG Capital<br>
                    Marché à Terme Marocain
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        current_year = datetime.now().year
        
        st.markdown(f"""
            <div style='
                text-align: center;
                font-size: 0.75em;
                color: {config.COLORS["text_muted"]};
                margin-top: 20px;
                padding-top: 15px;
                border-top: 1px solid #e2e8f0;
                line-height: 1.6;
            '>
                © {current_year} MASI Futures Pro<br>
                <span style='color: {config.COLORS["primary"]}; font-weight: 600;'>
                    Conforme Instruction BAM N° IN-2026-01
                </span><br>
                <span style='color: #9ca3af;'>
                    Usage professionnel et éducatif
                </span>
            </div>
        """, unsafe_allow_html=True)

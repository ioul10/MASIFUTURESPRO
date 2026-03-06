# ============================================
# SIDEBAR - MASI Futures Pro
# Version Finale V.0.2 Beta
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
            
            status_text.text("📊 Connexion à BKAM...")
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
        # EN-TÊTE (Simple et Propre)
        # ────────────────────────────────────────
        st.markdown(f"""
            <div style='text-align: center; padding: 20px 0;'>
                <div style='font-size: 3em; margin-bottom: 10px;'>📈</div>
                <h1 style='font-size: 1.8em; margin: 0; color: {config.COLORS["primary"]}; font-weight: 700;'>
                    {config.APP_NAME}
                </h1>
                <p style='color: {config.COLORS["text_muted"]}; margin: 8px 0; font-size: 0.95em; font-weight: 600;'>
                    v0.2 Beta
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # ────────────────────────────────────────
        # STATUT DES DONNÉES
        # ────────────────────────────────────────
        st.markdown("### 🔗 Statut des Données")
        
        statut_bkam = st.session_state.get('statut_bkam', '🟢')
        statut_bourse = st.session_state.get('statut_bourse', '🟢')
        statut_news = st.session_state.get('statut_news', '🟢')
        
        st.write(f"{statut_bkam} **BKAM** (Taux)")
        st.write(f"{statut_bourse} **Bourse de Casablanca**")
        st.write(f"{statut_news} **News** (Ilboursa)")
        
        st.divider()
        
        # ────────────────────────────────────────
        # NAVIGATION
        # ────────────────────────────────────────
        st.markdown("### 🧭 Navigation")
        
        indice_defaut = st.selectbox(
            "🇲🇦 Indice de Référence",
            config.INDICES,
            index=0
        )
        st.session_state['indice_defaut'] = indice_defaut
        
        st.info(f"💰 Multiplicateur: **{config.MULTIPLICATEUR} MAD/point**")
        
        st.divider()
        
        # ────────────────────────────────────────
        # DÉVELOPPEURS
        # ────────────────────────────────────────
        st.markdown("### 👥 Développeurs")
        
        st.write("**👤 OULMADANI Ilyas**")
        st.write("**👤 ATANANE Oussama**")
        
        st.divider()
        
        # ────────────────────────────────────────
        # INFORMATIONS
        # ────────────────────────────────────────
        st.markdown("### 📚 Informations")
        
        st.write("📖 **Basé sur:**")
        st.write("Document CDG Capital")
        st.write("Marché à Terme Marocain")
        
        st.divider()
        
        # Footer
        current_year = datetime.now().year
        st.caption(f"© {current_year} MASI Futures Pro")
        st.caption("Conforme Instruction BAM N° IN-2026-01")

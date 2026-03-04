# ============================================
# SIDEBAR COMPONENT - MASI Futures Pro
# Navigation + Statut Connexions
# ============================================

import streamlit as st
import config

def render_sidebar():
    """
    Affiche la sidebar avec :
    - Logo + Nom + Version
    - Statut des connexions (BKAM, Bourse, News)
    - Navigation entre les pages
    - Settings rapides
    """
    
    with st.sidebar:
        # Logo et Nom (Version compacte)
        st.markdown(f"""
            <div style='text-align: center; padding: 20px 0;'>
                <h1 style='font-size: 2em; margin: 0; color: {config.COLORS["primary"]};'>
                    📈 {config.APP_NAME}
                </h1>
                <p style='color: {config.COLORS["text_muted"]}; margin: 5px 0;'>
                    v{config.APP_VERSION}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Statut des Connexions
        st.markdown("### 🔗 Statut des Données")
        
        # Ces statuts seront mis à jour dynamiquement plus tard
        # Pour l'instant, on affiche des indicateurs statiques
        statut_bkam = st.session_state.get('statut_bkam', '🟢')
        statut_bourse = st.session_state.get('statut_bourse', '🟢')
        statut_news = st.session_state.get('statut_news', '🟢')
        
        st.markdown(f"""
            <div style='font-size: 0.9em; line-height: 1.8;'>
                {statut_bkam} BKAM (Taux)<br>
                {statut_bourse} Bourse de Casablanca<br>
                {statut_news} News (Ilboursa)
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "Pages",
            ["🏠 Accueil", "🧮 Pricing", "📊 Indices"],
            label_visibility="collapsed",
            index=0
        )
        
        st.divider()
        
        # Settings Rapides
        st.markdown("### ⚙️ Settings")
        
        # Indice par défaut
        indice_defaut = st.selectbox(
            "Indice",
            config.INDICES,
            index=0
        )
        st.session_state['indice_defaut'] = indice_defaut
        
        # Multiplicateur (info seulement)
        st.info(f"Multiplicateur: {config.MULTIPLICATEUR} MAD/pt")
        
        st.divider()
        
        # Footer Sidebar
        st.markdown(f"""
            <div style='text-align: center; font-size: 0.75em; color: {config.COLORS["text_muted"]};'>
                © 2026 MASI Futures Pro<br>
                Basé sur document CDG Capital
            </div>
        """, unsafe_allow_html=True)
    
    return page
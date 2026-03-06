# ============================================
# SIDEBAR - MASI Futures Pro
# Version avec Logo PNG
# ============================================

import streamlit as st
import config
import time

def render_sidebar():
    """Affiche la sidebar avec logo"""
    
    with st.sidebar:
        # ────────────────────────────────────────
        # ANIMATION DE CHARGEMENT
        # ────────────────────────────────────────
        if 'sidebar_initialized' not in st.session_state:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔍 Vérification des connexions...")
            time.sleep(0.3)
            progress_bar.progress(33)
            
            status_text.text("📊 Connexion à BKAM...")
            time.sleep(0.3)
            progress_bar.progress(66)
            
            status_text.text("✅ Prêt !")
            time.sleep(0.2)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state['sidebar_initialized'] = True
        
        # ────────────────────────────────────────
        # LOGO CDG CAPITAL (PNG)
        # ────────────────────────────────────────
        
        # Option 1: Si tu as un fichier logo.png
        try:
            st.image(
                "assets/logo_cdg.png",  # Chemin vers ton logo
                use_container_width=True,
                output_format="PNG"
            )
        except:
            # Fallback: Emoji si logo non trouvé
            st.markdown(f"""
                <div style='
                    text-align: center;
                    font-size: 4em;
                    margin: 20px 0;
                    padding: 20px;
                    background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
                '>
                    📊
                </div>
            """, unsafe_allow_html=True)
        
        # Titre de l'application
        st.markdown(f"""
            <div style='
                text-align: center;
                margin: 15px 0;
                padding: 15px;
                background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(30, 58, 95, 0.2);
            '>
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
        """, unsafe_allow_html=True)  # ← ICI LE PARAMÈTRE IMPORTANT !
        
        st.divider()
        
        # ────────────────────────────────────────
        # STATUT DES DONNÉES
        # ────────────────────────────────────────
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
            '>
                <div style='margin-bottom: 8px;'>
                    <span style='font-size: 1.2em;'>{statut_bkam}</span>
                    <span style='margin-left: 8px; color: #1e3a5f;'>BKAM (Taux)</span>
                </div>
                <div style='margin-bottom: 8px;'>
                    <span style='font-size: 1.2em;'>{statut_bourse}</span>
                    <span style='margin-left: 8px; color: #1e3a5f;'>Bourse de Casablanca</span>
                </div>
                <div>
                    <span style='font-size: 1.2em;'>{statut_news}</span>
                    <span style='margin-left: 8px; color: #1e3a5f;'>News (Ilboursa)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
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
        
        st.info(f"💰 Multiplicateur: {config.MULTIPLICATEUR} MAD/pt")
        
        st.divider()
        
        # Footer
        st.markdown(f"""
            <div style='
                text-align: center;
                font-size: 0.75em;
                color: {config.COLORS["text_muted"]};
                margin-top: 20px;
            '>
                © 2026 MASI Futures Pro<br>
                Basé sur document CDG Capital
            </div>
        """, unsafe_allow_html=True)

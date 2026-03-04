import streamlit as st
import config

def render_sidebar():
    """Affiche la sidebar"""
    
    with st.sidebar:
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
        
        st.markdown("### 🔗 Statut des Données")
        
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
        
        st.markdown("### 🧭 Navigation")
        
        indice_defaut = st.selectbox("Indice", config.INDICES, index=0)
        st.session_state['indice_defaut'] = indice_defaut
        
        st.info(f"Multiplicateur: {config.MULTIPLICATEUR} MAD/pt")
        
        st.divider()
        
        st.markdown(f"""
            <div style='text-align: center; font-size: 0.75em; color: {config.COLORS["text_muted"]};'>
                © 2026 MASI Futures Pro<br>
                Basé sur document CDG Capital
            </div>
        """, unsafe_allow_html=True)

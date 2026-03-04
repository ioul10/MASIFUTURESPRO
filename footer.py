# ============================================
# FOOTER COMPONENT - MASI Futures Pro
# ============================================

import streamlit as st
from datetime import datetime
import config

def render_footer():
    """Affiche un footer professionnel et discret"""
    
    st.divider()
    
    st.markdown(f"""
        <div style='
            text-align: center;
            padding: 30px 20px;
            color: {config.COLORS["text_muted"]};
            font-size: 0.85em;
            line-height: 1.6;
        '>
            <p style='margin: 0 0 10px 0;'>
                <strong style='color: {config.COLORS["primary"]};'>{config.APP_NAME}</strong> 
                v{config.APP_VERSION}
            </p>
            <p style='margin: 0 0 10px 0;'>
                Basé sur le document "Introduction des Contrats Futures sur les Indices MASI et MASI20"<br>
                CDG Capital — Marché à Terme Marocain
            </p>
            <p style='margin: 0; opacity: 0.7;'>
                © {datetime.now().year} — Application à usage professionnel et éducatif
            </p>
        </div>
    """, unsafe_allow_html=True)
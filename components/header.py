# ============================================
# HEADER - MASI Futures Pro
# Version Originale (Avant Animation)
# ============================================

import streamlit as st
import config
from datetime import datetime

def render_header():
    """Affiche le header de l'application"""
    
    # Header simple et propre
    st.markdown(f"""
        <div style='
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
            box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
        '>
            <h1 style='
                margin: 0;
                color: white;
                font-size: 2em;
                font-weight: 700;
            '>
                📊 {config.APP_NAME}
            </h1>
            <p style='
                margin: 10px 0 0 0;
                color: rgba(255,255,255,0.9);
                font-size: 1em;
            '>
                Plateforme de Pricing des Futures MASI/MASI20
            </p>
        </div>
    """, unsafe_allow_html=True)

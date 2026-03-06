# ============================================
# HEADER - MASI Futures Pro
# En-tête professionnel sans horloge dupliquée
# ============================================

import streamlit as st
import config
from datetime import datetime

def render_header():
    """Affiche le header de l'application"""
    
    # Header principal avec dégradé CDG Capital
    st.markdown(f"""
        <div style='
            padding: 25px 30px;
            margin-bottom: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, {config.COLORS["primary"]} 0%, {config.COLORS["secondary"]} 100%);
            box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
        '>
            <div>
                <h1 style='
                    margin: 0;
                    color: white;
                    font-size: 1.8em;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
                '>
                    📊 {config.APP_NAME}
                </h1>
                <p style='
                    margin: 8px 0 0 0;
                    color: rgba(255,255,255,0.9);
                    font-size: 1em;
                '>
                    Plateforme de Pricing des Futures MASI/MASI20
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    



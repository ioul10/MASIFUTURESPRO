# ============================================
# HEADER - MASI Futures Pro
# Version Corrigée - Affichage Propre
# ============================================

import streamlit as st
import config
from datetime import datetime

def render_header():
    """Affiche le header de l'application"""
    
    # Header principal - Version simplifiée et robuste
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
    """, unsafe_allow_html=True)  # ← IMPORTANT: Ce paramètre est obligatoire !
    
    # Barre d'information marché (optionnelle - simplifiée)
    st.markdown(f"""
        <div style='
            padding: 12px 20px;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;
            border-left: 4px solid {config.COLORS["primary"]};
        '>
            <p style='
                margin: 0;
                font-size: 0.95em;
                color: #1e3a5f;
                font-weight: 600;
            '>
                🇲🇦 Bourse de Casablanca — Marché à Terme
            </p>
            <p style='
                margin: 5px 0 0 0;
                font-size: 0.85em;
                color: #64748b;
            '>
                Indices : MASI • MASI20 | Multiplicateur : {config.MULTIPLICATEUR} MAD/point
            </p>
        </div>
    """, unsafe_allow_html=True)  # ← IMPORTANT: Ce paramètre est obligatoire !

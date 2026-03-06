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
            
            <div style='text-align: right;'>
                <p style='
                    margin: 0;
                    color: rgba(255,255,255,0.85);
                    font-size: 0.9em;
                    font-weight: 500;
                '>
                    Conforme BAM IN-2026-01
                </p>
                <p style='
                    margin: 5px 0 0 0;
                    color: rgba(255,255,255,0.7);
                    font-size: 0.8em;
                '>
                    v{config.APP_VERSION}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Barre d'information contextuelle (optionnelle)
    st.markdown(f"""
        <div style='
            padding: 12px 20px;
            margin-bottom: 25px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 8px;
            border-left: 4px solid {config.COLORS["primary"]};
            display: flex;
            align-items: center;
            gap: 15px;
        '>
            <span style='font-size: 1.5em;'>🇲🇦</span>
            <div>
                <p style='margin: 0; font-size: 0.95em; color: #1e3a5f; font-weight: 600;'>
                    Bourse de Casablanca — Marché à Terme
                </p>
                <p style='margin: 3px 0 0 0; font-size: 0.85em; color: #64748b;'>
                    Indices : MASI • MASI20 | Multiplicateur : {config.MULTIPLICATEUR} MAD/point
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

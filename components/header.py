# ============================================
# HEADER COMPONENT - MASI Futures Pro
# Statut Marché + Date/Heure
# ============================================

import streamlit as st
from datetime import datetime
import config

def render_header(marche_ouvert=False):
    """
    Affiche le header avec :
    - Statut du marché (Ouvert/Fermé)
    - Date et heure actuelles
    - Dernière mise à jour des données
    """
    
    # Date et heure actuelles
    now = datetime.now()
    date_str = now.strftime("%A %d %B %Y")
    heure_str = now.strftime("%H:%M:%S")
    
    # Déterminer si le marché est ouvert (simplifié)
    # En production, vérifier les heures réelles de la Bourse de Casa
    jour_semaine = now.weekday()  # 0=Lundi, 6=Dimanche
    heure_actuelle = now.hour
    
    # Heures de cotation Bourse de Casablanca: 10:00 - 15:30
    marche_ouvert = (
        jour_semaine < 5 and  # Lundi à Vendredi
        10 <= heure_actuelle < 15.5  # 10:00 à 15:30
    )
    
    # Statut visuel
    if marche_ouvert:
        statut_color = config.COLORS['success']
        statut_text = "🟢 Marché Ouvert"
        statut_msg = "Cotation en cours"
    else:
        statut_color = config.COLORS['text_muted']
        statut_text = "⚪ Marché Fermé"
        statut_msg = "Prochaine ouverture: Lundi 10:00" if jour_semaine >= 5 else f"Demain 10:00"
    
    # Affichage du header
    st.markdown(f"""
        <div style='
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: linear-gradient(135deg, {config.COLORS["card"]} 0%, #f8fafc 100%);
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-left: 5px solid {statut_color};
        '>
            <div>
                <p style='margin: 0; font-size: 0.9em; color: {config.COLORS["text_muted"]};'>
                    {date_str}
                </p>
                <p style='margin: 5px 0 0 0; font-size: 1.3em; font-weight: 600; color: {config.COLORS["text"]};'>
                    {heure_str}
                </p>
            </div>
            
            <div style='text-align: right;'>
                <p style='margin: 0; font-size: 1.1em; font-weight: 700; color: {statut_color};'>
                    {statut_text}
                </p>
                <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {config.COLORS["text_muted"]};'>
                    {statut_msg}
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    return marche_ouvert

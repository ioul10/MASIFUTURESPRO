import streamlit as st
from datetime import datetime
import config

def render_header(marche_ouvert=False):
    """Affiche le header"""
    
    now = datetime.now()
    date_str = now.strftime("%A %d %B %Y")
    heure_str = now.strftime("%H:%M:%S")
    
    jour_semaine = now.weekday()
    heure_actuelle = now.hour
    
    marche_ouvert = (
        jour_semaine < 5 and
        10 <= heure_actuelle < 15.5
    )
    
    if marche_ouvert:
        statut_color = config.COLORS['success']
        statut_text = "🟢 Marché Ouvert"
        statut_msg = "Cotation en cours"
    else:
        statut_color = config.COLORS['text_muted']
        statut_text = "⚪ Marché Fermé"
        statut_msg = "Prochaine ouverture: Lundi 10:00" if jour_semaine >= 5 else f"Demain 10:00"
    
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

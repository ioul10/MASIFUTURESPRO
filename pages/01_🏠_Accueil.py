import streamlit as st
import config

st.title(f"Bienvenue sur {config.APP_NAME}")

st.markdown(f"""
    <div style='padding: 30px; background: linear-gradient(135deg, {config.COLORS["card"]} 0%, #f8fafc 100%); 
                border-radius: 16px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
        <h2 style='color: {config.COLORS["primary"]}; margin-top: 0;'>🎯 Objectif</h2>
        <p style='font-size: 1.1em; line-height: 1.8;'>
            {config.APP_NAME} est une plateforme professionnelle de pricing des contrats futures 
            sur les indices <strong>MASI</strong> et <strong>MASI20</strong>.
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

st.markdown("### 🚀 Actions Rapides")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["primary"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>🧮</h3>
            <h4 style='margin: 10px 0;'>Pricing</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Calculez le prix théorique F₀
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["success"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>📊</h3>
            <h4 style='margin: 10px 0;'>Indices</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                Niveaux MASI & MASI20
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='padding: 25px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-top: 4px solid {config.COLORS["warning"]};'>
            <h3 style='font-size: 2.5em; margin: 0;'>📰</h3>
            <h4 style='margin: 10px 0;'>Actualités</h4>
            <p style='color: {config.COLORS["text_muted"]};'>
                News du marché
            </p>
        </div>
    """, unsafe_allow_html=True)

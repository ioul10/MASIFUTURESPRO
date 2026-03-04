# ============================================
# PAGE 1: NEWS & INDICES - MASI Futures Pro
# ============================================

import streamlit as st
import config
from utils.scraping import get_indices_bourse
from components.news_widget import render_news_widget
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.title("📰 Actualités & Indices MASI")

# ────────────────────────────────────────────
# NIVEAUX DES INDICES
# ────────────────────────────────────────────
st.markdown("### 📊 Niveaux Actuels des Indices")

indices_data = get_indices_bourse()

if indices_data:
    col1, col2 = st.columns(2)
    
    for idx_name, idx_data in indices_data.items():
        with col1 if idx_name == 'MASI' else col2:
            couleur_variation = config.COLORS["success"] if "+" in idx_data["variation"] else config.COLORS["danger"]
            
            st.markdown(f"""
                <div style='padding: 25px; background: {config.COLORS["card"]}; 
                            border-radius: 12px; margin-bottom: 15px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                            border-left: 5px solid {config.COLORS["primary"]};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h3 style='margin: 0 0 10px 0; color: {config.COLORS["primary"]};'>
                                🇲 {idx_data['nom']}
                            </h3>
                            <p style='margin: 0; font-size: 2em; font-weight: 700; 
                                      color: {config.COLORS["text"]};'>
                                {idx_data['niveau']:,.2f}
                            </p>
                        </div>
                        <div style='text-align: right;'>
                            <p style='margin: 0; font-size: 1.3em; font-weight: 600; 
                                      color: {couleur_variation};'>
                                {idx_data['variation']}
                            </p>
                            <p style='margin: 5px 0 0 0; color: {config.COLORS["text_muted"]}; 
                                      font-size: 0.85em;'>
                                {idx_data['timestamp']}
                            </p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("❌ Impossible de récupérer les données des indices")

st.divider()


# ────────────────────────────────────────────
# GRAPHIQUE PLOTLY - MASI
# ────────────────────────────────────────────
st.markdown("### 📈 Évolution du MASI")

import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Données simulées (à remplacer par scraping réel plus tard)
dates = [datetime.now() - timedelta(days=i) for i in range(90)]
dates.reverse()

# Génération de prix simulés réalistes
np.random.seed(42)
base_price = 16655.58  # Niveau actuel approximatif
returns = np.random.normal(0.0001, 0.015, 90)  # Rendements journaliers
prices = base_price * np.exp(np.cumsum(returns))
prices = prices * (base_price / prices[-1])  # Ajuster au niveau actuel

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=prices,
    name='MASI',
    line=dict(color='#10B981', width=2),
    fill='tozeroy',
    fillcolor='rgba(16, 185, 129, 0.1)',
    hovertemplate='<b>%{x|%d %b %Y}</b><br>Prix: %{y:,.2f}<extra></extra>'
))

# Ligne de référence
fig.add_hline(
    y=base_price,
    line_dash="dash",
    line_color="#1E3A5F",
    annotation_text=f"Niveau actuel: {base_price:,.2f}",
    annotation_position="top right"
)

fig.update_layout(
    title='Évolution du MASI sur 90 jours',
    xaxis_title='Date',
    yaxis_title='Niveau de l\'indice',
    hovermode='x unified',
    height=500,
    template='plotly_white',
    xaxis=dict(
        showgrid=True,
        gridcolor='#E5E7EB'
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#E5E7EB',
        tickformat=',.0f'
    )
)

st.plotly_chart(fig, use_container_width=True)

# Statistiques
col1, col2, col3, col4 = st.columns(4)

variation_90j = ((prices[-1] - prices[0]) / prices[0]) * 100
plus_haut = max(prices)
plus_bas = min(prices)

with col1:
    st.metric("Variation (90j)", f"{variation_90j:+.2f}%", 
              delta=f"{prices[-1] - prices[0]:+.0f} pts")

with col2:
    st.metric("Plus Haut", f"{plus_haut:,.2f} pts")

with col3:
    st.metric("Plus Bas", f"{plus_bas:,.2f} pts")

with col4:
    st.metric("Volatilité", f"{np.std(returns)*100:.2f}%")

st.divider()
# ────────────────────────────────────────────
# CARACTÉRISTIQUES DES CONTRATS
# ────────────────────────────────────────────
st.markdown("### 📋 Caractéristiques des Contrats Futures")

specs = pd.DataFrame({
    "Paramètre": ["Sous-jacent", "Multiplicateur", "Règlement", "Échéances", "Devise", "Tick Size"],
    "Valeur": [
        "MASI / MASI20",
        f"{config.MULTIPLICATEUR} MAD/point",
        "Cash settlement (règlement en espèces)",
        "Mensuelles / Trimestrielles",
        config.DEVISE,
        "0.01 point"
    ]
})

st.dataframe(specs, use_container_width=True, hide_index=True)

st.divider()

# ────────────────────────────────────────────
# ACTUALITÉS
# ────────────────────────────────────────────
render_news_widget(max_news=5)

# ────────────────────────────────────────────
# INFO BOX
# ────────────────────────────────────────────
st.markdown(f"""
    <div style='padding: 20px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                border-left: 5px solid {config.COLORS["primary"]};
                border-radius: 12px; margin: 20px 0;'>
        <strong>💡 Le saviez-vous ?</strong><br>
        Le MASI (Moroccan All Shares Index) représente la performance de l'ensemble des actions 
        cotées à la Bourse de Casablanca, tandis que le MASI20 se concentre sur les 20 valeurs 
        les plus liquides du marché. Les contrats futures permettent de se couvrir contre les 
        variations de ces indices ou de spéculer sur leur évolution future.
    </div>
""", unsafe_allow_html=True)

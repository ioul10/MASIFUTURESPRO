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
# GRAPHIQUES PLOTLY - MASI & MASI20
# ────────────────────────────────────────────
st.markdown("### 📈 Évolution des Indices")

import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# Données simulées MASI
dates_masi = [datetime.now() - timedelta(days=i) for i in range(90)]
dates_masi.reverse()
np.random.seed(42)
base_masi = 16655.58
returns_masi = np.random.normal(0.0001, 0.015, 90)
prices_masi = base_masi * np.exp(np.cumsum(returns_masi))
prices_masi = prices_masi * (base_masi / prices_masi[-1])

# Données simulées MASI20
dates_masi20 = [datetime.now() - timedelta(days=i) for i in range(90)]
dates_masi20.reverse()
np.random.seed(43)
base_masi20 = 1876.54
returns_masi20 = np.random.normal(0.0001, 0.018, 90)
prices_masi20 = base_masi20 * np.exp(np.cumsum(returns_masi20))
prices_masi20 = prices_masi20 * (base_masi20 / prices_masi20[-1])

# ────────────────────────────────────────────
# GRAPHIQUE MASI
# ────────────────────────────────────────────
st.markdown("#### 🇲🇦 MASI - Moroccan All Shares Index")

fig_masi = go.Figure()

fig_masi.add_trace(go.Scatter(
    x=dates_masi,
    y=prices_masi,
    name='MASI',
    line=dict(color='#10B981', width=2),
    fill='tozeroy',
    fillcolor='rgba(16, 185, 129, 0.1)',
    hovertemplate='<b>%{x|%d %b %Y}</b><br>Prix: %{y:,.2f}<extra></extra>'
))

fig_masi.add_hline(
    y=base_masi,
    line_dash="dash",
    line_color="#1E3A5F",
    annotation_text=f"Niveau actuel: {base_masi:,.2f}",
    annotation_position="top right"
)

fig_masi.update_layout(
    title='Évolution du MASI sur 90 jours',
    xaxis_title='Date',
    yaxis_title='Niveau de l\'indice',
    hovermode='x unified',
    height=450,
    template='plotly_white',
    xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
    yaxis=dict(showgrid=True, gridcolor='#E5E7EB', tickformat=',.0f')
)

st.plotly_chart(fig_masi, use_container_width=True)

# Stats MASI
col1, col2, col3, col4 = st.columns(4)
variation_masi = ((prices_masi[-1] - prices_masi[0]) / prices_masi[0]) * 100

with col1:
    st.metric("Variation (90j)", f"{variation_masi:+.2f}%", 
              delta=f"{prices_masi[-1] - prices_masi[0]:+.0f} pts")
with col2:
    st.metric("Plus Haut", f"{max(prices_masi):,.2f} pts")
with col3:
    st.metric("Plus Bas", f"{min(prices_masi):,.2f} pts")
with col4:
    st.metric("Volatilité", f"{np.std(returns_masi)*100:.2f}%")

st.divider()

# ────────────────────────────────────────────
# GRAPHIQUE MASI20
# ────────────────────────────────────────────
st.markdown("#### 🇲🇦 MASI20 - Top 20 Capitalisation")

fig_masi20 = go.Figure()

fig_masi20.add_trace(go.Scatter(
    x=dates_masi20,
    y=prices_masi20,
    name='MASI20',
    line=dict(color=config.COLORS['primary'], width=2),
    fill='tozeroy',
    fillcolor='rgba(30, 58, 95, 0.1)',
    hovertemplate='<b>%{x|%d %b %Y}</b><br>Prix: %{y:,.2f}<extra></extra>'
))

fig_masi20.add_hline(
    y=base_masi20,
    line_dash="dash",
    line_color="#1E3A5F",
    annotation_text=f"Niveau actuel: {base_masi20:,.2f}",
    annotation_position="top right"
)

fig_masi20.update_layout(
    title='Évolution du MASI20 sur 90 jours',
    xaxis_title='Date',
    yaxis_title='Niveau de l\'indice',
    hovermode='x unified',
    height=450,
    template='plotly_white',
    xaxis=dict(showgrid=True, gridcolor='#E5E7EB'),
    yaxis=dict(showgrid=True, gridcolor='#E5E7EB', tickformat=',.0f')
)

st.plotly_chart(fig_masi20, use_container_width=True)

# Stats MASI20
col1, col2, col3, col4 = st.columns(4)
variation_masi20 = ((prices_masi20[-1] - prices_masi20[0]) / prices_masi20[0]) * 100

with col1:
    st.metric("Variation (90j)", f"{variation_masi20:+.2f}%", 
              delta=f"{prices_masi20[-1] - prices_masi20[0]:+.0f} pts")
with col2:
    st.metric("Plus Haut", f"{max(prices_masi20):,.2f} pts")
with col3:
    st.metric("Plus Bas", f"{min(prices_masi20):,.2f} pts")
with col4:
    st.metric("Volatilité", f"{np.std(returns_masi20)*100:.2f}%")

st.divider()

# ────────────────────────────────────────────
# COMPARAISON CÔTE À CÔTE
# ────────────────────────────────────────────
st.markdown("### 📊 Comparaison MASI vs MASI20")

# Normaliser pour comparaison
masi_normalized = [p / prices_masi[0] * 100 for p in prices_masi]
masi20_normalized = [p / prices_masi20[0] * 100 for p in prices_masi20]

fig_compare = go.Figure()

fig_compare.add_trace(go.Scatter(
    x=dates_masi,
    y=masi_normalized,
    name='MASI',
    line=dict(color='#10B981', width=2)
))

fig_compare.add_trace(go.Scatter(
    x=dates_masi20,
    y=masi20_normalized,
    name='MASI20',
    line=dict(color=config.COLORS['primary'], width=2, dash='dash')
))

fig_compare.update_layout(
    title='Performance Relative (Base 100)',
    xaxis_title='Date',
    yaxis_title='Performance (%)',
    hovermode='x unified',
    height=400,
    template='plotly_white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_compare, use_container_width=True)
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

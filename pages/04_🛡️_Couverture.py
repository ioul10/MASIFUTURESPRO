# =============================================================================
# PAGE 4: COUVERTURE DE PORTEFEUILLE — MASI Futures Pro
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from utils.calculations import calculer_beta, calculer_N_star

st.set_page_config(page_title="Couverture", page_icon="🛡️", layout="wide")
st.title("🛡️ Couverture de Portefeuille — Calcul de N*")

# Guide
with st.expander("📘 Guide — Couverture", expanded=True):
    st.markdown("""
        ### 🎯 Objectif
        Calculer le nombre optimal de contrats futures pour couvrir un portefeuille.
        
        ### 📐 Formule
        **N* = β × P / A**
        
        | Symbole | Signification |
        |---------|---------------|
        | **β** | Beta du portefeuille vs MASI20 |
        | **P** | Valeur du portefeuille (MAD) |
        | **A** | Valeur d'un contrat = Prix Future × 10 |
        
        ### 📁 Format d'Import
        `ticker, quantité, prix_achat`
    """)

st.divider()

# ─────────────────────────────────────────────────────────────────────────
# 1. IMPORT DU PORTEFEUILLE
# ─────────────────────────────────────────────────────────────────────────
st.markdown("### 📥 1. Import du Portefeuille")

uploaded_pf = st.file_uploader("Importer votre portefeuille (CSV)", type=['csv'])

if uploaded_pf:
    df_pf = pd.read_csv(uploaded_pf)
    st.success(f"✅ {len(df_pf)} lignes chargées")
    st.dataframe(df_pf.head(), use_container_width=True)
else:
    # Données de démo
    df_pf = pd.DataFrame({
        'ticker': ['ATW', 'BCP', 'IAM'],
        'quantité': [1000, 5000, 2000],
        'prix_achat': [485.0, 142.5, 128.0]
    })
    st.info("ℹ️ Données de démonstration utilisées")

# Calcul de la valeur du portefeuille
valeur_portefeuille = (df_pf['quantité'] * df_pf['prix_achat']).sum()
st.metric("💰 Valeur Totale du Portefeuille", f"{valeur_portefeuille:,.0f} MAD")

st.divider()

# ─────────────────────────────────────────────────────────────────────────
# 2. PARAMÈTRES DE COUVERTURE
# ─────────────────────────────────────────────────────────────────────────
st.markdown("### ⚙️ 2. Paramètres")

col1, col2 = st.columns(2)

with col1:
    prix_future = st.number_input("Prix Future MASI20", value=1876.54, step=10.0)
    multiplicateur = st.number_input("Multiplicateur (MAD/point)", value=10, disabled=True)
    
with col2:
    beta_input = st.number_input("Beta (β) — Optionnel", value=0.98, step=0.01, 
                                  help="Laisser vide pour calcul automatique")

# Calcul du Beta si pas fourni
if beta_input == 0.98:  # Valeur par défaut
    # Simulation : générer des rendements corrélés
    np.random.seed(42)
    rendements_masi = np.random.normal(0.0002, 0.012, 60)
    rendements_pf = rendements_masi * 0.98 + np.random.normal(0, 0.003, 60)
    beta_calcule = calculer_beta(rendements_pf, rendements_masi)
    beta_final = beta_calcule
    st.info(f"📊 Beta calculé automatiquement : **{beta_final:.3f}**")
else:
    beta_final = beta_input

st.divider()

# ─────────────────────────────────────────────────────────────────────────
# 3. RÉSULTAT N*
# ─────────────────────────────────────────────────────────────────────────
st.markdown("### 🎯 3. Nombre Optimal de Contrats (N*)")

if st.button("🧮 Calculer N*", type="primary", use_container_width=True):
    # Calcul N*
    valeur_contrat = prix_future * multiplicateur
    N_star = calculer_N_star(beta_final, valeur_portefeuille, prix_future, multiplicateur)
    
    # Affichage
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div style='padding:25px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                        border-radius:12px; text-align:center; color:white;'>
                <p style='margin:0; font-size:0.9em;'>🎯 Contrats à Vendre</p>
                <p style='margin:10px 0 0 0; font-size:2.5em; font-weight:700;'>{N_star:,}</p>
                <p style='margin:5px 0 0 0; font-size:0.85em;'>contrats MASI20</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Valeur d'un Contrat", f"{valeur_contrat:,.0f} MAD")
    
    with col3:
        notionnel_couvert = N_star * valeur_contrat
        st.metric("Notionnel Couvert", f"{notionnel_couvert:,.0f} MAD")
    
    # Formule détaillée
    st.info(f"""
        **Calcul :** N* = β × P / A = {beta_final:.3f} × {valeur_portefeuille:,.0f} / {valeur_contrat:,.0f} = **{N_star:,} contrats**
    """)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # 4. SIMULATION WHAT-IF
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("### 🧪 4. Simulation d'Impact")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scenario = st.slider("Variation du MASI20 (%)", -20.0, 20.0, -5.0, 1.0)
    
    with col2:
        # Calcul impact
        impact_non_couvert = valeur_portefeuille * (scenario / 100) * beta_final
        impact_couvert = impact_non_couvert + (N_star * multiplicateur * prix_future * (scenario / 100) * -1)
        protection = (1 - abs(impact_couvert) / abs(impact_non_couvert)) * 100 if impact_non_couvert != 0 else 100
        
        st.metric("Impact sans Couverture", f"{impact_non_couvert:,.0f} MAD", 
                 delta=f"{scenario*beta_final:.1f}%")
        st.metric("Impact avec Couverture", f"{impact_couvert:,.0f} MAD",
                 delta=f"{impact_couvert/impact_non_couvert*100-100:+.1f}%" if impact_non_couvert != 0 else "0%")
    
    # Barre de protection
    st.markdown(f"""
        <div style='padding:15px; background:#ecfdf5; border-radius:8px; margin:10px 0;'>
            <p style='margin:0; font-weight:600; color:#065f46;'>
                🛡️ Protection du portefeuille : {protection:.1f}%
            </p>
            <div style='background:#d1fae5; border-radius:4px; height:8px; margin-top:8px;'>
                <div style='background:#10B981; width:{min(protection,100)}%; height:100%; border-radius:4px; transition:width 0.3s;'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Graphique de corrélation
    st.markdown("### 📊 Corrélation Portefeuille vs MASI20")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rendements_masi * 100,
        y=rendements_pf * 100,
        mode='markers',
        name='Points',
        marker=dict(color='#1E3A5F', size=6, opacity=0.6)
    ))
    # Droite de régression
    x_line = np.array([-2, 2])
    y_line = beta_final * x_line
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode='lines',
        name=f'Beta = {beta_final:.3f}',
        line=dict(color='#F59E0B', width=2)
    ))
    fig.update_layout(
        title='Rendements Portefeuille vs MASI20',
        xaxis_title='MASI20 (%)',
        yaxis_title='Portefeuille (%)',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("💡 Conseil : Réévaluer N* régulièrement car le Beta évolue dans le temps")

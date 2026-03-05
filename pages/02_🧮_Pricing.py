# ────────────────────────────────────────────
# ONGLET: BETA DE PORTEFEUILLE & CALCUL N*
# ────────────────────────────────────────────

import streamlit as st
from utils.portfolio_builder import (
    get_masi20_constituents,
    generer_historique_prix,
    generer_historique_masi20
)
from utils.calculations import (
    calculer_beta,
    calculer_correlation,
    calculer_tracking_error,
    calculer_alpha,
    calculer_N_star
)
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from scipy import stats

st.title("🛡️ Couverture avec Futures MASI20")

st.markdown("""
    Calcul du Beta d'un portefeuille répliquant le MASI20 et du nombre optimal 
    de contrats futures (N*) pour la couverture.
""")

# Initialiser session state
if 'poids_modifiables' not in st.session_state:
    st.session_state['poids_modifiables'] = False
    st.session_state['constituents'] = get_masi20_constituents()
    st.session_state['historique_constituents'] = generer_historique_prix(
        st.session_state['constituents'], 
        jours=90
    )
    st.session_state['historique_masi20'] = generer_historique_masi20(
        st.session_state['historique_constituents'],
        st.session_state['constituents']
    )

constituents = st.session_state['constituents']
historique_constituents = st.session_state['historique_constituents']
historique_masi20 = st.session_state['historique_masi20']

# ────────────────────────────────────────────
# TABLEAU DES CONSTITUANTS
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📋 Constituants MASI20 et Poids")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("Composition actuelle du MASI20")

with col2:
    if st.button("✏️ Modifier les poids"):
        st.session_state['poids_modifiables'] = not st.session_state['poids_modifiables']
        st.rerun()

# Afficher le tableau
df_constituents = pd.DataFrame(constituents)
df_constituents['poids'] = df_constituents['poids'] * 100  # En pourcentage

if st.session_state['poids_modifiables']:
    edited_df = st.data_editor(
        df_constituents,
        column_config={
            "poids": st.column_config.NumberColumn(
                "Poids (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.2f"
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    total_poids = edited_df['poids'].sum()
    if total_poids > 0:
        edited_df['poids'] = edited_df['poids'] / total_poids * 100
        
        for idx, constituant in enumerate(st.session_state['constituents']):
            constituant['poids'] = edited_df.iloc[idx]['poids'] / 100
else:
    st.dataframe(
        df_constituents.style.format({'poids': '{:.2f}%'}),
        use_container_width=True,
        hide_index=True
    )

st.caption(f"📅 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ────────────────────────────────────────────
# CALCULS
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Paramètres de Couverture")

col1, col2, col3 = st.columns(3)

with col1:
    valeur_portefeuille = st.number_input(
        "💰 Valeur du portefeuille (MAD)",
        min_value=100_000,
        value=10_000_000,
        step=100_000
    )

with col2:
    prix_future_masi20 = st.number_input(
        "Prix Future MASI20",
        min_value=1000.0,
        value=historique_masi20['prix'][-1],
        step=50.0
    )

with col3:
    multiplicateur = 10

# Calcul des rendements du portefeuille
rendements_portefeuille = np.zeros(89)
for constituant in constituents:
    ticker = constituant['ticker']
    poids = constituant['poids']
    returns = historique_constituents[ticker]['returns'][1:]
    rendements_portefeuille += poids * returns

rendements_masi20 = historique_masi20['returns'][1:]

# Calculs statistiques
beta = calculer_beta(rendements_portefeuille, rendements_masi20)
correlation = calculer_correlation(rendements_portefeuille, rendements_masi20)
tracking_error = calculer_tracking_error(rendements_portefeuille, rendements_masi20)
alpha = calculer_alpha(rendements_portefeuille, rendements_masi20)
N_star = calculer_N_star(beta, valeur_portefeuille, prix_future_masi20, multiplicateur)

# ────────────────────────────────────────────
# RÉSULTATS
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Résultats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Beta", f"{beta:.4f}", f"{beta-1:+.4f} vs MASI20")

with col2:
    st.metric("Corrélation", f"{correlation:.4f}")

with col3:
    st.metric("Tracking Error", f"{tracking_error:.2f}%")

with col4:
    st.metric("Alpha", f"{alpha:+.2f}%")

# N* en évidence
st.divider()
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
        <div style='padding: 30px; background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%); 
                    border-radius: 12px; text-align: center; color: white;'>
            <p style='margin: 0; font-size: 1.1em;'>Nombre optimal de contrats N*</p>
            <p style='margin: 15px 0 0 0; font-size: 3.5em; font-weight: 800;'>{N_star:,}</p>
            <p style='margin: 10px 0 0 0;'>contrats</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    A = prix_future_masi20 * multiplicateur
    st.markdown(f"""
        **Formule:** N* = β × P / A
        
        β = {beta:.4f}  
        P = {valeur_portefeuille:,.0f} MAD  
        A = {A:,.0f} MAD
        
        **N* = {N_star:,} contrats**
    """)

# ────────────────────────────────────────────
# GRAPHIQUE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Corrélation Portefeuille vs MASI20")

slope, intercept, r_value, p_value, std_err = stats.linregress(rendements_masi20, rendements_portefeuille)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=rendements_masi20 * 100,
    y=rendements_portefeuille * 100,
    mode='markers',
    name='Rendements',
    marker=dict(size=6, color=config.COLORS['primary'], opacity=0.6)
))

x_line = np.array([min(rendements_masi20), max(rendements_masi20)])
y_line = slope * x_line + intercept

fig.add_trace(go.Scatter(
    x=x_line * 100,
    y=y_line * 100,
    mode='lines',
    name=f'Régression (R²={r_value**2:.4f})',
    line=dict(color='#10B981', width=2)
))

fig.update_layout(
    title='Rendements Quotidiens',
    xaxis_title='MASI20 (%)',
    yaxis_title='Portefeuille (%)',
    height=400,
    template='plotly_white'
)

st.plotly_chart(fig, use_container_width=True)

# ────────────────────────────────────────────
# GUIDE
# ────────────────────────────────────────────
with st.expander("📘 Guide Méthodologique"):
    st.markdown("""
        ### Formule N* = β × P / A
        
        - **β** = Beta du portefeuille (sensibilité au MASI20)
        - **P** = Valeur du portefeuille
        - **A** = Prix Future × Multiplicateur
        
        ### Interprétation
        
        - **Beta ≈ 1** : Portefeuille réplique bien l'indice
        - **Corrélation > 0.95** : Forte corrélation
        - **Tracking Error faible** : Bonne réplication
        
        Pour couvrir: **Vendre N* contrats futures**
    """)

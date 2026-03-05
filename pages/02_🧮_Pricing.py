# ============================================
# PAGE 2: PRICING - MASI Futures Pro
# Version avec Onglets
# ============================================

import streamlit as st
import config
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

# Configuration de la page
st.title("🧮 Pricing & Couverture")

# ────────────────────────────────────────────
# CRÉATION DES ONGLETS
# ────────────────────────────────────────────
tab1, tab2 = st.tabs(["🛡️ Calcul de N* (Beta)", "📊 Pricing Théorique"])

# ════════════════════════════════════════════
# ONGLET 1: CALCUL DE N* AVEC BETA
# ════════════════════════════════════════════
with tab1:
    st.markdown("""
        Calcul du nombre optimal de contrats futures (N*) pour couvrir un portefeuille
        en utilisant le Beta calculé à partir des constituants du MASI20.
    """)
    
    # ────────────────────────────────────────
    # INITIALISATION DES DONNÉES
    # ────────────────────────────────────────
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
        st.session_state['date_calcul'] = datetime.now()
    
    constituents = st.session_state['constituents']
    historique_constituents = st.session_state['historique_constituents']
    historique_masi20 = st.session_state['historique_masi20']
    
    # ────────────────────────────────────────
    # TABLEAU DES POIDS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 1. Constituants MASI20 et Pondérations")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown("Poids des actions dans le MASI20 (utilisés pour construire le portefeuille)")
    
    with col2:
        if st.button("✏️ Modifier les poids", use_container_width=True):
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
        
        # Normaliser les poids
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
    
    st.caption(f"📅 Date de calcul des poids: {st.session_state['date_calcul'].strftime('%d/%m/%Y %H:%M')}")
    
    if st.button("🔄 Actualiser les données"):
        st.session_state['historique_constituents'] = generer_historique_prix(
            st.session_state['constituents'], 
            jours=90
        )
        st.session_state['historique_masi20'] = generer_historique_masi20(
            st.session_state['historique_constituents'],
            st.session_state['constituents']
        )
        st.session_state['date_calcul'] = datetime.now()
        st.rerun()
    
    # ────────────────────────────────────────
    # PARAMÈTRES DE COUVERTURE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💰 2. Paramètres du Portefeuille")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        valeur_portefeuille = st.number_input(
            "Valeur du portefeuille à couvrir (MAD)",
            min_value=100_000,
            value=10_000_000,
            step=100_000
        )
    
    with col2:
        prix_future = st.number_input(
            "Prix Future MASI20 (points)",
            min_value=1000.0,
            value=historique_masi20['prix'][-1],
            step=50.0
        )
    
    with col3:
        multiplicateur = config.MULTIPLICATEUR
        st.info(f"Multiplicateur: {multiplicateur} MAD/point")
    
    # ────────────────────────────────────────
    # CALCULS
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🧮 3. Calculs Statistiques")
    
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
    
    # Calcul de N*
    N_star = calculer_N_star(beta, valeur_portefeuille, prix_future, multiplicateur)
    
    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Beta (β)",
            f"{beta:.4f}",
            delta=f"{beta-1:+.4f} vs MASI20"
        )
    
    with col2:
        st.metric(
            "Corrélation",
            f"{correlation:.4f}"
        )
    
    with col3:
        st.metric(
            "Tracking Error",
            f"{tracking_error:.2f}%"
        )
    
    with col4:
        st.metric(
            "Alpha (annualisé)",
            f"{alpha:+.2f}%"
        )
    
    # ────────────────────────────────────────
    # RÉSULTAT N*
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🎯 4. Nombre Optimal de Contrats (N*)")
    
    if st.button("🧮 Calculer N*", type="primary", use_container_width=True):
        A = prix_future * multiplicateur
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
                <div style='padding: 40px; background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%); 
                            border-radius: 16px; text-align: center; color: white;
                            box-shadow: 0 8px 24px rgba(30, 58, 95, 0.3);'>
                    <p style='margin: 0; font-size: 1.2em; opacity: 0.9;'>
                        Nombre optimal de contrats futures MASI20
                    </p>
                    <p style='margin: 20px 0 0 0; font-size: 4em; font-weight: 800;'>
                        {N_star:,}
                    </p>
                    <p style='margin: 10px 0 0 0; font-size: 1.1em; opacity: 0.8;'>
                        contrats à vendre pour couvrir
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                **Détails du calcul :**
                
                | Paramètre | Valeur |
                |-----------|--------|
                | Beta (β) | {beta:.4f} |
                | Valeur portefeuille (P) | {valeur_portefeuille:,.0f} MAD |
                | Prix Future | {prix_future:,.0f} pts |
                | Multiplicateur | {multiplicateur} MAD/pt |
                | Valeur notionnelle (A) | {A:,.0f} MAD |
                
                ---
                **Formule :**
                
                ```
                N* = β × P / A
                
                N* = {beta:.4f} × {valeur_portefeuille:,.0f} / {A:,.0f}
                
                N* = {N_star:,} contrats
                ```
            """)
    
    # ────────────────────────────────────────
    # GRAPHIQUE DE CORRÉLATION
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📈 5. Corrélation Portefeuille vs MASI20")
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(rendements_masi20, rendements_portefeuille)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rendements_masi20 * 100,
        y=rendements_portefeuille * 100,
        mode='markers',
        name='Rendements journaliers',
        marker=dict(size=8, color=config.COLORS['primary'], opacity=0.6)
    ))
    
    x_line = np.array([min(rendements_masi20), max(rendements_masi20)])
    y_line = slope * x_line + intercept
    
    fig.add_trace(go.Scatter(
        x=x_line * 100,
        y=y_line * 100,
        mode='lines',
        name=f'Ligne de régression (R²={r_value**2:.4f})',
        line=dict(color='#10B981', width=3)
    ))
    
    fig.update_layout(
        title='Rendements Quotidiens: Portefeuille vs MASI20',
        xaxis_title='Rendement MASI20 (%)',
        yaxis_title='Rendement Portefeuille (%)',
        height=450,
        template='plotly_white',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("R²", f"{r_value**2:.4f}")
    with col2:
        st.metric("Pente", f"{slope:.4f}")
    with col3:
        st.metric("Erreur Std", f"{std_err:.6f}")
    
    # ────────────────────────────────────────
    # GUIDE MÉTHODOLOGIQUE
    # ────────────────────────────────────────
    st.divider()
    with st.expander("📘 Guide Méthodologique Complet"):
        st.markdown("""
            ### 🎯 Objectif
            
            Déterminer le nombre optimal de contrats futures MASI20 (N*) pour couvrir un portefeuille 
            d'actions marocaines contre le risque de marché.
            
            ---
            
            ### 📐 Formule de N*
            
            **N* = β × P / A**
            
            | Symbole | Signification |
            |---------|---------------|
            | **N*** | Nombre optimal de contrats futures |
            | **β** | Beta du portefeuille par rapport au MASI20 |
            | **P** | Valeur du portefeuille à couvrir (MAD) |
            | **A** | Valeur notionnelle d'un contrat = Prix Future × Multiplicateur |
            
            ---
            
            ### 🔍 Qu'est-ce que le Beta ?
            
            Le **Beta (β)** mesure la sensibilité du portefeuille aux variations du MASI20.
            
            | Valeur | Interprétation |
            |--------|----------------|
            | β = 1 | Le portefeuille évolue comme l'indice |
            | β > 1 | Plus volatil que l'indice (risque élevé) |
            | β < 1 | Moins volatil que l'indice (risque faible) |
            
            **Calcul :**
            ```
            β = Cov(R_portefeuille, R_MASI20) / Var(R_MASI20)
            ```
            
            ---
            
            ### 📊 Méthodologie
            
            1. **Constituants MASI20** : 20 actions les plus liquides
            2. **Pondération** : Poids officiels de l'indice
            3. **Historique** : 90 jours de données
            4. **Rendements** : Calcul des rendements journaliers
            5. **Régression** : Beta par régression linéaire
            
            ---
            
            ### 📈 Interprétation
            
            | Métrique | Interprétation |
            |----------|----------------|
            | **Corrélation** | Proche de 1 = Forte corrélation positive |
            | **Tracking Error** | Faible = Bonne réplication de l'indice |
            | **Alpha** | Surperformance vs le benchmark |
            
            ---
            
            ### ⚠️ Limites
            
            - Beta calculé sur 90 jours historiques
            - Corrélation passée ≠ corrélation future
            - Coûts de transaction non inclus
            - Rééquilibrage périodique nécessaire
            
            ---
            
            ### 💡 Exemple
            
            Portefeuille: 10 000 000 MAD  
            Beta: 0.98  
            Prix Future: 1 876 pts  
            Multiplicateur: 10 MAD/pt  
            
            N* = 0.98 × 10 000 000 / (1 876 × 10) = **522 contrats**
            
            **Action : Vendre 522 contrats futures MASI20**
        """)

# ════════════════════════════════════════════
# ONGLET 2: PRICING THÉORIQUE
# ════════════════════════════════════════════
with tab2:
    st.markdown("""
        Calcul du prix théorique d'un future sur indice selon la formule de coût de portage.
    """)
    
    st.info("🚧 Section en cours de développement...")
    
    # Tu pourras ajouter le pricing théorique ici plus tard

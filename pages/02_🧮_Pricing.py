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
# ONGLET 3: ÉVOLUTION DU BETA
# ════════════════════════════════════════════
with tab3:
    st.markdown("""
        Analyse de l'évolution du Beta selon différentes périodes de calcul.
        Permet d'évaluer la stabilité du Beta dans le temps.
    """)
    
    # ────────────────────────────────────────
    # PÉRIODES À TESTER
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 1. Configuration des Périodes")
    
    periodes = st.multiselect(
        "Sélectionnez les périodes de calcul (en jours)",
        options=[30, 60, 90, 120, 180, 252],
        default=[30, 60, 90, 120]
    )
    
    if not periodes:
        st.warning("⚠️ Sélectionnez au moins une période")
        st.stop()
    
    # ────────────────────────────────────────
    # CALCUL DU BETA POUR CHAQUE PÉRIODE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🧮 2. Calcul du Beta par Période")
    
    results_beta = []
    
    for jours in sorted(periodes):
        # Régénérer l'historique pour cette période
        historique_temp = generer_historique_prix(constituents, jours=jours)
        masi20_temp = generer_historique_masi20(historique_temp, constituents)
        
        # Calcul des rendements
        rendements_pf = np.zeros(jours-1)
        for constituant in constituents:
            ticker = constituant['ticker']
            poids = constituant['poids']
            returns = historique_temp[ticker]['returns'][1:]
            rendements_pf += poids * returns
        
        rendements_masi = masi20_temp['returns'][1:]
        
        # Calcul Beta
        beta = calculer_beta(rendements_pf, rendements_masi)
        correlation = calculer_correlation(rendements_pf, rendements_masi)
        tracking_error = calculer_tracking_error(rendements_pf, rendements_masi)
        
        results_beta.append({
            'Période (jours)': jours,
            'Période (mois)': round(jours/21),
            'Beta': beta,
            'Corrélation': correlation,
            'Tracking Error (%)': tracking_error,
            'Date début': (datetime.now() - timedelta(days=jours)).strftime('%d/%m/%Y'),
            'Date fin': datetime.now().strftime('%d/%m/%Y')
        })
    
    df_beta = pd.DataFrame(results_beta)
    
    # ────────────────────────────────────────
    # AFFICHAGE DES RÉSULTATS
    # ────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(
            df_beta.style.format({
                'Beta': '{:.4f}',
                'Corrélation': '{:.4f}',
                'Tracking Error (%)': '{:.2f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("**📈 Statistiques du Beta**")
        
        beta_mean = df_beta['Beta'].mean()
        beta_std = df_beta['Beta'].std()
        beta_min = df_beta['Beta'].min()
        beta_max = df_beta['Beta'].max()
        
        st.metric("Beta Moyen", f"{beta_mean:.4f}")
        st.metric("Écart-type", f"{beta_std:.4f}")
        st.metric("Beta Minimum", f"{beta_min:.4f}")
        st.metric("Beta Maximum", f"{beta_max:.4f}")
        
        # Stabilité
        if beta_std < 0.05:
            st.success("✅ Beta très stable")
        elif beta_std < 0.10:
            st.info("ℹ️ Beta relativement stable")
        else:
            st.warning("⚠️ Beta instable")
    
    # ────────────────────────────────────────
    # GRAPHIQUE D'ÉVOLUTION
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📈 3. Évolution du Beta selon la Période")
    
    fig_beta = go.Figure()
    
    fig_beta.add_trace(go.Scatter(
        x=df_beta['Période (jours)'],
        y=df_beta['Beta'],
        mode='lines+markers',
        name='Beta',
        line=dict(color=config.COLORS['primary'], width=3),
        marker=dict(size=10),
        text=df_beta['Beta'].apply(lambda x: f'Beta: {x:.4f}'),
        hovertemplate='Période: %{x} jours<br>Beta: %{y:.4f}<extra></extra>'
    ))
    
    # Ligne de référence Beta = 1
    fig_beta.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="#10B981",
        annotation_text="Beta = 1 (Référence MASI20)",
        annotation_position="top right"
    )
    
    # Bande de confiance
    fig_beta.add_hrect(
        y0=beta_mean - beta_std,
        y1=beta_mean + beta_std,
        fillcolor="rgba(30, 58, 95, 0.1)",
        line_width=0,
        annotation_text="±1 Écart-type"
    )
    
    fig_beta.update_layout(
        title='Évolution du Beta selon la Période de Calcul',
        xaxis_title='Période (jours)',
        yaxis_title='Beta',
        height=450,
        template='plotly_white',
        xaxis=dict(tickmode='linear', tick0=min(periodes), dtick=30)
    )
    
    st.plotly_chart(fig_beta, use_container_width=True)
    
    # ────────────────────────────────────────
    # GRAPHIQUE COMPARATIF
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 4. Comparaison Beta, Corrélation et Tracking Error")
    
    fig_compare = go.Figure()
    
    # Normaliser pour affichage sur même graphique
    beta_norm = (df_beta['Beta'] - df_beta['Beta'].min()) / (df_beta['Beta'].max() - df_beta['Beta'].min())
    corr_norm = (df_beta['Corrélation'] - df_beta['Corrélation'].min()) / (df_beta['Corrélation'].max() - df_beta['Corrélation'].min())
    te_norm = (df_beta['Tracking Error (%)'] - df_beta['Tracking Error (%)'].min()) / (df_beta['Tracking Error (%)'].max() - df_beta['Tracking Error (%)'].min())
    
    fig_compare.add_trace(go.Scatter(
        x=df_beta['Période (jours)'],
        y=beta_norm,
        mode='lines+markers',
        name='Beta (normalisé)',
        line=dict(color=config.COLORS['primary'], width=2)
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=df_beta['Période (jours)'],
        y=corr_norm,
        mode='lines+markers',
        name='Corrélation (normalisé)',
        line=dict(color='#10B981', width=2)
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=df_beta['Période (jours)'],
        y=te_norm,
        mode='lines+markers',
        name='Tracking Error (normalisé)',
        line=dict(color='#EF4444', width=2)
    ))
    
    fig_compare.update_layout(
        title='Comparaison des Métriques par Période (Normalisées)',
        xaxis_title='Période (jours)',
        yaxis_title='Valeur Normalisée',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # ────────────────────────────────────────
    # INTERPRÉTATION
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 5. Interprétation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            **📊 Analyse du Beta :**
            
            - **Beta moyen :** {beta_mean:.4f}
            - **Stabilité :** {'✅ Stable' if beta_std < 0.05 else 'ℹ️ Moyenne' if beta_std < 0.10 else '⚠️ Instable'}
            - **Variation :** {beta_max - beta_min:.4f} (max - min)
            
            **📈 Tendance :**
            
            - Beta sur 30 jours : {df_beta[df_beta['Période (jours)']==30]['Beta'].values[0] if 30 in periodes else 'N/A'}
            - Beta sur 90 jours : {df_beta[df_beta['Période (jours)']==90]['Beta'].values[0] if 90 in periodes else 'N/A'}
            - Beta sur 252 jours : {df_beta[df_beta['Période (jours)']==252]['Beta'].values[0] if 252 in periodes else 'N/A'}
        """)
    
    with col2:
        st.markdown(f"""
            **🎯 Recommandations :**
            
            {'✅ Le Beta est stable sur différentes périodes. Vous pouvez utiliser le Beta 90 jours avec confiance.' if beta_std < 0.05 else '⚠️ Le Beta varie selon la période. Privilégiez une période longue (90-252 jours) pour plus de stabilité.'}
            
            **💡 Pour le calcul de N* :**
            
            - Utilisez le Beta sur **90 jours** pour une couverture à court terme
            - Utilisez le Beta sur **252 jours** pour une couverture structurelle
            - Surveillez l'évolution du Beta régulièrement
        """)
    
    # ────────────────────────────────────────
    # GUIDE
    # ────────────────────────────────────────
    with st.expander("📘 Guide d'Interprétation de l'Évolution du Beta"):
        st.markdown("""
            ### Pourquoi le Beta varie selon la période ?
            
            Le Beta n'est pas une constante fixe. Il évolue selon :
            
            1. **La période de calcul** : Plus la période est longue, plus le Beta est stable
            2. **Les conditions de marché** : Le Beta peut changer en période de crise
            3. **La composition du portefeuille** : Les poids des actions évoluent
            
            ### Comment interpréter les résultats ?
            
            | Observation | Interprétation | Action |
            |-------------|----------------|--------|
            | Beta stable sur toutes les périodes | Portefeuille cohérent | Utiliser Beta 90 jours |
            | Beta qui augmente avec la période | Risque croissant à long terme | Surveillance accrue |
            | Beta qui diminue avec la période | Risque décroissant à long terme | Ajustement possible |
            | Grande variation (>0.10) | Beta instable | Utiliser moyenne mobile |
            
            ### Quelle période choisir pour N* ?
            
            | Horizon de couverture | Période recommandée |
            |----------------------|---------------------|
            | Court terme (< 1 mois) | 30-60 jours |
            | Moyen terme (1-3 mois) | 90 jours |
            | Long terme (> 3 mois) | 180-252 jours |
            
            ### Limites
        
            - Le Beta passé ne prédit pas le Beta futur
            - Les marchés émergents (comme le Maroc) ont des Betas plus volatils
            - Les événements exceptionnels (COVID, crise) peuvent biaiser le calcul
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

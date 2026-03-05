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
    calculer_prix_theorique_future_bam,
    calculer_base_future,
    calculer_cout_portage,
    calculer_taux_dividende_indice,
    calculer_beta,
    calculer_correlation,
    calculer_tracking_error,
    calculer_alpha,
    calculer_N_star
)
from utils.scraping import get_taux_sans_risque
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy import stats

# Configuration de la page
st.title("🧮 Pricing & Couverture")

# ────────────────────────────────────────────
# CRÉATION DES ONGLETS
# ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🛡️ Calcul de N* (Beta)",
    "📈 Évolution du Beta",
    "📊 Pricing Théorique"
])

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
# ONGLET 2: ÉVOLUTION QUOTIDIENNE DU BETA
# ════════════════════════════════════════════
with tab2:
    st.markdown("""
        Évolution du Beta calculé de manière glissante sur les 90 jours.
        Permet de voir comment le Beta change jour après jour.
    """)
    
    # ────────────────────────────────────────
    # PARAMÈTRES
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### ⚙️ Paramètres de Calcul")
    
    col1, col2 = st.columns(2)
    
    with col1:
        window_size = st.slider(
            "Fenêtre de calcul du Beta (jours)",
            min_value=10,
            max_value=60,
            value=30,
            step=5,
            help="Nombre de jours utilisés pour calculer chaque Beta glissant"
        )
    
    with col2:
        st.info(f"Total de données disponibles: 90 jours")
    
    # ────────────────────────────────────────
    # CALCUL DU BETA GLISSANT
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🧮 Calcul du Beta Glissant")
    
    # Récupérer les rendements
    rendements_pf_total = np.zeros(89)
    for constituant in constituents:
        ticker = constituant['ticker']
        poids = constituant['poids']
        returns = historique_constituents[ticker]['returns'][1:]
        rendements_pf_total += poids * returns
    
    rendements_masi_total = historique_masi20['returns'][1:]
    dates = historique_masi20['dates'][1:]  # 89 jours
    
    # Calcul du Beta glissant
    rolling_betas = []
    rolling_correlations = []
    rolling_dates = []
    
    for i in range(window_size, len(rendements_pf_total)):
        # Fenêtre glissante
        pf_window = rendements_pf_total[i-window_size:i]
        masi_window = rendements_masi_total[i-window_size:i]
        
        # Calcul Beta
        beta = calculer_beta(pf_window, masi_window)
        correlation = calculer_correlation(pf_window, masi_window)
        
        rolling_betas.append(beta)
        rolling_correlations.append(correlation)
        rolling_dates.append(dates[i])
    
    # Création DataFrame
    df_rolling = pd.DataFrame({
        'Date': rolling_dates,
        'Beta': rolling_betas,
        'Corrélation': rolling_correlations
    })
    
    # ────────────────────────────────────────
    # AFFICHAGE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 Évolution du Beta au Cours du Temps")
    
    # Statistiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Beta Actuel (90 jours)", f"{rolling_betas[-1]:.4f}")
    
    with col2:
        st.metric("Beta Moyen", f"{np.mean(rolling_betas):.4f}")
    
    with col3:
        st.metric("Beta Minimum", f"{np.min(rolling_betas):.4f}")
    
    with col4:
        st.metric("Beta Maximum", f"{np.max(rolling_betas):.4f}")
    
    # ────────────────────────────────────────
    # GRAPHIQUE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📈 Graphique de l'Évolution du Beta")
    
    fig = go.Figure()
    
    # Ligne Beta glissant
    fig.add_trace(go.Scatter(
        x=df_rolling['Date'],
        y=df_rolling['Beta'],
        mode='lines',
        name='Beta Glissant',
        line=dict(color=config.COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 95, 0.1)',
        hovertemplate='Date: %{x|%d/%m/%Y}<br>Beta: %{y:.4f}<extra></extra>'
    ))
    
    # Ligne Beta = 1
    fig.add_hline(
        y=1.0,
        line_dash="dash",
        line_color="#10B981",
        annotation_text="Beta = 1 (Référence)",
        annotation_position="top right"
    )
    
    # Moyenne
    beta_mean = np.mean(rolling_betas)
    fig.add_hline(
        y=beta_mean,
        line_dash="dot",
        line_color="#F59E0B",
        annotation_text=f"Moyenne = {beta_mean:.4f}"
    )
    
    fig.update_layout(
        title=f'Évolution Quotidienne du Beta (Fenêtre Glissante: {window_size} jours)',
        xaxis_title='Date',
        yaxis_title='Beta',
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # ────────────────────────────────────────
    # TABLEAU DÉTAILLÉ
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Données Détaillées")
    
    # Afficher les 10 dernières valeurs
    df_display = df_rolling.tail(10).copy()
    df_display['Date'] = df_display['Date'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        df_display.style.format({
            'Beta': '{:.4f}',
            'Corrélation': '{:.4f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # ────────────────────────────────────────
    # INTERPRÉTATION
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💡 Interprétation")
    
    beta_actuel = rolling_betas[-1]
    beta_moyen = np.mean(rolling_betas)
    beta_std = np.std(rolling_betas)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            **📊 Analyse de Stabilité :**
            
            - **Volatilité du Beta :** {beta_std:.4f}
            - **Tendance :** {'↗️ Croissante' if rolling_betas[-1] > rolling_betas[0] else '↘️ Décroissante' if rolling_betas[-1] < rolling_betas[0] else '➡️ Stable'}
            - **Écart à la moyenne :** {beta_actuel - beta_moyen:+.4f}
        """)
    
    with col2:
        if beta_std < 0.05:
            st.success("✅ Beta très stable dans le temps")
        elif beta_std < 0.10:
            st.info("ℹ️ Beta relativement stable")
        else:
            st.warning("⚠️ Beta instable - Surveillance recommandée")
    
    # ────────────────────────────────────────
    # GUIDE
    # ────────────────────────────────────────
    with st.expander("📘 Comment interpréter ce graphique ?"):
        st.markdown("""
            ### Beta Glissant (Rolling Beta)
            
            Le Beta est calculé sur une fenêtre mobile de N jours (par défaut 30 jours).
            Chaque point représente le Beta calculé sur les 30 jours précédents.
            
            ### Interprétation
            
            | Observation | Signification |
            |-------------|---------------|
            | Ligne stable autour de 1 | Portefeuille réplique bien le MASI20 |
            | Ligne qui monte | Le risque systématique augmente |
            | Ligne qui descend | Le risque systématique diminue |
            | Grandes fluctuations | Beta instable - marché volatil |
            
            ### Pourquoi utiliser un Beta glissant ?
            
            1. **Détecter les changements de risque** : Le Beta n'est pas constant
            2. **Adapter la couverture** : Ajuster N* si le Beta change significativement
            3. **Identifier les régimes de marché** : Périodes calmes vs turbulentes
            
            ### Recommandation
            
            - Si le Beta est stable : Utiliser le Beta moyen pour N*
            - Si le Beta est instable : Utiliser le Beta récent (derniers jours)
            - Surveiller régulièrement l'évolution
        """)

# ════════════════════════════════════════════
# ONGLET 3: PRICING THÉORIQUE
# ════════════════════════════════════════════
with tab3:
    st.markdown("""
        Calcul du prix théorique d'un future sur indice selon la formule BAM:
        
        **F₀ = S × e^((r-d)t)**
        
        Où **d** est calculé automatiquement à partir des dividendes des constituants MASI20.
    """)
    
    # ────────────────────────────────────────
    # RÉCUPÉRATION DES DONNÉES OFFICIELLES
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🔄 1. Données Officielles MASI20")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Composition et dividendes récupérés depuis la Bourse de Casablanca")
    
    with col2:
        if st.button("🔄 Actualiser les données", use_container_width=True):
            if 'constituents' in cache_masi20:
                del cache_masi20['constituents']
            st.rerun()
    
    # Récupérer les constituents
    from utils.bourse_casa_scraper import (
        get_masi20_constituents_officiels,
        calculer_taux_dividende_masi20
    )
    
    constituents = get_masi20_constituents_officiels()
    
    # ────────────────────────────────────────
    # CALCUL DU TAUX DE DIVIDENDE
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💰 2. Calcul du Taux de Dividende (Formule BAM)")
    
    taux_dividende, df_details = calculer_taux_dividende_masi20(constituents)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Taux de Dividende (d)",
            f"{taux_dividende*100:.4f}%",
            help="Calculé selon: d = Σ(Pi × Di/Ci)"
        )
    
    with col2:
        st.metric(
            "Nombre de Constituants",
            f"{len(constituents)}",
            help="Actions composant le MASI20"
        )
    
    with col3:
        date_maj = datetime.now().strftime('%d/%m/%Y %H:%M')
        st.info(f"📅 MAJ: {date_maj}")
    
    # Afficher le détail
    with st.expander("📊 Voir le détail du calcul par action"):
        st.markdown("#### Détail du Calcul du Taux de Dividende")
        st.dataframe(df_details, use_container_width=True)
        
        st.caption(f"""
            **Formule:** d = Σ(Pi × Di/Ci)  
            **Résultat:** d = {taux_dividende*100:.4f}% = {taux_dividende:.6f}
        """)
    
    # ────────────────────────────────────────
    # PARAMÈTRES DE PRICING
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🔧 3. Paramètres de Pricing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        spot = st.number_input(
            "Niveau Spot MASI20 (S)",
            min_value=1000.0,
            value=1876.54,
            step=10.0,
            help="Cours de clôture du MASI20"
        )
    
    with col2:
        taux_bkam = get_taux_sans_risque('10ans')
        r = st.number_input(
            "Taux sans risque (r) %",
            min_value=0.0,
            max_value=15.0,
            value=taux_bkam * 100,
            step=0.1
        ) / 100
    
    with col3:
        jours = st.number_input(
            "Jours jusqu'échéance",
            min_value=1,
            max_value=365,
            value=90,
            step=1
        )
        t = jours / 360  # Base 360 selon BAM
    
# ════════════════════════════════════════════
# ONGLET 3: PRICING THÉORIQUE (CORRIGÉ)
# ════════════════════════════════════════════
with tab3:
    st.markdown("""
        Calcul du prix théorique d'un future sur indice selon la formule BAM :  
        **F₀ = S × e^((r - d)t)**
    """)

    # ────────────────────────────────────────
    # 1. Données officielles
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🔄 1. Données Officielles MASI20")

    if st.button("🔄 Actualiser les données", use_container_width=True):
        if 'constituents' in st.session_state:
            del st.session_state['constituents']
        st.rerun()

    # Récupération des constituants
    if 'constituents' not in st.session_state:
        st.session_state['constituents'] = get_masi20_constituents_officiels()

    constituents = st.session_state['constituents']

    # ────────────────────────────────────────
    # 2. Calcul du taux de dividende
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 💰 2. Taux de Dividende (Formule BAM)")

    taux_dividende, df_details = calculer_taux_dividende_indice(constituents)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux de Dividende (d)", f"{taux_dividende*100:.4f}%")
    with col2:
        st.metric("Nombre de constituants", len(constituents))
    with col3:
        st.info(f"📅 MAJ : {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    with st.expander("📊 Détail par action"):
        st.dataframe(df_details, use_container_width=True)

    # ────────────────────────────────────────
    # 3. Paramètres de pricing
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 🔧 3. Paramètres")

    col1, col2, col3 = st.columns(3)
    with col1:
        spot = st.number_input("Niveau Spot MASI20 (S)", value=1876.54, step=10.0)
    with col2:
        r = st.number_input("Taux sans risque (r) %", value=3.5, step=0.1) / 100
    with col3:
        jours = st.number_input("Jours jusqu'à échéance", value=90, step=1)
        t = jours / 360

    # ────────────────────────────────────────
    # 4. Calcul du prix théorique
    # ────────────────────────────────────────
    st.divider()
    st.markdown("### 📊 4. Prix Théorique du Future")

    F0 = calculer_prix_theorique_future_bam(spot, r, taux_dividende, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, taux_dividende, t)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style='padding:25px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                        border-radius:12px; text-align:center; color:white;'>
                <p style='margin:0; font-size:0.9em;'>Prix Théorique F₀</p>
                <p style='margin:10px 0 0 0; font-size:2.8em; font-weight:700;'>
                    {F0:,.2f}
                </p>
                <p style='margin:5px 0 0 0; font-size:0.85em;'>points</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        couleur = "#10B981" if base['points'] > 0 else "#EF4444"
        st.markdown(f"""
            <div style='padding:25px; background:white; border-radius:12px; text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08); border-left:5px solid {couleur};'>
                <p style='margin:0; font-size:0.9em; color:#6B7280;'>Base (F₀ - S)</p>
                <p style='margin:10px 0 0 0; font-size:2em; font-weight:700; color:{couleur};'>
                    {base['points']:+,.2f}
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%")
    with col4:
        st.metric("Valeur Notionnelle", f"{F0 * config.MULTIPLICATEUR:,.0f} MAD")

    # Formule détaillée
    st.info(f"""
        **Formule BAM appliquée :**  
        F₀ = S × e^((r - d) × t)  
        **F₀ = {F0:,.2f} points**  
        **Base** = {base['points']:+,.2f} points ({base['percentage']:+.2f}%)
    """)

    # Références réglementaires
    st.divider()
    st.markdown("### 📚 Références Réglementaires")
    st.markdown("""
        **Instruction BAM N° IN-2026-01**  
        Formule officielle : `Cours théorique = S × e^((r-d)t)`  
        Taux de dividende : `d = Σ(Pi × Di / Ci)`
    """)

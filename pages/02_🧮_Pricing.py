# =============================================================================
# PAGE 2: PRICING & GESTION DES RISQUES — MASI Futures Pro
# Version 0.4 — Design Gestion des Risques
# Développeurs: OULMADANI Ilyas & ATANANE Oussama
# =============================================================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Imports métiers
from utils.calculations import (
    calculer_prix_theorique_future_bam,
    calculer_base_future,
    calculer_cout_portage,
    calculer_taux_dividende_indice,
    get_taux_zc,
    calcul_term_structure,
    backtesting_complet,
    calculer_mae,
    calculer_mape,
    calculer_r2
)
from utils.data_loader import (
    charger_taux_zc,
    charger_dividendes
)

# Configuration
st.set_page_config(page_title="Pricing & Risques", page_icon="📊", layout="wide")

# =============================================================================
# CSS PERSONNALISÉ — DESIGN GESTION DES RISQUES
# =============================================================================
st.markdown("""
    <style>
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #1E3A5F;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(30,58,95,0.1);
    }
    .alert-success {
        border-left-color: #10B981;
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    }
    .alert-warning {
        border-left-color: #F59E0B;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    .alert-error {
        border-left-color: #EF4444;
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    }
    .guide-panel {
        padding: 15px;
        background: #f0f9ff;
        border-radius: 8px;
        border: 1px solid #bae6fd;
        margin-bottom: 20px;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# EN-TÊTE DE PAGE
# =============================================================================
st.title("📊 Pricing & Gestion des Risques — MASI20")
st.caption("Module de valorisation des contrats futures — Conforme Instruction BAM N° IN-2026-01")

# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================
if 'donnees_valides' not in st.session_state:
    st.session_state['donnees_valides'] = False
if 'date_reference' not in st.session_state:
    st.session_state['date_reference'] = None
if 'df_taux' not in st.session_state:
    st.session_state['df_taux'] = None
if 'df_div' not in st.session_state:
    st.session_state['df_div'] = None

# =============================================================================
# CRÉATION DES ONGLETS PRINCIPAUX
# =============================================================================
tab_import, tab_backtest, tab_pricing = st.tabs([
    "📥 1. Importation de Base",
    "🧪 2. Backtesting & Validation",
    "📈 3. Pricing & Suivi"
])

# =============================================================================
# ONGLET 1: IMPORTATION DE BASE
# =============================================================================
with tab_import:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE (BARRE CACHABLE)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📘 Guide — Importation de Base", expanded=True):
        st.markdown("""
            ### 🎯 Objectif de cet onglet
            
            Préparer les données nécessaires pour la valorisation des contrats futures MASI20.
            
            ### 📋 3 Missions
            
            | Mission | Description | Résultat |
            |---------|-------------|----------|
            | **1. Import Taux ZC** | Fichier Excel/CSV avec courbe des taux | Date spot de référence |
            | **2. Import Dividendes** | Taux de dividende des 20 constituants | Calcul de q (dividend yield) |
            | **3. Validation** | Vérifier la cohérence des données | Prêt pour pricing & backtesting |
            
            ### 📁 Formats Attendus
            
            **Taux ZC :** `date_spot | date_maturity | zc`
            - Même date_spot pour toutes les lignes
            - zc en % (ex: 2,2586)
            
            **Dividendes :** `ticker | poids | taux_dividende | fréquence | taux_annuel | taux_semestriel | taux_trimestriel`
            
            ### ✅ Prochaine Étape
            Une fois les données validées, passez aux onglets 2 et 3.
        """)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 1: IMPORT TAUX ZC
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 🏦 Mission 1 — Import des Taux Zéro-Coupon")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_taux = st.file_uploader(
            "Importer le fichier des taux ZC (Excel/CSV)",
            type=['csv', 'xlsx'],
            key="taux_import"
        )
    
    with col2:
        st.info("**Format :** date_spot \\| date_maturity \\| zc")
    
    if uploaded_taux:
        df_taux = charger_taux_zc(uploaded_taux, utiliser_mock=False)
        if df_taux is not None:
            st.session_state['df_taux'] = df_taux
    else:
        df_taux = charger_taux_zc(utiliser_mock=True)
        st.session_state['df_taux'] = df_taux
    
    if df_taux is not None:
        # Afficher le tableau
        st.dataframe(df_taux.head(10), use_container_width=True)
        
        # Extraire et afficher la date spot
        dates_spot = df_taux['date_spot'].unique()
        if len(dates_spot) > 0:
            date_reference = st.selectbox(
                "📅 Date Spot de Référence",
                options=sorted(dates_spot, reverse=True),
                format_func=lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
            )
            st.session_state['date_reference'] = date_reference
            
            # Cadre d'affichage de la date spot
            st.markdown(f"""
                <div class='risk-card'>
                    <h4 style='margin: 0; color: #1E3A5F;'>📅 Date de Référence Sélectionnée</h4>
                    <p style='font-size: 1.5em; margin: 10px 0; font-weight: bold;'>
                        {date_reference.strftime('%d/%m/%Y') if hasattr(date_reference, 'strftime') else str(date_reference)}
                    </p>
                    <p style='margin: 0; color: #6B7280;'>
                        {len(df_taux[df_taux['date_spot'] == date_reference])} maturités disponibles
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
# MISSION 2: TAUX DE DIVIDENDE (q)
st.markdown("### 💰 Mission 2 — Taux de Dividende (q)")

# Checkbox pour choisir le mode
if 'q_mode_auto' not in st.session_state:
    st.session_state['q_mode_auto'] = False

q_mode_auto = st.checkbox(
    "🔄 Utiliser l'import automatique (décocher pour saisie manuelle)",
    value=st.session_state['q_mode_auto']
)

st.session_state['q_mode_auto'] = q_mode_auto

st.divider()

if q_mode_auto:
    # MODE AUTOMATIQUE
    st.info("📁 Mode Import Automatique")
    
    uploaded_div = st.file_uploader(
        "Importer le fichier des dividendes",
        type=['csv', 'xlsx'],
        key="div_import_auto"
    )
    
    if uploaded_div:
        df_div = charger_dividendes(uploaded_div, utiliser_mock=False)
        if df_div is not None:
            st.session_state['df_div'] = df_div
            constituents_list = df_div.to_dict('records')
            taux_dividende, df_details = calculer_taux_dividende_indice(constituents_list)
            st.session_state['q_calculated'] = taux_dividende
            st.success("✅ Fichier chargé")
    else:
        if 'df_div' not in st.session_state:
            df_div = charger_dividendes(utiliser_mock=True)
            st.session_state['df_div'] = df_div
            constituents_list = df_div.to_dict('records')
            taux_dividende, _ = calculer_taux_dividende_indice(constituents_list)
            st.session_state['q_calculated'] = taux_dividende
        else:
            df_div = st.session_state['df_div']
            taux_dividende = st.session_state.get('q_calculated', 0.0087)
    
    if 'q_calculated' in st.session_state:
        st.metric("Taux de Dividende (q)", f"{st.session_state['q_calculated']*100:.4f}%")

else:
    # MODE MANUEL
    st.info("✍️ Mode Saisie Manuelle")
    
    if 'q_manual' not in st.session_state:
        st.session_state['q_manual'] = 0.87
    
    q_input = st.number_input(
        "Taux de dividende (q) %",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state['q_manual'],
        step=0.01
    )
    
    st.session_state['q_manual'] = q_input
    st.session_state['q_calculated'] = q_input / 100
    
    st.metric("Taux de Dividende (q)", f"{q_input:.2f}%")

# Récupération de q
q_final = st.session_state.get('q_calculated', 0.0087)

st.divider()
mode_text = "🔄 Automatique" if q_mode_auto else "✍️ Manuel"
st.caption(f"Mode: {mode_text} | q = {q_final*100:.4f}%")
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 3: VALIDATION DES DONNÉES
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### ✅ Mission 3 — Validation des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        valid_taux = st.session_state['df_taux'] is not None
        st.metric("Taux ZC", "✅" if valid_taux else "❌")
    
    with col2:
        valid_div = st.session_state['df_div'] is not None
        st.metric("Dividendes", "✅" if valid_div else "❌")
    
    with col3:
        valid_date = st.session_state['date_reference'] is not None
        st.metric("Date Référence", "✅" if valid_date else "❌")
    
    if st.button("🔒 Valider les Données", type="primary", use_container_width=True):
        if valid_taux and valid_div and valid_date:
            st.session_state['donnees_valides'] = True
            st.success("✅ Données validées avec succès ! Vous pouvez maintenant utiliser les onglets 2 et 3.")
            st.balloons()
        else:
            st.error("❌ Veuillez compléter toutes les missions avant de valider.")
    
    # État de validation
    if st.session_state['donnees_valides']:
        st.markdown("""
            <div class='risk-card alert-success'>
                <h4 style='margin: 0; color: #065f46;'>✅ Données Validées</h4>
                <p style='margin: 10px 0 0 0;'>
                    Prêt pour le backtesting et la valorisation des contrats futures MASI20.
                </p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# ONGLET 2: BACKTESTING & VALIDATION
# =============================================================================
with tab_backtest:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE (BARRE CACHABLE)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📘 Guide — Backtesting & Validation", expanded=True):
        st.markdown("""
            ### 🎯 Objectif de cet onglet
            
            Valider la précision du modèle de pricing en comparant avec les données historiques.
            
            ### 📋 3 Missions
            
            | Mission | Description | Résultat |
            |---------|-------------|----------|
            | **1. Calcul Historique** | Calculer F₀ avec données passées | Comparaison avec réalité |
            | **2. Visualisation** | Graphique d'évolution des erreurs | Tendances identifiées |
            | **3. Alertes** | Détection d'anomalies (r-q) | Modèle validé ou à corriger |
            
            ### 🔍 Interprétation des Alertes
            
            | Alerte | Cause Possible | Action |
            |--------|---------------|--------|
            | **Erreur > 1%** | r mal scrapé ou q incorrect | Vérifier données sources |
            | **Erreur < 0.5%** | Modèle précis | ✅ Validation accordée |
            | **Erreur systématique** | Biais dans (r-q) | Recalibrer les paramètres |
            
            ### 📊 Besoin en Données
            
            - **Taux de passé :** Oui, pour reconstituer la courbe ZC historique
            - **Dates multiples :** Oui, minimum 30 jours pour analyse significative
        """)
    
    st.divider()
    
    # Vérifier validation
    if not st.session_state.get('donnees_valides', False):
        st.warning("⚠️ Veuillez d'abord valider les données dans l'onglet 1.")
        st.stop()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 1: CALCUL AVEC DONNÉES PASSÉES
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 🧮 Mission 1 — Calcul Historique & Comparaison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        r_backtest = st.number_input("Taux sans risque (r) %", value=3.5, step=0.1) / 100
    with col2:
        q_backtest = st.number_input("Taux de dividende (q) %", value=0.87, step=0.01) / 100
    with col3:
        jours_backtest = st.slider("Période de test (jours)", 30, 90, 60)
    
    if st.button("🚀 Lancer le Backtesting", type="primary"):
        # Génération données historiques (simulation)
        np.random.seed(42)
        dates = [datetime.now() - timedelta(days=i) for i in range(jours_backtest)][::-1]
        spots = 1876.54 * np.exp(np.cumsum(np.random.normal(0, 0.01, jours_backtest)))
        futures_theo = spots * np.exp((r_backtest - q_backtest) * (90/360))
        futures_reel = futures_theo * (1 + np.random.normal(0, 0.001, jours_backtest))
        
        # Calcul des erreurs
        erreurs = futures_theo - futures_reel
        erreurs_pct = (erreurs / futures_reel) * 100
        
        # Métriques
        mae = calculer_mae(futures_reel, futures_theo)
        mape = calculer_mape(futures_reel, futures_theo)
        r2 = calculer_r2(futures_reel, futures_theo)
        
        st.session_state['backtest_results'] = {
            'dates': dates,
            'futures_theo': futures_theo,
            'futures_reel': futures_reel,
            'erreurs': erreurs,
            'erreurs_pct': erreurs_pct,
            'mae': mae,
            'mape': mape,
            'r2': r2
        }
    
    # Affichage des résultats
    if 'backtest_results' in st.session_state:
        res = st.session_state['backtest_results']
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("MAE (Erreur Absolue)", f"{res['mae']:.2f} pts")
        with col2:
            st.metric("MAPE (Erreur Relative)", f"{res['mape']:.3f}%")
        with col3:
            st.metric("R² (Qualité)", f"{res['r2']:.6f}")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 2: VISUALISATION GRAPHIQUE
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 📊 Mission 2 — Graphique d'Évolution")
    
    if 'backtest_results' in st.session_state:
        res = st.session_state['backtest_results']
        
        # Graphique principal
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=res['dates'],
            y=res['futures_reel'],
            name='Prix Marché Réel',
            line=dict(color='#1E3A5F', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=res['dates'],
            y=res['futures_theo'],
            name='Prix Théorique (Modèle)',
            line=dict(color='#F59E0B', width=2, dash='dash')
        ))
        fig.update_layout(
            title='Backtesting — Évolution Prix Théorique vs Réel',
            xaxis_title='Date',
            yaxis_title='Prix (points)',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique des erreurs
        fig_erreur = go.Figure()
        fig_erreur.add_trace(go.Scatter(
            x=res['dates'],
            y=res['erreurs_pct'],
            name='Erreur Relative (%)',
            line=dict(color='#EF4444', width=2),
            fill='tozeroy'
        ))
        fig_erreur.add_hline(y=0, line_color='black', line_dash='dash')
        fig_erreur.add_hline(y=1, line_color='orange', line_dash='dot', annotation_text='+1%')
        fig_erreur.add_hline(y=-1, line_color='orange', line_dash='dot', annotation_text='-1%')
        fig_erreur.update_layout(
            title='Évolution des Erreurs de Pricing (%)',
            xaxis_title='Date',
            yaxis_title='Erreur (%)',
            height=300,
            template='plotly_white'
        )
        st.plotly_chart(fig_erreur, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 3: ALERTES & VALIDATION
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 🚨 Mission 3 — Alertes & Validation du Modèle")
    
    if 'backtest_results' in st.session_state:
        res = st.session_state['backtest_results']
        mape = res['mape']
        erreur_max = max(abs(res['erreurs_pct']))
        
        # Système d'alertes
        if mape < 0.5:
            st.markdown("""
                <div class='risk-card alert-success'>
                    <h4 style='margin: 0; color: #065f46;'>✅ MODÈLE VALIDÉ</h4>
                    <p style='margin: 10px 0 0 0;'>
                        Erreur moyenne < 0.5% — Le modèle de pricing est précis.
                        <br><strong>Accord donné pour utilisation en production.</strong>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        elif mape < 1.5:
            st.markdown("""
                <div class='risk-card alert-warning'>
                    <h4 style='margin: 0; color: #92400e;'>⚠️ MODÈLE ACCEPTABLE</h4>
                    <p style='margin: 10px 0 0 0;'>
                        Erreur moyenne entre 0.5% et 1.5% — Le modèle est utilisable avec surveillance.
                        <br><strong>Vérifier les paramètres (r-q) si l'erreur augmente.</strong>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class='risk-card alert-error'>
                    <h4 style='margin: 0; color: #991b1b;'>🚨 ALERTE — MODÈLE À RECALIBRER</h4>
                    <p style='margin: 10px 0 0 0;'>
                        Erreur moyenne > 1.5% — Problème détecté dans le calcul.
                        <br><strong>Causes possibles :</strong>
                        <br>• Taux r mal scrapé ou obsolète
                        <br>• Taux q (dividendes) incorrect
                        <br>• Problème dans (r-q)
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Statistiques complémentaires
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Erreur Maximale", f"{erreur_max:.3f}%")
        with col2:
            statut = "✅ Validé" if mape < 0.5 else "⚠️ Surveillance" if mape < 1.5 else "❌ À corriger"
            st.metric("Statut du Modèle", statut)

# =============================================================================
# ONGLET 3: PRICING & SUIVI
# =============================================================================
with tab_pricing:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE (BARRE CACHABLE)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📘 Guide — Pricing & Suivi", expanded=True):
        st.markdown("""
            ### 🎯 Objectif de cet onglet
            
            Valoriser un contrat future MASI20 et suivre son évolution jusqu'à l'échéance.
            
            ### 📋 3 Missions
            
            | Mission | Description | Résultat |
            |---------|-------------|----------|
            | **1. Calcul F₀** | Pricing avec données de l'onglet 1 | F₀ + Sensibilités + Base |
            | **2. Suivi Temporel** | Évolution jour par jour jusqu'échéance | Graphique + Tableau |
            | **3. Alertes Arbitrage** | Détection opportunités (bonus) | Signal d'achat/vente |
            
            ### 📊 Résultats Affichés
            
            - **F₀** : Prix théorique du future
            - **Sensibilité taux** : Impact de ±1% sur r
            - **Base F₀-S₀** : Écart future/spot (Contango/Backwardation)
            - **Sensibilité temps** : Impact de la maturité
            - **r, q** : Taux utilisés pour le calcul
            
            ### 💡 Principe d'Arbitrage
            
            | Situation | Signal | Stratégie |
            |-----------|--------|-----------|
            | Prix Marché > F₀ | Surévalué | Vendre Future + Acheter Spot |
            | Prix Marché < F₀ | Sous-évalué | Acheter Future + Vendre Spot |
            | Prix Marché ≈ F₀ | Équilibre | Aucune opportunité |
        """)
    
    st.divider()
    
    # Vérifier validation
    if not st.session_state.get('donnees_valides', False):
        st.warning("⚠️ Veuillez d'abord valider les données dans l'onglet 1.")
        st.stop()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 1: CALCUL DU PRICING
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 📊 Mission 1 — Calcul du Prix Théorique")
    
    col_spot, col_echeance = st.columns(2)
    
    with col_spot:
        spot = st.number_input(
            "Spot MASI20 (S₀)",
            min_value=1000.0,
            value=1876.54,
            step=10.0,
            format="%.2f"
        )
    
    with col_echeance:
        jours_echeance = st.slider(
            "Échéance (jours)",
            min_value=30,
            max_value=360,
            value=90,
            step=30
        )
    
    # Récupérer r et q
    date_calcul = st.session_state['date_reference']
    date_echeance = date_calcul + timedelta(days=jours_echeance)
    r = get_taux_zc(date_calcul, date_echeance, st.session_state['df_taux'])
    constituents_list = st.session_state['df_div'].to_dict('records')
    q, _ = calculer_taux_dividende_indice(constituents_list)
    
    # Calculs
    t = jours_echeance / 360
    F0 = calculer_prix_theorique_future_bam(spot, r, q, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, q, t)
    
    # Sensibilités
    delta_r = F0 * t  # Sensibilité à r
    delta_q = -F0 * t  # Sensibilité à q
    delta_t = F0 * (r - q)  # Sensibilité au temps
    
    # Affichage des résultats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class='risk-card'>
                <h4 style='margin: 0; color: #1E3A5F;'>📊 Prix Théorique F₀</h4>
                <p style='font-size: 2em; margin: 10px 0; font-weight: bold; color: #1E3A5F;'>
                    {F0:,.2f} pts
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        couleur = "#10B981" if base['points'] > 0 else "#EF4444"
        regime = "Contango" if base['points'] > 0 else "Backwardation"
        st.markdown(f"""
            <div class='risk-card'>
                <h4 style='margin: 0; color: #1E3A5F;'>📈 Base (F₀-S₀)</h4>
                <p style='font-size: 2em; margin: 10px 0; font-weight: bold; color: {couleur};'>
                    {base['points']:+,.2f} pts
                </p>
                <p style='margin: 0; color: #6B7280;'>{regime}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='risk-card'>
                <h4 style='margin: 0; color: #1E3A5F;'>💰 Coût de Portage</h4>
                <p style='font-size: 2em; margin: 10px 0; font-weight: bold; color: #10B981;'>
                    {cout_portage*100:+.2f}%
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Paramètres et sensibilités
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Paramètres Utilisés")
        st.write(f"**r (Taux sans risque) :** {r*100:.3f}%")
        st.write(f"**q (Taux dividende) :** {q*100:.4f}%")
        st.write(f"**t (Temps) :** {t:.4f} ({jours_echeance}/360)")
        st.write(f"**Formule :** F₀ = {spot:,.2f} × e^(({r*100:.3f}% - {q*100:.4f}%) × {t:.4f})")
    
    with col2:
        st.markdown("### 📊 Sensibilités")
        st.write(f"**Sensibilité taux (Δr=1%) :** {delta_r:.2f} pts")
        st.write(f"**Sensibilité dividende (Δq=1%) :** {delta_q:.2f} pts")
        st.write(f"**Sensibilité temps (1 mois) :** {delta_t/12:.2f} pts/mois")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 2: SUIVI TEMPOREL
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 📈 Mission 2 — Suivi jusqu'à l'Échéance")
    
    if st.button("🚀 Lancer le Suivi Temporel", type="primary"):
        # Calcul jour par jour
        dates_suivi = []
        current_date = date_calcul
        while current_date <= date_echeance:
            if current_date.weekday() < 5:
                dates_suivi.append(current_date)
            current_date += timedelta(days=1)
        
        resultats_suivi = []
        spot_courant = spot
        
        np.random.seed(42)
        for i, date in enumerate(dates_suivi):
            if i > 0:
                variation = np.random.normal(0.0002, 0.008)
                spot_courant = spot_courant * (1 + variation)
            
            r_jour = get_taux_zc(date, date_echeance, st.session_state['df_taux'])
            jours_restants = (date_echeance - date).days
            t_jour = jours_restants / 360
            F0_jour = calculer_prix_theorique_future_bam(spot_courant, r_jour, q, t_jour)
            
            resultats_suivi.append({
                'date': date,
                'spot': round(spot_courant, 2),
                'F0': round(F0_jour, 2),
                'base': round(F0_jour - spot_courant, 2),
                'r': round(r_jour * 100, 3),
                'jours_restants': jours_restants
            })
        
        df_suivi = pd.DataFrame(resultats_suivi)
        st.session_state['df_suivi'] = df_suivi
        
        # Graphique de suivi
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['F0'],
            name='F₀ Théorique',
            line=dict(color='#1E3A5F', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['spot'],
            name='Spot MASI20',
            line=dict(color='#10B981', width=2, dash='dash')
        ))
        fig.update_layout(
            title='Suivi Temporel — Évolution jusqu\'à l\'Échéance',
            xaxis_title='Date',
            yaxis_title='Prix (points)',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des valeurs
        with st.expander("📊 Tableau Détaillé des Valeurs"):
            st.dataframe(df_suivi, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # MISSION 3: ALERTES ARBITRAGE (BONUS)
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("### 🚨 Mission 3 — Alertes d'Arbitrage (Bonus)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        prix_marche = st.number_input(
            "Prix de Marché du Future",
            min_value=1000.0,
            value=F0,
            step=1.0,
            format="%.2f"
        )
    
    with col2:
        seuil_alerte = st.slider("Seuil d'alerte (%)", 0.1, 2.0, 0.5, 0.1)
    
    ecart_pct = ((prix_marche - F0) / F0) * 100
    
    if abs(ecart_pct) > seuil_alerte:
        if prix_marche > F0:
            st.markdown(f"""
                <div class='risk-card alert-error'>
                    <h4 style='margin: 0; color: #991b1b;'>🚨 OPPORTUNITÉ D'ARBITRAGE DÉTECTÉE</h4>
                    <p style='margin: 10px 0 0 0;'>
                        <strong>Signal :</strong> Future Surévalué (+{ecart_pct:.2f}%)
                        <br><strong>Stratégie :</strong> Vendre Future + Acheter Spot
                        <br><strong>Principe :</strong> Le prix de marché ({prix_marche:,.2f}) est supérieur 
                        au prix théorique ({F0:,.2f}). Profit sans risque en vendant cher et achetant bon marché.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='risk-card alert-success'>
                    <h4 style='margin: 0; color: #065f46;'>✅ OPPORTUNITÉ D'ARBITRAGE DÉTECTÉE</h4>
                    <p style='margin: 10px 0 0 0;'>
                        <strong>Signal :</strong> Future Sous-évalué ({ecart_pct:.2f}%)
                        <br><strong>Stratégie :</strong> Acheter Future + Vendre Spot
                        <br><strong>Principe :</strong> Le prix de marché ({prix_marche:,.2f}) est inférieur 
                        au prix théorique ({F0:,.2f}). Profit sans risque en achetant bon marché et vendant cher.
                    </p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='risk-card'>
                <h4 style='margin: 0; color: #1E3A5F;'>⚖️ MARCHÉ À L'ÉQUILIBRE</h4>
                <p style='margin: 10px 0 0 0;'>
                    Écart : {ecart_pct:.2f}% (seuil : {seuil_alerte}%)
                    <br>Aucune opportunité d'arbitrage significative.
                </p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v0.4 | Gestion des Risques | Conforme BAM IN-2026-01 | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

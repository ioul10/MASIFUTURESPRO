# =============================================================================
# PAGE 2: PRICING THÉORIQUE — MASI Futures Pro
# Version 0.3 — Conforme Instruction BAM N° IN-2026-01
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
    detecter_arbitrage
)
from utils.data_loader import (
    charger_taux_zc,
    charger_dividendes,
    charger_historique_masi20,
    widget_upload_taux_zc,
    widget_upload_dividendes
)
from data.test_data import get_dividendes_masi20_mock

# Configuration
st.set_page_config(page_title="Pricing Théorique", page_icon="🧮", layout="wide")

# =============================================================================
# EN-TÊTE DE PAGE
# =============================================================================
st.title("🧮 Pricing Théorique — Instruction BAM N° IN-2026-01")
st.caption("Calcul du cours théorique avec Term Structure et Backtesting")

# =============================================================================
# INITIALISATION DES DONNÉES (SESSION STATE)
# =============================================================================
if 'taux_zc_loaded' not in st.session_state:
    st.session_state['taux_zc_loaded'] = False
if 'dividendes_loaded' not in st.session_state:
    st.session_state['dividendes_loaded'] = False
if 'historique_loaded' not in st.session_state:
    st.session_state['historique_loaded'] = False

# =============================================================================
# CRÉATION DES ONGLETS PRINCIPAUX
# =============================================================================
tab_import, tab_pricing, tab_suivi, tab_backtest = st.tabs([
    "📥 1. Import des Données",
    "📊 2. Pricing Instantané",
    "📈 3. Suivi Temporel",
    "🧪 4. Backtesting"
])

# =============================================================================
# ONGLET 1: IMPORT DES DONNÉES
# =============================================================================
with tab_import:
    st.markdown("### 📥 Importez Vos Données de Test")
    st.info("💡 Pour cette version de test, vous pouvez utiliser les données mockées ou importer vos propres fichiers CSV.")
    
    st.divider()
    
    # Section Taux ZC
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏦 Taux Zéro-Coupon (r)")
        uploaded_taux = st.file_uploader(
            "Importer fichier taux ZC",
            type=['csv', 'xlsx'],
            key="taux_uploader",
            help="Format: date_spot, date_maturity, zc"
        )
        
        if uploaded_taux:
            df_taux = charger_taux_zc(uploaded_taux, utiliser_mock=False)
            if df_taux is not None:
                st.session_state['df_taux'] = df_taux
                st.session_state['taux_zc_loaded'] = True
        else:
            if not st.session_state.get('taux_zc_loaded', False):
                df_taux = charger_taux_zc(utiliser_mock=True)
                st.session_state['df_taux'] = df_taux
                st.session_state['taux_zc_loaded'] = True
            else:
                df_taux = st.session_state.get('df_taux')
        
        if df_taux is not None:
            with st.expander("📊 Aperçu des taux ZC"):
                st.dataframe(df_taux.head(10), use_container_width=True)
                st.caption(f"{len(df_taux)} lignes • {df_taux['date_spot'].nunique()} dates • {df_taux['date_maturity'].nunique()} maturités")
    
    with col2:
        st.markdown("#### 💰 Dividendes MASI20 (q)")
        uploaded_div = st.file_uploader(
            "Importer fichier dividendes",
            type=['csv', 'xlsx'],
            key="div_uploader",
            help="Format: ticker, poids, cours, dividende_annuel, ..."
        )
        
        if uploaded_div:
            df_div = charger_dividendes(uploaded_div, utiliser_mock=False)
            if df_div is not None:
                st.session_state['df_div'] = df_div
                st.session_state['dividendes_loaded'] = True
        else:
            if not st.session_state.get('dividendes_loaded', False):
                df_div = charger_dividendes(utiliser_mock=True)
                st.session_state['df_div'] = df_div
                st.session_state['dividendes_loaded'] = True
            else:
                df_div = st.session_state.get('df_div')
        
        if df_div is not None:
            with st.expander("📊 Aperçu des dividendes"):
                st.dataframe(df_div.head(10), use_container_width=True)
                st.caption(f"{len(df_div)} actions • Poids total: {df_div['poids'].sum():.1%}")
    
    st.divider()
    
    # Section Historique (pour backtesting)
    st.markdown("#### 📈 Historique MASI20 (pour backtesting)")
    uploaded_hist = st.file_uploader(
        "Importer historique (optionnel)",
        type=['csv', 'xlsx'],
        key="hist_uploader",
        help="Format: date, spot_masi20, prix_future_reel"
    )
    
    if uploaded_hist:
        df_hist = charger_historique_masi20(uploaded_hist, utiliser_mock=False)
        if df_hist is not None:
            st.session_state['df_hist'] = df_hist
            st.session_state['historique_loaded'] = True
    else:
        if not st.session_state.get('historique_loaded', False):
            df_hist = charger_historique_masi20(utiliser_mock=True, jours=90)
            st.session_state['df_hist'] = df_hist
            st.session_state['historique_loaded'] = True
        else:
            df_hist = st.session_state.get('df_hist')
    
    if df_hist is not None:
        with st.expander("📊 Aperçu de l'historique"):
            st.dataframe(df_hist.head(10), use_container_width=True)
            st.caption(f"{len(df_hist)} jours de données")
    
    st.divider()
    
    # Bouton de validation
    if st.button("✅ Valider les Données et Continuer", type="primary", use_container_width=True):
        st.session_state['donnees_valides'] = True
        st.success("✅ Données prêtes pour le pricing !")
        st.balloons()

# =============================================================================
# ONGLET 2: PRICING INSTANTANÉ (Cas 1)
# =============================================================================
with tab_pricing:
    st.markdown("### 📊 Pricing Instantané — Formule BAM")
    st.info("🎯 Calcule le prix théorique F₀ pour un future à une date donnée.")
    
    # Vérifier si les données sont chargées
    if not st.session_state.get('donnees_valides', False):
        st.warning("⚠️ Veuillez d'abord importer/valider les données dans l'onglet 1.")
        st.stop()
    
    st.divider()
    
    # Section 1: Paramètres de base
    st.subheader("🔧 1. Paramètres de Valorisation")
    
    col_spot, col_echeance, col_info = st.columns(3)
    
    with col_spot:
        spot = st.number_input(
            "Niveau Spot MASI20 (S)",
            min_value=1000.0,
            value=1876.54,
            step=10.0,
            format="%.2f"
        )
    
    with col_echeance:
        jours_echeance = st.slider(
            "Échéance du future (jours)",
            min_value=30,
            max_value=360,
            value=90,
            step=30
        )
    
    with col_info:
        date_echeance = datetime.now() + timedelta(days=jours_echeance)
        st.info(f"📅 Échéance: {date_echeance.strftime('%d/%m/%Y')}")
    
    st.divider()
    
    # Section 2: Calcul du taux de dividende (d)
    st.subheader("💰 2. Taux de Dividende (d)")
    
    # Convertir DataFrame en liste de dicts pour calculs
    constituents_list = df_div.to_dict('records')
    
    # Calcul du taux de dividende avec filtrage par date
    taux_dividende, df_details = calculer_taux_dividende_indice(constituents_list, date_echeance)
    
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric("Taux de Dividende (d)", f"{taux_dividende*100:.4f}%")
    with col_d2:
        st.metric("Nombre d'actions", f"{len(df_div)}")
    with col_d3:
        nb_inclus = len(df_details[df_details['Inclus'] == '✅'])
        st.metric("Dividendes inclus", f"{nb_inclus}/{len(df_details)}")
    
    with st.expander("📊 Détail du calcul par action"):
        st.dataframe(df_details, use_container_width=True)
        st.caption(f"**Taux de dividende total:** d = {taux_dividende*100:.4f}%")
    
    st.divider()
    
    # Section 3: Taux sans risque (r)
    st.subheader("🏦 3. Taux Sans Risque (r)")
    
    # Récupérer le taux ZC approprié
    r = get_taux_zc(datetime.now(), date_echeance, df_taux)
    
    st.info(f"**Taux utilisé:** r = {r*100:.2f}% (ZC le plus proche de l'échéance)")
    
    with st.expander("📊 Détail du taux ZC sélectionné"):
        # Trouver le taux sélectionné
        df_filtre = df_taux[df_taux['date_spot'] <= datetime.now()].copy()
        df_filtre['ecart'] = abs((df_filtre['date_maturity'] - date_echeance).dt.days)
        meilleur = df_filtre.loc[df_filtre['ecart'].idxmin()]
        st.write(f"**Date de publication:** {meilleur['date_spot'].strftime('%d/%m/%Y')}")
        st.write(f"**Maturité:** {meilleur['date_maturity'].strftime('%d/%m/%Y')}")
        st.write(f"**Taux:** {meilleur['zc']}%")
    
    st.divider()
    
    # Section 4: Calcul du prix théorique
    st.subheader("📊 4. Prix Théorique du Future")
    
    # Calculs
    t = jours_echeance / 360  # Base 360 selon BAM
    F0 = calculer_prix_theorique_future_bam(spot, r, taux_dividende, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, taux_dividende, t)
    
    # Affichage des résultats
    col_f0, col_base, col_cp, col_vn = st.columns(4)
    
    with col_f0:
        st.markdown(f"""
            <div style='padding:25px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                        border-radius:12px; text-align:center; color:white;'>
                <p style='margin:0; font-size:0.9em; opacity:0.9;'>Prix Théorique F₀</p>
                <p style='margin:10px 0 0 0; font-size:2.5em; font-weight:700;'>{F0:,.2f}</p>
                <p style='margin:5px 0 0 0; font-size:0.85em; opacity:0.8;'>points</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_base:
        couleur = "#10B981" if base['points'] > 0 else "#EF4444"
        regime = "Contango" if base['points'] > 0 else "Backwardation"
        st.markdown(f"""
            <div style='padding:25px; background:white; border-radius:12px; text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08); border-left:5px solid {couleur};'>
                <p style='margin:0; font-size:0.9em; color:#6B7280;'>Base (F₀ - S)</p>
                <p style='margin:10px 0 0 0; font-size:2em; font-weight:700; color:{couleur};'>{base['points']:+,.2f}</p>
                <p style='margin:5px 0 0 0; font-size:0.85em; color:#6B7280;'>{base['percentage']:+.2f}% ({regime})</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_cp:
        st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%", help="(r - d) × t")
    
    with col_vn:
        multiplicateur = config.MULTIPLICATEUR if hasattr(config, 'MULTIPLICATEUR') else 10
        st.metric("Valeur Notionnelle", f"{F0 * multiplicateur:,.0f} MAD")
    
    # Formule détaillée
    st.info(f"""
        **Formule BAM appliquée :**
        
        `F₀ = S × e^((r - d) × t)`
        
        `F₀ = {spot:,.2f} × e^(({r*100:.2f}% - {taux_dividende*100:.4f}%) × {t:.4f})`
        
        **Résultat : F₀ = {F0:,.2f} points**
    """)
    
    st.divider()
    
    # Section 5: Term Structure
    st.subheader("📈 5. Structure par Terme")
    
    echeances = [30, 90, 180, 360]
    df_term = calcul_term_structure(spot, r, taux_dividende, echeances)
    
    # Affichage des cartes
    col1, col2, col3, col4 = st.columns(4)
    for col, (_, row) in zip([col1, col2, col3, col4], df_term.iterrows()):
        couleur = "#10B981" if row['Contango'] else "#EF4444"
        col.markdown(f"""
            <div style='padding: 20px; background: white; border-radius: 12px; 
                        text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        border-left: 4px solid {couleur};'>
                <p style='margin: 0; font-size: 0.9em; color: #6B7280;'>{row['Mois']} mois</p>
                <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; color: {couleur};'>
                    {row['F0']:,.2f}
                </p>
                <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {couleur};'>
                    Base: {row['Base_pts']:+,.2f} pts
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Graphique Term Structure
    fig_term = go.Figure()
    fig_term.add_trace(go.Scatter(
        x=df_term['Mois'].astype(str) + ' mois',
        y=df_term['F0'],
        mode='lines+markers',
        name='Prix théorique',
        line=dict(color=config.COLORS.get('primary', '#1E3A5F'), width=3),
        marker=dict(size=10)
    ))
    fig_term.add_hline(y=spot, line_dash="dash", line_color="#10B981", annotation_text=f'Spot = {spot:,.2f}')
    fig_term.update_layout(
        title='Structure par Terme des Prix Futures',
        xaxis_title='Échéance',
        yaxis_title='Prix (points)',
        height=400,
        template='plotly_white'
    )
    st.plotly_chart(fig_term, use_container_width=True)
    
    # Interprétation
    base_3m = df_term[df_term['Mois'] == 3]['Base_pts'].values[0] if len(df_term[df_term['Mois'] == 3]) > 0 else 0
    if base_3m > 0:
        st.success("📈 **Contango** : Courbe ascendante (r > d) — Marché normal")
    elif base_3m < 0:
        st.warning("📉 **Backwardation** : Courbe descendante (d > r) — Dividendes élevés")
    else:
        st.info("⚖️ **Équilibre** : r ≈ d")

# =============================================================================
# ONGLET 3: SUIVI TEMPOREL (Cas 2)
# =============================================================================
with tab_suivi:
    st.markdown("### 📈 Suivi Temporel du Prix Théorique")
    st.info("🎯 Suit l'évolution de F₀ jour après jour jusqu'à l'échéance.")
    
    if not st.session_state.get('donnees_valides', False):
        st.warning("⚠️ Veuillez d'abord importer/valider les données dans l'onglet 1.")
        st.stop()
    
    st.divider()
    
    # Paramètres du suivi
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date de début", value=datetime.now())
    with col2:
        date_fin = st.date_input("Date de fin (échéance)", value=datetime.now() + timedelta(days=90))
    
    if date_fin <= date_debut:
        st.error("❌ La date de fin doit être après la date de début")
        st.stop()
    
    if st.button("🚀 Lancer le Suivi Temporel", type="primary"):
        # Récupérer les paramètres
        spot_initial = st.session_state.get('spot_initial', 1876.54)
        constituents_list = df_div.to_dict('records')
        taux_dividende, _ = calculer_taux_dividende_indice(constituents_list, date_fin)
        
        # Générer les dates (jours de bourse)
        dates = []
        current_date = date_debut
        while current_date <= date_fin:
            if current_date.weekday() < 5:  # Lundi à Vendredi
                dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Calcul jour par jour
        resultats = []
        spot_courant = spot_initial
        
        # Simulation de l'évolution du spot (marche aléatoire pour la démo)
        np.random.seed(42)
        for i, date in enumerate(dates):
            # Spot évolue légèrement (simulation)
            if i > 0:
                variation = np.random.normal(0.0002, 0.008)
                spot_courant = spot_courant * (1 + variation)
            
            # Récupérer r pour cette date
            r = get_taux_zc(date, date_fin, df_taux)
            
            # Temps restant
            jours_restants = (date_fin - date).days
            t = jours_restants / 360
            
            # Calcul F₀
            F0 = calculer_prix_theorique_future_bam(spot_courant, r, taux_dividende, t)
            
            resultats.append({
                'date': date,
                'spot': round(spot_courant, 2),
                'r': round(r * 100, 3),
                't': round(t, 4),
                'F0_theorique': round(F0, 2)
            })
        
        df_suivi = pd.DataFrame(resultats)
        
        # Graphique
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['spot'],
            name='Spot MASI20',
            line=dict(color='#1E3A5F', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['F0_theorique'],
            name='F₀ Théorique',
            line=dict(color='#F59E0B', width=2, dash='dash')
        ))
        fig.update_layout(
            title='Évolution du Prix Théorique vs Spot',
            xaxis_title='Date',
            yaxis_title='Prix (points)',
            height=500,
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        base_moyenne = (df_suivi['F0_theorique'] - df_suivi['spot']).mean()
        with col1:
            st.metric("Base Moyenne", f"{base_moyenne:+.2f} pts")
        with col2:
            st.metric("Jours de suivi", len(df_suivi))
        with col3:
            convergence = abs(df_suivi.iloc[-1]['F0_theorique'] - df_suivi.iloc[-1]['spot'])
            st.metric("Convergence à l'échéance", f"{convergence:.2f} pts")
        
        # Données brutes
        with st.expander("📊 Voir les données détaillées"):
            st.dataframe(df_suivi, use_container_width=True)

# =============================================================================
# ONGLET 4: BACKTESTING (Cas 3)
# =============================================================================
with tab_backtest:
    st.markdown("### 🧪 Backtesting — Validation du Modèle")
    st.info("🎯 Compare les prix théoriques avec les prix de marché réels.")
    
    if not st.session_state.get('donnees_valides', False):
        st.warning("⚠️ Veuillez d'abord importer/valider les données dans l'onglet 1.")
        st.stop()
    
    st.divider()
    
    # Paramètres de backtesting
    col1, col2 = st.columns(2)
    with col1:
        r_backtest = st.number_input("Taux sans risque (r) %", value=3.5, step=0.1) / 100
    with col2:
        d_backtest = st.number_input("Taux de dividende (d) %", value=0.87, step=0.01) / 100
    
    if st.button("🧮 Lancer le Backtesting", type="primary"):
        # Vérifier si on a des données réelles
        if df_hist is not None and 'prix_future_reel' in df_hist.columns:
            # Backtesting avec données réelles
            resultats = backtesting_complet(
                df_hist,
                col_spot='spot_masi20',
                col_future_reel='prix_future_reel',
                r=r_backtest,
                d=d_backtest
            )
            
            # Affichage des métriques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("MAE (Erreur Absolue)", f"{resultats['mae']:.2f} pts")
            with col2:
                st.metric("MAPE (Erreur Relative)", f"{resultats['mape']:.3f}%")
            with col3:
                st.metric("R² (Qualité)", f"{resultats['r2']:.6f}")
            
            # Interprétation
            if resultats['mape'] < 0.5:
                st.success("✅ **Modèle très précis** (MAPE < 0.5%)")
            elif resultats['mape'] < 1.5:
                st.info("ℹ️ **Modèle acceptable** (MAPE 0.5-1.5%)")
            else:
                st.warning("⚠️ **Modèle à recalibrer** (MAPE > 1.5%)")
            
            # Graphique
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=resultats['df']['date'],
                y=resultats['df']['future_reel'],
                name='Prix Marché',
                line=dict(color='#1E3A5F', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=resultats['df']['date'],
                y=resultats['df']['future_theo'],
                name='Prix Théorique',
                line=dict(color='#F59E0B', width=2, dash='dash')
            ))
            fig.update_layout(
                title='Backtesting — Prix Théorique vs Prix de Marché',
                xaxis_title='Date',
                yaxis_title='Prix (points)',
                height=500,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Données détaillées
            with st.expander("📊 Voir les données de backtesting"):
                st.dataframe(resultats['df'], use_container_width=True)
        
        else:
            # Backtesting avec données simulées
            st.warning("⚠️ Pas de prix future réel disponible — utilisation de données simulées")
            
            # Simulation
            np.random.seed(42)
            jours = 60
            dates = [datetime.now() - timedelta(days=i) for i in range(jours)][::-1]
            spots = spot * np.exp(np.cumsum(np.random.normal(0, 0.01, jours)))
            futures_theo = spots * np.exp((r_backtest - d_backtest) * (90/360))
            futures_reel = futures_theo * (1 + np.random.normal(0, 0.001, jours))
            
            # Métriques
            mae = np.mean(np.abs(futures_theo - futures_reel))
            mape = np.mean(np.abs((futures_theo - futures_reel) / futures_reel)) * 100
            r2 = 1 - np.sum((futures_theo - futures_reel)**2) / np.sum((futures_reel - np.mean(futures_reel))**2)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("MAE", f"{mae:.2f} pts")
            with col2:
                st.metric("MAPE", f"{mape:.3f}%")
            with col3:
                st.metric("R²", f"{r2:.6f}")
            
            # Graphique
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=futures_reel, name='Prix Marché (simulé)', line=dict(color='#1E3A5F')))
            fig.add_trace(go.Scatter(x=dates, y=futures_theo, name='Prix Théorique', line=dict(color='#F59E0B', dash='dash')))
            fig.update_layout(title='Backtesting (Données Simulées)', height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v{config.APP_VERSION if hasattr(config, 'APP_VERSION') else '0.3'} | Conforme BAM IN-2026-01 | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

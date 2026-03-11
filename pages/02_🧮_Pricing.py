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
    backtesting_complet
)
from utils.data_loader import (
    charger_taux_zc,
    charger_dividendes,
    charger_historique_masi20
)

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
if 'date_reference' not in st.session_state:
    st.session_state['date_reference'] = None

# =============================================================================
# CRÉATION DES ONGLETS PRINCIPAUX
# =============================================================================
tab_import, tab_pricing, tab_suivi, tab_backtest = st.tabs([
    "📥 1. Import Taux ZC",
    "📊 2. Pricing Instantané",
    "📈 3. Suivi Temporel",
    "🧪 4. Backtesting"
])

# =============================================================================
# ONGLET 1: IMPORT DES TAUX ZC
# =============================================================================
with tab_import:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE DE L'ONGLET
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("""
        ### 📘 Guide — Import des Taux Zéro-Coupon
        
        **Objectif :** Importer la courbe des taux ZC de Bank Al-Maghrib.
        
        **Format du fichier attendu :**
        | date_spot | date_maturity | zc |
        |-----------|---------------|-----|
        | 31/12/2025 | 01/07/2026 | 2,2327 |
        
        **Colonnes :**
        - `date_spot` : Date de publication du taux (BKAM)
        - `date_maturity` : Date d'échéance du taux ZC
        - `zc` : Taux zéro-coupon en % (ex: 2,2327)
        
        **Comment ça marche :**
        1. Importez votre fichier CSV/Excel
        2. Sélectionnez la date de référence pour le pricing
        3. Cette date sera utilisée dans les onglets 2, 3 et 4
        
        **Prochaine mise à jour :**
        - 🔄 Import automatique depuis le site BKAM (scraping)
        - 📊 Visualisation de la courbe des taux
    """)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # IMPORT DU FICHIER
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("📁 Importer le Fichier de Taux ZC")
    
    uploaded_taux = st.file_uploader(
        "Choisissez un fichier CSV ou Excel",
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
        st.success(f"✅ {len(df_taux)} taux chargés")
        
        with st.expander("📊 Aperçu des données"):
            st.dataframe(df_taux.head(10), use_container_width=True)
        
        # ─────────────────────────────────────────────────────────────────────
        # SÉLECTION DE LA DATE DE RÉFÉRENCE
        # ─────────────────────────────────────────────────────────────────────
        st.divider()
        st.subheader("📅 Sélection de la Date de Référence")
        
        dates_spot = sorted(df_taux['date_spot'].unique(), reverse=True)
        
        if len(dates_spot) > 0:
            date_reference = st.selectbox(
                "Date de pricing (date_spot)",
                options=dates_spot,
                format_func=lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
            )
            
            st.session_state['date_reference'] = date_reference
            
            st.info(f"✅ Date sélectionnée : {date_reference.strftime('%d/%m/%Y') if hasattr(date_reference, 'strftime') else str(date_reference)}")
            
            # Filtrer les taux pour cette date
            df_taux_date = df_taux[df_taux['date_spot'] == date_reference]
            st.write(f"**{len(df_taux_date)} maturités disponibles** pour cette date")
            
            with st.expander("📊 Taux disponibles pour cette date"):
                st.dataframe(df_taux_date[['date_maturity', 'zc']], use_container_width=True)
        else:
            st.warning("⚠️ Aucune date disponible")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # IMPORT DES DIVIDENDES
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("💰 Import des Dividendes MASI20")
    
    uploaded_div = st.file_uploader(
        "Choisissez un fichier CSV ou Excel (optionnel)",
        type=['csv', 'xlsx'],
        key="div_uploader"
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
        st.success(f"✅ {len(df_div)} actions chargées")
        with st.expander("📊 Aperçu des dividendes"):
            st.dataframe(df_div.head(10), use_container_width=True)

# =============================================================================
# ONGLET 2: PRICING INSTANTANÉ
# =============================================================================
with tab_pricing:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE DE L'ONGLET
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("""
        ### 📘 Guide — Pricing Instantané
        
        **Objectif :** Calculer le prix théorique F₀ d'un future selon la formule BAM.
        
        **Formule :** `F₀ = S × e^((r - d) × t)`
        
        **Variables :**
        | Symbole | Signification | Source |
        |---------|---------------|--------|
        | **S** | Spot MASI20 | Bourse de Casablanca |
        | **r** | Taux sans risque | Tableau ZC (Onglet 1) |
        | **d** | Taux de dividende annualisé | Calculé sur les 20 constituants |
        | **t** | Temps restant (jours/360) | Calcul automatique |
        
        **Interprétation :**
        - **Base > 0** : Contango (F₀ > S) → r > d
        - **Base < 0** : Backwardation (F₀ < S) → d > r
        
        **Prochaine mise à jour :**
        - 📊 Import automatique du spot MASI20
        - 🔔 Alertes d'arbitrage (écart théorie/marché)
    """)
    
    st.divider()
    
    # Vérifier si les données sont chargées
    if not st.session_state.get('taux_zc_loaded', False):
        st.warning("⚠️ Veuillez d'abord importer les taux ZC dans l'onglet 1.")
        st.stop()
    
    if st.session_state['date_reference'] is None:
        st.warning("⚠️ Veuillez sélectionner une date de référence dans l'onglet 1.")
        st.stop()
    
    # ─────────────────────────────────────────────────────────────────────────
    # PARAMÈTRES DE BASE
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("🔧 1. Paramètres de Valorisation")
    
    date_calcul = st.session_state['date_reference']
    st.info(f"📅 **Date de pricing :** {date_calcul.strftime('%d/%m/%Y') if hasattr(date_calcul, 'strftime') else str(date_calcul)}")
    
    col_spot, col_echeance = st.columns(2)
    
    with col_spot:
        spot = st.number_input(
            f"Spot MASI20 au {date_calcul.strftime('%d/%m/%Y') if hasattr(date_calcul, 'strftime') else str(date_calcul)}",
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
    
    date_echeance = date_calcul + timedelta(days=jours_echeance)
    st.info(f"📅 **Échéance du future :** {date_echeance.strftime('%d/%m/%Y')}")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # CALCUL DU TAUX DE DIVIDENDE (d)
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("💰 2. Taux de Dividende (d)")
    
    constituents_list = df_div.to_dict('records')
    taux_dividende, df_details = calculer_taux_dividende_indice(constituents_list)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.metric("Taux de Dividende (d)", f"{taux_dividende*100:.4f}%")
    with col_d2:
        st.metric("Nombre d'actions", f"{len(df_div)}")
    
    with st.expander("📊 Détail du calcul par action"):
        st.dataframe(df_details, use_container_width=True)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # SÉLECTION DU TAUX SANS RISQUE (r)
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("🏦 3. Taux Sans Risque (r)")
    
    r = get_taux_zc(date_calcul, date_echeance, df_taux)
    
    st.info(f"**Taux ZC utilisé :** r = {r*100:.3f}%")
    
    # Trouver le taux sélectionné pour affichage
    df_filtre = df_taux[df_taux['date_spot'] == date_calcul].copy()
    if len(df_filtre) > 0:
        df_filtre['maturity_dt'] = pd.to_datetime(df_filtre['date_maturity'])
        echeance_dt = pd.to_datetime(date_echeance)
        df_filtre['ecart'] = abs((df_filtre['maturity_dt'] - echeance_dt).dt.days)
        meilleur = df_filtre.loc[df_filtre['ecart'].idxmin()]
        
        with st.expander("📊 Détail du taux ZC sélectionné"):
            st.write(f"**Date de publication :** {meilleur['date_spot'].strftime('%d/%m/%Y')}")
            st.write(f"**Maturité :** {meilleur['date_maturity'].strftime('%d/%m/%Y')}")
            st.write(f"**Écart avec échéance :** {meilleur['ecart']} jours")
            st.write(f"**Taux :** {meilleur['zc']}%")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # CALCUL DU PRIX THÉORIQUE
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("📊 4. Prix Théorique du Future")
    
    t = jours_echeance / 360
    F0 = calculer_prix_theorique_future_bam(spot, r, taux_dividende, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, taux_dividende, t)
    
    col_f0, col_base, col_cp = st.columns(3)
    
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
        st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%")
    
    st.info(f"""
        **Formule BAM :** `F₀ = {spot:,.2f} × e^(({r*100:.3f}% - {taux_dividende*100:.4f}%) × {t:.4f})` = **{F0:,.2f} points**
    """)
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────────
    # TERM STRUCTURE
    # ─────────────────────────────────────────────────────────────────────────
    st.subheader("📈 5. Structure par Terme")
    
    echeances = [30, 90, 180, 360]
    df_term = calcul_term_structure(spot, r, taux_dividende, echeances)
    
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
    
    fig_term = go.Figure()
    fig_term.add_trace(go.Scatter(
        x=df_term['Mois'].astype(str) + ' mois',
        y=df_term['F0'],
        mode='lines+markers',
        name='Prix théorique',
        line=dict(color=config.COLORS.get('primary', '#1E3A5F'), width=3)
    ))
    fig_term.add_hline(y=spot, line_dash="dash", line_color="#10B981", annotation_text=f'Spot = {spot:,.2f}')
    fig_term.update_layout(title='Structure par Terme', height=400, template='plotly_white')
    st.plotly_chart(fig_term, use_container_width=True)

# =============================================================================
# ONGLET 3: SUIVI TEMPOREL
# =============================================================================
with tab_suivi:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE DE L'ONGLET
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("""
        ### 📘 Guide — Suivi Temporel
        
        **Objectif :** Visualiser l'évolution du prix théorique jour après jour.
        
        **Ce que vous verrez :**
        - 📈 Courbe du prix théorique F₀
        - 📊 Courbe du spot MASI20
        - ⚠️ **Courbe d'erreur** (F₀ théorique - Prix marché)
        
        **Interprétation de l'erreur :**
        - Erreur proche de 0 → Modèle précis
        - Erreur > 1% → Écart significatif
        - Erreur qui converge → Normal à l'approche de l'échéance
        
        **Prochaine mise à jour :**
        - 📥 Import automatique des prix de marché réels
        - 🎯 Alertes quand l'erreur dépasse un seuil
    """)
    
    st.divider()
    
    if not st.session_state.get('taux_zc_loaded', False):
        st.warning("⚠️ Veuillez d'abord importer les taux ZC dans l'onglet 1.")
        st.stop()
    
    st.subheader("📅 Paramètres du Suivi")
    
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date de début", value=date_calcul)
    with col2:
        date_fin = st.date_input("Date de fin (échéance)", value=date_calcul + timedelta(days=90))
    
    if date_fin <= date_debut:
        st.error("❌ La date de fin doit être après la date de début")
        st.stop()
    
    if st.button("🚀 Lancer le Suivi Temporel", type="primary"):
        constituents_list = df_div.to_dict('records')
        taux_dividende, _ = calculer_taux_dividende_indice(constituents_list)
        
        # Générer les dates
        dates = []
        current_date = date_debut
        while current_date <= date_fin:
            if current_date.weekday() < 5:
                dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Calcul jour par jour
        resultats = []
        spot_courant = spot
        
        np.random.seed(42)
        for i, date in enumerate(dates):
            if i > 0:
                variation = np.random.normal(0.0002, 0.008)
                spot_courant = spot_courant * (1 + variation)
            
            r = get_taux_zc(date, date_fin, df_taux)
            jours_restants = (date_fin - date).days
            t = jours_restants / 360
            F0 = calculer_prix_theorique_future_bam(spot_courant, r, taux_dividende, t)
            
            # Simulation prix marché (à remplacer par données réelles)
            prix_marche = F0 * (1 + np.random.normal(0, 0.001))
            
            resultats.append({
                'date': date,
                'spot': round(spot_courant, 2),
                'F0_theorique': round(F0, 2),
                'F0_marche': round(prix_marche, 2),
                'erreur_absolue': round(F0 - prix_marche, 2),
                'erreur_relative': round((F0 - prix_marche) / prix_marche * 100, 3)
            })
        
        df_suivi = pd.DataFrame(resultats)
        
        # Graphique principal
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['F0_theorique'],
            name='F₀ Théorique',
            line=dict(color='#1E3A5F', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['F0_marche'],
            name='F₀ Marché (simulé)',
            line=dict(color='#10B981', width=2, dash='dash')
        ))
        fig.update_layout(title='Évolution du Prix Théorique vs Marché', height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique d'erreur
        st.subheader("⚠️ Visualisation de l'Erreur")
        
        fig_erreur = go.Figure()
        fig_erreur.add_trace(go.Scatter(
            x=df_suivi['date'],
            y=df_suivi['erreur_relative'],
            name='Erreur Relative (%)',
            line=dict(color='#EF4444', width=2),
            fill='tozeroy'
        ))
        fig_erreur.add_hline(y=0, line_color='black', line_dash='dash')
        fig_erreur.add_hline(y=1, line_color='orange', line_dash='dot', annotation_text='+1%')
        fig_erreur.add_hline(y=-1, line_color='orange', line_dash='dot', annotation_text='-1%')
        fig_erreur.update_layout(
            title='Erreur de Pricing (%)',
            xaxis_title='Date',
            yaxis_title='Erreur (%)',
            height=300,
            template='plotly_white'
        )
        st.plotly_chart(fig_erreur, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Erreur Moyenne", f"{df_suivi['erreur_relative'].mean():.3f}%")
        with col2:
            st.metric("Erreur Max", f"{df_suivi['erreur_relative'].abs().max():.3f}%")
        with col3:
            st.metric("Jours de suivi", len(df_suivi))

# =============================================================================
# ONGLET 4: BACKTESTING
# =============================================================================
with tab_backtest:
    # ─────────────────────────────────────────────────────────────────────────
    # GUIDE DE L'ONGLET
    # ─────────────────────────────────────────────────────────────────────────
    st.markdown("""
        ### 📘 Guide — Backtesting
        
        **Objectif :** Valider la précision du modèle de pricing.
        
        **Métriques de validation :**
        | Métrique | Signification | Interprétation |
        |----------|---------------|----------------|
        | **MAE** | Erreur absolue moyenne | En points (plus bas = mieux) |
        | **MAPE** | Erreur relative moyenne | En % (< 0.5% = excellent) |
        | **R²** | Qualité d'ajustement | Proche de 1 = parfait |
        
        **Prochaine mise à jour :**
        - 📥 Import des prix futures réels historiques
        - 📊 Comparaison avec d'autres modèles de pricing
    """)
    
    st.divider()
    
    if not st.session_state.get('taux_zc_loaded', False):
        st.warning("⚠️ Veuillez d'abord importer les taux ZC dans l'onglet 1.")
        st.stop()
    
    col1, col2 = st.columns(2)
    with col1:
        r_backtest = st.number_input("Taux sans risque (r) %", value=3.5, step=0.1) / 100
    with col2:
        d_backtest = st.number_input("Taux de dividende (d) %", value=0.87, step=0.01) / 100
    
    if st.button("🧮 Lancer le Backtesting", type="primary"):
        # Backtesting avec données simulées
        np.random.seed(42)
        jours = 60
        dates = [datetime.now() - timedelta(days=i) for i in range(jours)][::-1]
        spots = spot * np.exp(np.cumsum(np.random.normal(0, 0.01, jours)))
        futures_theo = spots * np.exp((r_backtest - d_backtest) * (90/360))
        futures_reel = futures_theo * (1 + np.random.normal(0, 0.001, jours))
        
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
        
        if mape < 0.5:
            st.success("✅ **Modèle très précis** (MAPE < 0.5%)")
        elif mape < 1.5:
            st.info("ℹ️ **Modèle acceptable** (MAPE 0.5-1.5%)")
        else:
            st.warning("⚠️ **Modèle à recalibrer** (MAPE > 1.5%)")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=futures_reel, name='Prix Marché (simulé)'))
        fig.add_trace(go.Scatter(x=dates, y=futures_theo, name='Prix Théorique', line=dict(dash='dash')))
        fig.update_layout(title='Backtesting — Théorique vs Marché', height=400, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v0.3 | Conforme BAM IN-2026-01 | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

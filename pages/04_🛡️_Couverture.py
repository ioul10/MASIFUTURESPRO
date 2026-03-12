# =============================================================================
# PAGE 4: CONSTRUCTION & COUVERTURE DE PORTEFEUILLE — MASI Futures Pro
# Version 1.0
# Développeurs: OULMADANI Ilyas & ATANANE Oussama
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Portfolio & Couverture", page_icon="🛡️", layout="wide")

# =============================================================================
# CSS PERSONNALISÉ
# =============================================================================
st.markdown("""
    <style>
    .portfolio-card {
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin: 10px 0;
    }
    .weight-slider {
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# EN-TÊTE
# =============================================================================
st.title("🛡️ Construction & Couverture de Portefeuille")
st.caption("Gestion professionnelle de portefeuille et calcul de couverture optimale")

# =============================================================================
# INITIALISATION SESSION STATE
# =============================================================================
if 'portfolio_df' not in st.session_state:
    # Portfolio par défaut (MASI20)
    st.session_state['portfolio_df'] = pd.DataFrame({
        'ticker': ['ATW', 'BCP', 'IAM', 'OCP', 'CIH', 'CFG'],
        'nom': ['Attijariwafa Bank', 'Banque Populaire', 'Maroc Telecom', 
                'OCP Group', 'CIH Bank', 'CFG Bank'],
        'quantité': [1000, 5000, 2000, 100, 2000, 3000],
        'prix': [485.0, 142.5, 128.0, 7850.0, 245.0, 165.0],
        'secteur': ['Banque', 'Banque', 'Télécom', 'Mines', 'Banque', 'Banque']
    })

if 'mode_construction' not in st.session_state:
    st.session_state['mode_construction'] = False

# =============================================================================
# ONGLETS PRINCIPAUX
# =============================================================================
tab_builder, tab_coverage, tab_analytics = st.tabs([
    "🎨 1. Construction du Portefeuille",
    "🛡️ 2. Couverture (N*)",
    "📊 3. Analytics"
])

# =============================================================================
# ONGLET 1: CONSTRUCTION DU PORTEFEUILLE
# =============================================================================
with tab_builder:
    st.markdown("### 🎯 Mode de Saisie")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mode_import = st.radio(
            "Choisissez un mode :",
            ["📥 Import CSV", "🎨 Construction Interactive"],
            index=1 if st.session_state['mode_construction'] else 0
        )
    
    st.session_state['mode_construction'] = (mode_import == "🎨 Construction Interactive")
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # MODE 1: IMPORT CSV
    # ─────────────────────────────────────────────────────────────────────
    if not st.session_state['mode_construction']:
        st.markdown("### 📥 Import d'un Portefeuille (CSV)")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_pf = st.file_uploader(
                "Importer votre fichier CSV",
                type=['csv'],
                help="Format: ticker, quantité, prix, secteur"
            )
        
        with col2:
            if st.button("📄 Télécharger Template"):
                template = pd.DataFrame({
                    'ticker': ['ATW', 'BCP', 'IAM'],
                    'quantité': [1000, 5000, 2000],
                    'prix': [485.0, 142.5, 128.0],
                    'secteur': ['Banque', 'Banque', 'Télécom']
                })
                csv = template.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Template CSV",
                    data=csv,
                    file_name="template_portefeuille.csv",
                    mime="text/csv"
                )
        
        if uploaded_pf:
            try:
                df_import = pd.read_csv(uploaded_pf)
                # Validation des colonnes
                required_cols = ['ticker', 'quantité', 'prix']
                if all(col in df_import.columns for col in required_cols):
                    st.session_state['portfolio_df'] = df_import
                    st.success(f"✅ Portefeuille importé avec succès ({len(df_import)} lignes)")
                else:
                    st.error(f"❌ Colonnes manquantes. Requises: {required_cols}")
            except Exception as e:
                st.error(f"❌ Erreur de lecture: {e}")
        else:
            st.info("💡 Utilisez le bouton ci-dessus pour importer votre portefeuille")
    
    # ─────────────────────────────────────────────────────────────────────
    # MODE 2: CONSTRUCTION INTERACTIVE
    # ─────────────────────────────────────────────────────────────────────
    else:
        st.markdown("### 🎨 Construction Interactive du Portefeuille")
        
        df_pf = st.session_state['portfolio_df']
        
        # Ajouter une ligne
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("➕ Ajouter une ligne", use_container_width=True):
                new_row = pd.DataFrame({
                    'ticker': ['NEW'],
                    'nom': ['Nouvelle Action'],
                    'quantité': [100],
                    'prix': [100.0],
                    'secteur': ['Autre']
                })
                df_pf = pd.concat([df_pf, new_row], ignore_index=True)
                st.session_state['portfolio_df'] = df_pf
                st.rerun()
        
        st.divider()
        
        # Tableau éditable
        st.markdown("### 📋 Composition du Portefeuille")
        
        # Calcul des valeurs
        df_pf['valeur'] = df_pf['quantité'] * df_pf['prix']
        total_valeur = df_pf['valeur'].sum()
        df_pf['poids'] = (df_pf['valeur'] / total_valeur * 100) if total_valeur > 0 else 0
        
        # Affichage éditable ligne par ligne
        for idx in range(len(df_pf)):
            with st.container():
                col_ticker, col_nom, col_qty, col_price, col_sector, col_value, col_weight, col_action = st.columns([1.5, 2, 1, 1, 1.5, 1.5, 1.5, 0.5])
                
                with col_ticker:
                    df_pf.loc[idx, 'ticker'] = st.text_input(
                        "Ticker",
                        value=df_pf.loc[idx, 'ticker'],
                        key=f"ticker_{idx}",
                        label_visibility="collapsed"
                    )
                
                with col_nom:
                    df_pf.loc[idx, 'nom'] = st.text_input(
                        "Nom",
                        value=df_pf.loc[idx, 'nom'],
                        key=f"nom_{idx}",
                        label_visibility="collapsed"
                    )
                
                with col_qty:
                    df_pf.loc[idx, 'quantité'] = st.number_input(
                        "Quantité",
                        min_value=0,
                        value=int(df_pf.loc[idx, 'quantité']),
                        key=f"qty_{idx}",
                        label_visibility="collapsed"
                    )
                
                with col_price:
                    df_pf.loc[idx, 'prix'] = st.number_input(
                        "Prix",
                        min_value=0.0,
                        value=float(df_pf.loc[idx, 'prix']),
                        step=0.01,
                        key=f"price_{idx}",
                        label_visibility="collapsed"
                    )
                
                with col_sector:
                    df_pf.loc[idx, 'secteur'] = st.selectbox(
                        "Secteur",
                        ['Banque', 'Télécom', 'Mines', 'Immobilier', 'Distribution', 'Autre'],
                        index=['Banque', 'Télécom', 'Mines', 'Immobilier', 'Distribution', 'Autre'].index(df_pf.loc[idx, 'secteur']) if df_pf.loc[idx, 'secteur'] in ['Banque', 'Télécom', 'Mines', 'Immobilier', 'Distribution', 'Autre'] else 5,
                        key=f"sector_{idx}",
                        label_visibility="collapsed"
                    )
                
                # Calcul automatique
                valeur_ligne = df_pf.loc[idx, 'quantité'] * df_pf.loc[idx, 'prix']
                poids_ligne = (valeur_ligne / total_valeur * 100) if total_valeur > 0 else 0
                
                with col_value:
                    st.text(f"{valeur_ligne:,.0f} MAD")
                
                with col_weight:
                    st.text(f"{poids_ligne:.1f}%")
                
                with col_action:
                    if st.button("🗑️", key=f"del_{idx}"):
                        df_pf = df_pf.drop(idx).reset_index(drop=True)
                        st.session_state['portfolio_df'] = df_pf
                        st.rerun()
                
                st.markdown("---")
        
        # Sauvegarder
        st.session_state['portfolio_df'] = df_pf
    
    st.divider()
    
    # ─────────────────────────────────────────────────────────────────────
    # RÉCAPITULATIF DU PORTEFEUILLE
    # ─────────────────────────────────────────────────────────────────────
    st.markdown("### 📊 Récapitulatif du Portefeuille")
    
    df_pf = st.session_state['portfolio_df']
    df_pf['valeur'] = df_pf['quantité'] * df_pf['prix']
    total_valeur = df_pf['valeur'].sum()
    df_pf['poids'] = (df_pf['valeur'] / total_valeur * 100) if total_valeur > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Valeur Totale", f"{total_valeur:,.0f} MAD")
    with col2:
        st.metric("📦 Nombre de Lignes", len(df_pf))
    with col3:
        st.metric("🏦 Secteurs", df_pf['secteur'].nunique())
    with col4:
        avg_weight = df_pf['poids'].mean()
        st.metric("⚖️ Poids Moyen", f"{avg_weight:.1f}%")
    
    # Tableau récapitulatif
    st.dataframe(
        df_pf[['ticker', 'nom', 'quantité', 'prix', 'valeur', 'poids', 'secteur']].round(2),
        use_container_width=True
    )
    
    # Visualisation
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(
            df_pf,
            values='poids',
            names='ticker',
            title='🥧 Allocation par Action'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        df_sector = df_pf.groupby('secteur')['poids'].sum().reset_index()
        fig_bar = px.bar(
            df_sector,
            x='secteur',
            y='poids',
            title='📊 Allocation par Secteur',
            color='poids',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# ONGLET 2: COUVERTURE (N*)
# =============================================================================
with tab_coverage:
    st.markdown("### 🛡️ Calcul de la Couverture Optimale (N*)")
    
    df_pf = st.session_state['portfolio_df']
    total_valeur = df_pf['valeur'].sum()
    
    # Paramètres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        prix_future = st.number_input(
            "Prix Future MASI20",
            min_value=1000.0,
            value=1876.54,
            step=10.0
        )
    
    with col2:
        multiplicateur = st.number_input(
            "Multiplicateur (MAD/point)",
            value=10,
            disabled=True
        )
    
    with col3:
        beta_pf = st.number_input(
            "Beta du Portefeuille (β)",
            min_value=0.0,
            max_value=2.0,
            value=0.98,
            step=0.01
        )
    
    st.divider()
    
    # Calcul N*
    if st.button("🧮 Calculer N*", type="primary", use_container_width=True):
        valeur_contrat = prix_future * multiplicateur
        N_star = round(beta_pf * total_valeur / valeur_contrat)
        
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col4:
            ratio_couverture = (notionnel_couvert / total_valeur * 100) if total_valeur > 0 else 0
            st.metric("Taux de Couverture", f"{ratio_couverture:.1f}%")
        
        st.info(f"""
            **Formule :** N* = β × P / A = {beta_pf:.2f} × {total_valeur:,.0f} / {valeur_contrat:,.0f} = **{N_star:,} contrats**
        """)
        
        st.divider()
        
        # Simulation
        st.markdown("### 🧪 Simulation d'Impact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            scenario = st.slider(
                "Variation du MASI20 (%)",
                min_value=-20.0,
                max_value=20.0,
                value=-5.0,
                step=1.0
            )
        
        with col2:
            impact_non_couvert = total_valeur * (scenario / 100) * beta_pf
            impact_couvert = impact_non_couvert - (N_star * multiplicateur * prix_future * (scenario / 100))
            protection = (1 - abs(impact_couvert) / abs(impact_non_couvert)) * 100 if impact_non_couvert != 0 else 100
            
            st.metric("Impact sans Couverture", f"{impact_non_couvert:,.0f} MAD")
            st.metric("Impact avec Couverture", f"{impact_couvert:,.0f} MAD")
        
        # Barre de protection
        st.markdown(f"""
            <div style='padding:20px; background:#ecfdf5; border-radius:12px; margin:15px 0;'>
                <p style='margin:0; font-size:1.1em; font-weight:600; color:#065f46;'>
                    🛡️ Protection du portefeuille : **{protection:.1f}%**
                </p>
                <div style='background:#d1fae5; border-radius:8px; height:12px; margin-top:10px; overflow:hidden;'>
                    <div style='background:linear-gradient(90deg,#10B981,#34D399); width:{min(protection,100)}%; height:100%; border-radius:8px; transition:width 0.5s ease;'></div>
                </div>
                <p style='margin:10px 0 0 0; color:#065f46; font-size:0.9em;'>
                    Perte évitée : **{abs(impact_non_couvert - impact_couvert):,.0f} MAD**
                </p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# ONGLET 3: ANALYTICS
# =============================================================================
with tab_analytics:
    st.markdown("### 📊 Analytics du Portefeuille")
    
    df_pf = st.session_state['portfolio_df']
    
    # Métriques avancées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Concentration
        top3_weight = df_pf.nlargest(3, 'poids')['poids'].sum()
        st.metric("🎯 Concentration Top 3", f"{top3_weight:.1f}%")
    
    with col2:
        # Diversification
        nb_lignes = len(df_pf)
        poids_ideal = 100 / nb_lignes if nb_lignes > 0 else 0
        st.metric("📈 Poids Idéal (si égal)", f"{poids_ideal:.1f}%")
    
    with col3:
        # Secteur dominant
        df_sector = df_pf.groupby('secteur')['poids'].sum()
        secteur_max = df_sector.idxmax() if len(df_sector) > 0 else "N/A"
        poids_max = df_sector.max() if len(df_sector) > 0 else 0
        st.metric(f"🏦 Secteur Dominant ({secteur_max})", f"{poids_max:.1f}%")
    
    st.divider()
    
    # Graphique de concentration
    st.markdown("### 📊 Concentration du Portefeuille")
    
    df_sorted = df_pf.nlargest(10, 'poids').sort_values('poids', ascending=True)
    
    fig = px.bar(
        df_sorted,
        x='poids',
        y='ticker',
        orientation='h',
        title='📊 Top 10 Positions par Poids',
        color='poids',
        color_continuous_scale='Blues'
    )
    fig.update_layout(height=400, yaxis_title='Action', xaxis_title='Poids (%)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertes
    st.divider()
    st.markdown("### ⚠️ Alertes de Concentration")
    
    alertes = []
    
    if top3_weight > 50:
        alertes.append(f"⚠️ **Forte concentration** : Les 3 premières positions représentent {top3_weight:.1f}% du portefeuille")
    
    if poids_max > 30:
        alertes.append(f"⚠️ **Secteur {secteur_max} dominant** : {poids_max:.1f}% du portefeuille")
    
    if nb_lignes < 10:
        alertes.append(f"⚠️ **Portefeuille peu diversifié** : Seulement {nb_lignes} lignes")
    
    if len(alertes) == 0:
        st.success("✅ **Portefeuille bien diversifié** - Aucune alerte majeure")
    else:
        for alerte in alertes:
            st.warning(alerte)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v1.0 | Portfolio & Couverture | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

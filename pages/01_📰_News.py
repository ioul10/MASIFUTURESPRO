# ============================================
# PAGE 1: NEWS & INDICES - MASI Futures Pro
# Version Organisée avec 3 Onglets
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
# NIVEAUX ACTUELS (Toujours visible)
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
# GÉNÉRATION DES DONNÉES SIMULÉES
# ────────────────────────────────────────────
def generer_donnees_historiques(nom_indice, niveau_actuel, jours=90):
    """Génère des données historiques simulées réalistes"""
    np.random.seed(42 if nom_indice == 'MASI' else 43)
    
    dates = [datetime.now() - timedelta(days=i) for i in range(jours)]
    dates.reverse()
    
    # Génération de prix avec tendance et volatilité
    base_price = niveau_actuel
    returns = np.random.normal(0.0001, 0.015, jours)
    prices = base_price * np.exp(np.cumsum(returns))
    prices = prices * (base_price / prices[-1])
    
    # Génération OHLC (Open, High, Low, Close)
    opens = prices * (1 + np.random.uniform(-0.005, 0.005, jours))
    highs = np.maximum(opens, prices) * (1 + np.random.uniform(0, 0.01, jours))
    lows = np.minimum(opens, prices) * (1 - np.random.uniform(0, 0.01, jours))
    
    # Calcul des rendements
    returns_daily = np.diff(prices) / prices[:-1]
    
    return {
        'dates': dates,
        'prices': prices,
        'opens': opens,
        'highs': highs,
        'lows': lows,
        'returns': returns_daily
    }

# Récupérer les niveaux actuels
niveau_masi = indices_data['MASI']['niveau'] if indices_data else 16655.58
niveau_masi20 = indices_data['MASI20']['niveau'] if indices_data and 'MASI20' in indices_data else 1876.54

# Générer les données
donnees_masi = generer_donnees_historiques('MASI', niveau_masi)
donnees_masi20 = generer_donnees_historiques('MASI20', niveau_masi20)

# ────────────────────────────────────────────
# FONCTION POUR CALCULER LES STATISTIQUES
# ────────────────────────────────────────────
def calculer_statistiques(donnees, nom_indice):
    """Calcule toutes les statistiques pour un indice"""
    prices = donnees['prices']
    returns = donnees['returns']
    
    stats = {
        'prix_minimum': min(prices),
        'prix_maximum': max(prices),
        'moyenne': np.mean(prices),
        'mediane': np.median(prices),
        'amplitude': max(prices) - min(prices),
        'performance_cumulee': ((prices[-1] - prices[0]) / prices[0]) * 100,
        'volatilite_quotidienne': np.std(returns) * 100,
        'volatilite_annualisee': np.std(returns) * np.sqrt(252) * 100,
        'rendement_minimum': min(returns) * 100,
        'rendement_maximum': max(returns) * 100,
        'etendu_rendements': (max(returns) - min(returns)) * 100,
        'skewness': pd.Series(returns).skew(),
        'kurtosis': pd.Series(returns).kurtosis()
    }
    
    return stats

# Calculer les statistiques
stats_masi = calculer_statistiques(donnees_masi, 'MASI')
stats_masi20 = calculer_statistiques(donnees_masi20, 'MASI20')

# ────────────────────────────────────────────
# INTERPRÉTATIONS DES STATISTIQUES
# ────────────────────────────────────────────
interpretations = {
    'prix_minimum': "Le prix le plus bas atteint sur la période. Indique le support historique.",
    'prix_maximum': "Le prix le plus haut atteint sur la période. Indique la résistance historique.",
    'moyenne': "Le prix moyen sur la période. Utile pour identifier si le cours actuel est au-dessus ou en-dessous de la normale.",
    'mediane': "Le prix médian (50% des observations sont au-dessus, 50% en-dessous). Moins sensible aux valeurs extrêmes que la moyenne.",
    'amplitude': "La différence entre le plus haut et le plus bas. Mesure l'étendue des variations de prix.",
    'performance_cumulee': "Le rendement total sur la période en pourcentage. Montre la performance globale.",
    'volatilite_quotidienne': "L'écart-type des rendements journaliers. Mesure le risque quotidien. Plus c'est élevé, plus le prix fluctue.",
    'volatilite_annualisee': "La volatilité quotidienne multipliée par √252 (jours de trading). Standard pour comparer les risques annuels.",
    'rendement_minimum': "La pire perte journalière sur la période. Utile pour évaluer le risque de perte maximale.",
    'rendement_maximum': "Le meilleur gain journalière sur la période. Montre le potentiel de gain maximal.",
    'etendu_rendements': "La différence entre le meilleur et le pire rendement journalier. Mesure l'amplitude des variations quotidiennes.",
    'skewness': "Mesure l'asymétrie de la distribution des rendements.\n• Positif: Plus de gains extrêmes\n• Négatif: Plus de pertes extrêmes\n• Zéro: Distribution symétrique",
    'kurtosis': "Mesure l'aplatissement de la distribution.\n• Élevé (>3): Plus de valeurs extrêmes (fat tails)\n• Faible (<3): Distribution plus plate\n• Normal: 3 pour une distribution normale"
}

# ────────────────────────────────────────────
# ONGLETS PRINCIPAUX
# ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🇲🇦 MASI", "🇲🇦 MASI20", "📊 Comparaison"])

# ────────────────────────────────────────────
# ONGLET 1: MASI
# ────────────────────────────────────────────
with tab1:
    st.markdown("### 📈 Évolution du MASI")
    
    # Graphique
    fig_masi = go.Figure()
    
    fig_masi.add_trace(go.Scatter(
        x=donnees_masi['dates'],
        y=donnees_masi['prices'],
        name='MASI',
        line=dict(color='#10B981', width=2),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig_masi.update_layout(
        title='Évolution du MASI sur 90 jours',
        xaxis_title='Date',
        yaxis_title='Niveau de l\'indice',
        height=450,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_masi, use_container_width=True)
    
    # Tableau détaillé OHLC
    st.divider()
    st.markdown("### 📋 Données Détaillées")
    
    df_masi = pd.DataFrame({
        'Date': [d.strftime('%d/%m/%Y') for d in donnees_masi['dates']],
        'Price': donnees_masi['prices'],
        'Open': donnees_masi['opens'],
        'High': donnees_masi['highs'],
        'Low': donnees_masi['lows'],
        'Change %': np.concatenate([[0], np.diff(donnees_masi['prices']) / donnees_masi['prices'][:-1] * 100])
    })
    
    st.dataframe(
        df_masi.style.format({
            'Price': '{:,.2f}',
            'Open': '{:,.2f}',
            'High': '{:,.2f}',
            'Low': '{:,.2f}',
            'Change %': '{:+.2f}%'
        }),
        use_container_width=True,
        height=400
    )
    
    # Statistiques
    st.divider()
    st.markdown("### 📊 Mesures Statistiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Prix et Performance**")
        for key in ['prix_minimum', 'prix_maximum', 'moyenne', 'mediane', 'amplitude', 'performance_cumulee']:
            valeur = stats_masi[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    if key in ['moyenne', 'mediane', 'prix_minimum', 'prix_maximum', 'amplitude']:
                        st.metric(key.replace('_', ' ').title(), f"{valeur:,.2f}")
                    else:
                        st.metric(key.replace('_', ' ').title(), f"{valeur:+.2f}%")
                with col_info:
                    if st.button("?", key=f"masi_{key}"):
                        st.info(interpretations[key])
    
    with col2:
        st.markdown("**Rendements et Volatilité**")
        for key in ['volatilite_quotidienne', 'volatilite_annualisee', 'rendement_minimum', 'rendement_maximum', 'etendu_rendements']:
            valeur = stats_masi[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    st.metric(key.replace('_', ' ').title(), f"{valeur:.2f}%")
                with col_info:
                    if st.button("?", key=f"masi_{key}"):
                        st.info(interpretations[key])
        
        st.markdown("**Distribution**")
        for key in ['skewness', 'kurtosis']:
            valeur = stats_masi[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    st.metric(key.title(), f"{valeur:.4f}")
                with col_info:
                    if st.button("?", key=f"masi_{key}"):
                        st.info(interpretations[key])

# ────────────────────────────────────────────
# ONGLET 2: MASI20
# ────────────────────────────────────────────
with tab2:
    st.markdown("### 📈 Évolution du MASI20")
    
    # Graphique
    fig_masi20 = go.Figure()
    
    fig_masi20.add_trace(go.Scatter(
        x=donnees_masi20['dates'],
        y=donnees_masi20['prices'],
        name='MASI20',
        line=dict(color=config.COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 95, 0.1)'
    ))
    
    fig_masi20.update_layout(
        title='Évolution du MASI20 sur 90 jours',
        xaxis_title='Date',
        yaxis_title='Niveau de l\'indice',
        height=450,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_masi20, use_container_width=True)
    
    # Tableau détaillé OHLC
    st.divider()
    st.markdown("### 📋 Données Détaillées")
    
    df_masi20 = pd.DataFrame({
        'Date': [d.strftime('%d/%m/%Y') for d in donnees_masi20['dates']],
        'Price': donnees_masi20['prices'],
        'Open': donnees_masi20['opens'],
        'High': donnees_masi20['highs'],
        'Low': donnees_masi20['lows'],
        'Change %': np.concatenate([[0], np.diff(donnees_masi20['prices']) / donnees_masi20['prices'][:-1] * 100])
    })
    
    st.dataframe(
        df_masi20.style.format({
            'Price': '{:,.2f}',
            'Open': '{:,.2f}',
            'High': '{:,.2f}',
            'Low': '{:,.2f}',
            'Change %': '{:+.2f}%'
        }),
        use_container_width=True,
        height=400
    )
    
    # Statistiques
    st.divider()
    st.markdown("### 📊 Mesures Statistiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Prix et Performance**")
        for key in ['prix_minimum', 'prix_maximum', 'moyenne', 'mediane', 'amplitude', 'performance_cumulee']:
            valeur = stats_masi20[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    if key in ['moyenne', 'mediane', 'prix_minimum', 'prix_maximum', 'amplitude']:
                        st.metric(key.replace('_', ' ').title(), f"{valeur:,.2f}")
                    else:
                        st.metric(key.replace('_', ' ').title(), f"{valeur:+.2f}%")
                with col_info:
                    if st.button("?", key=f"masi20_{key}"):
                        st.info(interpretations[key])
    
    with col2:
        st.markdown("**Rendements et Volatilité**")
        for key in ['volatilite_quotidienne', 'volatilite_annualisee', 'rendement_minimum', 'rendement_maximum', 'etendu_rendements']:
            valeur = stats_masi20[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    st.metric(key.replace('_', ' ').title(), f"{valeur:.2f}%")
                with col_info:
                    if st.button("?", key=f"masi20_{key}"):
                        st.info(interpretations[key])
        
        st.markdown("**Distribution**")
        for key in ['skewness', 'kurtosis']:
            valeur = stats_masi20[key]
            with st.container():
                col_stat, col_info = st.columns([4, 1])
                with col_stat:
                    st.metric(key.title(), f"{valeur:.4f}")
                with col_info:
                    if st.button("?", key=f"masi20_{key}"):
                        st.info(interpretations[key])

# ────────────────────────────────────────────
# ONGLET 3: COMPARAISON
# ────────────────────────────────────────────
with tab3:
    st.markdown("### 📊 Comparaison MASI vs MASI20")
    
    # Normaliser pour comparaison
    masi_normalized = [p / donnees_masi['prices'][0] * 100 for p in donnees_masi['prices']]
    masi20_normalized = [p / donnees_masi20['prices'][0] * 100 for p in donnees_masi20['prices']]
    
    fig_compare = go.Figure()
    
    fig_compare.add_trace(go.Scatter(
        x=donnees_masi['dates'],
        y=masi_normalized,
        name='MASI',
        line=dict(color='#10B981', width=2)
    ))
    
    fig_compare.add_trace(go.Scatter(
        x=donnees_masi20['dates'],
        y=masi20_normalized,
        name='MASI20',
        line=dict(color=config.COLORS['primary'], width=2, dash='dash')
    ))
    
    fig_compare.update_layout(
        title='Performance Relative (Base 100)',
        xaxis_title='Date',
        yaxis_title='Performance (%)',
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Tableau comparatif des statistiques
    st.divider()
    st.markdown("### 📋 Tableau Comparatif des Statistiques")
    
    df_compare = pd.DataFrame({
        'Statistique': [
            'Prix Minimum', 'Prix Maximum', 'Moyenne', 'Médiane',
            'Performance Cumulée', 'Volatilité Annualisée',
            'Rendement Maximum', 'Rendement Minimum', 'Skewness'
        ],
        'MASI': [
            f"{stats_masi['prix_minimum']:,.2f}",
            f"{stats_masi['prix_maximum']:,.2f}",
            f"{stats_masi['moyenne']:,.2f}",
            f"{stats_masi['mediane']:,.2f}",
            f"{stats_masi['performance_cumulee']:+.2f}%",
            f"{stats_masi['volatilite_annualisee']:.2f}%",
            f"{stats_masi['rendement_maximum']:+.2f}%",
            f"{stats_masi['rendement_minimum']:+.2f}%",
            f"{stats_masi['skewness']:.4f}"
        ],
        'MASI20': [
            f"{stats_masi20['prix_minimum']:,.2f}",
            f"{stats_masi20['prix_maximum']:,.2f}",
            f"{stats_masi20['moyenne']:,.2f}",
            f"{stats_masi20['mediane']:,.2f}",
            f"{stats_masi20['performance_cumulee']:+.2f}%",
            f"{stats_masi20['volatilite_annualisee']:.2f}%",
            f"{stats_masi20['rendement_maximum']:+.2f}%",
            f"{stats_masi20['rendement_minimum']:+.2f}%",
            f"{stats_masi20['skewness']:.4f}"
        ]
    })
    
    st.dataframe(df_compare, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────
# ACTUALITÉS (En bas de page)
# ────────────────────────────────────────────
st.divider()
render_news_widget(max_news=5)

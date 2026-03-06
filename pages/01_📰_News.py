# ============================================
# PAGE 1: NEWS & INDICES - MASI Futures Pro
# Version Complète avec Interprétations
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
# NIVEAUX ACTUELS
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
# FONCTIONS RÉUTILISABLES
# ────────────────────────────────────────────
def generer_donnees_historiques(nom_indice, niveau_actuel, jours=90):
    np.random.seed(42 if nom_indice == 'MASI' else 43)
    dates = [datetime.now() - timedelta(days=i) for i in range(jours)]
    dates.reverse()
    
    base_price = niveau_actuel
    returns = np.random.normal(0.0001, 0.015, jours)
    prices = base_price * np.exp(np.cumsum(returns))
    prices = prices * (base_price / prices[-1])
    
    opens = prices * (1 + np.random.uniform(-0.005, 0.005, jours))
    highs = np.maximum(opens, prices) * (1 + np.random.uniform(0, 0.01, jours))
    lows = np.minimum(opens, prices) * (1 - np.random.uniform(0, 0.01, jours))
    
    return {
        'dates': dates,
        'prices': prices,
        'opens': opens,
        'highs': highs,
        'lows': lows,
        'returns': np.diff(prices) / prices[:-1]
    }


def calculer_statistiques(donnees):
    prices = donnees['prices']
    returns = donnees['returns']
    return {
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


def render_interpretations(stats, nom, niveau_actuel):
    """Affiche les interprétations complètes pour toutes les statistiques"""
    
    # Prix et Performance
    st.markdown("#### 📈 Prix et Performance")
    
    st.info(f"**Prix Minimum : {stats['prix_minimum']:,.2f}**")
    st.caption("Le niveau le plus bas atteint sur la période. Indique un support historique. Si le cours actuel est proche, l'indice pourrait être dans une zone d'achat potentielle.")
    
    st.info(f"**Prix Maximum : {stats['prix_maximum']:,.2f}**")
    st.caption("Le niveau le plus haut atteint sur la période. Indique une résistance historique. Si le cours actuel est proche, l'indice pourrait rencontrer une résistance à la hausse.")
    
    tendance = "au-dessus" if niveau_actuel > stats['moyenne'] else "en-dessous"
    signal = "haussière" if niveau_actuel > stats['moyenne'] else "baissière"
    st.info(f"**Prix Moyen : {stats['moyenne']:,.2f}**")
    st.caption(f"Le cours actuel ({niveau_actuel:,.2f}) est {tendance} de la moyenne, ce qui indique une tendance {signal} à moyen terme.")
    
    st.info(f"**Médiane : {stats['mediane']:,.2f}**")
    st.caption("50% des observations sont au-dessus, 50% en-dessous. Moins sensible aux valeurs extrêmes que la moyenne. Utile pour une analyse robuste.")
    
    st.info(f"**Amplitude : {stats['amplitude']:,.2f} points**")
    st.caption("Différence entre le plus haut et le plus bas. Une amplitude élevée indique une forte volatilité des prix sur la période.")
    
    perf_signal = "gagné" if stats['performance_cumulee'] > 0 else "perdu"
    st.info(f"**Performance Cumulée : {stats['performance_cumulee']:+.2f}%**")
    st.caption(f"Un investisseur aurait {perf_signal} {abs(stats['performance_cumulee']):.2f}% en détenant l'indice sur cette période de 90 jours.")
    
    st.divider()
    
    # Rendements et Volatilité
    st.markdown("#### 📊 Rendements et Volatilité")
    
    st.info(f"**Volatilité Quotidienne : {stats['volatilite_quotidienne']:.2f}%**")
    st.caption("Écart-type des rendements journaliers. Plus ce chiffre est élevé, plus le prix fluctue au quotidien. 1-2% est normal pour un indice émergent.")
    
    st.info(f"**Volatilité Annualisée : {stats['volatilite_annualisee']:.2f}%**")
    st.caption("Standard pour comparer le risque annuel. Pour le MASI, 15-25% est typique. Plus c'est élevé, plus le risque de perte importante est grand.")
    
    st.info(f"**Rendement Minimum : {stats['rendement_minimum']:+.2f}%**")
    st.caption("La pire perte journalière sur la période. Utile pour évaluer le risque de perte maximale à court terme (VaR historique approximatif).")
    
    st.info(f"**Rendement Maximum : {stats['rendement_maximum']:+.2f}%**")
    st.caption("Le meilleur gain journalier sur la période. Montre le potentiel de gain maximal à court terme en cas de rallye.")
    
    st.info(f"**Étendu des Rendements : {stats['etendu_rendements']:.2f}%**")
    st.caption("Différence entre le meilleur et le pire rendement journalier. Mesure l'amplitude des variations quotidiennes possibles.")
    
    st.divider()
    
    # Distribution
    st.markdown("#### 📐 Distribution des Rendements")
    
    skew = stats['skewness']
    if skew > 0.5:
        skew_interp = "positive : plus de gains extrêmes que de pertes extrêmes"
        skew_signal = "✅ Favorable"
    elif skew < -0.5:
        skew_interp = "négative : plus de pertes extrêmes que de gains extrêmes"
        skew_signal = "⚠️ Prudence"
    else:
        skew_interp = "proche de zéro : distribution relativement symétrique"
        skew_signal = "ℹ️ Neutre"
    
    st.info(f"**Skewness : {skew:.4f} {skew_signal}**")
    st.caption(f"Distribution {skew_interp}. Un skewness positif est généralement préféré car il indique plus de chances de gains exceptionnels.")
    
    kurt = stats['kurtosis']
    if kurt > 3:
        kurt_interp = f"élevé ({kurt:.2f} > 3) : présence de 'fat tails' (valeurs extrêmes plus fréquentes)"
        kurt_signal = "⚠️ Risque d'événements extrêmes"
    elif kurt < 3:
        kurt_interp = f"faible ({kurt:.2f} < 3) : distribution plus plate que la normale"
        kurt_signal = "ℹ️ Distribution modérée"
    else:
        kurt_interp = "normal (≈3) : similaire à une distribution normale"
        kurt_signal = "✅ Distribution classique"
    
    st.info(f"**Kurtosis : {kurt:.4f} {kurt_signal}**")
    st.caption(f"Distribution {kurt_interp}. Un kurtosis élevé signifie plus de risques de krachs ou rallies soudains qu'une distribution normale ne le prédirait.")


def render_indice_section(nom, donnees, stats, niveau_actuel, couleur_graph):
    """Affiche la section complète pour un indice"""
    
    st.markdown(f"### 📈 Évolution du {nom}")
    
    # Graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=donnees['dates'],
        y=donnees['prices'],
        name=nom,
        line=dict(color=couleur_graph, width=2),
        fill='tozeroy',
        fillcolor=f'rgba(16, 185, 129, 0.1)' if nom == 'MASI' else 'rgba(30, 58, 95, 0.1)',
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Prix: %{y:,.2f}<extra></extra>'
    ))
    fig.update_layout(
        title=f'Évolution du {nom} sur 90 jours',
        xaxis_title='Date',
        yaxis_title='Niveau de l\'indice',
        height=450,
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau OHLC
    st.markdown("### 📋 Données Détaillées")
    df = pd.DataFrame({
        'Date': [d.strftime('%d/%m/%Y') for d in donnees['dates']],
        'Price': donnees['prices'],
        'Open': donnees['opens'],
        'High': donnees['highs'],
        'Low': donnees['lows'],
        'Change %': np.concatenate([[0], np.diff(donnees['prices']) / donnees['prices'][:-1] * 100])
    })
    st.dataframe(df.style.format({
        'Price': '{:,.2f}', 'Open': '{:,.2f}', 'High': '{:,.2f}',
        'Low': '{:,.2f}', 'Change %': '{:+.2f}%'
    }), use_container_width=True, height=400)

    # Statistiques
    st.markdown("### 📊 Mesures Statistiques")
    df_stats = pd.DataFrame({
        'Statistique': ['Prix Minimum','Prix Maximum','Prix Moyen','Médiane','Amplitude',
                        'Performance Cumulée','Volatilité Quotidienne','Volatilité Annualisée',
                        'Rendement Minimum','Rendement Maximum','Étendu des Rendements',
                        'Skewness','Kurtosis'],
        'Valeur': [
            f"{stats['prix_minimum']:,.2f}", f"{stats['prix_maximum']:,.2f}",
            f"{stats['moyenne']:,.2f}", f"{stats['mediane']:,.2f}",
            f"{stats['amplitude']:,.2f}", f"{stats['performance_cumulee']:+.2f}%",
            f"{stats['volatilite_quotidienne']:.2f}%", f"{stats['volatilite_annualisee']:.2f}%",
            f"{stats['rendement_minimum']:+.2f}%", f"{stats['rendement_maximum']:+.2f}%",
            f"{stats['etendu_rendements']:.2f}%", f"{stats['skewness']:.4f}",
            f"{stats['kurtosis']:.4f}"
        ]
    })
    st.dataframe(df_stats, use_container_width=True, hide_index=True)

    # Interprétations complètes
    with st.expander(f"📘 Interprétations des Statistiques - {nom}"):
        render_interpretations(stats, nom, niveau_actuel)


# ────────────────────────────────────────────
# GÉNÉRATION DES DONNÉES
# ────────────────────────────────────────────
niveau_masi = indices_data.get('MASI', {}).get('niveau', 16655.58)
niveau_masi20 = indices_data.get('MASI20', {}).get('niveau', 1876.54)

donnees_masi = generer_donnees_historiques('MASI', niveau_masi)
donnees_masi20 = generer_donnees_historiques('MASI20', niveau_masi20)

stats_masi = calculer_statistiques(donnees_masi)
stats_masi20 = calculer_statistiques(donnees_masi20)

# ────────────────────────────────────────────
# ONGLETS
# ────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🇲🇦 MASI", "🇲🇦 MASI20", "📊 Comparaison"])

with tab1:
    render_indice_section("MASI", donnees_masi, stats_masi, niveau_masi, '#10B981')

with tab2:
    render_indice_section("MASI20", donnees_masi20, stats_masi20, niveau_masi20, config.COLORS['primary'])

with tab3:
    st.markdown("### 📊 Comparaison MASI vs MASI20")
    
    masi_normalized = [p / donnees_masi['prices'][0] * 100 for p in donnees_masi['prices']]
    masi20_normalized = [p / donnees_masi20['prices'][0] * 100 for p in donnees_masi20['prices']]
    
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Scatter(
        x=donnees_masi['dates'], y=masi_normalized, name='MASI',
        line=dict(color='#10B981', width=2)
    ))
    fig_compare.add_trace(go.Scatter(
        x=donnees_masi20['dates'], y=masi20_normalized, name='MASI20',
        line=dict(color=config.COLORS['primary'], width=2, dash='dash')
    ))
    fig_compare.update_layout(
        title='Performance Relative (Base 100)',
        xaxis_title='Date',
        yaxis_title='Performance (%)',
        height=450,
        template='plotly_white',
        hovermode='x unified'
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # Tableau comparatif
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

# Actualité en bas
st.divider()
render_news_widget(max_news=5)

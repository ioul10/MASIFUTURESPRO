# ============================================
# PAGE 2: PRICING - MASI Futures Pro
# Version Organisée et Professionnelle
# ============================================

import streamlit as st
import config
from utils.calculations import *
from utils.scraping import get_spot_indice, get_taux_sans_risque
import plotly.graph_objects as go
import numpy as np

# Configuration de la page
st.title("🧮 Pricing des Futures sur Indice")

st.markdown("""
    <div style='padding: 20px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                border-left: 5px solid #1E3A5F; border-radius: 8px; margin-bottom: 30px;'>
        <h3 style='margin: 0 0 10px 0; color: #1E3A5F;'>📐 Formule de Pricing</h3>
        <p style='margin: 0; font-size: 1.1em; font-family: monospace;'>
            F₀ = S₀ × e^((r-q)T)
        </p>
        <p style='margin: 10px 0 0 0; color: #6B7280; font-size: 0.9em;'>
            Où : S₀ = Spot, r = Taux sans risque, q = Dividendes, T = Maturité (années)
        </p>
    </div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────
# SECTION 1 : PARAMÈTRES D'ENTRÉE
# ────────────────────────────────────────────
st.markdown("### 🔧 Paramètres de Valorisation")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Indice Sous-Jacent**")
    indice = st.selectbox(
        "Indice",
        config.INDICES,
        index=0,
        label_visibility="collapsed"
    )
    
    spot_auto = get_spot_indice(indice)
    spot = st.number_input(
        f"Niveau Spot {indice}",
        min_value=1000.0,
        value=spot_auto,
        step=50.0,
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**💰 Taux et Dividendes**")
    taux_bkam = get_taux_sans_risque('10ans')
    r = st.number_input(
        "Taux sans risque r (%)",
        min_value=0.0,
        max_value=15.0,
        value=taux_bkam * 100,
        step=0.1,
        label_visibility="collapsed"
    ) / 100
    
    q = st.number_input(
        "Rendement dividendes q (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.1,
        label_visibility="collapsed"
    ) / 100

with col3:
    st.markdown("**📅 Maturité**")
    jours = st.number_input(
        "Jours jusqu'échéance",
        min_value=1,
        max_value=365,
        value=90,
        step=1,
        label_visibility="collapsed"
    )
    T = jours_vers_annees(jours)

# ────────────────────────────────────────────
# SECTION 2 : CALCULS
# ────────────────────────────────────────────
F0 = prix_future_theorique(spot, r, q, T)
base = base_future(F0, spot)
sensibilites = calcul_sensibilites(spot, r, q, T)
cout_port = calcul_cout_portage(r, q, T)
valeur_notionnelle = F0 * config.MULTIPLICATEUR

# ────────────────────────────────────────────
# SECTION 3 : RÉSULTATS PRINCIPAUX
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Résultats de la Valorisation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%); 
                    border-radius: 12px; text-align: center; color: white;
                    box-shadow: 0 4px 12px rgba(30, 58, 95, 0.3);'>
            <p style='margin: 0; font-size: 0.9em; opacity: 0.9;'>Prix Future F₀</p>
            <p style='margin: 10px 0 0 0; font-size: 2.2em; font-weight: 700;'>
                {F0:,.2f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; opacity: 0.8;'>points</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    couleur_base = "#10B981" if base['points'] > 0 else "#EF4444"
    st.markdown(f"""
        <div style='padding: 25px; background: white; border-radius: 12px; text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid {couleur_base};'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280;'>Base (F₀-S₀)</p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; color: {couleur_base};'>
                {base['points']:+,.2f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: #6B7280;'>
                {base['percentage']:+.2f}%
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='padding: 25px; background: white; border-radius: 12px; text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #3B82F6;'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280;'>Coût de Portage</p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; color: #3B82F6;'>
                {cout_port*100:+.2f}%
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: #6B7280;'>
                (r-q)×T
            </p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style='padding: 25px; background: white; border-radius: 12px; text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #F59E0B;'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280;'>Valeur Notionnelle</p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; color: #F59E0B;'>
                {valeur_notionnelle:,.0f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: #6B7280;'>
                MAD
            </p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# SECTION 4 : SENSIBILITÉS (GRECQUES)
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Sensibilités (Grecques)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Sensibilités Absolues")
    st.metric("dF/dr (Taux)", f"{sensibilites['df_dr']:,.2f} pts/+1% taux")
    st.metric("dF/dq (Dividendes)", f"{sensibilites['df_dq']:,.2f} pts/+1% div.")
    st.metric("dF/dS (Delta)", f"{sensibilites['df_dS']:.4f}")
    st.metric("dF/dT (Theta)", f"{sensibilites['df_dT']:,.2f} pts/an")

with col2:
    st.markdown("#### Impact Relatif")
    st.metric("+1% sur r", f"{sensibilites['df_dr']/F0*100:+.2f}%")
    st.metric("+1% sur q", f"{sensibilites['df_dq']/F0*100:+.2f}%")
    st.metric("+1 point sur S", f"{1/F0*100:+.4f}%")
    st.metric("+1 mois sur T", f"{sensibilites['df_dT']/F0*(1/12)*100:+.2f}%")

# ────────────────────────────────────────────
# SECTION 5 : TERM STRUCTURE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Structure par Terme des Futures")

echeances = [30, 60, 90, 120, 180, 252]
df_term = calcul_term_structure(spot, r, q, echeances)

# Affichage simple du tableau (sans style complexe)
st.dataframe(
    df_term.round({
        'F0': 2,
        'Base_pts': 2,
        'Base_pct': 2
    }),
    use_container_width=True,
    hide_index=True
)

# Graphique de la term structure
fig_term = go.Figure()

fig_term.add_trace(go.Scatter(
    x=df_term['Mois'],
    y=df_term['F0'],
    mode='lines+markers',
    name='Prix Future',
    line=dict(color=config.COLORS['primary'], width=3),
    marker=dict(size=8)
))

fig_term.add_hline(
    y=spot,
    line_dash="dash",
    line_color="#10B981",
    annotation_text=f"Spot = {spot:,.0f}",
    annotation_position="top left"
)

fig_term.update_layout(
    title='Courbe des Futures par Échéance',
    xaxis_title='Mois jusqu\'à l\'échéance',
    yaxis_title='Prix Future (points)',
    height=400,
    template='plotly_white',
    xaxis=dict(tickmode='linear', tick0=1, dtick=1)
)

st.plotly_chart(fig_term, use_container_width=True)
# ────────────────────────────────────────────
# SECTION 6 : ARBITRAGE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 🎯 Détection d'Arbitrage")

col1, col2 = st.columns([3, 1])

with col1:
    prix_marche = st.number_input(
        "Prix Future Observé sur le Marché (optionnel)",
        min_value=0.0,
        value=float(F0),
        step=10.0
    )

with col2:
    seuil = st.slider(
        "Seuil d'arbitrage (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1
    ) / 100

# Analyse d'arbitrage
arbitrage = detecter_arbitrage(prix_marche, F0, seuil)

# Affichage du résultat
if arbitrage['arbitrage_possible']:
    st.markdown(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%); 
                    border-left: 5px solid #F59E0B; border-radius: 12px; margin: 20px 0;
                    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);'>
            <h3 style='margin: 0 0 15px 0; color: #C2410C;'>
                ⚠️ {arbitrage['statut']}
            </h3>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
                <div>
                    <p style='margin: 5px 0;'><strong>Signal :</strong> {arbitrage['signal']}</p>
                    <p style='margin: 5px 0;'><strong>Écart :</strong> {arbitrage['ecart_pct']:+.2f}%</p>
                </div>
                <div>
                    <p style='margin: 5px 0;'><strong>Stratégie :</strong></p>
                    <p style='margin: 5px 0; color: #C2410C; font-weight: 600;'>
                        {arbitrage['strategie']}
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); 
                    border-left: 5px solid #10B981; border-radius: 12px; margin: 20px 0;
                    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);'>
            <h3 style='margin: 0 0 15px 0; color: #047857;'>
                ✅ {arbitrage['statut']}
            </h3>
            <p style='margin: 5px 0;'>
                L'écart de {arbitrage['ecart_pct']:+.2f}% est dans la zone normale 
                (seuil: ±{seuil*100:.1f}%).
            </p>
            <p style='margin: 10px 0 0 0; color: #047857;'>
                Aucune opportunité d'arbitrage détectée.
            </p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# SECTION 7 : INTERPRÉTATION
# ────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Interprétation")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        **📊 Analyse du Prix Future :**
        - Le future cote à **{F0:,.2f} points**
        - Prime de **{base['percentage']:+.2f}%** vs spot
        - Valeur notionnelle : **{valeur_notionnelle:,.0f} MAD**/contrat
        - Coût de portage : **{cout_port*100:+.2f}%**
    """)

with col2:
    st.markdown(f"""
        **📈 Sensibilité Principale :**
        - Delta : **{sensibilites['df_dS']:.4f}** (1 point de spot = {sensibilites['df_dS']:.2f} pts de future)
        - Sensibilité taux : **{sensibilites['df_dr']:,.0f} pts** par +1% de r
        - Sensibilité temps : **{sensibilites['df_dT']:,.0f} pts** par an
    """)

# Info box
st.markdown(f"""
    <div style='padding: 20px; background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); 
                border-left: 5px solid #1E3A5F; border-radius: 12px; margin: 20px 0;'>
        <strong>💡 Le saviez-vous ?</strong><br>
        La convergence du prix future vers le spot à l'échéance est garantie par l'arbitrage. 
        Si F₀ ≠ S₀ à T=0, un arbitragiste pourrait réaliser un profit sans risque, 
        ce qui ramènerait les prix à l'équilibre (Document §7.2 - CDG Capital).
    </div>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
# SECTION 8: COUVERTURE AVEC MASI20 (NOUVEAU)
# ────────────────────────────────────────────
st.divider()
st.markdown("### 🛡️ Couverture de Portefeuille avec Futures MASI20")

from utils.portfolio_builder import (
    get_masi20_constituents,
    generer_historique_prix,
    generer_historique_masi20,
    calculer_valeur_portefeuille
)

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
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("#### 📋 Constituants MASI20 et Poids")

with col2:
    if st.button("✏️ Modifier les poids"):
        st.session_state['poids_modifiables'] = not st.session_state['poids_modifiables']
        st.rerun()

# Afficher le tableau
df_constituents = pd.DataFrame(constituents)
df_constituents['poids'] = df_constituents['poids'] * 100  # En pourcentage

if st.session_state['poids_modifiables']:
    # Mode édition
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
    
    # Normaliser les poids pour que la somme fasse 100%
    total_poids = edited_df['poids'].sum()
    if total_poids > 0:
        edited_df['poids'] = edited_df['poids'] / total_poids * 100
        
        # Mettre à jour session_state
        for idx, constituant in enumerate(st.session_state['constituents']):
            constituant['poids'] = edited_df.iloc[idx]['poids'] / 100
else:
    # Mode lecture
    st.dataframe(
        df_constituents.style.format({
            'poids': '{:.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

# Date de dernière mise à jour
st.caption(f"📅 Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ────────────────────────────────────────────
# CALCUL DU PORTEFEUILLE ET BETA
# ────────────────────────────────────────────
st.divider()
st.markdown("#### 📊 Calcul du Beta et N*")

col1, col2, col3 = st.columns(3)

with col1:
    valeur_portefeuille = st.number_input(
        "💰 Valeur du portefeuille à couvrir (MAD)",
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
    multiplicateur = config.MULTIPLICATEUR

# Calculs
rendements_portefeuille = np.zeros(89)  # 90 jours - 1
for constituant in constituents:
    ticker = constituant['ticker']
    poids = constituant['poids']
    returns = historique_constituents[ticker]['returns'][1:]  # Enlever le premier 0
    rendements_portefeuille += poids * returns

rendements_masi20 = historique_masi20['returns'][1:]

beta = calculer_beta(rendements_portefeuille, rendements_masi20)
correlation = calculer_correlation(rendements_portefeuille, rendements_masi20)
tracking_error = calculer_tracking_error(rendements_portefeuille, rendements_masi20)
alpha = calculer_alpha(rendements_portefeuille, rendements_masi20)

N_star = calculer_N_star(beta, valeur_portefeuille, prix_future_masi20, multiplicateur)

# Affichage des résultats
st.divider()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Beta du Portefeuille",
        f"{beta:.4f}",
        delta=f"{beta-1:+.4f} vs MASI20",
        help="Sensibilité du portefeuille aux variations du MASI20"
    )

with col2:
    st.metric(
        "Corrélation",
        f"{correlation:.4f}",
        help="Corrélation entre le portefeuille et le MASI20 (1 = parfaite)"
    )

with col3:
    st.metric(
        "Tracking Error",
        f"{tracking_error:.2f}%",
        help="Écart-type de la différence de performance (annualisé)"
    )

with col4:
    st.metric(
        "Alpha (annualisé)",
        f"{alpha:+.2f}%",
        help="Surperformance par rapport au benchmark"
    )

# ────────────────────────────────────────────
# RÉSULTAT N*
# ────────────────────────────────────────────
st.divider()
st.markdown("#### 🎯 Nombre Optimal de Contrats (N*)")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
        <div style='padding: 30px; background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%); 
                    border-radius: 12px; text-align: center; color: white;
                    box-shadow: 0 8px 24px rgba(30, 58, 95, 0.3);'>
            <p style='margin: 0; font-size: 1.1em; opacity: 0.9;'>
                Nombre optimal de contrats futures MASI20
            </p>
            <p style='margin: 15px 0 0 0; font-size: 3.5em; font-weight: 800;'>
                {N_star:,}
            </p>
            <p style='margin: 10px 0 0 0; font-size: 1em; opacity: 0.8;'>
                contrats
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    valeur_notionnelle_contrat = prix_future_masi20 * multiplicateur
    st.markdown(f"""
        **Détails du calcul :**
        
        • Valeur portefeuille (P): {valeur_portefeuille:,.0f} MAD
        
        • Beta (β): {beta:.4f}
        
        • Prix Future: {prix_future_masi20:,.0f} pts
        
        • Multiplicateur: {multiplicateur} MAD/pt
        
        • Valeur notionnelle/contrat: {valeur_notionnelle_contrat:,.0f} MAD
        
        **Formule :**
        
        N* = β × P / A
        
        N* = {beta:.4f} × {valeur_portefeuille:,.0f} / {valeur_notionnelle_contrat:,.0f}
        
        N* = **{N_star:,} contrats**
    """)

# ────────────────────────────────────────────
# GRAPHIQUE DE CORRÉLATION
# ────────────────────────────────────────────
st.divider()
st.markdown("#### 📈 Corrélation Portefeuille vs MASI20")

fig_scatter = go.Figure()

fig_scatter.add_trace(go.Scatter(
    x=rendements_masi20 * 100,
    y=rendements_portefeuille * 100,
    mode='markers',
    name='Rendements journaliers',
    marker=dict(
        size=6,
        color=config.COLORS['primary'],
        opacity=0.6
    )
))

# Ligne de régression
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(rendements_masi20, rendements_portefeuille)
x_line = np.array([min(rendements_masi20), max(rendements_masi20)])
y_line = slope * x_line + intercept

fig_scatter.add_trace(go.Scatter(
    x=x_line * 100,
    y=y_line * 100,
    mode='lines',
    name=f'Ligne de régression (R²={r_value**2:.4f})',
    line=dict(color='#10B981', width=2)
))

fig_scatter.update_layout(
    title='Rendements Quotidiens: Portefeuille vs MASI20',
    xaxis_title='Rendement MASI20 (%)',
    yaxis_title='Rendement Portefeuille (%)',
    height=450,
    template='plotly_white',
    showlegend=True
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Stats supplémentaires
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("R² (Coefficient de détermination)", f"{r_value**2:.4f}")

with col2:
    st.metric("Pente de régression", f"{slope:.4f}")

with col3:
    st.metric("Erreur standard", f"{std_err:.6f}")

# ────────────────────────────────────────────
# GUIDE MÉTHODOLOGIQUE
# ────────────────────────────────────────────
with st.expander("📘 Guide Méthodologique - Calcul de N*"):
    st.markdown("""
        ### 🎯 Objectif
        
        Déterminer le nombre optimal de contrats futures MASI20 nécessaires pour couvrir 
        un portefeuille d'actions marocaines contre le risque de marché.
        
        ### 📐 Formule de N*
        
        **N* = β × P / A**
        
        Où :
        - **N*** = Nombre optimal de contrats futures
        - **β** = Beta du portefeuille par rapport à l'indice MASI20
        - **P** = Valeur totale du portefeuille à couvrir (MAD)
        - **A** = Valeur notionnelle d'un contrat future = Prix Future × Multiplicateur
        
        ### 🔍 Qu'est-ce que le Beta ?
        
        Le **Beta (β)** mesure la sensibilité du portefeuille aux variations de l'indice de référence (MASI20).
        
        - **β = 1** : Le portefeuille évolue comme l'indice
        - **β > 1** : Le portefeuille est plus volatil que l'indice
        - **β < 1** : Le portefeuille est moins volatil que l'indice
        
        **Calcul du Beta :**
        ```
        β = Cov(R_portefeuille, R_MASI20) / Var(R_MASI20)
        ```
        
        ### 📊 Méthodologie de Construction du Portefeuille
        
        1. **Récupération des constituants MASI20** : Les 20 actions les plus liquides
        2. **Pondération** : Utilisation des poids officiels de l'indice MASI20
        3. **Historique** : 90 jours de données de prix
        4. **Calcul des rendements** : Rendements logarithmiques journaliers
        5. **Régression** : Calcul du Beta par régression linéaire
        
        ### 📈 Interprétation des Résultats
        
        **Corrélation (ρ) :**
        - Proche de 1 : Forte corrélation positive
        - Proche de 0 : Aucune corrélation
        - Proche de -1 : Forte corrélation négative
        
        **Tracking Error :**
        Mesure l'écart-type de la différence de performance entre le portefeuille et l'indice.
        Plus il est faible, mieux le portefeuille réplique l'indice.
        
        **Alpha (α) :**
        Mesure la surperformance (ou sous-performance) du portefeuille par rapport 
        à ce que prédit le modèle CAPM.
        
        ### ⚠️ Limites
        
        - Le Beta est calculé sur 90 jours historiques et peut évoluer
        - La corrélation passée ne préjuge pas des corrélations futures
        - Les coûts de transaction ne sont pas pris en compte
        - Le rééquilibrage du portefeuille peut être nécessaire périodiquement
        
        ### 💡 Exemple Pratique
        
        Pour un portefeuille de 10 000 000 MAD avec β = 0.98 :
        - Prix Future MASI20 = 1 876 pts
        - Multiplicateur = 10 MAD/pt
        - Valeur notionnelle/contrat = 18 760 MAD
        
        N* = 0.98 × 10 000 000 / 18 760 = **522 contrats**
        
        Pour couvrir le portefeuille, il faut vendre 522 contrats futures MASI20.
    """)

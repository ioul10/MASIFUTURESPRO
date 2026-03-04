# ============================================
# PAGE 2: PRICING - MASI Futures Pro
# Cœur de l'Application
# ============================================

import streamlit as st
import config
from utils.calculations import (
    prix_future_theorique,
    base_future,
    calcul_sensibilites,
    sensibilite_relative,
    calcul_term_structure,
    detecter_arbitrage,
    calcul_cout_portage,
    jours_vers_annees
)
from utils.scraping import get_spot_indice, get_taux_sans_risque

st.title("🧮 Pricing Future sur Indice")

st.markdown("""
    ### 📐 Formule de Pricing (Absence d'Arbitrage)
    
    $$F_0 = S_0 \\times e^{(r-q)T}$$
    
    **Où :**
    - **S₀** = Niveau spot de l'indice (données temps réel)
    - **r** = Taux sans risque (BKAM)
    - **q** = Rendement en dividendes attendu
    - **T** = Maturité en années
""")

st.divider()

# ────────────────────────────────────────────
# INPUTS
# ────────────────────────────────────────────
st.markdown("### 🔧 Paramètres de Valorisation")

col1, col2, col3 = st.columns(3)

with col1:
    # Sélection de l'indice
    indice = st.selectbox(
        "Indice Sous-Jacent",
        config.INDICES,
        index=0
    )
    
    # Spot (auto ou manuel)
    spot_auto = get_spot_indice(indice)
    spot = st.number_input(
        f"Niveau Spot {indice} (S₀)",
        min_value=1000.0,
        value=spot_auto,
        step=50.0,
        help="Niveau actuel de l'indice"
    )

with col2:
    # Taux sans risque (BKAM)
    taux_bkam = get_taux_sans_risque('10ans')
    r = st.number_input(
        "Taux sans risque (r) en %",
        min_value=0.0,
        max_value=15.0,
        value=taux_bkam * 100,
        step=0.1,
        help="Taux des bons du Trésor (BKAM)"
    ) / 100
    
    # Rendement dividendes
    q = st.number_input(
        "Rendement dividendes (q) en %",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.1,
        help="Dividendes moyens attendus"
    ) / 100

with col3:
    # Maturité
    jours = st.number_input(
        "Jours jusqu'à l'échéance",
        min_value=1,
        max_value=365,
        value=90,
        step=1
    )
    T = jours_vers_annees(jours)

# ────────────────────────────────────────────
# CALCULS
# ────────────────────────────────────────────
F0 = prix_future_theorique(spot, r, q, T)
base = base_future(F0, spot)
sensibilites = calcul_sensibilites(spot, r, q, T)
sens_rel = sensibilite_relative(sensibilites, spot, r, q, T)
cout_port = calcul_cout_portage(r, q, T)

# ────────────────────────────────────────────
# RÉSULTATS PRINCIPAUX
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Résultats de la Valorisation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center;
                    border-left: 5px solid {config.COLORS["primary"]};
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <p style='margin: 0; color: {config.COLORS["text_muted"]}; font-size: 0.9em;'>
                Prix Future F₀
            </p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; 
                      color: {config.COLORS["primary"]};'>
                {F0:,.2f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {config.COLORS["text_muted"]};'>
                points
            </p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    couleur_base = config.COLORS["success"] if base['points'] > 0 else config.COLORS["danger"]
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center;
                    border-left: 5px solid {couleur_base};
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <p style='margin: 0; color: {config.COLORS["text_muted"]}; font-size: 0.9em;'>
                Base (F₀-S₀)
            </p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; 
                      color: {couleur_base};'>
                {base['points']:+,.2f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {config.COLORS["text_muted"]};'>
                {base['percentage']:+.2f}%
            </p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center;
                    border-left: 5px solid {config.COLORS["info"]};
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <p style='margin: 0; color: {config.COLORS["text_muted"]}; font-size: 0.9em;'>
                Coût de Portage
            </p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; 
                      color: {config.COLORS["info"]};'>
                {cout_port*100:+.2f}%
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {config.COLORS["text_muted"]};'>
                (r-q)×T
            </p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; text-align: center;
                    border-left: 5px solid {config.COLORS["warning"]};
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <p style='margin: 0; color: {config.COLORS["text_muted"]}; font-size: 0.9em;'>
                Valeur Notionnelle
            </p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; 
                      color: {config.COLORS["warning"]};'>
                {F0 * config.MULTIPLICATEUR:,.0f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {config.COLORS["text_muted"]};'>
                MAD
            </p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# SENSIBILITÉS
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Sensibilités (Grecques)")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h4 style='margin-top: 0; color: {config.COLORS["primary"]};'>Sensibilités Absolues</h4>
            <p><strong>dF/dr :</strong> {sensibilites['df_dr']:,.2f} pts par 1% de taux</p>
            <p><strong>dF/dq :</strong> {sensibilites['df_dq']:,.2f} pts par 1% de dividende</p>
            <p><strong>dF/dS :</strong> {sensibilites['df_dS']:.4f} (Delta)</p>
            <p><strong>dF/dT :</strong> {sensibilites['df_dT']:,.2f} pts par an</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='padding: 20px; background: {config.COLORS["card"]}; 
                    border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h4 style='margin-top: 0; color: {config.COLORS["primary"]};'>Sensibilités Relatives</h4>
            <p><strong>+1% sur r :</strong> {sens_rel['dr_1pct']*100:+.2f}%</p>
            <p><strong>+1% sur q :</strong> {sens_rel['dq_1pct']*100:+.2f}%</p>
            <p><strong>+1 point sur S :</strong> {sens_rel['dS_1pct']:+.2f}%</p>
            <p><strong>+1 mois sur T :</strong> {sens_rel['dT_1mois']*100:+.2f}%</p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# TERM STRUCTURE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Structure par Terme des Futures")

echeances = [30, 60, 90, 120, 180, 252]
df_term = calcul_term_structure(spot, r, q, echeances)

# Affichage tableau
st.dataframe(
    df_term.style.format({
        'F0': '{:,.2f}',
        'Base_pts': '{:+,.2f}',
        'Base_pct': '{:+.2f}%'
    }),
    use_container_width=True,
    hide_index=True
)

# ────────────────────────────────────────────
# ARBITRAGE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 🎯 Détection d'Arbitrage")

col1, col2 = st.columns([2, 1])

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

# Analyse
arbitrage = detecter_arbitrage(prix_marche, F0, seuil)

# Affichage du signal
if arbitrage['arbitrage_possible']:
    st.markdown(f"""
        <div style='padding: 20px; background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); 
                    border-left: 5px solid {config.COLORS["warning"]};
                    border-radius: 12px; margin: 20px 0;'>
            <h3 style='margin-top: 0; color: {config.COLORS["warning"]};'>
                {arbitrage['statut']}
            </h3>
            <p style='font-size: 1.1em;'><strong>Signal :</strong> {arbitrage['signal']}</p>
            <p style='font-size: 1.1em;'><strong>Écart :</strong> {arbitrage['ecart_pct']:+.2f}%</p>
            <p style='font-size: 1.2em; margin-top: 15px;'>
                <strong>Stratégie recommandée :</strong><br>
                {arbitrage['strategie']}
            </p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div style='padding: 20px; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); 
                    border-left: 5px solid {config.COLORS["success"]};
                    border-radius: 12px; margin: 20px 0;'>
            <h3 style='margin-top: 0; color: {config.COLORS["success"]};'>
                {arbitrage['statut']}
            </h3>
            <p style='font-size: 1.1em;'>L'écart ({arbitrage['ecart_pct']:+.2f}%) est dans la zone normale.</p>
            <p style='font-size: 1.1em;'>Aucune opportunité d'arbitrage détectée.</p>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# NEWS WIDGET
# ────────────────────────────────────────────
st.divider()
from components.news_widget import render_news_widget
render_news_widget(max_news=3)

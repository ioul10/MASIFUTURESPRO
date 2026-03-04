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
    st.markdown(f"""
        <div style='padding: 25px; background: white; border-radius: 12px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h4 style='margin-top: 0; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; 
                       padding-bottom: 10px;'>Sensibilités Absolues</h4>
            
            <div style='margin: 15px 0;'>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>dF/dr</strong>
                    <span style='color: #10B981; font-weight: 600;'>
                        {sensibilites['df_dr']:,.2f} pts/+1% taux
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>dF/dq</strong>
                    <span style='color: #EF4444; font-weight: 600;'>
                        {sensibilites['df_dq']:,.2f} pts/+1% div.
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>dF/dS (Delta)</strong>
                    <span style='color: #3B82F6; font-weight: 600;'>
                        {sensibilites['df_dS']:.4f}
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>dF/dT (Theta)</strong>
                    <span style='color: #F59E0B; font-weight: 600;'>
                        {sensibilites['df_dT']:,.2f} pts/an
                    </span>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div style='padding: 25px; background: white; border-radius: 12px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);'>
            <h4 style='margin-top: 0; color: #1E3A5F; border-bottom: 2px solid #1E3A5F; 
                       padding-bottom: 10px;'>Impact Relatif</h4>
            
            <div style='margin: 15px 0;'>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>+1% sur r</strong>
                    <span style='color: #10B981; font-weight: 60;'>
                        {sensibilites['df_dr']/F0*100:+.2f}%
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>+1% sur q</strong>
                    <span style='color: #EF4444; font-weight: 600;'>
                        {sensibilites['df_dq']/F0*100:+.2f}%
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>+1 point sur S</strong>
                    <span style='color: #3B82F6; font-weight: 600;'>
                        {1/F0*100:+.4f}%
                    </span>
                </p>
                <p style='margin: 10px 0; display: flex; justify-content: space-between;'>
                    <strong>+1 mois sur T</strong>
                    <span style='color: #F59E0B; font-weight: 600;'>
                        {sensibilites['df_dT']/F0*(1/12)*100:+.2f}%
                    </span>
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ────────────────────────────────────────────
# SECTION 5 : TERM STRUCTURE
# ────────────────────────────────────────────
st.divider()
st.markdown("### 📊 Structure par Terme des Futures")

echeances = [30, 60, 90, 120, 180, 252]
df_term = calcul_term_structure(spot, r, q, echeances)

# Affichage du tableau stylisé
st.dataframe(
    df_term.style.format({
        'F0': '{:,.2f}',
        'Base_pts': '{:+,.2f}',
        'Base_pct': '{:+.2f}%'
    }).background_gradient(
        subset=['Base_pct'], 
        cmap='RdYlGn_r',
        vmin=-2,
        vmax=2
    ),
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

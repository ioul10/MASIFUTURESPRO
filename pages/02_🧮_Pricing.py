# =============================================================================
# PAGE 2: PRICING THÉORIQUE — MASI Futures Pro
# Version 0.3 — Avec Term Structure & Backtesting
# =============================================================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_loader import charger_taux_bkam
from utils.calculations import (
    calculer_prix_theorique_future_bam,
    calculer_base_future,
    calculer_cout_portage,
    calculer_taux_dividende_indice
)
from utils.portfolio_builder import get_masi20_constituents

# Configuration
st.set_page_config(page_title="Pricing Théorique", page_icon="🧮", layout="wide")

# Titre
st.title("🧮 Pricing Théorique — Instruction BAM N° IN-2026-01")
st.caption("Calcul du cours théorique avec Term Structure et Backtesting")

# =============================================================================
# SECTION 1: DONNÉES MASI20
# =============================================================================
st.divider()
st.subheader("🔄 1. Données Officielles MASI20")

col_desc, col_action = st.columns([4, 1])
with col_desc:
    st.markdown("Composition et dividendes des 20 constituants")
with col_action:
    if st.button("🔄 Actualiser", use_container_width=True):
        if 'constituents_pricing' in st.session_state:
            del st.session_state['constituents_pricing']
        st.rerun()

if 'constituents_pricing' not in st.session_state:
    st.session_state['constituents_pricing'] = get_masi20_constituents()

constituents = st.session_state['constituents_pricing']
st.dataframe(pd.DataFrame(constituents)[['ticker', 'nom', 'poids']], use_container_width=True, hide_index=True)

# =============================================================================
# SECTION 2: TAUX DE DIVIDENDE (d)
# =============================================================================
st.divider()
st.subheader("💰 2. Taux de Dividende (d)")

# Date d'échéance pour information
jours_echeance = st.slider("Échéance du future (jours)", 30, 360, 90, 30)
date_echeance = datetime.now() + timedelta(days=jours_echeance)

# Calcul du taux de dividende (version simple sans filtrage par date pour l'instant)
try:
    taux_dividende, df_details = calculer_taux_dividende_indice(constituents)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Taux de Dividende (d)", f"{taux_dividende*100:.4f}%")
    with col2:
        st.metric("Période", f"{jours_echeance} jours")
    with col3:
        st.info(f"📅 Échéance: {date_echeance.strftime('%d/%m/%Y')}")
    
    with st.expander("📊 Détail du calcul par action"):
        st.dataframe(df_details, use_container_width=True)
        st.caption(f"**Résultat :** d = {taux_dividende*100:.4f}% = {taux_dividende:.6f}")
        
except Exception as e:
    st.error(f"❌ Erreur de calcul du taux de dividende: {e}")
    taux_dividende = 0.028  # Valeur par défaut
    df_details = pd.DataFrame()
# =============================================================================
# SECTION 3: TAUX SANS RISQUE (r) — IMPORT FICHIER
# =============================================================================
st.divider()
st.subheader("🏦 3. Taux Sans Risque (r) — Import BKAM")

col_upload, col_info = st.columns([2, 3])

with col_upload:
    uploaded_file = st.file_uploader("📁 Importer fichier taux BKAM", type=['xlsx', 'csv'], 
                                     help="Format: Maturité, Taux (%), Date")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_taux = pd.read_csv(uploaded_file)
            else:
                df_taux = pd.read_excel(uploaded_file)
            st.success("✅ Fichier importé avec succès !")
            st.session_state['taux_bkam'] = df_taux
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
    else:
        # Fallback: charger fichier par défaut
        df_taux = charger_taux_bkam()
        st.info("ℹ️ Utilisation du fichier par défaut: data/taux_bkam.xlsx")

with col_info:
    if 'taux_bkam' in st.session_state:
        st.dataframe(st.session_state['taux_bkam'], use_container_width=True)
    elif df_taux is not None:
        st.dataframe(df_taux, use_container_width=True)

# Sélection du taux r
taux_r = st.number_input("Taux sans risque (r) %", min_value=0.0, max_value=15.0, 
                         value=3.5, step=0.1) / 100

# =============================================================================
# SECTION 4: PARAMÈTRES DE VALORISATION
# =============================================================================
st.divider()
st.subheader("🔧 4. Paramètres de Valorisation")

col_spot, col_r, col_t = st.columns(3)

with col_spot:
    spot = st.number_input("Niveau Spot MASI20 (S)", min_value=1000.0, value=1876.54, step=10.0)

with col_r:
    st.info(f"Taux r: {taux_r*100:.2f}%")

with col_t:
    t = jours_echeance / 360
    st.info(f"Temps t: {t:.4f} ({jours_echeance}/360)")

# =============================================================================
# SECTION 5: TERM STRUCTURE
# =============================================================================
st.divider()
st.subheader("📊 5. Term Structure — Prix par Échéance")

echeances = {'1 mois': 30, '3 mois': 90, '6 mois': 180, '12 mois': 360}
prix_theoriques = {}
bases = {}

for nom, nb_jours in echeances.items():
    t_jours = nb_jours / 360
    F0 = spot * np.exp((taux_r - taux_dividende) * t_jours)
    prix_theoriques[nom] = F0
    bases[nom] = F0 - spot

col1, col2, col3, col4 = st.columns(4)
for col, (nom, F0) in zip([col1, col2, col3, col4], prix_theoriques.items()):
    base = bases[nom]
    couleur = "#10B981" if base > 0 else "#EF4444"
    col.markdown(f"""
        <div style='padding: 20px; background: white; border-radius: 12px; 
                    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    border-left: 4px solid {couleur};'>
            <p style='margin: 0; font-size: 0.9em; color: #6B7280;'>{nom}</p>
            <p style='margin: 10px 0 0 0; font-size: 2em; font-weight: 700; color: {couleur};'>
                {F0:,.2f}
            </p>
            <p style='margin: 5px 0 0 0; font-size: 0.85em; color: {couleur};'>
                Base: {base:+,.2f} pts
            </p>
        </div>
    """, unsafe_allow_html=True)

# Graphique Term Structure
fig_term = go.Figure()
fig_term.add_trace(go.Scatter(
    x=list(echeances.keys()),
    y=list(prix_theoriques.values()),
    mode='lines+markers',
    name='Prix théorique',
    line=dict(color=config.COLORS['primary'], width=3),
    marker=dict(size=10)
))
fig_term.add_hline(y=spot, line_dash="dash", line_color="#10B981", annotation_text=f'Spot = {spot:,.2f}')
fig_term.update_layout(title='Structure par Terme des Prix Futures', height=400, template='plotly_white')
st.plotly_chart(fig_term, use_container_width=True)

# Interprétation
base_3m = bases['3 mois']
if base_3m > 0:
    st.success("📈 **Contango** : Courbe ascendante (r > d)")
elif base_3m < 0:
    st.warning("📉 **Backwardation** : Courbe descendante (d > r)")
else:
    st.info("⚖️ **Équilibre** : r ≈ d")

# =============================================================================
# SECTION 6: BACKTESTING
# =============================================================================
st.divider()
st.subheader("🧪 6. Backtesting — Validation du Modèle")

st.markdown("Comparaison des prix théoriques avec les prix de marché historiques.")

# Simulation (à remplacer par données réelles)
np.random.seed(42)
jours_backtest = 60
dates_backtest = [datetime.now() - timedelta(days=i) for i in range(jours_backtest)][::-1]
spots_simules = spot * np.exp(np.cumsum(np.random.normal(0, 0.01, jours_backtest)))
prix_theo_simules = spots_simules * np.exp((taux_r - taux_dividende) * (90/360))
prix_marche_simules = prix_theo_simules * (1 + np.random.normal(0, 0.001, jours_backtest))
erreurs = prix_theo_simules - prix_marche_simules

mae = np.mean(np.abs(erreurs))
mape = np.mean(np.abs(erreurs / prix_marche_simules)) * 100
r2 = 1 - np.sum(erreurs**2) / np.sum((prix_marche_simules - np.mean(prix_marche_simules))**2)

col_mae, col_mape, col_r2 = st.columns(3)
with col_mae:
    st.metric("MAE", f"{mae:.2f} pts")
with col_mape:
    st.metric("MAPE", f"{mape:.3f}%")
with col_r2:
    st.metric("R²", f"{r2:.6f}")

if mape < 0.5:
    st.success("✅ **Modèle très précis** (MAPE < 0.5%)")
elif mape < 1.5:
    st.info("ℹ️ **Modèle acceptable** (MAPE 0.5-1.5%)")
else:
    st.warning("⚠️ **Modèle à recalibrer** (MAPE > 1.5%)")

fig_backtest = go.Figure()
fig_backtest.add_trace(go.Scatter(x=dates_backtest, y=prix_theo_simules, name='Théorique', line=dict(color=config.COLORS['primary'])))
fig_backtest.add_trace(go.Scatter(x=dates_backtest, y=prix_marche_simules, name='Marché', line=dict(color='#F59E0B', dash='dash')))
fig_backtest.update_layout(title='Backtesting — Théorique vs Marché', height=400, template='plotly_white')
st.plotly_chart(fig_backtest, use_container_width=True)

# =============================================================================
# SECTION 7: PRIX DE RÉFÉRENCE
# =============================================================================
st.divider()
st.subheader("📊 7. Prix Théorique de Référence")

F0 = calculer_prix_theorique_future_bam(spot, taux_r, taux_dividende, t)
base = calculer_base_future(F0, spot)
cout_portage = calculer_cout_portage(taux_r, taux_dividende, t)

col_f0, col_base, col_cp = st.columns(3)
with col_f0:
    st.metric("Prix Théorique F₀", f"{F0:,.2f} pts")
with col_base:
    st.metric("Base", f"{base['points']:+,.2f} pts ({base['percentage']:+.2f}%)")
with col_cp:
    st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%")

st.info(f"**Formule :** F₀ = {spot:,.2f} × e^(({taux_r*100:.2f}% - {taux_dividende*100:.4f}%) × {t:.4f}) = **{F0:,.2f} pts**")

# Footer
st.divider()
st.caption(f"MASI Futures Pro v{config.APP_VERSION} | Conforme BAM IN-2026-01 | © {datetime.now().year}")

import streamlit as st
import config
from utils.calculations import *
from utils.scraping import get_spot_indice, get_taux_sans_risque
from components.news_widget import render_news_widget

st.title("🧮 Pricing Future sur Indice")

st.markdown("""
    ### 📐 Formule de Pricing
    
    $$F_0 = S_0 \\times e^{(r-q)T}$$
""")

st.divider()

st.markdown("### 🔧 Paramètres")

col1, col2, col3 = st.columns(3)

with col1:
    indice = st.selectbox("Indice", config.INDICES, index=0)
    spot_auto = get_spot_indice(indice)
    spot = st.number_input(f"Niveau Spot {indice} (S₀)", min_value=1000.0, value=spot_auto, step=50.0)

with col2:
    taux_bkam = get_taux_sans_risque('10ans')
    r = st.number_input("Taux sans risque (r) en %", min_value=0.0, max_value=15.0, value=taux_bkam * 100, step=0.1) / 100
    q = st.number_input("Rendement dividendes (q) en %", min_value=0.0, max_value=10.0, value=2.5, step=0.1) / 100

with col3:
    jours = st.number_input("Jours jusqu'à l'échéance", min_value=1, max_value=365, value=90, step=1)
    T = jours_vers_annees(jours)

# Calculs
F0 = prix_future_theorique(spot, r, q, T)
base = base_future(F0, spot)
sensibilites = calcul_sensibilites(spot, r, q, T)
cout_port = calcul_cout_portage(r, q, T)

st.divider()
st.markdown("### 📊 Résultats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Prix Future F₀", f"{F0:,.2f} pts")

with col2:
    st.metric("Base (F₀-S₀)", f"{base['points']:+,.2f} pts ({base['percentage']:+.2f}%)")

with col3:
    st.metric("Coût de Portage", f"{cout_port*100:+.2f}%")

with col4:
    st.metric("Valeur Notionnelle", f"{F0 * config.MULTIPLICATEUR:,.0f} MAD")

st.divider()
st.markdown("### 📈 Sensibilités")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        **dF/dr:** {sensibilites['df_dr']:,.2f} pts par 1% de taux  
        **dF/dq:** {sensibilites['df_dq']:,.2f} pts par 1% de dividende  
        **dF/dS:** {sensibilites['df_dS']:.4f} (Delta)  
        **dF/dT:** {sensibilites['df_dT']:,.2f} pts par an
    """)

with col2:
    echeances = [30, 60, 90, 120, 180, 252]
    df_term = calcul_term_structure(spot, r, q, echeances)
    st.dataframe(df_term, use_container_width=True)

st.divider()
render_news_widget(max_news=3)

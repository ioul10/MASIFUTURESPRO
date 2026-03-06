# =============================================================================
# PAGE 3: SUIVI DES RISQUES - MASI Futures Pro
# Module de Risk Management Complet
# =============================================================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Suivi des Risques | MASI Futures Pro",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Suivi des Risques")
st.caption("Module de Risk Management — Conformité BAM & Gestion des Limites")

# =============================================================================
# INITIALISATION DES DONNÉES
# =============================================================================

# Récupérer les données actuelles
from utils.scraping import get_indices_bourse

indices_data = get_indices_bourse()
niveau_masi20 = indices_data.get('MASI20', {}).get('niveau', 18573) if indices_data else 18573

# =============================================================================
# SECTION 1: INPUTS UTILISATEUR
# =============================================================================
st.divider()
st.subheader("📝 Paramètres de Position")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Position & Contrat**")
    niveau_masi20_input = st.number_input(
        "Niveau MASI20",
        min_value=1000.0,
        value=niveau_masi20,
        step=50.0
    )
    taille_contrat = st.number_input(
        "Taille du contrat (MAD/point)",
        min_value=1,
        value=10,
        step=1
    )
    nb_contrats = st.number_input(
        "Nombre de contrats",
        min_value=1,
        value=1,
        step=1
    )
    sens_position = st.selectbox(
        "Sens de la position",
        ["Long", "Short"],
        index=0
    )

with col2:
    st.markdown("**Volatilité & Rendements**")
    vol_quotidienne = st.number_input(
        "Volatilité quotidienne (%)",
        min_value=0.0,
        max_value=10.0,
        value=1.00,
        step=0.01
    ) / 100
    
    vol_annualisee = st.number_input(
        "Volatilité annualisée (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.88,
        step=0.01
    ) / 100
    
    rendement_min = st.number_input(
        "Rendement minimum historique (%)",
        min_value=-100.0,
        max_value=0.0,
        value=-5.64,
        step=0.01
    ) / 100
    
    rendement_max = st.number_input(
        "Rendement maximum historique (%)",
        min_value=0.0,
        max_value=100.0,
        value=3.17,
        step=0.01
    ) / 100

with col3:
    st.markdown("**Marges & Limites**")
    depot_garantie = st.number_input(
        "Dépôt de garantie (MAD)",
        min_value=0,
        value=1000,
        step=100
    )
    seuil_suspension = st.number_input(
        "Seuil de suspension (%)",
        min_value=0.0,
        max_value=20.0,
        value=3.0,
        step=0.1
    ) / 100

# =============================================================================
# SECTION 2: CALCULS NOTIONNEL & EXPOSITION
# =============================================================================
st.divider()
st.subheader("💰 Notionnel & Exposition")

# Calculs
valeur_contrat = niveau_masi20_input * taille_contrat
notionnel_total = valeur_contrat * nb_contrats
delta = taille_contrat * nb_contrats
variation_1pct = notionnel_total * 0.01

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Valeur du contrat",
        f"{valeur_contrat:,.0f} MAD",
        help="Valeur notionnelle d'un contrat"
    )

with col2:
    st.metric(
        "Notionnel total",
        f"{notionnel_total:,.0f} MAD",
        help="Exposition totale au MASI20"
    )

with col3:
    st.metric(
        "Delta",
        f"{delta:+,} MAD/pt",
        help="Sensibilité au sous-jacent"
    )

with col4:
    st.metric(
        "Variation 1%",
        f"{variation_1pct:,.0f} MAD",
        help="Impact d'un mouvement de 1%"
    )

# =============================================================================
# SECTION 3: RISQUE JOURNALIER
# =============================================================================
st.divider()
st.subheader("📈 Risque Journalier")

# Calculs P&L
pl_moyen_journalier = abs(variation_1pct * vol_quotidienne)
pl_stress_moins_3pct = abs(notionnel_total * -0.03)
pl_stress_plus_3pct = abs(notionnel_total * 0.03)
pl_pire_historique = abs(notionnel_total * rendement_min)
pl_meilleur_historique = abs(notionnel_total * rendement_max)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**P&L Moyen**")
    st.info(f"**{pl_moyen_journalier:,.0f} MAD**\n\nGain ou perte moyen attendu sur une journée normale.")

with col2:
    st.markdown("**P&L Stress Scenarios**")
    st.warning(f"**Stress -3%**: {pl_stress_moins_3pct:,.0f} MAD\n\n**Stress +3%**: {pl_stress_plus_3pct:,.0f} MAD")

with col3:
    st.markdown("**P&L Historique**")
    st.error(f"**Pire cas**: {pl_pire_historique:,.0f} MAD\n\n**Meilleur cas**: {pl_meilleur_historique:,.0f} MAD")

# =============================================================================
# SECTION 4: VALUE AT RISK (VaR)
# =============================================================================
st.divider()
st.subheader("⚠️ Value at Risk (VaR)")

# Calculs VaR
z_score_95 = -1.65
z_score_99 = -2.33

var_95 = abs(z_score_95 * vol_quotidienne * notionnel_total)
var_99 = abs(z_score_99 * vol_quotidienne * notionnel_total)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**VaR Paramétrique 95%**")
    st.metric(
        f"Z-score = {z_score_95}",
        f"{var_95:,.0f} MAD",
        help="Perte maximale journalière avec 95% de confiance"
    )
    st.caption(f"Perte potentielle en conditions normales de marché (5% de risque)")

with col2:
    st.markdown("**VaR Paramétrique 99%**")
    st.metric(
        f"Z-score = {z_score_99}",
        f"{var_99:,.0f} MAD",
        help="Perte maximale journalière avec 99% de confiance"
    )
    st.caption(f"Perte potentielle en conditions extrêmes (1% de risque)")

# Visualisation VaR
fig_var = go.Figure()

fig_var.add_trace(go.Bar(
    x=['VaR 95%', 'VaR 99%'],
    y=[var_95, var_99],
    marker_color=['#F59E0B', '#EF4444'],
    text=[f"{var_95:,.0f} MAD", f"{var_99:,.0f} MAD"],
    textposition='auto'
))

fig_var.update_layout(
    title="Value at Risk - Comparaison",
    xaxis_title="Niveau de Confiance",
    yaxis_title="Perte Potentielle (MAD)",
    height=300,
    template='plotly_white',
    showlegend=False
)

st.plotly_chart(fig_var, use_container_width=True)

# =============================================================================
# SECTION 5: MARGE & LEVIER
# =============================================================================
st.divider()
st.subheader("🏦 Marge & Levier")

# Calculs
leverage = notionnel_total / depot_garantie if depot_garantie > 0 else 0
variation_pct_absorbee = (depot_garantie / notionnel_total) * 100 if notionnel_total > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Marge initiale totale",
        f"{depot_garantie:,.0f} MAD",
        help="Capital réellement immobilisé"
    )

with col2:
    st.metric(
        "Levier",
        f"{leverage:,.0f}x",
        help=f"1 MAD de marge contrôle {leverage:,.0f} MAD de marché"
    )

with col3:
    st.metric(
        "Variation % absorbée par marge",
        f"{variation_pct_absorbee:.2f}%",
        help="Mouvement nécessaire pour consommer toute la marge"
    )

# =============================================================================
# SECTION 6: RISQUE MARKET MAKING
# =============================================================================
st.divider()
st.subheader("📊 Risque Market Making")

# Paramètres Market Making
st.markdown("**Paramètres par Échéance**")

col1, col2, col3, col4 = st.columns(4)

echances_data = {
    'Échéance 1': {'spread': 75, 'contrats': 60},
    'Échéance 2': {'spread': 90, 'contrats': 50},
    'Échéance 3': {'spread': 100, 'contrats': 40},
    'Échéance 4': {'spread': 110, 'contrats': 30}
}

volumes = []
for i, (col, (echeance, data)) in enumerate(zip([col1, col2, col3, col4], echances_data.items())):
    with col:
        st.markdown(f"**{echeance}**")
        spread = st.number_input(
            f"Spread max (bps)",
            min_value=0,
            max_value=500,
            value=data['spread'],
            step=5,
            key=f"spread_{i}"
        )
        contrats = st.number_input(
            f"Contrats minimum",
            min_value=0,
            max_value=200,
            value=data['contrats'],
            step=5,
            key=f"contrats_{i}"
        )
        volumes.append(niveau_masi20_input * taille_contrat * contrats)
        st.caption(f"Spread: {spread} bps | Volume: {contrats} contrats")

# Calcul volume total et % utilisation limite
volume_total = sum(volumes)
limite_5mdh = 5_000_000  # 5 millions MAD
pct_utilisation_limite = (volume_total / limite_5mdh) * 100 if limite_5mdh > 0 else 0

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Volume minimum coté (total)",
        f"{volume_total:,.0f} MAD",
        help="Montant minimum que le market maker doit afficher"
    )

with col2:
    st.metric(
        "% utilisation limite 5MDH",
        f"{pct_utilisation_limite:.2f}%",
        help="Niveau d'utilisation de la limite d'encours autorisée"
    )

# =============================================================================
# SECTION 7: ALERTES
# =============================================================================
st.divider()
st.subheader("🚨 Système d'Alertes")

# Logique des alertes
alerte_volatilite = vol_quotidienne < 0.02  # < 2%
alerte_marge = pl_pire_historique < depot_garantie
alerte_limite = pct_utilisation_limite < 100

col1, col2, col3 = st.columns(3)

with col1:
    if alerte_volatilite:
        st.success("✅ **Alerte volatilité**\n\nLe marché est dans un régime normal (pas de variation extrême).")
    else:
        st.error("❌ **Alerte volatilité**\n\nVolatilité élevée détectée ! Risque accru.")

with col2:
    if alerte_marge:
        st.success("✅ **Alerte marge**\n\nLa perte potentielle reste inférieure à la marge disponible.")
    else:
        st.error("❌ **Alerte marge**\n\nRisque de call de marge ! Augmentez le dépôt.")

with col3:
    if alerte_limite:
        st.success("✅ **Alerte limite encours**\n\nLa position respecte les limites de risque internes.")
    else:
        st.error("❌ **Alerte limite encours**\n\nLimite d'encours dépassée ! Réduisez l'exposition.")

# =============================================================================
# SECTION 8: TABLEAU RÉCAPITULATIF
# =============================================================================
st.divider()
st.subheader("📋 Tableau Récapitulatif des Risques")

df_resume = pd.DataFrame({
    'Métrique': [
        'Niveau MASI20',
        'Valeur du contrat',
        'Notionnel total',
        'Delta',
        'Volatilité quotidienne',
        'Volatilité annualisée',
        'P&L moyen journalier',
        'VaR 95%',
        'VaR 99%',
        'Marge initiale',
        'Levier',
        'Variation % absorbée'
    ],
    'Valeur': [
        f"{niveau_masi20_input:,.2f}",
        f"{valeur_contrat:,.0f} MAD",
        f"{notionnel_total:,.0f} MAD",
        f"{delta:+,} MAD/pt",
        f"{vol_quotidienne*100:.2f}%",
        f"{vol_annualisee*100:.2f}%",
        f"{pl_moyen_journalier:,.0f} MAD",
        f"{var_95:,.0f} MAD",
        f"{var_99:,.0f} MAD",
        f"{depot_garantie:,.0f} MAD",
        f"{leverage:,.0f}x",
        f"{variation_pct_absorbee:.2f}%"
    ],
    'Interprétation': [
        'Niveau actuel de l\'indice',
        'Valeur notionnelle d\'un contrat',
        'Exposition totale au MASI20',
        '+1 point MASI20 → +10 MAD de P&L',
        'Mouvement moyen quotidien',
        'Risque annualisé',
        'Gain ou perte moyen attendu',
        'Perte max avec 95% confiance',
        'Perte max avec 99% confiance',
        'Capital immobilisé',
        'Effet de levier très élevé',
        'Variation pour consommer la marge'
    ]
})

st.dataframe(
    df_resume,
    use_container_width=True,
    hide_index=True
)

# =============================================================================
# SECTION 9: EXPORT RAPPORT
# =============================================================================
st.divider()
st.subheader("📄 Export du Rapport de Risque")

col1, col2 = st.columns(2)

with col1:
    # Export CSV
    csv_data = df_resume.to_csv(index=False, sep=';')
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv_data,
        file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Export Excel (simplifié)
    excel_buffer = pd.ExcelWriter('rapport.xlsx', engine='xlsxwriter')
    df_resume.to_excel(excel_buffer, sheet_name='Risques', index=False)
    excel_buffer.close()
    
    st.download_button(
        label="📥 Télécharger en Excel",
        data=open('rapport.xlsx', 'rb').read(),
        file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(
    f"MASI Futures Pro v{config.APP_VERSION} | "
    f"Module de Risk Management | "
    f"© {datetime.now().year} — Conforme Instruction BAM N° IN-2026-01"
)

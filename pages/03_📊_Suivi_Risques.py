# =============================================================================
# PAGE 3: SUIVI DES RISQUES - MASI Futures Pro
# Module de Risk Management Complet - Formules Corrigées
# =============================================================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

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
        "Dépôt de garantie par contrat (MAD)",
        min_value=0,
        value=1000,
        step=100
    )
    
    st.markdown("**Seuils d'Alerte**")
    seuil_vol_alerte = st.number_input(
        "Seuil volatilité alerte (%)",
        min_value=0.0,
        max_value=20.0,
        value=2.0,
        step=0.1
    ) / 100
    
    limite_encours = st.number_input(
        "Limite d'encours (MAD)",
        min_value=0,
        value=5_000_000,
        step=100_000,
        help="Limite d'encours par sens, toutes maturités confondues"
    )

# =============================================================================
# SECTION 2: NOTIONNEL & EXPOSITION (FORMULES CORRIGÉES)
# =============================================================================
st.divider()
st.subheader("💰 Notionnel & Exposition")

# Calculs corrigés
valeur_contrat = niveau_masi20_input * taille_contrat
notionnel_total = valeur_contrat * nb_contrats
delta = taille_contrat * nb_contrats  # Correction: multiplication, pas division
variation_1pct = notionnel_total * 0.01

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Valeur contrat",
        f"{valeur_contrat:,.0f}",
        delta=f"{valeur_contrat/niveau_masi20_input:.0f} MAD/pt",
        help="Niveau MASI20 × Taille du contrat"
    )

with col2:
    st.metric(
        "Notionnel total",
        f"{notionnel_total:,.0f}",
        delta=f"{nb_contrats} contrat(s)",
        help="Valeur contrat × Nombre de contrats"
    )

with col3:
    st.metric(
        "Delta",
        f"{delta:+,}",
        help="Taille contrat × Nb contrats (+1 pt MASI20 → +{delta} MAD P&L)"
    )

with col4:
    st.metric(
        "Variation 1%",
        f"{variation_1pct:,.0f}",
        delta=f"{variation_1pct/notionnel_total*100:.1f}%",
        help="Notionnel total × 1%"
    )

# =============================================================================
# SECTION 3: RISQUE JOURNALIER (FORMULES CORRIGÉES)
# =============================================================================
st.divider()
st.subheader("📈 Risque Journalier")

# Calculs corrigés
pl_moyen_journalier = vol_quotidienne * notionnel_total
pl_stress_moins_3pct = notionnel_total * (-0.03)
pl_stress_plus_3pct = notionnel_total * 0.03
pl_pire_historique = rendement_min * notionnel_total
pl_meilleur_historique = rendement_max * notionnel_total

col1, col2 = st.columns(2)

with col1:
    st.markdown("**P&L Quotidien**")
    st.info(f"""
    **P&L moyen journalier**: {pl_moyen_journalier:,.0f} MAD
    
    **P&L stress -3%**: {pl_stress_moins_3pct:,.0f} MAD
    
    **P&L stress +3%**: {pl_stress_plus_3pct:,.0f} MAD
    """)

with col2:
    st.markdown("**P&L Historique**")
    st.warning(f"""
    **P&L pire historique**: {pl_pire_historique:,.0f} MAD
    
    **P&L meilleur historique**: {pl_meilleur_historique:,.0f} MAD
    """)

# =============================================================================
# SECTION 4: VALUE AT RISK - VaR (FORMULES CORRIGÉES)
# =============================================================================
st.divider()
st.subheader("⚠️ Value at Risk (VaR)")

# Z-scores standards
z_score_95 = -1.65
z_score_99 = -2.33

# Calculs VaR corrigés
var_95 = notionnel_total * z_score_95 * vol_quotidienne
var_99 = notionnel_total * z_score_99 * vol_quotidienne

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Paramètres**")
    st.write(f"**Z-score 95%**: {z_score_95}")
    st.write(f"**Z-score 99%**: {z_score_99}")
    st.write(f"**Volatilité quotidienne**: {vol_quotidienne*100:.2f}%")

with col2:
    st.markdown("**VaR paramétrique (95%)**")
    st.metric(
        "VaR_95%",
        f"{abs(var_95):,.0f} MAD",
        help=f"Notionnel total × Z-score × Vol = {notionnel_total:,.0f} × {z_score_95} × {vol_quotidienne:.4f}"
    )
    st.caption("Perte maximale journalière avec 95% de confiance")

with col3:
    st.markdown("**VaR paramétrique (99%)**")
    st.metric(
        "VaR_99%",
        f"{abs(var_99):,.0f} MAD",
        help=f"Notionnel total × Z-score × Vol = {notionnel_total:,.0f} × {z_score_99} × {vol_quotidienne:.4f}"
    )
    st.caption("Perte maximale journalière avec 99% de confiance")

# Visualisation VaR
fig_var = go.Figure()

fig_var.add_trace(go.Bar(
    x=['VaR 95%', 'VaR 99%'],
    y=[abs(var_95), abs(var_99)],
    marker_color=['#F59E0B', '#EF4444'],
    text=[f"{abs(var_95):,.0f} MAD", f"{abs(var_99):,.0f} MAD"],
    textposition='auto'
))

fig_var.update_layout(
    title="Value at Risk - Comparaison des Niveaux de Confiance",
    xaxis_title="Niveau de Confiance",
    yaxis_title="Perte Potentielle (MAD)",
    height=300,
    template='plotly_white',
    showlegend=False
)

st.plotly_chart(fig_var, use_container_width=True)

# =============================================================================
# SECTION 5: MARGE & LEVIER (FORMULES CORRIGÉES)
# =============================================================================
st.divider()
st.subheader("🏦 Marge & Levier")

# Calculs corrigés
marge_initiale_totale = nb_contrats * depot_garantie
leverage = notionnel_total / marge_initiale_totale if marge_initiale_totale > 0 else 0
variation_pct_absorbee = marge_initiale_totale / notionnel_total if notionnel_total > 0 else 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Marge initiale totale",
        f"{marge_initiale_totale:,.0f} MAD",
        help=f"Nb contrats × Dépôt garantie = {nb_contrats} × {depot_garantie} MAD"
    )

with col2:
    st.metric(
        "Leverage",
        f"{leverage:,.0f}x",
        help=f"Notionnel / Marge = {notionnel_total:,.0f} / {marge_initiale_totale:,.0f}"
    )

with col3:
    st.metric(
        "Variation % absorbée par marge",
        f"{variation_pct_absorbee*100:.2f}%",
        help=f"Marge / Notionnel = {marge_initiale_totale:,.0f} / {notionnel_total:,.0f}"
    )

# =============================================================================
# SECTION 6: RISQUE MARKET MAKING
# =============================================================================
st.divider()
st.subheader("📊 Risque Market Making")

st.markdown("**Paramètres par Échéance**")

col1, col2, col3, col4 = st.columns(4)

echances_data = {
    'Échéance 1': {'spread': 75, 'contrats': 60},
    'Échéance 2': {'spread': 90, 'contrats': 50},
    'Échéance 3': {'spread': 100, 'contrats': 40},
    'Échéance 4': {'spread': 110, 'contrats': 30}
}

volumes_echeances = []
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
        contrats_min = st.number_input(
            f"Nb contrats minimum",
            min_value=0,
            max_value=200,
            value=data['contrats'],
            step=5,
            key=f"contrats_{i}"
        )
        volume_echeance = niveau_masi20_input * taille_contrat * contrats_min
        volumes_echeances.append(volume_echeance)
        st.caption(f"Volume: {volume_echeance:,.0f} MAD")

volume_minimum_cote = sum(volumes_echeances)
pct_utilisation_limite = (volume_minimum_cote / limite_encours) * 100 if limite_encours > 0 else 0

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Volume minimum coté",
        f"{volume_minimum_cote:,.0f} MAD",
        help="Somme des volumes par échéance"
    )

with col2:
    st.metric(
        "% utilisation limite encours",
        f"{pct_utilisation_limite:.2f}%",
        help=f"Volume / Limite = {volume_minimum_cote:,.0f} / {limite_encours:,.0f}"
    )

# =============================================================================
# SECTION 7: ALERTES (AVEC LIMITES UTILISATEUR)
# =============================================================================
st.divider()
st.subheader("🚨 Système d'Alertes")

# Logique des alertes avec seuils utilisateur
alerte_volatilite = vol_quotidienne <= seuil_vol_alerte
alerte_marge = abs(var_99) <= marge_initiale_totale
alerte_limite_encours = notionnel_total <= limite_encours

col1, col2, col3 = st.columns(3)

with col1:
    if alerte_volatilite:
        st.success(f"""
        ✅ **Alerte volatilité**
        
        Le marché est dans un régime normal.
        
        Volatilité {vol_quotidienne*100:.2f}% ≤ Seuil {seuil_vol_alerte*100:.1f}%
        """)
    else:
        st.error(f"""
        ❌ **Alerte volatilité**
        
        Volatilité élevée détectée !
        
        Volatilité {vol_quotidienne*100:.2f}% > Seuil {seuil_vol_alerte*100:.1f}%
        """)

with col2:
    if alerte_marge:
        st.success(f"""
        ✅ **Alerte marge**
        
        La perte potentielle (VaR 99%) reste inférieure à la marge disponible.
        
        VaR 99% {abs(var_99):,.0f} MAD ≤ Marge {marge_initiale_totale:,.0f} MAD
        """)
    else:
        st.error(f"""
        ❌ **Alerte marge**
        
        Risque de call de marge !
        
        VaR 99% {abs(var_99):,.0f} MAD > Marge {marge_initiale_totale:,.0f} MAD
        """)

with col3:
    if alerte_limite_encours:
        st.success(f"""
        ✅ **Alerte limite encours**
        
        La position respecte les limites de risque internes.
        
        Notionnel {notionnel_total:,.0f} MAD ≤ Limite {limite_encours:,.0f} MAD
        """)
    else:
        st.error(f"""
        ❌ **Alerte limite encours**
        
        Limite d'encours dépassée !
        
        Notionnel {notionnel_total:,.0f} MAD > Limite {limite_encours:,.0f} MAD
        """)

# =============================================================================
# SECTION 8: TABLEAU RÉCAPITULATIF (FORMAT EXCEL)
# =============================================================================
st.divider()
st.subheader("📋 Tableau Récapitulatif des Risques")

# Création du tableau format Excel
df_resume = pd.DataFrame({
    'Métrique': [
        'Niveau MASI20',
        'Taille du contrat',
        'Nombre de contrats',
        'Sens position',
        'Volatilité quotidienne',
        'Volatilité annualisée',
        'Rendement minimum',
        'Rendement maximum',
        'Dépôt de garantie',
        'Seuil suspension',
        '',
        'NOTIONNEL & EXPOSITION',
        'Valeur contrat',
        'Notionnel total',
        'Delta',
        'Variation 1%',
        '',
        'RISQUE JOURNALIER',
        'P&L moyen journalier',
        'P&L stress -3%',
        'P&L stress +3%',
        'P&L pire historique',
        'P&L meilleur historique',
        '',
        'MARGE & LEVIER',
        'Marge initiale totale',
        'Leverage',
        'Variation % absorbée par marge',
        '',
        'VALUE AT RISK',
        'VaR paramétrique (95%)',
        'VaR paramétrique (99%)',
        '',
        'RISQUE MARKET MAKING',
        'Volume minimum coté',
        '% utilisation limite encours'
    ],
    'Valeur': [
        f"{niveau_masi20_input:,.2f}",
        f"{taille_contrat}",
        f"{nb_contrats}",
        sens_position,
        f"{vol_quotidienne*100:.2f}%",
        f"{vol_annualisee*100:.2f}%",
        f"{rendement_min*100:.2f}%",
        f"{rendement_max*100:.2f}%",
        f"{depot_garantie:,.0f}",
        f"{seuil_vol_alerte*100:.1f}%",
        '',
        '',
        f"{valeur_contrat:,.0f}",
        f"{notionnel_total:,.0f}",
        f"{delta:+,}",
        f"{variation_1pct:,.0f}",
        '',
        '',
        f"{pl_moyen_journalier:,.0f}",
        f"{pl_stress_moins_3pct:,.0f}",
        f"{pl_stress_plus_3pct:,.0f}",
        f"{pl_pire_historique:,.0f}",
        f"{pl_meilleur_historique:,.0f}",
        '',
        '',
        f"{marge_initiale_totale:,.0f}",
        f"{leverage:,.0f}x",
        f"{variation_pct_absorbee*100:.2f}%",
        '',
        '',
        f"{abs(var_95):,.0f}",
        f"{abs(var_99):,.0f}",
        '',
        '',
        f"{volume_minimum_cote:,.0f}",
        f"{pct_utilisation_limite:.2f}%"
    ]
})

st.dataframe(
    df_resume,
    use_container_width=True,
    hide_index=True
)

# =============================================================================
# SECTION 9: EXPORT EXCEL/CSV
# =============================================================================
st.divider()
st.subheader("📄 Export du Rapport")

col1, col2 = st.columns(2)

with col1:
    csv_data = df_resume.to_csv(index=False, sep=';', decimal=',')
    st.download_button(
        label="📥 Télécharger en CSV",
        data=csv_data,
        file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    try:
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_resume.to_excel(writer, sheet_name='Risques', index=False)
        
        st.download_button(
            label="📥 Télécharger en Excel",
            data=buffer.getvalue(),
            file_name=f"rapport_risque_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )
    except:
        st.warning("Installez xlsxwriter pour l'export Excel: `pip install xlsxwriter`")

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(
    f"MASI Futures Pro v{config.APP_VERSION} | "
    f"Module de Risk Management | "
    f"© {datetime.now().year} — Conforme Instruction BAM N° IN-2026-01"
)

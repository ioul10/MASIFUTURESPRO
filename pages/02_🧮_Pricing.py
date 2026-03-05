# =============================================================================
# PAGE 2: PRICING & COUVERTURE - MASI Futures Pro
# Version Professionnelle - Conforme Instruction BAM N° IN-2026-01
# =============================================================================

import streamlit as st
import config
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy import stats

# Imports métiers
from utils.portfolio_builder import (
    get_masi20_constituents,
    generer_historique_prix,
    generer_historique_masi20
)
from utils.calculations import (
    calculer_prix_theorique_future_bam,
    calculer_base_future,
    calculer_cout_portage,
    calculer_taux_dividende_indice,
    calculer_beta,
    calculer_correlation,
    calculer_tracking_error,
    calculer_alpha,
    calculer_N_star
)
from utils.scraping import get_taux_sans_risque

# =============================================================================
# CONFIGURATION DE LA PAGE
# =============================================================================
st.set_page_config(
    page_title="Pricing & Couverture | MASI Futures Pro",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Pricing & Couverture")
st.caption("Conforme à l'Instruction BAM N° IN-2026-01 — Modalités de détermination des cours de clôture")

# =============================================================================
# INITIALISATION DES DONNÉES (Session State)
# =============================================================================
def init_portfolio_data():
    """Initialise les données du portefeuille MASI20 dans le session_state"""
    if 'portfolio_initialized' not in st.session_state:
        st.session_state['constituents'] = get_masi20_constituents()
        st.session_state['historique_constituents'] = generer_historique_prix(
            st.session_state['constituents'], jours=90
        )
        st.session_state['historique_masi20'] = generer_historique_masi20(
            st.session_state['historique_constituents'],
            st.session_state['constituents']
        )
        st.session_state['date_calcul'] = datetime.now()
        st.session_state['portfolio_initialized'] = True

init_portfolio_data()

# =============================================================================
# CRÉATION DES ONGLETS PRINCIPAUX
# =============================================================================
tab_couverture, tab_beta_evolution, tab_pricing = st.tabs([
    "🛡️ Couverture (N*)",
    "📈 Évolution du Beta",
    "📊 Pricing Théorique (BAM)"
])

# =============================================================================
# ONGLET 1: COUVERTURE DE PORTEFEUILLE - CALCUL DE N*
# =============================================================================
with tab_couverture:
    
    st.markdown("""
        ### 🎯 Objectif
        Déterminer le nombre optimal de contrats futures MASI20 (**N***) pour couvrir 
        un portefeuille d'actions marocaines contre le risque de marché.
    """)
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 1: CONSTITUANTS ET PONDÉRATIONS
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📋 1. Composition du Portefeuille MASI20")
    
    col_info, col_action = st.columns([4, 1])
    
    with col_info:
        st.markdown("Pondérations officielles des 20 actions composant l'indice MASI20")
    
    with col_action:
        if st.button("✏️ Modifier", use_container_width=True, key="edit_weights_btn"):
            st.session_state['edit_mode'] = not st.session_state.get('edit_mode', False)
            st.rerun()
    
    # Préparation du DataFrame
    df_constituents = pd.DataFrame(st.session_state['constituents'])
    df_constituents['poids_pct'] = df_constituents['poids'] * 100
    
    # Affichage mode édition / lecture
    if st.session_state.get('edit_mode', False):
        edited_df = st.data_editor(
            df_constituents[['ticker', 'nom', 'poids_pct']],
            column_config={
                "poids_pct": st.column_config.NumberColumn(
                    "Poids (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.2f"
                )
            },
            hide_index=True,
            use_container_width=True,
            key="weights_editor"
        )
        # Normalisation et mise à jour
        if edited_df['poids_pct'].sum() > 0:
            edited_df['poids_pct'] = edited_df['poids_pct'] / edited_df['poids_pct'].sum() * 100
            for idx, c in enumerate(st.session_state['constituents']):
                c['poids'] = edited_df.iloc[idx]['poids_pct'] / 100
    else:
        st.dataframe(
            df_constituents[['ticker', 'nom', 'poids_pct']].style.format({'poids_pct': '{:.2f}%'}),
            use_container_width=True,
            hide_index=True
        )
    
    st.caption(f"📅 Dernière mise à jour : {st.session_state['date_calcul'].strftime('%d/%m/%Y %H:%M')}")
    
    if st.button("🔄 Actualiser les données historiques", key="refresh_data_btn"):
        st.session_state['historique_constituents'] = generer_historique_prix(
            st.session_state['constituents'], jours=90
        )
        st.session_state['historique_masi20'] = generer_historique_masi20(
            st.session_state['historique_constituents'],
            st.session_state['constituents']
        )
        st.session_state['date_calcul'] = datetime.now()
        st.rerun()
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 2: PARAMÈTRES DE COUVERTURE
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("💰 2. Paramètres de la Couverture")
    
    col_valeur, col_prix_future, col_mult = st.columns(3)
    
    with col_valeur:
        valeur_portefeuille = st.number_input(
            "Valeur du portefeuille à couvrir (MAD)",
            min_value=100_000,
            value=10_000_000,
            step=100_000,
            format="%d"
        )
    
    with col_prix_future:
        prix_future = st.number_input(
            "Prix Future MASI20 (points)",
            min_value=1000.0,
            value=st.session_state['historique_masi20']['prix'][-1],
            step=50.0,
            format="%.2f"
        )
    
    with col_mult:
        multiplicateur = config.MULTIPLICATEUR
        st.info(f"Multiplicateur : **{multiplicateur} MAD/point**")
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 3: CALCULS STATISTIQUES
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🧮 3. Métriques de Risque")
    
    # Calcul des rendements
    rendements_pf = np.zeros(89)
    for c in st.session_state['constituents']:
        returns = st.session_state['historique_constituents'][c['ticker']]['returns'][1:]
        rendements_pf += c['poids'] * returns
    
    rendements_masi = st.session_state['historique_masi20']['returns'][1:]
    
    # Calculs
    beta = calculer_beta(rendements_pf, rendements_masi)
    correlation = calculer_correlation(rendements_pf, rendements_masi)
    tracking_error = calculer_tracking_error(rendements_pf, rendements_masi)
    alpha = calculer_alpha(rendements_pf, rendements_masi)
    N_star = calculer_N_star(beta, valeur_portefeuille, prix_future, multiplicateur)
    
    # Affichage des métriques
    col_b, col_c, col_te, col_a = st.columns(4)
    
    with col_b:
        st.metric(
            "Beta (β)",
            f"{beta:.4f}",
            delta=f"{beta-1:+.4f} vs MASI20",
            help="Sensibilité du portefeuille aux variations du MASI20"
        )
    with col_c:
        st.metric(
            "Corrélation",
            f"{correlation:.4f}",
            help="Corrélation linéaire portefeuille / MASI20"
        )
    with col_te:
        st.metric(
            "Tracking Error",
            f"{tracking_error:.2f}%",
            help="Écart-type annualisé de la différence de performance"
        )
    with col_a:
        st.metric(
            "Alpha (annualisé)",
            f"{alpha:+.2f}%",
            help="Surperformance par rapport au benchmark"
        )
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 4: RÉSULTAT N*
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🎯 4. Nombre Optimal de Contrats (N*)")
    
    if st.button("🧮 Calculer N*", type="primary", use_container_width=True, key="calc_n_btn"):
        A = prix_future * multiplicateur
        
        col_result, col_detail = st.columns([2, 1])
        
        with col_result:
            st.markdown(f"""
                <div style='padding:40px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                            border-radius:16px; text-align:center; color:white;
                            box-shadow:0 8px 24px rgba(30,58,95,0.3);'>
                    <p style='margin:0; font-size:1.1em; opacity:0.9;'>
                        Contrats futures MASI20 à vendre
                    </p>
                    <p style='margin:20px 0 0 0; font-size:4em; font-weight:800;'>
                        {N_star:,}
                    </p>
                    <p style='margin:10px 0 0 0; font-size:1em; opacity:0.8;'>
                        pour couvrir {valeur_portefeuille:,.0f} MAD
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        with col_detail:
            st.markdown(f"""
                **Détails du calcul :**
                
                | Paramètre | Valeur |
                |-----------|--------|
                | Beta (β) | {beta:.4f} |
                | Valeur portefeuille (P) | {valeur_portefeuille:,.0f} MAD |
                | Prix Future | {prix_future:,.0f} pts |
                | Multiplicateur | {multiplicateur} MAD/pt |
                | Valeur notionnelle (A) | {A:,.0f} MAD |
                
                **Formule :** `N* = β × P / A`
                
                **Calcul :** `{beta:.4f} × {valeur_portefeuille:,.0f} / {A:,.0f} = {N_star:,}`
            """)
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 5: GRAPHIQUE DE CORRÉLATION
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📈 5. Analyse de Corrélation")
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(rendements_masi, rendements_pf)
    
    fig_scatter = go.Figure()
    
    fig_scatter.add_trace(go.Scatter(
        x=rendements_masi * 100,
        y=rendements_pf * 100,
        mode='markers',
        name='Rendements journaliers',
        marker=dict(size=6, color=config.COLORS['primary'], opacity=0.6),
        hovertemplate='MASI20: %{x:.2f}%<br>Portefeuille: %{y:.2f}%<extra></extra>'
    ))
    
    x_line = np.array([min(rendements_masi), max(rendements_masi)])
    y_line = slope * x_line + intercept
    
    fig_scatter.add_trace(go.Scatter(
        x=x_line * 100,
        y=y_line * 100,
        mode='lines',
        name=f'Régression (R²={r_value**2:.4f})',
        line=dict(color='#10B981', width=2)
    ))
    
    fig_scatter.update_layout(
        title='Rendements Quotidiens : Portefeuille vs MASI20',
        xaxis_title='Rendement MASI20 (%)',
        yaxis_title='Rendement Portefeuille (%)',
        height=400,
        template='plotly_white',
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    col_r2, col_slope, col_err = st.columns(3)
    with col_r2:
        st.metric("R²", f"{r_value**2:.4f}")
    with col_slope:
        st.metric("Pente", f"{slope:.4f}")
    with col_err:
        st.metric("Erreur Std", f"{std_err:.6f}")
    
    # ────────────────────────────────────────────────────────────────────────
    # GUIDE MÉTHODOLOGIQUE
    # ────────────────────────────────────────────────────────────────────────
    with st.expander("📘 Guide Méthodologique — Calcul de N*"):
        st.markdown("""
            ### 📐 Formule de N*
            
            **N* = β × P / A**
            
            | Symbole | Description |
            |---------|-------------|
            | **N*** | Nombre optimal de contrats futures |
            | **β** | Beta du portefeuille vs MASI20 |
            | **P** | Valeur du portefeuille (MAD) |
            | **A** | Valeur notionnelle/contrat = Prix Future × Multiplicateur |
            
            ### 🔍 Interprétation du Beta
            
            | Valeur | Signification |
            |--------|---------------|
            | β = 1 | Portefeuille réplique l'indice |
            | β > 1 | Plus volatil que l'indice |
            | β < 1 | Moins volatil que l'indice |
            
            ### ⚠️ Limites
            
            - Beta calculé sur 90 jours historiques
            - Corrélation passée ≠ corrélation future
            - Coûts de transaction non inclus
            - Rééquilibrage périodique recommandé
            
            ### 💡 Exemple
            
            Pour un portefeuille de 10M MAD avec β=0.98 :
            - Prix Future = 1 876 pts, Multiplicateur = 10 MAD/pt
            - N* = 0.98 × 10 000 000 / (1 876 × 10) = **522 contrats**
            
            **Action :** Vendre 522 contrats futures MASI20 pour couvrir le portefeuille.
        """)

# =============================================================================
# ONGLET 2: ÉVOLUTION QUOTIDIENNE DU BETA (ROLLING BETA)
# =============================================================================
with tab_beta_evolution:
    
    st.markdown("""
        ### 📊 Analyse de Stabilité du Beta
        Évolution du Beta calculé en fenêtre glissante pour évaluer sa stabilité dans le temps.
    """)
    
    # ────────────────────────────────────────────────────────────────────────
    # PARAMÈTRES
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    col_window, col_info = st.columns(2)
    
    with col_window:
        window_size = st.slider(
            "Fenêtre de calcul (jours)",
            min_value=10, max_value=60, value=30, step=5,
            help="Nombre de jours pour chaque calcul de Beta glissant"
        )
    
    with col_info:
        st.info(f"📈 Données disponibles : **90 jours**")
    
    # ────────────────────────────────────────────────────────────────────────
    # CALCUL DU BETA GLISSANT
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    
    rendements_pf_total = np.zeros(89)
    for c in st.session_state['constituents']:
        returns = st.session_state['historique_constituents'][c['ticker']]['returns'][1:]
        rendements_pf_total += c['poids'] * returns
    
    rendements_masi_total = st.session_state['historique_masi20']['returns'][1:]
    dates = st.session_state['historique_masi20']['dates'][1:]
    
    rolling_betas, rolling_corrs, rolling_dates = [], [], []
    
    for i in range(window_size, len(rendements_pf_total)):
        pf_win = rendements_pf_total[i-window_size:i]
        masi_win = rendements_masi_total[i-window_size:i]
        
        rolling_betas.append(calculer_beta(pf_win, masi_win))
        rolling_corrs.append(calculer_correlation(pf_win, masi_win))
        rolling_dates.append(dates[i])
    
    df_rolling = pd.DataFrame({
        'Date': rolling_dates,
        'Beta': rolling_betas,
        'Corrélation': rolling_corrs
    })
    
    # ────────────────────────────────────────────────────────────────────────
    # AFFICHAGE DES RÉSULTATS
    # ────────────────────────────────────────────────────────────────────────
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Beta Actuel", f"{rolling_betas[-1]:.4f}")
    with col_stat2:
        st.metric("Beta Moyen", f"{np.mean(rolling_betas):.4f}")
    with col_stat3:
        st.metric("Beta Min", f"{np.min(rolling_betas):.4f}")
    with col_stat4:
        st.metric("Beta Max", f"{np.max(rolling_betas):.4f}")
    
    # Graphique
    st.divider()
    fig_beta = go.Figure()
    
    fig_beta.add_trace(go.Scatter(
        x=df_rolling['Date'],
        y=df_rolling['Beta'],
        mode='lines',
        name='Beta Glissant',
        line=dict(color=config.COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(30,58,95,0.1)',
        hovertemplate='Date: %{x|%d/%m/%Y}<br>Beta: %{y:.4f}<extra></extra>'
    ))
    
    fig_beta.add_hline(y=1.0, line_dash="dash", line_color="#10B981",
                       annotation_text="Beta = 1 (Référence)", annotation_position="top right")
    
    beta_mean = np.mean(rolling_betas)
    fig_beta.add_hline(y=beta_mean, line_dash="dot", line_color="#F59E0B",
                       annotation_text=f"Moyenne = {beta_mean:.4f}")
    
    fig_beta.update_layout(
        title=f'Évolution du Beta — Fenêtre Glissante : {window_size} jours',
        xaxis_title='Date',
        yaxis_title='Beta',
        height=450,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_beta, use_container_width=True)
    
    # Interprétation
    beta_std = np.std(rolling_betas)
    col_interp1, col_interp2 = st.columns(2)
    
    with col_interp1:
        st.markdown(f"""
            **📊 Analyse de Stabilité :**
            - Volatilité du Beta : **{beta_std:.4f}**
            - Tendance : **{'↗️ Croissante' if rolling_betas[-1] > rolling_betas[0] else '↘️ Décroissante' if rolling_betas[-1] < rolling_betas[0] else '➡️ Stable'}**
            - Écart à la moyenne : **{rolling_betas[-1] - beta_mean:+.4f}**
        """)
    
    with col_interp2:
        if beta_std < 0.05:
            st.success("✅ Beta très stable — Utilisation recommandée")
        elif beta_std < 0.10:
            st.info("ℹ️ Beta relativement stable — Surveillance modérée")
        else:
            st.warning("⚠️ Beta instable — Réévaluation fréquente conseillée")
    
    # Guide
    with st.expander("📘 Interprétation du Beta Glissant"):
        st.markdown("""
            ### Pourquoi un Beta glissant ?
            Le Beta n'est pas une constante : il évolue avec les conditions de marché.
            
            ### Lecture du graphique
            | Observation | Interprétation |
            |-------------|----------------|
            | Ligne stable autour de 1 | Bonne réplication de l'indice |
            | Tendance haussière | Risque systématique en augmentation |
            | Fortes fluctuations | Marché volatil — prudence |
            
            ### Recommandation pour N*
            - Beta stable (< 0.05) : Utiliser la moyenne
            - Beta instable (> 0.10) : Privilégier la valeur récente
            - Surveiller régulièrement l'évolution
        """)

# =============================================================================
# ONGLET 3: PRICING THÉORIQUE — CONFORME INSTRUCTION BAM N° IN-2026-01
# =============================================================================
with tab_pricing:
    
    st.markdown("""
        ### 📐 Pricing Théorique — Instruction BAM N° IN-2026-01
        Calcul du cours théorique d'un contrat future sur indice selon la formule officielle :
        
        **Cours théorique = S × e^((r - d) × t)**
    """)
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 1: DONNÉES OFFICIELLES MASI20
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔄 1. Données Officielles MASI20")
    
    col_desc, col_refresh = st.columns([4, 1])
    
    with col_desc:
        st.markdown("Composition et dividendes des constituants MASI20")
    
    with col_refresh:
        if st.button("🔄 Actualiser", use_container_width=True, key="refresh_pricing_btn"):
            if 'constituents_pricing' in st.session_state:
                del st.session_state['constituents_pricing']
            st.rerun()
    
    # Chargement des constituants
    if 'constituents_pricing' not in st.session_state:
        st.session_state['constituents_pricing'] = get_masi20_constituents()
    
    constituents_pricing = st.session_state['constituents_pricing']
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 2: CALCUL DU TAUX DE DIVIDENDE (Formule BAM)
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("💰 2. Taux de Dividende — Formule BAM")
    
    taux_dividende, df_details_div = calculer_taux_dividende_indice(constituents_pricing)
    
    col_td1, col_td2, col_td3 = st.columns(3)
    
    with col_td1:
        st.metric(
            "Taux de Dividende (d)",
            f"{taux_dividende*100:.4f}%",
            help="Calculé selon : d = Σ(Pi × Di / Ci)"
        )
    with col_td2:
        st.metric("Constituants", f"{len(constituents_pricing)}")
    with col_td3:
        st.info(f"📅 MAJ : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with st.expander("📊 Détail du calcul par action"):
        st.dataframe(df_details_div, use_container_width=True)
        st.caption(f"**Résultat :** d = {taux_dividende*100:.4f}% = {taux_dividende:.6f}")
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 3: PARAMÈTRES DE PRICING
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔧 3. Paramètres de Valorisation")
    
    col_spot, col_r, col_t = st.columns(3)
    
    with col_spot:
        spot = st.number_input(
            "Niveau Spot MASI20 (S)",
            min_value=1000.0,
            value=1876.54,
            step=10.0,
            format="%.2f",
            help="Cours de clôture de l'indice"
        )
    
    with col_r:
        taux_bkam = get_taux_sans_risque('10ans')
        r = st.number_input(
            "Taux sans risque (r) %",
            min_value=0.0,
            max_value=15.0,
            value=taux_bkam * 100,
            step=0.1,
            format="%.2f"
        ) / 100
    
    with col_t:
        jours = st.number_input(
            "Jours jusqu'échéance",
            min_value=1,
            max_value=365,
            value=90,
            step=1
        )
        t = jours / 360  # Base 360 selon BAM
    
    # ────────────────────────────────────────────────────────────────────────
    # SECTION 4: CALCUL DU PRIX THÉORIQUE
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 4. Prix Théorique du Future")
    
    F0 = calculer_prix_theorique_future_bam(spot, r, taux_dividende, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, taux_dividende, t)
    
    col_f0, col_base, col_cp, col_vn = st.columns(4)
    
    with col_f0:
        st.markdown(f"""
            <div style='padding:25px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                        border-radius:12px; text-align:center; color:white;'>
                <p style='margin:0; font-size:0.9em; opacity:0.9;'>Prix Théorique F₀</p>
                <p style='margin:10px 0 0 0; font-size:2.8em; font-weight:700;'>
                    {F0:,.2f}
                </p>
                <p style='margin:5px 0 0 0; font-size:0.85em; opacity:0.8;'>points</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_base:
        couleur = "#10B981" if base['points'] > 0 else "#EF4444"
        st.markdown(f"""
            <div style='padding:25px; background:white; border-radius:12px; text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08); border-left:5px solid {couleur};'>
                <p style='margin:0; font-size:0.9em; color:#6B7280;'>Base (F₀ - S)</p>
                <p style='margin:10px 0 0 0; font-size:2em; font-weight:700; color:{couleur};'>
                    {base['points']:+,.2f}
                </p>
                <p style='margin:5px 0 0 0; font-size:0.85em; color:#6B7280;'>
                    {base['percentage']:+.2f}%
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_cp:
        st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%", help="(r - d) × t")
    
    with col_vn:
        st.metric("Valeur Notionnelle", f"{F0 * config.MULTIPLICATEUR:,.0f} MAD", 
                 help=f"{config.MULTIPLICATEUR} MAD/point")
    
    # Formule détaillée
    st.info(f"""
        **Formule BAM appliquée (Instruction N° IN-2026-01) :**
        
        `F₀ = S × e^((r - d) × t)`
        
        `F₀ = {spot:,.2f} × e^(({r*100:.2f}% - {taux_dividende*100:.4f}%) × {t:.4f})`
        
        **Résultat : F₀ = {F0:,.2f} points**
        
        **Base :** {base['points']:+,.2f} points ({base['percentage']:+.2f}%)
    """)
    
    # ────────────────────────────────────────────────────────────────────────
    # RÉFÉRENCES RÉGLEMENTAIRES
    # ────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📚 Références Réglementaires")
    
    st.markdown("""
        **Instruction Bank Al-Maghrib N° IN-2026-01**
        
        *Modalités de détermination des cours de clôture des instruments financiers à terme*
        
        ---
        
        **Article 2 — Cours théorique d'un contrat à terme sur indice :**
        
        ```
        Cours théorique = S × e^((r - d) × t)
        
        Où :
        • S  : Prix spot (cash) ou valeur de l'indice cash
        • r  : Taux d'intérêt sans risque
        • d  : Taux de dividende (dividend yield)
        • t  : Temps jusqu'à l'échéance [nb de jours / 360]
               (inclure tous les jours de la semaine)
        
        Taux de dividende de l'indice :
        d = Σ(Pi × Di / Ci)
        
        Où :
        • i  : Les actions qui constituent l'indice
        • Di : Dividende par action i
        • Ci : Cours de l'action i
        • Pi : Poids du titre i dans l'indice
        ```
    """)
    
    # Info box
    st.success("""
        ✅ **Conformité :** Cette application applique strictement la formule officielle 
        de Bank Al-Maghrib pour le calcul des cours théoriques des futures sur indice.
    """)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(
    f"MASI Futures Pro v{config.APP_VERSION} | "
    f"Basé sur l'Instruction BAM N° IN-2026-01 | "
    f"© {datetime.now().year} — Usage professionnel et éducatif"
)

# =============================================================================
# PAGE 2: PRICING & COUVERTURE - MASI Futures Pro
# Version Renouvelée - Avec Term Structure & Backtesting
# Développeurs: OULMADANI Ilyas & ATANANE Oussama | v0.2 Beta
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
# NIVEAU 1: IMPORTS ET CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
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

# Configuration de la page
st.set_page_config(
    page_title="Pricing & Couverture | MASI Futures Pro",
    page_icon="🧮",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────────────────────
# NIVEAU 2: EN-TÊTE DE LA PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.title("🧮 Pricing & Couverture")
st.caption("Conforme à l'Instruction BAM N° IN-2026-01 — Modalités de détermination des cours de clôture")

# ─────────────────────────────────────────────────────────────────────────────
# NIVEAU 3: INITIALISATION DES DONNÉES (Session State)
# ─────────────────────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# NIVEAU 4: CRÉATION DES ONGLETS PRINCIPAUX
# ─────────────────────────────────────────────────────────────────────────────
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
    
    st.divider()
    st.subheader("📋 1. Composition du Portefeuille MASI20")
    
    col_info, col_action = st.columns([4, 1])
    
    with col_info:
        st.markdown("Pondérations officielles des 20 actions composant l'indice MASI20")
    
    with col_action:
        if st.button("✏️ Modifier", use_container_width=True, key="edit_weights_btn"):
            st.session_state['edit_mode'] = not st.session_state.get('edit_mode', False)
            st.rerun()
    
    df_constituents = pd.DataFrame(st.session_state['constituents'])
    df_constituents['poids_pct'] = df_constituents['poids'] * 100
    
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
    
    st.divider()
    st.subheader("🧮 3. Métriques de Risque")
    
    rendements_pf = np.zeros(89)
    for c in st.session_state['constituents']:
        returns = st.session_state['historique_constituents'][c['ticker']]['returns'][1:]
        rendements_pf += c['poids'] * returns
    
    rendements_masi = st.session_state['historique_masi20']['returns'][1:]
    
    beta = calculer_beta(rendements_pf, rendements_masi)
    correlation = calculer_correlation(rendements_pf, rendements_masi)
    tracking_error = calculer_tracking_error(rendements_pf, rendements_masi)
    alpha = calculer_alpha(rendements_pf, rendements_masi)
    N_star = calculer_N_star(beta, valeur_portefeuille, prix_future, multiplicateur)
    
    col_b, col_c, col_te, col_a = st.columns(4)
    
    with col_b:
        st.metric("Beta (β)", f"{beta:.4f}", delta=f"{beta-1:+.4f} vs MASI20",
                 help="Sensibilité du portefeuille aux variations du MASI20")
    with col_c:
        st.metric("Corrélation", f"{correlation:.4f}",
                 help="Corrélation linéaire portefeuille / MASI20")
    with col_te:
        st.metric("Tracking Error", f"{tracking_error:.2f}%",
                 help="Écart-type annualisé de la différence de performance")
    with col_a:
        st.metric("Alpha (annualisé)", f"{alpha:+.2f}%",
                 help="Surperformance par rapport au benchmark")
    
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
                    <p style='margin:0; font-size:1.1em; opacity:0.9;'>Contrats futures MASI20 à vendre</p>
                    <p style='margin:20px 0 0 0; font-size:4em; font-weight:800;'>{N_star:,}</p>
                    <p style='margin:10px 0 0 0; font-size:1em; opacity:0.8;'>pour couvrir {valeur_portefeuille:,.0f} MAD</p>
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
    
    st.divider()
    st.subheader("📈 5. Analyse de Corrélation")
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(rendements_masi, rendements_pf)
    
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=rendements_masi * 100, y=rendements_pf * 100, mode='markers',
        name='Rendements journaliers',
        marker=dict(size=6, color=config.COLORS['primary'], opacity=0.6),
        hovertemplate='MASI20: %{x:.2f}%<br>Portefeuille: %{y:.2f}%<extra></extra>'
    ))
    
    x_line = np.array([min(rendements_masi), max(rendements_masi)])
    y_line = slope * x_line + intercept
    fig_scatter.add_trace(go.Scatter(
        x=x_line * 100, y=y_line * 100, mode='lines',
        name=f'Régression (R²={r_value**2:.4f})',
        line=dict(color='#10B981', width=2)
    ))
    
    fig_scatter.update_layout(
        title='Rendements Quotidiens : Portefeuille vs MASI20',
        xaxis_title='Rendement MASI20 (%)', yaxis_title='Rendement Portefeuille (%)',
        height=400, template='plotly_white', showlegend=True, hovermode='x unified'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    col_r2, col_slope, col_err = st.columns(3)
    with col_r2: st.metric("R²", f"{r_value**2:.4f}")
    with col_slope: st.metric("Pente", f"{slope:.4f}")
    with col_err: st.metric("Erreur Std", f"{std_err:.6f}")
    
    with st.expander("📘 Guide Complet — Couverture de Portefeuille"):
        st.markdown("""
            ### 📐 Formule de N*
            **N* = β × P / A**
            
            | Symbole | Description | Unité |
            |---------|-------------|-------|
            | **N*** | Nombre optimal de contrats futures | contrats |
            | **β** | Beta du portefeuille vs MASI20 | sans unité |
            | **P** | Valeur du portefeuille à couvrir | MAD |
            | **A** | Valeur notionnelle/contrat = Prix Future × Multiplicateur | MAD |
            
            ### 🔍 Qu'est-ce que le Beta (β) ?
            Le **Beta** mesure la sensibilité du portefeuille aux variations de l'indice de référence.
            
            **Formule :** `β = Cov(R_portefeuille, R_MASI20) / Var(R_MASI20)`
            
            | Valeur | Interprétation |
            |--------|----------------|
            | β = 1 | Portefeuille réplique exactement l'indice |
            | β > 1 | Plus volatil que l'indice → N* plus élevé |
            | β < 1 | Moins volatil que l'indice → N* plus faible |
            
            ### 📊 Qu'est-ce que la Corrélation ?
            La **corrélation** mesure la force de la relation linéaire entre deux séries.
            
            **Formule :** `ρ = Cov(Rp, Rb) / (σp × σb)`
            
            | Valeur | Interprétation |
            |--------|----------------|
            | ρ > 0.90 | Forte corrélation → Couverture efficace ✅ |
            | 0.70-0.90 | Corrélation modérée → Couverture acceptable ⚠️ |
            | ρ < 0.70 | Faible corrélation → Couverture peu fiable ❌ |
            
            ### ⚠️ Limites
            - Beta historique ≠ Beta futur
            - Corrélation instable selon les régimes de marché
            - Coûts de transaction non inclus
            - Rééquilibrage périodique nécessaire
            
            ### 💡 Exemple
            Portefeuille: 10M MAD, β=0.98, Future=1 876 pts, Multiplicateur=10
            → N* = 0.98 × 10 000 000 / (1 876 × 10) = **522 contrats**
            
            **Action :** Vendre 522 contrats futures MASI20 pour couvrir.
        """)

# =============================================================================
# ONGLET 2: ÉVOLUTION QUOTIDIENNE DU BETA (ROLLING BETA)
# =============================================================================
with tab_beta_evolution:
    
    st.markdown("""
        ### 📊 Analyse de Stabilité du Beta
        Évolution du Beta calculé en fenêtre glissante pour évaluer sa stabilité dans le temps.
    """)
    
    st.divider()
    col_window, col_info = st.columns(2)
    
    with col_window:
        window_size = st.slider("Fenêtre de calcul (jours)", min_value=10, max_value=60, 
                               value=30, step=5, help="Nombre de jours pour chaque calcul")
    with col_info:
        st.info(f"📈 Données disponibles : **90 jours**")
    
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
    
    df_rolling = pd.DataFrame({'Date': rolling_dates, 'Beta': rolling_betas, 'Corrélation': rolling_corrs})
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1: st.metric("Beta Actuel", f"{rolling_betas[-1]:.4f}")
    with col_stat2: st.metric("Beta Moyen", f"{np.mean(rolling_betas):.4f}")
    with col_stat3: st.metric("Beta Min", f"{np.min(rolling_betas):.4f}")
    with col_stat4: st.metric("Beta Max", f"{np.max(rolling_betas):.4f}")
    
    st.divider()
    fig_beta = go.Figure()
    
    fig_beta.add_trace(go.Scatter(
        x=df_rolling['Date'], y=df_rolling['Beta'], mode='lines',
        name='Beta Glissant', line=dict(color=config.COLORS['primary'], width=2),
        fill='tozeroy', fillcolor='rgba(30,58,95,0.1)',
        hovertemplate='Date: %{x|%d/%m/%Y}<br>Beta: %{y:.4f}<extra></extra>'
    ))
    
    fig_beta.add_hline(y=1.0, line_dash="dash", line_color="#10B981",
                      annotation_text="Beta = 1 (Référence)", annotation_position="top right")
    
    beta_mean = np.mean(rolling_betas)
    fig_beta.add_hline(y=beta_mean, line_dash="dot", line_color="#F59E0B",
                      annotation_text=f"Moyenne = {beta_mean:.4f}")
    
    fig_beta.update_layout(
        title=f'Évolution du Beta — Fenêtre Glissante : {window_size} jours',
        xaxis_title='Date', yaxis_title='Beta',
        yaxis=dict(range=[0.85, 1.20], tickformat='.3f'),
        height=450, template='plotly_white', hovermode='x unified'
    )
    st.plotly_chart(fig_beta, use_container_width=True)
    
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
    
    with st.expander("📘 Guide Complet — Évolution du Beta"):
        st.markdown("""
            ### 🔁 Comment est calculé le Beta Glissant ?
            
            **Méthode :** Fenêtre mobile (sliding window)
            
            Pour chaque point du graphique :
            1. Sélectionner une fenêtre de N jours consécutifs (ex: 30 jours)
            2. Extraire les rendements du portefeuille et du MASI20 sur cette fenêtre
            3. Calculer le Beta : `β = Cov(Rp, Rb) / Var(Rb)`
            4. Décaler la fenêtre d'un jour et répéter
            
            **Exemple avec fenêtre = 30 jours :**
            ```
            Jour 30 → Beta calculé sur jours [1-30]
            Jour 31 → Beta calculé sur jours [2-31]
            ...
            Jour 90 → Beta calculé sur jours [61-90]
            ```
            
            **→ Réponse :** Le Beta est **recalculé à chaque nouvelle fenêtre**, 
            pas avec un seul delta fixe. Chaque point représente un Beta indépendant.
            
            ### 📊 Qu'est-ce que la Corrélation ?
            
            La **corrélation de Pearson** mesure la force de la relation **linéaire** 
            entre deux séries de rendements.
            
            **Formule :** `ρ = Cov(Rp, Rb) / (σp × σb)`
            
            | Valeur de ρ | Interprétation | Pour la couverture |
            |-------------|----------------|-------------------|
            | +1.00 | Parfaite positive | Couverture très efficace ✅ |
            | +0.70 à +0.99 | Forte positive | Bonne efficacité ✅ |
            | +0.30 à +0.69 | Modérée positive | Couverture acceptable ⚠️ |
            | < +0.30 | Faible | Couverture peu fiable ❌ |
            
            ### 📈 Lecture du Graphique [0.85 - 1.20]
            
            **Pourquoi cette plage ?** Un Beta proche de 1 indique une bonne réplication.
            
            | Observation | Interprétation | Action |
            |-------------|----------------|--------|
            | Stable autour de 1.00 | Bonne réplication | Utiliser Beta moyen pour N* |
            | Tendance haussière | Risque en augmentation | Surveiller et ajuster N* |
            | Fortes fluctuations | Beta instable | Privilégier Beta récent |
            | Sortie de [0.85-1.20] | Divergence significative | Investiguer les causes |
            
            ### 🎯 Comment utiliser pour N* ?
            
            - **Beta stable** (écart-type < 0.05) → Utiliser la **moyenne**
            - **Beta instable** (écart-type > 0.10) → Utiliser le **Beta récent**
            - **Corrélation faible** (< 0.70) → Reconsidérer la stratégie de couverture
        """)

# =============================================================================
# ONGLET 3: PRICING THÉORIQUE — VERSION RENOUVELÉE
# =============================================================================
with tab_pricing:
    
    st.markdown("""
        ### 📐 Pricing Théorique — Instruction BAM N° IN-2026-01
        Calcul du cours théorique avec **Term Structure** (multi-échéances) et **Backtesting**
    """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 1: DONNÉES OFFICIELLES MASI20
    # ─────────────────────────────────────────────────────────────────────────
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
    
    if 'constituents_pricing' not in st.session_state:
        st.session_state['constituents_pricing'] = get_masi20_constituents()
    constituents_pricing = st.session_state['constituents_pricing']
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 2: CALCUL DU TAUX DE DIVIDENDE
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("💰 2. Taux de Dividende — Formule BAM")
    
    taux_dividende, df_details_div = calculer_taux_dividende_indice(constituents_pricing)
    
    col_td1, col_td2, col_td3 = st.columns(3)
    with col_td1:
        st.metric("Taux de Dividende (d)", f"{taux_dividende*100:.4f}%",
                 help="Calculé selon : d = Σ(Pi × Di / Ci)")
    with col_td2:
        st.metric("Constituants", f"{len(constituents_pricing)}")
    with col_td3:
        st.info(f"📅 MAJ : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with st.expander("📊 Détail du calcul par action"):
        st.dataframe(df_details_div, use_container_width=True)
        st.caption(f"**Résultat :** d = {taux_dividende*100:.4f}% = {taux_dividende:.6f}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 3: PARAMÈTRES DE PRICING
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔧 3. Paramètres de Valorisation")
    
    col_spot, col_r, col_t = st.columns(3)
    
    with col_spot:
        spot = st.number_input("Niveau Spot MASI20 (S)", min_value=1000.0, value=1876.54,
                              step=10.0, format="%.2f", help="Cours de clôture de l'indice")
    
    with col_r:
        taux_bkam = get_taux_sans_risque('10ans')
        r = st.number_input("Taux sans risque (r) %", min_value=0.0, max_value=15.0,
                           value=taux_bkam * 100, step=0.1, format="%.2f") / 100
    
    with col_t:
        jours = st.number_input("Jours jusqu'échéance de référence", min_value=1, max_value=365, value=90, step=1)
        t = jours / 360
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 4: TERM STRUCTURE — PRIX PAR ÉCHÉANCE (NOUVEAU)
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Term Structure — Prix Théoriques par Échéance")
    
    # Calcul pour différentes maturités
    echeances = {
        '1 mois': 30,
        '3 mois': 90,
        '6 mois': 180,
        '12 mois': 360
    }
    
    prix_theoriques = {}
    bases = {}
    
    for nom, nb_jours in echeances.items():
        t_jours = nb_jours / 360
        F0 = spot * np.exp((r - taux_dividende) * t_jours)
        prix_theoriques[nom] = F0
        bases[nom] = F0 - spot
    
    # Affichage des métriques
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
    
    # Graphique de la Term Structure
    st.divider()
    st.markdown("### 📈 Courbe des Prix Théoriques")
    
    fig_term = go.Figure()
    
    fig_term.add_trace(go.Scatter(
        x=list(echeances.keys()),
        y=list(prix_theoriques.values()),
        mode='lines+markers',
        name='Prix théorique',
        line=dict(color=config.COLORS['primary'], width=3),
        marker=dict(size=10),
        text=[f"{F0:,.2f} pts" for F0 in prix_theoriques.values()],
        textposition='top center'
    ))
    
    # Ligne du spot
    fig_term.add_hline(y=spot, line_dash="dash", line_color="#10B981", 
                      annotation_text=f'Spot = {spot:,.2f}', annotation_position="top right")
    
    fig_term.update_layout(
        title='Structure par Terme des Prix Futures',
        xaxis_title='Échéance',
        yaxis_title='Prix (points)',
        height=400,
        template='plotly_white',
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_term, use_container_width=True)
    
    # Interprétation
    base_3m = bases['3 mois']
    if base_3m > 0:
        st.success(f"📈 **Contango** : La courbe est ascendante (r > d). Le marché anticipe une hausse des prix.")
    elif base_3m < 0:
        st.warning(f"📉 **Backwardation** : La courbe est descendante (d > r). Les dividendes dominent le coût de portage.")
    else:
        st.info("⚖️ **Équilibre** : r ≈ d, prix constants sur toutes les échéances.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 5: BACKTESTING — THÉORIQUE VS RÉEL (NOUVEAU)
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🧪 Backtesting — Validation du Modèle")
    
    st.markdown("""
        Comparaison des prix théoriques avec les prix de marché historiques pour valider la précision du modèle.
    """)
    
    # Simulation de backtesting (données mockées pour l'exemple)
    # Dans la version finale, il faudra scraper les prix réels des futures
    
    np.random.seed(42)
    jours_backtest = 60
    dates_backtest = [datetime.now() - timedelta(days=i) for i in range(jours_backtest)][::-1]
    
    # Prix spot simulés
    spots_simules = spot * np.exp(np.cumsum(np.random.normal(0, 0.01, jours_backtest)))
    
    # Prix théoriques simulés
    prix_theo_simules = spots_simules * np.exp((r - taux_dividende) * (90/360))
    
    # Prix de marché simulés (avec bruit)
    prix_marche_simules = prix_theo_simules * (1 + np.random.normal(0, 0.001, jours_backtest))
    
    # Erreurs
    erreurs = prix_theo_simules - prix_marche_simules
    erreurs_abs = np.abs(erreurs)
    erreurs_rel = np.abs(erreurs / prix_marche_simules) * 100
    
    # Métriques
    mae = np.mean(erreurs_abs)
    mape = np.mean(erreurs_rel)
    r2 = 1 - np.sum(erreurs**2) / np.sum((prix_marche_simules - np.mean(prix_marche_simules))**2)
    
    col_mae, col_mape, col_r2 = st.columns(3)
    
    with col_mae:
        st.metric("MAE (Erreur Absolue Moyenne)", f"{mae:.2f} pts",
                 help="Erreur moyenne entre théorique et marché")
    
    with col_mape:
        st.metric("MAPE (Erreur Relative)", f"{mape:.3f}%",
                 help="Pourcentage d'erreur moyen")
    
    with col_r2:
        st.metric("R² (Coefficient de détermination)", f"{r2:.6f}",
                 help="Qualité de l'ajustement (1 = parfait)")
    
    # Interprétation
    if mape < 0.5:
        st.success("✅ **Modèle très précis** : L'erreur relative est inférieure à 0.5%")
    elif mape < 1.5:
        st.info("ℹ️ **Modèle acceptable** : L'erreur relative est entre 0.5% et 1.5%")
    else:
        st.warning("⚠️ **Modèle à recalibrer** : L'erreur relative dépasse 1.5%")
    
    # Graphique de backtesting
    st.divider()
    fig_backtest = go.Figure()
    
    fig_backtest.add_trace(go.Scatter(
        x=dates_backtest,
        y=prix_theo_simules,
        mode='lines',
        name='Prix théorique',
        line=dict(color=config.COLORS['primary'], width=2)
    ))
    
    fig_backtest.add_trace(go.Scatter(
        x=dates_backtest,
        y=prix_marche_simules,
        mode='lines',
        name='Prix marché',
        line=dict(color='#F59E0B', width=2, dash='dash')
    ))
    
    fig_backtest.add_trace(go.Scatter(
        x=dates_backtest,
        y=erreurs,
        mode='lines',
        name='Erreur',
        line=dict(color='#EF4444', width=1),
        yaxis='y2'
    ))
    
    fig_backtest.update_layout(
        title='Backtesting — Prix Théorique vs Prix de Marché (60 jours)',
        xaxis_title='Date',
        yaxis_title='Prix (points)',
        yaxis2=dict(title='Erreur (pts)', overlaying='y', side='right'),
        height=500,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_backtest, use_container_width=True)
    
    st.caption("""
        **Note :** Les données de marché sont simulées pour cette démonstration. 
        Dans la version finale, les prix réels des futures seront scrapés depuis la Bourse de Casablanca.
    """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 6: PRIX THÉORIQUE DE RÉFÉRENCE
    # ─────────────────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📊 Prix Théorique de Référence")
    
    F0 = calculer_prix_theorique_future_bam(spot, r, taux_dividende, t)
    base = calculer_base_future(F0, spot)
    cout_portage = calculer_cout_portage(r, taux_dividende, t)
    
    col_f0, col_base, col_cp, col_vn = st.columns(4)
    
    with col_f0:
        st.markdown(f"""
            <div style='padding:25px; background:linear-gradient(135deg,#1E3A5F,#2E5C8A);
                        border-radius:12px; text-align:center; color:white;'>
                <p style='margin:0; font-size:0.9em; opacity:0.9;'>Prix Théorique F₀</p>
                <p style='margin:10px 0 0 0; font-size:2.8em; font-weight:700;'>{F0:,.2f}</p>
                <p style='margin:5px 0 0 0; font-size:0.85em; opacity:0.8;'>points</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_base:
        couleur = "#10B981" if base['points'] > 0 else "#EF4444"
        st.markdown(f"""
            <div style='padding:25px; background:white; border-radius:12px; text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.08); border-left:5px solid {couleur};'>
                <p style='margin:0; font-size:0.9em; color:#6B7280;'>Base (F₀ - S)</p>
                <p style='margin:10px 0 0 0; font-size:2em; font-weight:700; color:{couleur};'>{base['points']:+,.2f}</p>
                <p style='margin:5px 0 0 0; font-size:0.85em; color:#6B7280;'>{base['percentage']:+.2f}%</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_cp:
        st.metric("Coût de Portage", f"{cout_portage*100:+.2f}%", help="(r - d) × t")
    with col_vn:
        st.metric("Valeur Notionnelle", f"{F0 * config.MULTIPLICATEUR:,.0f} MAD", 
                 help=f"{config.MULTIPLICATEUR} MAD/point")
    
    st.info(f"""
        **Formule BAM appliquée (Instruction N° IN-2026-01) :**
        
        `F₀ = S × e^((r - d) × t)`
        
        `F₀ = {spot:,.2f} × e^(({r*100:.2f}% - {taux_dividende*100:.4f}%) × {t:.4f})`
        
        **Résultat : F₀ = {F0:,.2f} points** | **Base :** {base['points']:+,.2f} points ({base['percentage']:+.2f}%)
    """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 7: RÉFÉRENCES RÉGLEMENTAIRES
    # ─────────────────────────────────────────────────────────────────────────
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
    
    st.success("""
        ✅ **Conformité :** Cette application applique strictement la formule officielle 
        de Bank Al-Maghrib pour le calcul des cours théoriques des futures sur indice.
    """)
    
    # ─────────────────────────────────────────────────────────────────────────
    # SECTION 8: GUIDE COMPLET
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("📘 Guide Complet — Pricing Théorique BAM"):
        st.markdown("""
            ### 📐 Formule Officielle — Instruction BAM N° IN-2026-01
            
            **Cours théorique = S × e^((r - d) × t)**
            
            | Variable | Signification | Source |
            |----------|---------------|--------|
            | **S** | Prix spot de l'indice | Bourse de Casablanca |
            | **r** | Taux sans risque | BKAM (Bons du Trésor) |
            | **d** | Taux de dividende | Calculé : Σ(Pi×Di/Ci) |
            | **t** | Temps (jours/360) | Calcul avec tous les jours |
            
            ### 💰 Calcul du Taux de Dividende (d)
            
            **Formule : d = Σ (Pi × Di / Ci)**
            
            | Symbole | Signification |
            |---------|---------------|
            | **Pi** | Poids du titre i dans l'indice |
            | **Di** | Dividende annuel par action i |
            | **Ci** | Cours actuel de l'action i |
            
            ### 📊 Term Structure
            
            La **structure par terme** montre l'évolution des prix théoriques selon la maturité :
            
            - **Contango** : Courbe ascendante (r > d) → Marché normal
            - **Backwardation** : Courbe descendante (d > r) → Dividendes élevés
            - Permet d'identifier les échéances attractives
            
            ### 🧪 Backtesting
            
            Le **backtesting** compare les prix théoriques avec les prix de marché :
            
            **Métriques de validation :**
            - **MAE** : Erreur absolue moyenne (en points)
            - **MAPE** : Erreur relative moyenne (en %)
            - **R²** : Qualité de l'ajustement (1 = parfait)
            
            **Interprétation :**
            - MAPE < 0.5% → Modèle très précis ✅
            - MAPE 0.5-1.5% → Modèle acceptable ⚠️
            - MAPE > 1.5% → Modèle à recalibrer ❌
            
            ### 🎓 Fondement : Absence d'Arbitrage
            
            > À l'équilibre, aucun trader ne peut réaliser un profit sans risque 
            > en exploitant la différence entre future et spot.
            
            **Stratégies d'arbitrage :**
            - Si Prix Marché > Cours Théorique → Vendre Future + Acheter Spot
            - Si Prix Marché < Cours Théorique → Acheter Future + Vendre Spot
            - À l'équilibre : Prix Marché = Cours Théorique
            
            ### ⚠️ Limites
            
            - Marchés parfaits ≠ réalité (coûts de transaction existent)
            - Dividendes estimés, pas garantis
            - Taux sans risque variable
            - Liquidité modérée sur MASI20 futures
            - Données historiques limitées pour le backtesting
            
            ### 💡 Bonnes Pratiques
            
            1. Actualiser régulièrement r, d et S
            2. Utiliser la Term Structure pour choisir l'échéance optimale
            3. Valider régulièrement le modèle via backtesting
            4. Comparer avec le prix marché comme benchmark
            5. Intégrer les coûts de transaction dans l'analyse
            6. Documenter les hypothèses pour traçabilité
        """)

# =============================================================================
# NIVEAU 1: FOOTER
# =============================================================================
st.divider()
st.caption(
    f"MASI Futures Pro v{config.APP_VERSION} | "
    f"Basé sur l'Instruction BAM N° IN-2026-01 | "
    f"© {datetime.now().year} — Usage professionnel et éducatif"
)

# =============================================================================
# PAGE 4: CONSTRUCTION & COUVERTURE DE PORTEFEUILLE — MASI Futures Pro
# Version 2.0
# Développeurs: OULMADANI Ilyas & ATANANE Oussama
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Portfolio & Couverture", page_icon="🛡️", layout="wide")

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
    <style>
    .result-box {
        padding: 28px;
        background: linear-gradient(135deg, #1E3A5F, #2E5C8A);
        border-radius: 14px;
        text-align: center;
        color: white;
    }
    .result-box .label { font-size: 0.85em; opacity: 0.8; margin-bottom: 6px; }
    .result-box .value { font-size: 3em; font-weight: 700; line-height: 1; }
    .result-box .sub   { font-size: 0.8em; opacity: 0.65; margin-top: 6px; }

    .formula-card {
        background: #f0f4ff;
        border-left: 4px solid #2E5C8A;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 18px;
    }
    .formula-card .formula {
        font-size: 1.4em;
        font-weight: 600;
        color: #1E3A5F;
        margin: 6px 0 4px;
        font-family: monospace;
    }
    .formula-card .legend {
        font-size: 0.82em;
        color: #444;
        margin-top: 4px;
    }

    .prot-bar-wrap {
        background: #e8f5e9;
        border-radius: 8px;
        height: 12px;
        overflow: hidden;
        margin-top: 8px;
    }
    .prot-bar {
        height: 12px;
        border-radius: 8px;
        background: linear-gradient(90deg, #10B981, #34D399);
        transition: width 0.4s ease;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DONNÉES DE RÉFÉRENCE — MASI20
# =============================================================================
MASI20_STOCKS = {
    "ATW":  {"nom": "Attijariwafa Bank",          "secteur": "Banques",       "prix": 485.00},
    "BCP":  {"nom": "Banque Centrale Populaire",  "secteur": "Banques",       "prix": 142.50},
    "IAM":  {"nom": "Maroc Telecom",              "secteur": "Télécom",       "prix": 128.00},
    "OCP":  {"nom": "OCP Group",                  "secteur": "Mines",         "prix": 185.00},
    "CIH":  {"nom": "CIH Bank",                   "secteur": "Banques",       "prix": 245.00},
    "CFG":  {"nom": "CFG Bank",                   "secteur": "Banques",       "prix": 165.00},
    "BMCE": {"nom": "Bank of Africa",             "secteur": "Banques",       "prix": 198.00},
    "WAA":  {"nom": "Wafa Assurance",             "secteur": "Assurances",    "prix": 3600.00},
    "CMT":  {"nom": "Ciments du Maroc",           "secteur": "Matériaux",     "prix": 1490.00},
    "HOL":  {"nom": "Holcim Maroc",               "secteur": "Matériaux",     "prix": 410.00},
    "LHM":  {"nom": "LafargeHolcim Maroc",        "secteur": "Matériaux",     "prix": 1650.00},
    "MNG":  {"nom": "Managem",                    "secteur": "Mines",         "prix": 1880.00},
    "MSA":  {"nom": "BMCI",                       "secteur": "Banques",       "prix": 620.00},
    "ADH":  {"nom": "Addoha",                     "secteur": "Immobilier",    "prix": 15.80},
    "ALM":  {"nom": "Aluminium du Maroc",         "secteur": "Industrie",     "prix": 1340.00},
    "BOA":  {"nom": "BOA Maroc",                  "secteur": "Banques",       "prix": 175.00},
    "RDS":  {"nom": "Résidences Dar Saada",       "secteur": "Immobilier",    "prix": 55.00},
    "TMA":  {"nom": "Total Maroc",                "secteur": "Énergie",       "prix": 990.00},
    "SNP":  {"nom": "Sonasid",                    "secteur": "Industrie",     "prix": 590.00},
    "CSR":  {"nom": "Cosumar",                    "secteur": "Agroalimentaire","prix": 310.00},
}

SECTEUR_COLORS = {
    "Banques":        "#2563EB",
    "Télécom":        "#7C3AED",
    "Mines":          "#D97706",
    "Assurances":     "#059669",
    "Matériaux":      "#DC2626",
    "Immobilier":     "#DB2777",
    "Industrie":      "#0891B2",
    "Énergie":        "#65A30D",
    "Agroalimentaire":"#EA580C",
}

# =============================================================================
# SESSION STATE
# =============================================================================
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = []   # liste de dicts {ticker, poids}

# =============================================================================
# EN-TÊTE
# =============================================================================
st.title("🛡️ Construction & Couverture de Portefeuille")
st.caption("MASI Futures Pro — Gestion professionnelle et calcul de couverture optimale N*")

tab_builder, tab_coverage = st.tabs([
    "🎨  Construction du Portefeuille",
    "🛡️  Couverture Optimale (N*)",
])

# =============================================================================
# ONGLET 1 — CONSTRUCTION DU PORTEFEUILLE
# =============================================================================
with tab_builder:

    # ── Sélecteur d'action ──────────────────────────────────────────────────
    st.markdown("### ➕ Ajouter une action au portefeuille")

    already_in = [row["ticker"] for row in st.session_state["portfolio"]]
    available  = {k: v for k, v in MASI20_STOCKS.items() if k not in already_in}

    if not available:
        st.success("✅ Toutes les actions du MASI20 ont été ajoutées au portefeuille.")
    else:
        col_sel, col_poids, col_btn = st.columns([3, 1.5, 1])

        with col_sel:
            options_display = {
                f"{ticker} — {info['nom']} ({info['secteur']})": ticker
                for ticker, info in available.items()
            }
            choix_label = st.selectbox(
                "Action MASI20",
                list(options_display.keys()),
                label_visibility="collapsed",
                placeholder="Choisir une action…"
            )
            ticker_choisi = options_display[choix_label]

        with col_poids:
            poids_initial = round(100 / (len(st.session_state["portfolio"]) + 1), 1)
            poids_input = st.number_input(
                "Pondération (%)",
                min_value=0.1,
                max_value=100.0,
                value=float(poids_initial),
                step=0.1,
                label_visibility="collapsed"
            )

        with col_btn:
            if st.button("➕ Ajouter", use_container_width=True, type="primary"):
                st.session_state["portfolio"].append({
                    "ticker": ticker_choisi,
                    "poids":  poids_input
                })
                st.rerun()

    st.divider()

    # ── Portefeuille courant ─────────────────────────────────────────────────
    if not st.session_state["portfolio"]:
        st.info("💡 Sélectionnez une action ci-dessus pour commencer à construire votre portefeuille.")
    else:
        pf = st.session_state["portfolio"]
        total_poids = sum(r["poids"] for r in pf)

        # Alerte somme des poids
        if abs(total_poids - 100) > 0.01:
            delta = round(100 - total_poids, 2)
            signe = "+" if delta > 0 else ""
            st.error(
                f"⚠️ La somme des pondérations est **{total_poids:.2f}%** "
                f"({signe}{delta}%). Corrigez avant de passer à la couverture."
            )
        else:
            st.success("✅ La somme des pondérations est bien égale à 100%.")

        # ── Métriques ──────────────────────────────────────────────────────
        total_valeur_ref = sum(
            MASI20_STOCKS[r["ticker"]]["prix"] * (r["poids"] / 100) * 1000
            for r in pf
        )
        nb_secteurs = len({MASI20_STOCKS[r["ticker"]]["secteur"] for r in pf})

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("📦 Nombre de lignes",      len(pf))
        mc2.metric("🏦 Secteurs représentés",  nb_secteurs)
        mc3.metric("⚖️ Somme des poids",       f"{total_poids:.2f}%")
        mc4.metric("⚡ Poids moyen",            f"{(total_poids/len(pf)):.1f}%")

        st.divider()

        # ── Tableau éditable ───────────────────────────────────────────────
        st.markdown("### 📋 Composition & ajustement des pondérations")

        header = st.columns([1, 2, 1.5, 1.2, 1.2, 1.2, 1.2, 0.6])
        for h, label in zip(header, ["Ticker","Nom","Secteur","Prix (MAD)","Poids (%)","Valeur (MAD*)","Barre","❌"]):
            h.markdown(f"<small style='color:grey'>{label}</small>", unsafe_allow_html=True)

        to_delete = None
        new_weights = []

        for i, row in enumerate(pf):
            info    = MASI20_STOCKS[row["ticker"]]
            valeur  = info["prix"] * (row["poids"] / 100) * 1000

            c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([1, 2, 1.5, 1.2, 1.2, 1.2, 1.2, 0.6])
            c1.markdown(f"**{row['ticker']}**")
            c2.write(info["nom"])
            c3.write(info["secteur"])
            c4.write(f"{info['prix']:,.2f}")

            new_w = c5.number_input(
                "poids", min_value=0.1, max_value=100.0,
                value=float(row["poids"]), step=0.1,
                key=f"w_{i}", label_visibility="collapsed"
            )
            new_weights.append(new_w)

            c6.write(f"{valeur:,.0f}")

            pct = min(row["poids"], 100)
            c7.markdown(
                f"<div style='background:#e5e7eb;border-radius:99px;height:8px;margin-top:14px'>"
                f"<div style='width:{pct}%;background:#2563EB;height:8px;border-radius:99px'></div></div>",
                unsafe_allow_html=True
            )

            if c8.button("🗑️", key=f"del_{i}"):
                to_delete = i

        # Appliquer suppressions / mises à jour
        if to_delete is not None:
            st.session_state["portfolio"].pop(to_delete)
            st.rerun()

        for i, w in enumerate(new_weights):
            st.session_state["portfolio"][i]["poids"] = w

        st.caption("*Valeur calculée à titre indicatif sur une base de 1 000 unités par action.")

        # Boutons d'action rapide
        col_eq, col_reset, _ = st.columns([1.5, 1.5, 5])
        with col_eq:
            if st.button("⚖️ Égaliser les poids", use_container_width=True):
                equal = round(100 / len(pf), 2)
                for row in st.session_state["portfolio"]:
                    row["poids"] = equal
                # ajuster le dernier pour arriver pile à 100
                diff = round(100 - equal * len(pf), 2)
                st.session_state["portfolio"][-1]["poids"] = round(equal + diff, 2)
                st.rerun()
        with col_reset:
            if st.button("🗑️ Vider le portefeuille", use_container_width=True):
                st.session_state["portfolio"] = []
                st.rerun()

        st.divider()

        # ── Visualisations ─────────────────────────────────────────────────
        st.markdown("### 📊 Analyse graphique")
        vc1, vc2 = st.columns(2)

        # Camembert par action
        with vc1:
            labels = [r["ticker"] for r in pf]
            vals   = [r["poids"]  for r in pf]
            colors = [SECTEUR_COLORS.get(MASI20_STOCKS[r["ticker"]]["secteur"], "#888") for r in pf]
            fig_pie = go.Figure(go.Pie(
                labels=labels, values=vals,
                hole=0.45,
                marker=dict(colors=colors),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Poids : %{value:.1f}%<extra></extra>"
            ))
            fig_pie.update_layout(
                title="Allocation par action",
                showlegend=False,
                margin=dict(t=40, b=10, l=10, r=10),
                height=320
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Barres par secteur
        with vc2:
            df_sec = pd.DataFrame([
                {
                    "Secteur": MASI20_STOCKS[r["ticker"]]["secteur"],
                    "Poids":   r["poids"]
                }
                for r in pf
            ]).groupby("Secteur", as_index=False)["Poids"].sum().sort_values("Poids", ascending=False)

            fig_bar = go.Figure(go.Bar(
                x=df_sec["Secteur"], y=df_sec["Poids"],
                marker_color=[SECTEUR_COLORS.get(s, "#888") for s in df_sec["Secteur"]],
                text=df_sec["Poids"].round(1).astype(str) + "%",
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"
            ))
            fig_bar.update_layout(
                title="Allocation sectorielle",
                yaxis_title="Poids (%)",
                xaxis_tickangle=-30,
                margin=dict(t=40, b=40, l=10, r=10),
                height=320,
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# =============================================================================
# ONGLET 2 — COUVERTURE OPTIMALE (N*)
# =============================================================================
with tab_coverage:

    # ── Rappel de la formule ────────────────────────────────────────────────
    st.markdown("""
    <div class="formula-card">
        <div style="font-size:0.82em;color:#555;margin-bottom:2px">
            Formule de couverture optimale (Hull, Options, Futures and Other Derivatives) :
        </div>
        <div class="formula">N* = β × P / A</div>
        <div class="legend">
            <b>P</b> = Valeur du portefeuille à couvrir (MAD) &nbsp;|&nbsp;
            <b>A</b> = Valeur notionnelle d'un contrat future = Prix future × Multiplicateur &nbsp;|&nbsp;
            <b>β</b> = Bêta du portefeuille par rapport au MASI20
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Paramètres")

    # ── Synchronisation depuis l'onglet 1 ──────────────────────────────────
    pf_valeur_sync = 0.0
    if st.session_state["portfolio"]:
        poids_ok = abs(sum(r["poids"] for r in st.session_state["portfolio"]) - 100) < 0.01
        if poids_ok:
            pf_valeur_sync = sum(
                MASI20_STOCKS[r["ticker"]]["prix"] * (r["poids"] / 100) * 1000
                for r in st.session_state["portfolio"]
            )
            st.info(
                f"💼 Portefeuille détecté depuis l'onglet 1 — "
                f"Valeur indicative : **{pf_valeur_sync:,.0f} MAD**. "
                f"Vous pouvez l'utiliser ci-dessous ou saisir une valeur personnalisée."
            )

    pc1, pc2, pc3 = st.columns(3)

    with pc1:
        valeur_defaut = float(pf_valeur_sync) if pf_valeur_sync > 0 else 16_000_000.0
        P = st.number_input(
            "💰 Valeur du portefeuille P (MAD)",
            min_value=0.0,
            value=valeur_defaut,
            step=100_000.0,
            format="%.0f"
        )

    with pc2:
        F = st.number_input(
            "📈 Prix future MASI20 (points)",
            min_value=100.0,
            value=1_876.54,
            step=1.0,
            format="%.2f"
        )

    with pc3:
        M = st.number_input(
            "✖️ Multiplicateur (MAD/point)",
            min_value=1,
            value=10,
            disabled=True,
            help="Fixé à 10 MAD par point d'indice selon les spécifications du contrat MASI20."
        )

    beta = st.slider(
        "📐 Bêta du portefeuille (β) par rapport au MASI20",
        min_value=0.10,
        max_value=2.50,
        value=0.98,
        step=0.01,
        help=(
            "β < 1 : portefeuille moins volatile que l'indice | "
            "β = 1 : suit parfaitement l'indice | "
            "β > 1 : portefeuille plus volatile que l'indice"
        )
    )

    st.divider()

    # ── Calcul N* ───────────────────────────────────────────────────────────
    A      = F * M
    N_star = round(beta * P / A) if A > 0 else 0
    notionnel_couvert = N_star * A
    taux_couverture   = (notionnel_couvert / P * 100) if P > 0 else 0

    st.markdown("### 🎯 Résultat du calcul")

    rc1, rc2, rc3, rc4 = st.columns(4)

    with rc1:
        st.markdown(f"""
            <div class="result-box">
                <div class="label">Contrats à vendre (position courte)</div>
                <div class="value">{N_star:,}</div>
                <div class="sub">contrats MASI20 futures</div>
            </div>
        """, unsafe_allow_html=True)

    with rc2:
        st.metric("Valeur notionnelle A", f"{A:,.0f} MAD",
                  help="A = Prix future × Multiplicateur")

    with rc3:
        st.metric("Notionnel couvert",    f"{notionnel_couvert:,.0f} MAD")

    with rc4:
        st.metric("Taux de couverture",   f"{taux_couverture:.1f}%")

    st.markdown(f"""
    > **Formule appliquée :**  
    > N* = β × P / A = {beta:.2f} × {P:,.0f} / {A:,.0f} = **{N_star:,} contrats**
    """)

    st.divider()

    # ── Simulation d'impact ─────────────────────────────────────────────────
    st.markdown("### 🧪 Simulation d'impact de marché")

    sc1, sc2 = st.columns([2, 3])

    with sc1:
        variation = st.slider(
            "Variation du MASI20 (%)",
            min_value=-25.0,
            max_value=25.0,
            value=-10.0,
            step=1.0
        )

    with sc2:
        perte_pf        = P * (variation / 100) * beta
        gain_futures    = N_star * M * F * (-variation / 100)
        impact_net      = perte_pf + gain_futures
        protection_pct  = (
            min((abs(gain_futures) / abs(perte_pf)) * 100, 100)
            if perte_pf != 0 else 100
        )
        val_finale_sans = P + perte_pf
        val_finale_avec = P + impact_net

        col_a, col_b, col_c = st.columns(3)
        col_a.metric(
            "Impact sans couverture",
            f"{perte_pf:+,.0f} MAD",
            delta_color="inverse"
        )
        col_b.metric(
            "Gain sur futures",
            f"{gain_futures:+,.0f} MAD",
            delta_color="normal"
        )
        col_c.metric(
            "Impact net (avec couverture)",
            f"{impact_net:+,.0f} MAD",
            delta_color="inverse"
        )

    # Barre de protection
    prot_display = max(0, min(protection_pct, 100))
    signe        = "baisse" if variation < 0 else "hausse"
    st.markdown(f"""
    <div style="background:#ecfdf5;border-radius:12px;padding:18px 22px;margin-top:12px">
        <div style="font-weight:600;color:#065f46;font-size:1.05em">
            🛡️ Protection du portefeuille : {prot_display:.1f}%
            &nbsp;|&nbsp; Variation MASI20 : <b>{variation:+.0f}%</b> ({signe})
        </div>
        <div class="prot-bar-wrap">
            <div class="prot-bar" style="width:{prot_display}%"></div>
        </div>
        <div style="margin-top:10px;color:#065f46;font-size:0.88em">
            Valeur finale <b>sans</b> couverture : <b>{val_finale_sans:,.0f} MAD</b> &nbsp;|&nbsp;
            Valeur finale <b>avec</b> couverture : <b>{val_finale_avec:,.0f} MAD</b> &nbsp;|&nbsp;
            Perte évitée : <b>{abs(perte_pf - impact_net):,.0f} MAD</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Graphique scénarios ─────────────────────────────────────────────────
    st.markdown("### 📈 Comparaison selon les scénarios de marché")

    scenarios = np.arange(-25, 26, 1)
    pertes_sans = [P * (v / 100) * beta for v in scenarios]
    pertes_avec = [
        P * (v / 100) * beta + N_star * M * F * (-v / 100)
        for v in scenarios
    ]

    fig_scen = go.Figure()
    fig_scen.add_trace(go.Scatter(
        x=scenarios, y=pertes_sans,
        name="Sans couverture",
        line=dict(color="#DC2626", width=2),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.08)"
    ))
    fig_scen.add_trace(go.Scatter(
        x=scenarios, y=pertes_avec,
        name="Avec couverture (N*)",
        line=dict(color="#10B981", width=2),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"
    ))
    fig_scen.add_vline(
        x=variation, line_dash="dot",
        line_color="#2E5C8A", line_width=1.5,
        annotation_text=f"Scénario sélectionné : {variation:+.0f}%",
        annotation_position="top right"
    )
    fig_scen.add_hline(y=0, line_color="grey", line_width=0.8)
    fig_scen.update_layout(
        xaxis_title="Variation du MASI20 (%)",
        yaxis_title="Impact sur le portefeuille (MAD)",
        legend=dict(orientation="h", y=1.05),
        margin=dict(t=30, b=40, l=10, r=10),
        height=380,
        hovermode="x unified"
    )
    st.plotly_chart(fig_scen, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v2.0 | Portfolio & Couverture | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

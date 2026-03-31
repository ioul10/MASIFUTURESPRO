# =============================================================================
# PAGE : CONSTRUCTION, BÊTA & COUVERTURE DE PORTEFEUILLE — MASI Futures Pro
# Version 3.0
# Développeurs: OULMADANI Ilyas & ATANANE Oussama
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Portfolio & Couverture", page_icon="🛡️", layout="wide")

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>
.result-box {
    padding: 28px 20px;
    background: linear-gradient(135deg, #1E3A5F, #2E5C8A);
    border-radius: 14px;
    text-align: center;
    color: white;
}
.result-box .label { font-size: 0.82em; opacity: 0.75; margin-bottom: 6px; }
.result-box .value { font-size: 3em; font-weight: 700; line-height: 1; }
.result-box .sub   { font-size: 0.78em; opacity: 0.60; margin-top: 6px; }

.formula-card {
    background: #f0f4ff;
    border-left: 4px solid #2E5C8A;
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 18px;
}
.formula-card .formula {
    font-size: 1.35em;
    font-weight: 600;
    color: #1E3A5F;
    margin: 6px 0 4px;
    font-family: monospace;
}
.formula-card .legend { font-size: 0.82em; color: #444; margin-top: 4px; }

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
}
.info-banner {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.88em;
    color: #1e40af;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DONNÉES DE RÉFÉRENCE — MASI20
# =============================================================================
MASI20_STOCKS = {
    "ATW":  {"nom": "Attijariwafa Bank",         "secteur": "Banques",         "prix": 485.00,  "yf": "ATW.CS"},
    "BCP":  {"nom": "Banque Centrale Populaire", "secteur": "Banques",         "prix": 142.50,  "yf": "BCP.CS"},
    "IAM":  {"nom": "Maroc Telecom",             "secteur": "Télécom",         "prix": 128.00,  "yf": "IAM.CS"},
    "OCP":  {"nom": "OCP Group",                 "secteur": "Mines",           "prix": 185.00,  "yf": "OCP.CS"},
    "CIH":  {"nom": "CIH Bank",                  "secteur": "Banques",         "prix": 245.00,  "yf": "CIH.CS"},
    "CFG":  {"nom": "CFG Bank",                  "secteur": "Banques",         "prix": 165.00,  "yf": "CFG.CS"},
    "BMCE": {"nom": "Bank of Africa",            "secteur": "Banques",         "prix": 198.00,  "yf": "BOA.CS"},
    "WAA":  {"nom": "Wafa Assurance",            "secteur": "Assurances",      "prix": 3600.00, "yf": "WAA.CS"},
    "CMT":  {"nom": "Ciments du Maroc",          "secteur": "Matériaux",       "prix": 1490.00, "yf": "CMT.CS"},
    "HOL":  {"nom": "Holcim Maroc",              "secteur": "Matériaux",       "prix": 410.00,  "yf": "HOL.CS"},
    "MNG":  {"nom": "Managem",                   "secteur": "Mines",           "prix": 1880.00, "yf": "MNG.CS"},
    "ADH":  {"nom": "Addoha",                    "secteur": "Immobilier",      "prix": 15.80,   "yf": "ADH.CS"},
    "ALM":  {"nom": "Aluminium du Maroc",        "secteur": "Industrie",       "prix": 1340.00, "yf": "ALM.CS"},
    "BOA":  {"nom": "BOA Maroc",                 "secteur": "Banques",         "prix": 175.00,  "yf": "BOAM.CS"},
    "TMA":  {"nom": "Total Maroc",               "secteur": "Énergie",         "prix": 990.00,  "yf": "TMA.CS"},
    "SNP":  {"nom": "Sonasid",                   "secteur": "Industrie",       "prix": 590.00,  "yf": "SNP.CS"},
    "CSR":  {"nom": "Cosumar",                   "secteur": "Agroalimentaire", "prix": 310.00,  "yf": "CSR.CS"},
    "MSA":  {"nom": "BMCI",                      "secteur": "Banques",         "prix": 620.00,  "yf": "BMCI.CS"},
    "RDS":  {"nom": "Résidences Dar Saada",      "secteur": "Immobilier",      "prix": 55.00,   "yf": "RDS.CS"},
    "LHM":  {"nom": "LafargeHolcim Maroc",       "secteur": "Matériaux",       "prix": 1650.00, "yf": "LHM.CS"},
}

MASI_INDEX_YF = "^MASI.CS"

SECTEUR_COLORS = {
    "Banques":         "#2563EB",
    "Télécom":         "#7C3AED",
    "Mines":           "#D97706",
    "Assurances":      "#059669",
    "Matériaux":       "#DC2626",
    "Immobilier":      "#DB2777",
    "Industrie":       "#0891B2",
    "Énergie":         "#65A30D",
    "Agroalimentaire": "#EA580C",
}

# =============================================================================
# SESSION STATE
# =============================================================================
for key, default in [
    ("portfolio",    []),
    ("hist_data",    {}),
    ("index_data",   None),
    ("betas",        {}),
    ("beta_pf",      None),
    ("data_loaded",  False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# =============================================================================
# HELPERS
# =============================================================================
def beta_color(b: float) -> str:
    if b < 0.8:  return "#059669"
    if b < 1.2:  return "#2563EB"
    return "#DC2626"

def beta_label(b: float) -> str:
    if b < 0.8:  return "Défensif"
    if b < 1.2:  return "Neutre"
    return "Agressif"

def compute_beta(stock_ret: pd.Series, index_ret: pd.Series) -> float:
    """β = Cov(Ri, Rm) / Var(Rm)"""
    combined = pd.concat([stock_ret, index_ret], axis=1).dropna()
    if len(combined) < 10:
        return np.nan
    cov = np.cov(combined.iloc[:, 0].values, combined.iloc[:, 1].values)
    return round(cov[0, 1] / cov[1, 1], 4) if cov[1, 1] != 0 else np.nan

def safe_close(raw: "pd.DataFrame") -> "pd.Series":
    """Extrait la colonne Close quelle que soit la version de yfinance."""
    if isinstance(raw.columns, pd.MultiIndex):
        return raw["Close"].iloc[:, 0]
    return raw["Close"]

def download_data(tickers: list, period_days: int = 90):
    try:
        import yfinance as yf
    except ImportError:
        return {}, None, ["yfinance non installé — lancez : pip install yfinance"]

    end   = datetime.today()
    start = end - timedelta(days=period_days)
    errors = []

    # Indice MASI
    idx_series = None
    try:
        raw = yf.download(MASI_INDEX_YF, start=start, end=end,
                          progress=False, auto_adjust=True)
        if raw.empty:
            raise ValueError("Aucune donnée")
        idx_series = safe_close(raw)
        idx_series.name = "MASI"
    except Exception as e:
        errors.append(f"Indice MASI ({MASI_INDEX_YF}) : {e}")

    # Actions
    hist = {}
    for ticker in tickers:
        yf_tk = MASI20_STOCKS[ticker]["yf"]
        try:
            raw = yf.download(yf_tk, start=start, end=end,
                              progress=False, auto_adjust=True)
            if raw.empty:
                raise ValueError("Aucune donnée retournée")
            s = safe_close(raw)
            s.name = ticker
            hist[ticker] = s
        except Exception as e:
            errors.append(f"{ticker} ({yf_tk}) : {e}")

    return hist, idx_series, errors

# =============================================================================
# EN-TÊTE
# =============================================================================
st.title("🛡️ Construction & Couverture de Portefeuille")
st.caption("MASI Futures Pro v3.0 — Données réelles · Bêta calculé · Couverture optimale N*")

tab_builder, tab_beta, tab_coverage = st.tabs([
    "🎨  Construction du Portefeuille",
    "📐  Bêta & Données Historiques",
    "🛡️  Couverture Optimale (N*)",
])

# =============================================================================
# ONGLET 1 — CONSTRUCTION DU PORTEFEUILLE
# =============================================================================
with tab_builder:

    st.markdown("### ➕ Ajouter une action MASI20")

    already_in = [r["ticker"] for r in st.session_state["portfolio"]]
    available  = {k: v for k, v in MASI20_STOCKS.items() if k not in already_in}

    if not available:
        st.success("✅ Toutes les actions du MASI20 ont été ajoutées.")
    else:
        col_sel, col_poids, col_btn = st.columns([3, 1.5, 1])
        with col_sel:
            options = {
                f"{tk}  —  {info['nom']}  ({info['secteur']})": tk
                for tk, info in available.items()
            }
            choix         = st.selectbox("Action", list(options.keys()), label_visibility="collapsed")
            ticker_choisi = options[choix]
        with col_poids:
            n = len(st.session_state["portfolio"]) + 1
            poids_def = round(100 / n, 1)
            poids_input = st.number_input(
                "Poids (%)", min_value=0.1, max_value=100.0,
                value=float(poids_def), step=0.1, label_visibility="collapsed"
            )
        with col_btn:
            if st.button("➕ Ajouter", use_container_width=True, type="primary"):
                st.session_state["portfolio"].append({"ticker": ticker_choisi, "poids": poids_input})
                st.session_state["data_loaded"] = False
                st.rerun()

    st.divider()

    if not st.session_state["portfolio"]:
        st.info("💡 Sélectionnez une action ci-dessus pour commencer à construire votre portefeuille.")
    else:
        pf          = st.session_state["portfolio"]
        total_poids = round(sum(r["poids"] for r in pf), 2)

        if abs(total_poids - 100) > 0.01:
            delta = round(100 - total_poids, 2)
            st.error(f"⚠️ Somme des pondérations = **{total_poids:.2f}%** "
                     f"({'+'if delta>0 else ''}{delta}%). Corrigez avant de calculer le bêta.")
        else:
            st.success("✅ Somme des pondérations = 100% — portefeuille valide.")

        nb_secteurs = len({MASI20_STOCKS[r["ticker"]]["secteur"] for r in pf})
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("📦 Lignes",          len(pf))
        mc2.metric("🏦 Secteurs",        nb_secteurs)
        mc3.metric("⚖️ Somme des poids", f"{total_poids:.2f}%")
        mc4.metric("⚡ Poids moyen",     f"{total_poids/len(pf):.1f}%")

        st.divider()
        st.markdown("### 📋 Composition & ajustement des pondérations")

        headers = ["Ticker","Nom","Secteur","Prix réf. (MAD)","Poids (%)","Valeur (MAD*)","Barre","❌"]
        hcols   = st.columns([1, 2.2, 1.5, 1.3, 1.2, 1.4, 1.2, 0.5])
        for hc, hl in zip(hcols, headers):
            hc.markdown(f"<small style='color:grey'>{hl}</small>", unsafe_allow_html=True)

        to_delete   = None
        new_weights = []

        for i, row in enumerate(pf):
            info   = MASI20_STOCKS[row["ticker"]]
            valeur = info["prix"] * (row["poids"] / 100) * 1000
            c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([1, 2.2, 1.5, 1.3, 1.2, 1.4, 1.2, 0.5])
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

        if to_delete is not None:
            st.session_state["portfolio"].pop(to_delete)
            st.session_state["data_loaded"] = False
            st.rerun()

        for i, w in enumerate(new_weights):
            if st.session_state["portfolio"][i]["poids"] != w:
                st.session_state["portfolio"][i]["poids"] = w
                st.session_state["data_loaded"] = False

        st.caption("*Valeur indicative sur une base de 1 000 unités par ligne.")

        col_eq, col_rst, _ = st.columns([1.5, 1.5, 5])
        with col_eq:
            if st.button("⚖️ Égaliser les poids", use_container_width=True):
                eq   = round(100 / len(pf), 2)
                diff = round(100 - eq * len(pf), 2)
                for row in st.session_state["portfolio"]:
                    row["poids"] = eq
                st.session_state["portfolio"][-1]["poids"] = round(eq + diff, 2)
                st.session_state["data_loaded"] = False
                st.rerun()
        with col_rst:
            if st.button("🗑️ Vider le portefeuille", use_container_width=True):
                for k in ["portfolio","hist_data","index_data","betas","beta_pf"]:
                    st.session_state[k] = [] if k == "portfolio" else ({} if k in ("hist_data","betas") else None)
                st.session_state["data_loaded"] = False
                st.rerun()

        st.divider()
        st.markdown("### 📊 Analyse graphique")
        vc1, vc2 = st.columns(2)

        with vc1:
            labels = [r["ticker"] for r in pf]
            vals   = [r["poids"]  for r in pf]
            colors = [SECTEUR_COLORS.get(MASI20_STOCKS[r["ticker"]]["secteur"], "#888") for r in pf]
            fig_pie = go.Figure(go.Pie(
                labels=labels, values=vals, hole=0.45,
                marker=dict(colors=colors), textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>"
            ))
            fig_pie.update_layout(title="Allocation par action", showlegend=False,
                                  margin=dict(t=40,b=10,l=10,r=10), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)

        with vc2:
            df_sec = (
                pd.DataFrame([
                    {"Secteur": MASI20_STOCKS[r["ticker"]]["secteur"], "Poids": r["poids"]}
                    for r in pf
                ]).groupby("Secteur", as_index=False)["Poids"].sum()
                .sort_values("Poids", ascending=False)
            )
            fig_bar = go.Figure(go.Bar(
                x=df_sec["Secteur"], y=df_sec["Poids"],
                marker_color=[SECTEUR_COLORS.get(s,"#888") for s in df_sec["Secteur"]],
                text=df_sec["Poids"].round(1).astype(str)+"%", textposition="outside",
            ))
            fig_bar.update_layout(title="Allocation sectorielle", yaxis_title="Poids (%)",
                                  xaxis_tickangle=-30, margin=dict(t=40,b=40,l=10,r=10),
                                  height=320, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)


# =============================================================================
# ONGLET 2 — BÊTA & DONNÉES HISTORIQUES
# =============================================================================
with tab_beta:

    st.markdown("### 📐 Calcul du Bêta par régression linéaire")

    st.markdown("""
    <div class="formula-card">
        <div style="font-size:0.82em;color:#555;margin-bottom:2px">
            Formule du bêta — CAPM (Capital Asset Pricing Model) :
        </div>
        <div class="formula">β = Cov(Ri, Rm) / Var(Rm)</div>
        <div class="legend">
            <b>Ri</b> = rendements journaliers de l'action &nbsp;|&nbsp;
            <b>Rm</b> = rendements journaliers du MASI &nbsp;|&nbsp;
            Période : <b>3 mois glissants</b> · Fréquence : <b>journalière</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state["portfolio"]:
        st.info("💡 Construisez d'abord votre portefeuille dans l'onglet 1.")
    else:
        poids_ok = abs(sum(r["poids"] for r in st.session_state["portfolio"]) - 100) < 0.01

        if not poids_ok:
            st.warning("⚠️ Les pondérations ne somment pas à 100%. Corrigez-les dans l'onglet 1.")

        col_btn, col_info = st.columns([2, 5])
        with col_btn:
            load_btn = st.button(
                "🔄 Télécharger les cours & Calculer les bêtas",
                type="primary", use_container_width=True, disabled=not poids_ok
            )
        with col_info:
            st.markdown("""
            <div class="info-banner">
                📡 Source : <b>Yahoo Finance</b> (suffix <code>.CS</code> — Bourse de Casablanca) ·
                Fenêtre : <b>3 mois glissants</b> · Fréquence : <b>journalière</b>.
                Si un ticker n'est pas disponible sur Yahoo Finance, un avertissement s'affiche
                et l'action est exclue du calcul du bêta.
            </div>
            """, unsafe_allow_html=True)

        # Téléchargement
        if load_btn:
            tickers = [r["ticker"] for r in st.session_state["portfolio"]]
            prog    = st.progress(0, text="Connexion à Yahoo Finance…")

            hist, idx_series, errors = download_data(tickers, period_days=90)

            prog.progress(60, text="Calcul des rendements et des bêtas…")

            st.session_state["hist_data"]   = hist
            st.session_state["index_data"]  = idx_series
            st.session_state["data_loaded"] = True
            st.session_state["betas"]       = {}
            st.session_state["beta_pf"]     = None

            if errors:
                for e in errors:
                    st.warning(f"⚠️ {e}")

            if idx_series is not None:
                idx_ret = idx_series.pct_change().dropna()
                for tk, series in hist.items():
                    stk_ret = series.pct_change().dropna()
                    st.session_state["betas"][tk] = compute_beta(stk_ret, idx_ret)

                # Bêta portefeuille = somme pondérée (sur actions avec bêta valide)
                num, denom = 0.0, 0.0
                for row in st.session_state["portfolio"]:
                    tk = row["ticker"]
                    b  = st.session_state["betas"].get(tk, np.nan)
                    if not np.isnan(b):
                        num   += (row["poids"] / 100) * b
                        denom += row["poids"] / 100
                if denom > 0:
                    st.session_state["beta_pf"] = round(num / denom, 4)

            prog.progress(100, text="Terminé ✅")
            st.success("✅ Données téléchargées et bêtas calculés avec succès.")
            st.rerun()

        # Affichage résultats
        if st.session_state["data_loaded"] and st.session_state["betas"]:

            st.divider()

            # --- Bêta du portefeuille ---
            beta_pf = st.session_state["beta_pf"]
            if beta_pf is not None:
                col_card, col_interp = st.columns([1.5, 4])
                with col_card:
                    st.markdown(f"""
                    <div class="result-box">
                        <div class="label">Bêta du portefeuille</div>
                        <div class="value">{beta_pf:.3f}</div>
                        <div class="sub">{beta_label(beta_pf)} vs MASI</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_interp:
                    impact = beta_pf * 10
                    if beta_pf < 0.8:
                        msg = (f"Avec β = **{beta_pf:.3f}**, le portefeuille est <b>défensif</b> : "
                               f"il amplifie moins les variations du MASI. "
                               f"Pour une baisse de 10% de l'indice, la perte estimée est de "
                               f"<b>{impact:.1f}%</b>.")
                    elif beta_pf <= 1.2:
                        msg = (f"Avec β = **{beta_pf:.3f}**, le portefeuille suit <b>fidèlement</b> le MASI. "
                               f"Pour une baisse de 10% de l'indice, la perte estimée est de "
                               f"<b>{impact:.1f}%</b>.")
                    else:
                        msg = (f"Avec β = **{beta_pf:.3f}**, le portefeuille est <b>agressif</b> : "
                               f"il amplifie les variations du MASI. "
                               f"Pour une baisse de 10% de l'indice, la perte estimée est de "
                               f"<b>{impact:.1f}%</b>.")

                    st.markdown(f"""
                    <div style='background:#f8fafc;border-radius:10px;padding:18px 20px;
                                border:1px solid #e2e8f0;'>
                        <div style='font-size:0.82em;color:#64748b;margin-bottom:6px'>Interprétation</div>
                        <div style='font-size:0.96em;line-height:1.6'>{msg}</div>
                        <div style='margin-top:12px;font-size:0.80em;color:#94a3b8'>
                            β &lt; 0.8 → Défensif &nbsp;|&nbsp;
                            0.8 ≤ β ≤ 1.2 → Neutre &nbsp;|&nbsp;
                            β &gt; 1.2 → Agressif
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # --- Tableau des bêtas individuels ---
            st.markdown("### 📊 Bêta individuel par action")

            rows_beta = []
            for row in st.session_state["portfolio"]:
                tk   = row["ticker"]
                info = MASI20_STOCKS[tk]
                b    = st.session_state["betas"].get(tk, np.nan)
                rows_beta.append({
                    "Ticker":          tk,
                    "Nom":             info["nom"],
                    "Secteur":         info["secteur"],
                    "Poids (%)":       f"{row['poids']:.1f}",
                    "β individuel":    f"{b:.4f}" if not np.isnan(b) else "N/D",
                    "Contribution β":  f"{(row['poids']/100)*b:.4f}" if not np.isnan(b) else "N/D",
                    "Profil":          beta_label(b) if not np.isnan(b) else "N/D",
                })

            st.dataframe(pd.DataFrame(rows_beta), use_container_width=True, hide_index=True)

            # Graphique bêtas
            ok_rows = [r for r in rows_beta if r["β individuel"] != "N/D"]
            if ok_rows:
                fig_beta = go.Figure()
                fig_beta.add_hline(y=1, line_dash="dot", line_color="grey",
                                   annotation_text="β = 1 (marché)", annotation_position="right")
                fig_beta.add_bar(
                    x=[r["Ticker"] for r in ok_rows],
                    y=[float(r["β individuel"]) for r in ok_rows],
                    marker_color=[beta_color(float(r["β individuel"])) for r in ok_rows],
                    text=[r["β individuel"] for r in ok_rows],
                    textposition="outside",
                )
                fig_beta.update_layout(
                    title="Bêta individuel des actions du portefeuille",
                    yaxis_title="β", xaxis_title="Action",
                    height=360, margin=dict(t=40,b=40,l=10,r=10), showlegend=False
                )
                st.plotly_chart(fig_beta, use_container_width=True)

            st.divider()

            # --- Graphiques historiques par action ---
            st.markdown("### 📈 Cours historiques (3 mois) — Analyse par action")
            st.caption("Cliquez sur un ticker pour déplier le graphique de performance et la droite de régression.")

            idx_series = st.session_state["index_data"]

            for row in st.session_state["portfolio"]:
                tk = row["ticker"]
                if tk not in st.session_state["hist_data"]:
                    continue

                series = st.session_state["hist_data"][tk]
                info   = MASI20_STOCKS[tk]
                b      = st.session_state["betas"].get(tk, np.nan)
                color  = SECTEUR_COLORS.get(info["secteur"], "#2563EB")

                returns = series.pct_change().dropna()
                perf_3m = ((series.iloc[-1] / series.iloc[0]) - 1) * 100

                with st.expander(
                    f"**{tk}**  ·  {info['nom']}  ·  "
                    f"β = {'N/D' if np.isnan(b) else f'{b:.4f}'}  ·  "
                    f"Poids {row['poids']:.1f}%  ·  "
                    f"Perf 3 mois : {perf_3m:+.1f}%",
                    expanded=False
                ):
                    ec1, ec2, ec3, ec4 = st.columns(4)
                    ec1.metric("Cours actuel",
                               f"{series.iloc[-1]:,.2f} MAD",
                               f"{perf_3m:+.2f}% (3 mois)")
                    ec2.metric("Plus haut", f"{series.max():,.2f} MAD")
                    ec3.metric("Plus bas",  f"{series.min():,.2f} MAD")
                    ec4.metric("Volatilité annualisée",
                               f"{returns.std()*np.sqrt(252)*100:.1f}%")

                    # -- Graphique 1 : performance relative normalisée --
                    fig_hist = go.Figure()
                    s_norm = (series / series.iloc[0] - 1) * 100
                    fig_hist.add_trace(go.Scatter(
                        x=s_norm.index, y=s_norm.values,
                        name=tk, line=dict(color=color, width=2.5),
                        fill="tozeroy",
                        fillcolor=f"rgba({int(color[1:3],16)},"
                                  f"{int(color[3:5],16)},"
                                  f"{int(color[5:7],16)},0.07)",
                        hovertemplate=f"<b>{tk}</b><br>%{{x|%d/%m/%Y}}<br>%{{y:+.2f}}%<extra></extra>"
                    ))
                    if idx_series is not None:
                        idx_al = idx_series.reindex(series.index, method="ffill")
                        if not idx_al.dropna().empty:
                            idx_norm = (idx_al / idx_al.dropna().iloc[0] - 1) * 100
                            fig_hist.add_trace(go.Scatter(
                                x=idx_norm.index, y=idx_norm.values,
                                name="MASI (réf.)",
                                line=dict(color="#94a3b8", width=1.5, dash="dot"),
                                hovertemplate="<b>MASI</b><br>%{x|%d/%m/%Y}<br>%{y:+.2f}%<extra></extra>"
                            ))
                    fig_hist.add_hline(y=0, line_color="grey", line_width=0.7)
                    fig_hist.update_layout(
                        title=f"{info['nom']} ({tk}) — Performance relative sur 3 mois (base 100)",
                        yaxis_title="Performance (%)", xaxis_title="",
                        height=340, margin=dict(t=40,b=30,l=10,r=10),
                        legend=dict(orientation="h", y=1.1),
                        hovermode="x unified"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                    # -- Graphique 2 : droite de régression bêta --
                    if idx_series is not None and not np.isnan(b):
                        stk_ret = series.pct_change().dropna()
                        idx_ret = idx_series.pct_change().dropna()
                        combined = pd.concat([stk_ret, idx_ret], axis=1).dropna()
                        combined.columns = ["stock", "index"]

                        x_vals = combined["index"].values
                        y_vals = combined["stock"].values
                        x_line = np.linspace(x_vals.min(), x_vals.max(), 200)
                        y_line = b * x_line

                        # R²
                        y_pred = b * x_vals
                        ss_res = np.sum((y_vals - y_pred) ** 2)
                        ss_tot = np.sum((y_vals - y_vals.mean()) ** 2)
                        r2     = 1 - ss_res / ss_tot if ss_tot != 0 else 0

                        fig_reg = go.Figure()
                        fig_reg.add_trace(go.Scatter(
                            x=x_vals * 100, y=y_vals * 100,
                            mode="markers",
                            marker=dict(color=color, opacity=0.5, size=6),
                            name="Rendements journaliers",
                            hovertemplate="MASI : %{x:.3f}%<br>"+tk+" : %{y:.3f}%<extra></extra>"
                        ))
                        fig_reg.add_trace(go.Scatter(
                            x=x_line * 100, y=y_line * 100,
                            mode="lines",
                            line=dict(color="#1E3A5F", width=2),
                            name=f"Droite de régression  β = {b:.4f}  |  R² = {r2:.3f}"
                        ))
                        fig_reg.add_hline(y=0, line_color="lightgrey", line_width=0.8)
                        fig_reg.add_vline(x=0, line_color="lightgrey", line_width=0.8)
                        fig_reg.update_layout(
                            title=(f"Régression bêta — {tk} vs MASI  "
                                   f"(β = {b:.4f}, R² = {r2:.3f})"),
                            xaxis_title="Rendement MASI (%)",
                            yaxis_title=f"Rendement {tk} (%)",
                            height=340,
                            margin=dict(t=40,b=30,l=10,r=10),
                            legend=dict(orientation="h", y=1.1)
                        )
                        st.plotly_chart(fig_reg, use_container_width=True)

        elif st.session_state["data_loaded"]:
            st.warning("⚠️ Aucune donnée disponible. Vérifiez votre connexion Internet.")


# =============================================================================
# ONGLET 3 — COUVERTURE OPTIMALE (N*)
# =============================================================================
with tab_coverage:

    st.markdown("""
    <div class="formula-card">
        <div style="font-size:0.82em;color:#555;margin-bottom:2px">
            Formule de couverture optimale — Hull, Options Futures and Other Derivatives :
        </div>
        <div class="formula">N* = β × P / A</div>
        <div class="legend">
            <b>P</b> = Valeur du portefeuille (MAD) &nbsp;|&nbsp;
            <b>A</b> = Prix future × Multiplicateur (valeur notionnelle d'un contrat) &nbsp;|&nbsp;
            <b>β</b> = Bêta du portefeuille par rapport au MASI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Paramètres")

    # Synchronisation portefeuille
    pf          = st.session_state["portfolio"]
    poids_ok    = pf and abs(sum(r["poids"] for r in pf) - 100) < 0.01
    pf_val_sync = 0.0
    if poids_ok:
        pf_val_sync = sum(
            MASI20_STOCKS[r["ticker"]]["prix"] * (r["poids"] / 100) * 1000
            for r in pf
        )
        st.info(f"💼 Portefeuille détecté — valeur indicative : **{pf_val_sync:,.0f} MAD**")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        P = st.number_input(
            "💰 Valeur du portefeuille P (MAD)",
            min_value=0.0,
            value=float(pf_val_sync) if pf_val_sync > 0 else 16_000_000.0,
            step=100_000.0, format="%.0f"
        )
    with pc2:
        F = st.number_input(
            "📈 Prix future MASI20 (points)",
            min_value=100.0, value=1_876.54,
            step=1.0, format="%.2f"
        )
    with pc3:
        st.number_input(
            "✖️ Multiplicateur (MAD/point)",
            min_value=1, value=10, disabled=True,
            help="Fixé à 10 MAD/point selon les spécifications du contrat MASI20."
        )
        M = 10

    # Bêta : calculé ou manuel
    beta_calc = st.session_state["beta_pf"]
    if beta_calc is not None:
        st.success(f"✅ Bêta calculé automatiquement depuis l'onglet 2 : **β = {beta_calc:.4f}**")
        beta_def  = float(beta_calc)
        src_label = f"Calculé (régression 3 mois) : β = {beta_calc:.4f}"
    else:
        st.warning("⚠️ Bêta non encore calculé. Rendez-vous dans l'onglet **Bêta & Données Historiques** "
                   "ou saisissez une valeur manuellement ci-dessous.")
        beta_def  = 0.98
        src_label = "Manuel (valeur par défaut)"

    beta = st.slider(
        f"📐 Bêta du portefeuille (β) — {src_label}",
        min_value=0.10, max_value=2.50,
        value=beta_def, step=0.01,
        help="β < 0.8 : défensif | 0.8–1.2 : neutre | β > 1.2 : agressif"
    )

    st.divider()

    # Calcul N*
    A                 = F * M
    N_star            = round(beta * P / A) if A > 0 else 0
    notionnel_couvert = N_star * A
    taux_couverture   = (notionnel_couvert / P * 100) if P > 0 else 0

    st.markdown("### 🎯 Résultat")

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.markdown(f"""
        <div class="result-box">
            <div class="label">Contrats à vendre (position courte)</div>
            <div class="value">{N_star:,}</div>
            <div class="sub">contrats MASI20 futures</div>
        </div>
        """, unsafe_allow_html=True)
    rc2.metric("Valeur notionnelle A", f"{A:,.0f} MAD",
               help="A = Prix future × Multiplicateur")
    rc3.metric("Notionnel couvert",    f"{notionnel_couvert:,.0f} MAD")
    rc4.metric("Taux de couverture",   f"{taux_couverture:.1f}%")

    st.markdown(f"""
    > **Formule appliquée :**
    > N* = β × P / A = **{beta:.4f}** × {P:,.0f} / {A:,.0f} = **{N_star:,} contrats**
    """)

    st.divider()

    # Simulation
    st.markdown("### 🧪 Simulation d'impact de marché")

    sc1, sc2 = st.columns([2, 3])
    with sc1:
        variation = st.slider("Variation du MASI20 (%)",
                              min_value=-25.0, max_value=25.0,
                              value=-10.0, step=1.0)
    with sc2:
        perte_pf     = P * (variation / 100) * beta
        gain_futures = N_star * M * F * (-variation / 100)
        impact_net   = perte_pf + gain_futures
        protection   = min(abs(gain_futures) / abs(perte_pf) * 100, 100) if perte_pf != 0 else 100
        val_sans     = P + perte_pf
        val_avec     = P + impact_net

        ca, cb, cc = st.columns(3)
        ca.metric("Impact sans couverture", f"{perte_pf:+,.0f} MAD", delta_color="inverse")
        cb.metric("Gain sur futures",       f"{gain_futures:+,.0f} MAD")
        cc.metric("Impact net (couvert)",   f"{impact_net:+,.0f} MAD", delta_color="inverse")

    prot_d = max(0, min(protection, 100))
    st.markdown(f"""
    <div style="background:#ecfdf5;border-radius:12px;padding:18px 22px;margin-top:12px">
        <div style="font-weight:600;color:#065f46;font-size:1.05em">
            🛡️ Protection : {prot_d:.1f}% &nbsp;|&nbsp;
            Variation simulée : <b>{variation:+.0f}%</b>
        </div>
        <div class="prot-bar-wrap">
            <div class="prot-bar" style="width:{prot_d}%"></div>
        </div>
        <div style="margin-top:10px;color:#065f46;font-size:0.88em">
            Sans couverture → <b>{val_sans:,.0f} MAD</b> &nbsp;|&nbsp;
            Avec couverture → <b>{val_avec:,.0f} MAD</b> &nbsp;|&nbsp;
            Perte évitée : <b>{abs(perte_pf - impact_net):,.0f} MAD</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Graphique scénarios
    st.markdown("### 📈 Comparaison tous scénarios (-25% → +25%)")

    scenarios   = np.arange(-25, 26, 1)
    pertes_sans = [P * (v / 100) * beta for v in scenarios]
    pertes_avec = [P * (v/100)*beta + N_star*M*F*(-v/100) for v in scenarios]

    fig_scen = go.Figure()
    fig_scen.add_trace(go.Scatter(
        x=scenarios, y=pertes_sans, name="Sans couverture",
        line=dict(color="#DC2626", width=2),
        fill="tozeroy", fillcolor="rgba(220,38,38,0.08)"
    ))
    fig_scen.add_trace(go.Scatter(
        x=scenarios, y=pertes_avec, name=f"Avec couverture (N* = {N_star})",
        line=dict(color="#10B981", width=2),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.08)"
    ))
    fig_scen.add_vline(
        x=variation, line_dash="dot", line_color="#2E5C8A", line_width=1.5,
        annotation_text=f"Scénario : {variation:+.0f}%",
        annotation_position="top right"
    )
    fig_scen.add_hline(y=0, line_color="grey", line_width=0.8)
    fig_scen.update_layout(
        xaxis_title="Variation du MASI20 (%)",
        yaxis_title="Impact sur le portefeuille (MAD)",
        legend=dict(orientation="h", y=1.05),
        margin=dict(t=30, b=40, l=10, r=10),
        height=400, hovermode="x unified"
    )
    st.plotly_chart(fig_scen, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.divider()
st.caption(f"MASI Futures Pro v3.0 | Portfolio · Bêta · Couverture | © {datetime.now().year}")
st.caption("Développé par OULMADANI Ilyas & ATANANE Oussama")

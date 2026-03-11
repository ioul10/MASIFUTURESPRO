# =============================================================================
# CALCULS MÉTIERS — MASI Futures Pro
# Version 0.3 — Conforme Instruction BAM N° IN-2026-01
# =============================================================================

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# =============================================================================
# 1. PRICING DE BASE — FORMULE BAM
# =============================================================================

def prix_future_theorique(spot, r, q, T):
    """
    F₀ = S₀ × e^((r−q)T)
    
    Args:
        spot: Prix spot (S₀)
        r: Taux sans risque (décimal)
        q: Taux de dividende (décimal)
        T: Temps en années
    
    Returns:
        Prix théorique du future
    """
    return spot * np.exp((r - q) * T)


def calculer_prix_theorique_future_bam(spot, r, d, t):
    """
    Calcule le prix théorique d'un future selon la formule BAM
    F₀ = S × e^((r-d)t)
    
    Args:
        spot: Prix spot de l'indice (S)
        r: Taux sans risque (décimal)
        d: Taux de dividende (décimal)
        t: Temps jusqu'à l'échéance (jours/360)
    
    Returns:
        Prix théorique du future (F₀)
    """
    return spot * np.exp((r - d) * t)


def calculer_base_future(F0, S0):
    """
    Calcule la base (différence entre future et spot)
    
    Args:
        F0: Prix future théorique
        S0: Prix spot
    
    Returns:
        Dict avec base en points et pourcentage
    """
    base_pts = F0 - S0
    base_pct = (base_pts / S0) * 100 if S0 != 0 else 0
    return {'points': base_pts, 'percentage': base_pct}


def calculer_cout_portage(r, d, t):
    """
    Calcule le coût de portage
    Formule: (r - d) × t
    
    Args:
        r: Taux sans risque
        d: Taux de dividende
        t: Temps (jours/360)
    
    Returns:
        Coût de portage en pourcentage
    """
    return (r - d) * t


# =============================================================================
# 2. TAUX DE DIVIDENDE (d) — AVEC FILTRAGE PAR DATE
# =============================================================================

def calculer_taux_dividende_indice(constituents, date_echeance=None):
    """
    Calcule le taux de dividende de l'indice selon la formule BAM
    d = Σ(Pi × Di/Ci)
    
    Args:
        constituents: Liste des constituants avec:
            - ticker
            - poids (Pi)
            - dividende_annuel (Di)
            - cours (Ci)
            - prochaine_date_ex (optionnel)
            - statut (optionnel)
        date_echeance: datetime - Si fournie, filtre les dividendes avant cette date
    
    Returns:
        taux_dividende: Taux de dividende de l'indice (décimal)
        details: DataFrame avec le détail du calcul
    """
    
    taux_dividende_total = 0
    details = []
    
    for constituant in constituents:
        ticker = constituant['ticker']
        poids = constituant.get('poids', 0)
        dividende = constituant.get('dividende_annuel', 0)
        cours = constituant.get('cours', 1)
        date_ex = constituant.get('prochaine_date_ex', None)
        statut = constituant.get('statut', 'inconnu')
        
        # Filtrage par date d'échéance (si date_ex fournie)
        inclus = True
        if date_ex is not None and date_echeance is not None:
            if isinstance(date_ex, str):
                date_ex = datetime.strptime(date_ex, '%Y-%m-%d')
            inclus = date_ex <= date_echeance
        
        if not inclus:
            dividende = 0  # Exclu du calcul
        
        # Dividend yield du titre: Di/Ci
        dividend_yield = dividende / cours if cours > 0 else 0
        
        # Contribution pondérée: Pi × (Di/Ci)
        contribution = poids * dividend_yield
        taux_dividende_total += contribution
        
        details.append({
            'Ticker': ticker,
            'Nom': constituant.get('nom', ticker),
            'Poids': f"{poids*100:.2f}%",
            'Cours': f"{cours:,.2f} MAD",
            'Dividende Annuel': f"{dividende:,.2f} MAD",
            'Yield': f"{dividend_yield*100:.3f}%",
            'Contribution': f"{contribution*100:.4f}%",
            'Date Ex': date_ex.strftime('%d/%m/%Y') if date_ex else 'N/A',
            'Statut': statut,
            'Inclus': '✅' if inclus else '❌'
        })
    
    df_details = pd.DataFrame(details)
    return taux_dividende_total, df_details


# =============================================================================
# 3. TAUX SANS RISQUE (r) — DEPUIS TABLEAU ZC
# =============================================================================

def get_taux_zc(date_calcul, date_echeance, df_taux_zc):
    """
    Récupère le taux ZC le plus approprié pour une date de calcul et une échéance
    
    Args:
        date_calcul: datetime - Date à laquelle on price le future
        date_echeance: datetime - Échéance du future
        df_taux_zc: DataFrame avec colonnes [date_spot, date_maturity, zc]
    
    Returns:
        float: Taux zc en décimal (ex: 0.0285 pour 2.85%)
    """
    # Convertir les dates si nécessaire
    if not pd.api.types.is_datetime64_any_dtype(df_taux_zc['date_spot']):
        df_taux_zc['date_spot'] = pd.to_datetime(df_taux_zc['date_spot'])
    if not pd.api.types.is_datetime64_any_dtype(df_taux_zc['date_maturity']):
        df_taux_zc['date_maturity'] = pd.to_datetime(df_taux_zc['date_maturity'])
    
    # 1. Filtrer: taux publiés avant ou le jour de calcul
    df_filtre = df_taux_zc[df_taux_zc['date_spot'] <= date_calcul].copy()
    
    if len(df_filtre) == 0:
        return 0.035  # Valeur par défaut si aucune donnée
    
    # 2. Calculer l'écart en jours entre chaque maturity et l'échéance cible
    df_filtre['ecart'] = abs((df_filtre['date_maturity'] - date_echeance).dt.days)
    
    # 3. Prendre la ligne avec le plus petit écart
    meilleure = df_filtre.loc[df_filtre['ecart'].idxmin()]
    
    # 4. Retourner le taux en décimal
    return meilleure['zc'] / 100


# =============================================================================
# 4. SENSIBILITÉS (GRECQUES)
# =============================================================================

def calcul_sensibilites(spot, r, q, T):
    """
    Calcule les sensibilités du prix future
    
    Returns:
        Dict avec df_dr, df_dq, df_dS, df_dT, F0
    """
    F0 = prix_future_theorique(spot, r, q, T)
    
    df_dr = F0 * T
    df_dq = -F0 * T
    df_dS = np.exp((r - q) * T)
    df_dT = F0 * (r - q)
    
    return {
        'df_dr': df_dr,
        'df_dq': df_dq,
        'df_dS': df_dS,
        'df_dT': df_dT,
        'F0': F0
    }


def sensibilite_relative(sensibilites, spot, r, q, T):
    """
    Sensibilités relatives en %
    """
    F0 = sensibilites['F0']
    
    return {
        'dr_1pct': (sensibilites['df_dr'] / F0) * 1,
        'dq_1pct': (sensibilites['df_dq'] / F0) * 1,
        'dS_1pct': (sensibilites['df_dS'] * 1 / F0) * 100,
        'dT_1mois': (sensibilites['df_dT'] / F0) * (1/12)
    }


# =============================================================================
# 5. TERM STRUCTURE
# =============================================================================

def calcul_term_structure(spot, r, q, echeances_jours):
    """
    Calcule la structure par terme
    
    Args:
        spot: Prix spot
        r: Taux sans risque
        q: Taux de dividende
        echeances_jours: Liste des échéances en jours [30, 90, 180, 360]
    
    Returns:
        DataFrame avec la term structure
    """
    results = []
    
    for jours in echeances_jours:
        T = jours / 360  # Base 360 selon BAM
        F0 = prix_future_theorique(spot, r, q, T)
        base_pts = F0 - spot
        base_pct = (base_pts / spot) * 100 if spot != 0 else 0
        
        results.append({
            'Jours': jours,
            'Mois': round(jours / 30),
            'T_annees': T,
            'F0': round(F0, 2),
            'Base_pts': round(base_pts, 2),
            'Base_pct': round(base_pct, 3),
            'Contango': F0 > spot
        })
    
    return pd.DataFrame(results)


# =============================================================================
# 6. BACKTESTING — MÉTRIQUES DE VALIDATION
# =============================================================================

def calculer_mae(y_reel, y_pred):
    """
    Mean Absolute Error (Erreur Absolue Moyenne)
    """
    return np.mean(np.abs(np.array(y_reel) - np.array(y_pred)))


def calculer_mape(y_reel, y_pred):
    """
    Mean Absolute Percentage Error (Erreur Relative Moyenne en %)
    """
    y_reel, y_pred = np.array(y_reel), np.array(y_pred)
    mask = y_reel != 0
    return np.mean(np.abs((y_reel[mask] - y_pred[mask]) / y_reel[mask])) * 100


def calculer_r2(y_reel, y_pred):
    """
    R² (Coefficient de détermination)
    """
    y_reel, y_pred = np.array(y_reel), np.array(y_pred)
    ss_res = np.sum((y_reel - y_pred) ** 2)
    ss_tot = np.sum((y_reel - np.mean(y_reel)) ** 2)
    return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0


def backtesting_complet(df_donnees, col_spot, col_future_reel, r, d, col_date='date'):
    """
    Backtesting complet du modèle de pricing
    
    Args:
        df_donnees: DataFrame avec historique des prix
        col_spot: Nom de la colonne spot
        col_future_reel: Nom de la colonne prix future réel
        r: Taux sans risque (fixe ou colonne)
        d: Taux de dividende (fixe ou colonne)
        col_date: Nom de la colonne date
    
    Returns:
        Dict avec métriques et DataFrame des résultats
    """
    resultats = []
    
    for idx, row in df_donnees.iterrows():
        spot = row[col_spot]
        future_reel = row[col_future_reel]
        
        # Calcul du temps restant (suppose échéance fixe à J+90)
        jours_restants = 90 - idx
        t = max(jours_restants, 1) / 360
        
        # Prix théorique
        future_theo = calculer_prix_theorique_future_bam(spot, r, d, t)
        
        resultats.append({
            'date': row.get(col_date, idx),
            'spot': spot,
            'future_reel': future_reel,
            'future_theo': round(future_theo, 2),
            'ecart': round(future_theo - future_reel, 2),
            'ecart_pct': round((future_theo - future_reel) / future_reel * 100, 3)
        })
    
    df_resultats = pd.DataFrame(resultats)
    
    # Métriques globales
    mae = calculer_mae(df_resultats['future_reel'], df_resultats['future_theo'])
    mape = calculer_mape(df_resultats['future_reel'], df_resultats['future_theo'])
    r2 = calculer_r2(df_resultats['future_reel'], df_resultats['future_theo'])
    
    return {
        'mae': mae,
        'mape': mape,
        'r2': r2,
        'df': df_resultats
    }


# =============================================================================
# 7. ARBITRAGE
# =============================================================================

def detecter_arbitrage(prix_marche, prix_theorique, seuil=0.01):
    """
    Détecte les opportunités d'arbitrage
    
    Args:
        prix_marche: Prix de marché du future
        prix_theorique: Prix théorique calculé
        seuil: Seuil d'arbitrage (défaut 1%)
    
    Returns:
        Dict avec signal, stratégie, etc.
    """
    ecart_absolu = prix_marche - prix_theorique
    ecart_pct = (ecart_absolu / prix_theorique) * 100 if prix_theorique != 0 else 0
    
    if abs(ecart_pct) > seuil * 100:
        if prix_marche > prix_theorique:
            return {
                'signal': 'Surévalué',
                'statut': '⚠️ Opportunité d\'arbitrage',
                'strategie': 'Vendre Future + Acheter Spot',
                'ecart_pct': ecart_pct,
                'arbitrage_possible': True
            }
        else:
            return {
                'signal': 'Sous-évalué',
                'statut': '⚠️ Opportunité d\'arbitrage',
                'strategie': 'Acheter Future + Vendre Spot',
                'ecart_pct': ecart_pct,
                'arbitrage_possible': True
            }
    else:
        return {
            'signal': 'Équilibre',
            'statut': '✅ Pas d\'arbitrage',
            'strategie': 'Aucune opportunité',
            'ecart_pct': ecart_pct,
            'arbitrage_possible': False
        }


# =============================================================================
# 8. COUVERTURE — BETA ET N*
# =============================================================================

def calculer_beta(rendements_portefeuille, rendements_benchmark):
    """
    Calcule le Beta par régression linéaire
    Beta = Cov(Rp, Rb) / Var(Rb)
    """
    cov = np.cov(rendements_portefeuille, rendements_benchmark)[0, 1]
    var = np.var(rendements_benchmark, ddof=1)
    return cov / var if var != 0 else 1.0


def calculer_correlation(rendements_portefeuille, rendements_benchmark):
    """
    Calcule le coefficient de corrélation de Pearson
    """
    return np.corrcoef(rendements_portefeuille, rendements_benchmark)[0, 1]


def calculer_tracking_error(rendements_portefeuille, rendements_benchmark, annualise=True):
    """
    Calcule l'erreur de tracking (Tracking Error)
    TE = Std(Rp - Rb) × √252 (si annualisé)
    """
    tracking_diff = np.array(rendements_portefeuille) - np.array(rendements_benchmark)
    te = np.std(tracking_diff, ddof=1)
    
    if annualise:
        te *= np.sqrt(252)
    
    return te


def calculer_N_star(beta, valeur_portefeuille, prix_future, multiplicateur=10):
    """
    Calcule le nombre optimal de contrats futures pour couvrir un portefeuille
    Formule: N* = β × P / A
    Où A = Prix Future × Multiplicateur
    """
    A = prix_future * multiplicateur
    return round(beta * valeur_portefeuille / A)


def calculer_alpha(rendements_portefeuille, rendements_benchmark, taux_sans_risque=0.03):
    """
    Calcule l'Alpha de Jensen
    Alpha = Rp - [Rf + β × (Rb - Rf)]
    """
    beta = calculer_beta(rendements_portefeuille, rendements_benchmark)
    Rp = np.mean(rendements_portefeuille) * 252  # Annualisé
    Rb = np.mean(rendements_benchmark) * 252  # Annualisé
    
    alpha = Rp - (taux_sans_risque + beta * (Rb - taux_sans_risque))
    return alpha


# =============================================================================
# 9. UTILITAIRES
# =============================================================================

def jours_vers_annees(jours, base=360):
    """
    Conversion jours → années
    
    Args:
        jours: Nombre de jours
        base: Convention (360 ou 252)
    
    Returns:
        Temps en années
    """
    return jours / base

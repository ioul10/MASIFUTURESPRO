import numpy as np
import pandas as pd

def prix_future_theorique(spot, r, q, T):
    """F₀ = S₀ × e^((r−q)T)"""
    return spot * np.exp((r - q) * T)

def base_future(F0, S0):
    """Base = F₀ - S₀"""
    base_pts = F0 - S0
    base_pct = (base_pts / S0) * 100 if S0 != 0 else 0
    return {'points': base_pts, 'percentage': base_pct}

def calcul_sensibilites(spot, r, q, T):
    """Calcule les sensibilités du prix future"""
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
    """Sensibilités relatives en %"""
    F0 = sensibilites['F0']
    
    return {
        'dr_1pct': (sensibilites['df_dr'] / F0) * 1,
        'dq_1pct': (sensibilites['df_dq'] / F0) * 1,
        'dS_1pct': (sensibilites['df_dS'] * 1 / F0) * 100,
        'dT_1mois': (sensibilites['df_dT'] / F0) * (1/12)
    }

def calcul_term_structure(spot, r, q, echeances_jours):
    """Calcule la structure par terme"""
    results = []
    
    for jours in echeances_jours:
        T = jours / 252
        F0 = prix_future_theorique(spot, r, q, T)
        base = base_future(F0, spot)
        
        results.append({
            'Jours': jours,
            'Mois': round(jours / 30),
            'T_annees': T,
            'F0': F0,
            'Base_pts': base['points'],
            'Base_pct': base['percentage'],
            'Contango': F0 > spot
        })
    
    return pd.DataFrame(results)

def detecter_arbitrage(prix_marche, prix_theorique, seuil=0.01):
    """Détecte les opportunités d'arbitrage"""
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

def jours_vers_annees(jours):
    """Conversion jours → années"""
    return jours / 252

def calcul_cout_portage(r, q, T):
    """Coût de portage = (r - q) × T"""
    return (r - q) * T

# ────────────────────────────────────────────
# 9. CALCUL BETA ET N* (COUVERTURE)
# ────────────────────────────────────────────

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

def calculer_prix_theorique_future_bam(spot, r, d, t):
    """
    Calcule le prix théorique d'un future selon la formule BAM
    F₀ = S × e^((r-d)t)
    
    Args:
        spot: Prix spot de l'indice
        r: Taux sans risque (décimal)
        d: Taux de dividende (décimal)
        t: Temps jusqu'à l'échéance (jours/360)
    
    Returns:
        Prix théorique du future
    """
    return spot * np.exp((r - d) * t)

def calculer_base_future(F0, S0):
    """
    Calcule la base (différence entre future et spot)
    """
    base_pts = F0 - S0
    base_pct = (base_pts / S0) * 100 if S0 != 0 else 0
    return {'points': base_pts, 'percentage': base_pct}


# ============================================
# CALCULS FINANCIERS - Pricing Futures
# MASI Futures Pro - Version Alpha
# ============================================

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ────────────────────────────────────────────
# 1. PRICING DE BASE (§7.1 du document)
# ────────────────────────────────────────────

def prix_future_theorique(spot, r, q, T):
    """
    Calcule le prix théorique d'un future sur indice
    Formule: F₀ = S₀ × e^((r−q)T)  (Document §7.1)
    
    Args:
        spot: Niveau spot de l'indice (S₀) en points
        r: Taux sans risque annuel (décimal)
        q: Rendement dividendes annuel (décimal)
        T: Maturité en années
    
    Returns:
        Prix théorique du future (F₀) en points
    """
    return spot * np.exp((r - q) * T)

def base_future(F0, S0):
    """
    Calcule la base (différence entre future et spot)
    Formule: Base = F₀ - S₀
    
    Args:
        F0: Prix future théorique
        S0: Niveau spot
    
    Returns:
        Base en points et en pourcentage
    """
    base_pts = F0 - S0
    base_pct = (base_pts / S0) * 100 if S0 != 0 else 0
    return {'points': base_pts, 'percentage': base_pct}

# ────────────────────────────────────────────
# 2. SENSIBILITÉS (Grecques)
# ────────────────────────────────────────────

def calcul_sensibilites(spot, r, q, T):
    """
    Calcule les sensibilités du prix future (Grecques)
    
    Args:
        spot: Niveau spot (S₀)
        r: Taux sans risque
        q: Rendement dividendes
        T: Maturité en années
    
    Returns:
        Dict avec toutes les sensibilités
    """
    F0 = prix_future_theorique(spot, r, q, T)
    
    # dF/dr = S₀ × T × e^((r−q)T) = F₀ × T
    df_dr = F0 * T
    
    # dF/dq = -S₀ × T × e^((r−q)T) = -F₀ × T
    df_dq = -F0 * T
    
    # dF/dS = e^((r−q)T) (Delta)
    df_dS = np.exp((r - q) * T)
    
    # dF/dT = S₀ × (r−q) × e^((r−q)T) = F₀ × (r−q)
    df_dT = F0 * (r - q)
    
    return {
        'df_dr': df_dr,      # Sensibilité au taux (points par 1% de r)
        'df_dq': df_dq,      # Sensibilité aux dividendes (points par 1% de q)
        'df_dS': df_dS,      # Delta (variation de F pour 1 point de S)
        'df_dT': df_dT,      # Theta (variation de F par année)
        'F0': F0
    }

def sensibilite_relative(sensibilites, spot, r, q, T):
    """
    Calcule les sensibilités relatives (en %)
    Utile pour comprendre l'impact en pourcentage
    
    Args:
        sensibilites: Output de calcul_sensibilites()
        spot, r, q, T: Paramètres
    
    Returns:
        Dict avec sensibilités relatives
    """
    F0 = sensibilites['F0']
    
    return {
        'dr_1pct': (sensibilites['df_dr'] / F0) * 1,    # Impact de +1% sur r
        'dq_1pct': (sensibilites['df_dq'] / F0) * 1,    # Impact de +1% sur q
        'dS_1pct': (sensibilites['df_dS'] * 1 / F0) * 100,  # Impact de +1 point sur S
        'dT_1mois': (sensibilites['df_dT'] / F0) * (1/12)  # Impact de +1 mois
    }

# ────────────────────────────────────────────
# 3. TERM STRUCTURE (Courbe des Futures)
# ────────────────────────────────────────────

def calcul_term_structure(spot, r, q, echeances_jours):
    """
    Calcule la structure par terme des prix futures
    Pour plusieurs maturités
    
    Args:
        spot: Niveau spot actuel
        r: Taux sans risque
        q: Rendement dividendes
        echeances_jours: Liste des échéances en jours [30, 60, 90, 180, 365]
    
    Returns:
        DataFrame avec la courbe des futures
    """
    results = []
    
    for jours in echeances_jours:
        T = jours / 252  # Jours de trading
        F0 = prix_future_theorique(spot, r, q, T)
        base = base_future(F0, spot)
        
        results.append({
            'Jours': jours,
            'Mois': round(jours / 30),
            'T_annees': T,
            'F0': F0,
            'Base_pts': base['points'],
            'Base_pct': base['percentage'],
            'Contango': F0 > spot  # True si contango, False si backwardation
        })
    
    return pd.DataFrame(results)

# ────────────────────────────────────────────
# 4. ARBITRAGE (§7.2 du document)
# ────────────────────────────────────────────

def detecter_arbitrage(prix_marche, prix_theorique, seuil=0.01):
    """
    Détecte les opportunités d'arbitrage
    Condition d'absence d'arbitrage: F_market ≈ F_théorique
    
    Args:
        prix_marche: Prix future observé sur le marché
        prix_theorique: Prix future théorique calculé
        seuil: Seuil de tolérance (défaut: 1%)
    
    Returns:
        Dict avec signal, stratégie et détails
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

# ────────────────────────────────────────────
# 5. UTILITAIRES
# ────────────────────────────────────────────

def jours_vers_annees(jours):
    """Conversion jours → années (252 jours de trading)"""
    return jours / 252

def annees_vers_jours(annees):
    """Conversion années → jours (252 jours de trading)"""
    return annees * 252

def calcul_cout_portage(r, q, T):
    """
    Calcule le coût de portage (cost of carry)
    Formule: (r - q) × T
    """
    return (r - q) * T

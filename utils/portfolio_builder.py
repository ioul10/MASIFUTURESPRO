# ============================================
# PORTFOLIO BUILDER - MASI20 Constituents
# Données Mockées pour Développement
# ============================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_masi20_constituents():
    """
    Récupère la liste des constituants MASI20 avec leurs poids
    Données mockées basées sur une composition réaliste
    """
    constituents = [
        {'ticker': 'ATW', 'nom': 'Attijariwafa Bank', 'poids': 0.185, 'secteur': 'Banque'},
        {'ticker': 'BCP', 'nom': 'Banque Populaire', 'poids': 0.125, 'secteur': 'Banque'},
        {'ticker': 'IAM', 'nom': 'Maroc Telecom', 'poids': 0.105, 'secteur': 'Télécom'},
        {'ticker': 'OCP', 'nom': 'OCP Group', 'poids': 0.085, 'secteur': 'Chimie'},
        {'ticker': 'LAF', 'nom': 'LafargeHolcim Maroc', 'poids': 0.065, 'secteur': 'Ciment'},
        {'ticker': 'SNG', 'nom': 'Sonasid', 'poids': 0.055, 'secteur': 'Sidérurgie'},
        {'ticker': 'MNG', 'nom': 'Managem', 'poids': 0.045, 'secteur': 'Mines'},
        {'ticker': 'CIH', 'nom': 'CIH Bank', 'poids': 0.040, 'secteur': 'Banque'},
        {'ticker': 'BNA', 'nom': 'Bank Al-Maghrib', 'poids': 0.038, 'secteur': 'Banque'},
        {'ticker': 'SID', 'nom': 'Sidérurgie Nationale', 'poids': 0.035, 'secteur': 'Sidérurgie'},
        {'ticker': 'TIS', 'nom': 'Titan Cement', 'poids': 0.032, 'secteur': 'Ciment'},
        {'ticker': 'WAA', 'nom': 'Wafa Assurance', 'poids': 0.030, 'secteur': 'Assurance'},
        {'ticker': 'SAB', 'nom': 'SABIC Morocco', 'poids': 0.028, 'secteur': 'Chimie'},
        {'ticker': 'DAM', 'nom': 'Delta Holding', 'poids': 0.025, 'secteur': 'Divers'},
        {'ticker': 'HPS', 'nom': 'HPS Group', 'poids': 0.022, 'secteur': 'Technologie'},
        {'ticker': 'LUX', 'nom': 'Luxembourg Telecom', 'poids': 0.020, 'secteur': 'Télécom'},
        {'ticker': 'MAM', 'nom': 'Marsa Maroc', 'poids': 0.018, 'secteur': 'Transport'},
        {'ticker': 'NEH', 'nom': 'Nehad Group', 'poids': 0.015, 'secteur': 'Divers'},
        {'ticker': 'OUL', 'nom': 'Oulmes', 'poids': 0.012, 'secteur': 'Agroalimentaire'},
        {'ticker': 'RES', 'nom': 'Residence', 'poids': 0.010, 'secteur': 'Immobilier'}
    ]
    
    return constituents

def generer_historique_prix(constituents, jours=90):
    """
    Génère un historique de prix simulé pour les constituants
    """
    np.random.seed(42)
    dates = [datetime.now() - timedelta(days=i) for i in range(jours)]
    dates.reverse()
    
    historique = {}
    
    for constituant in constituents:
        ticker = constituant['ticker']
        # Prix initial réaliste (entre 100 et 2000 MAD)
        prix_initial = np.random.uniform(100, 2000)
        
        # Génération de prix avec tendance et volatilité
        returns = np.random.normal(0.0001, 0.015, jours)
        prix = prix_initial * np.exp(np.cumsum(returns))
        
        historique[ticker] = {
            'dates': dates,
            'prix': prix,
            'returns': np.concatenate([[0], np.diff(prix) / prix[:-1]])
        }
    
    return historique

def generer_historique_masi20(historique_constituents, constituents):
    """
    Génère l'historique MASI20 comme moyenne pondérée des constituants
    """
    dates = list(historique_constituents.values())[0]['dates']
    jours = len(dates)
    
    # Calcul du niveau MASI20 comme somme pondérée
    masi20_prices = np.zeros(jours)
    
    for constituant in constituents:
        ticker = constituant['ticker']
        poids = constituant['poids']
        prix = historique_constituents[ticker]['prix']
        # Normaliser pour que le prix initial soit autour de 100
        prix_normalise = prix / prix[0] * 100
        masi20_prices += poids * prix_normalise
    
    # Ajuster pour avoir un niveau réaliste (autour de 1800-2000)
    masi20_prices = masi20_prices * 18
    
    returns_masi20 = np.concatenate([[0], np.diff(masi20_prices) / masi20_prices[:-1]])
    
    return {
        'dates': dates,
        'prix': masi20_prices,
        'returns': returns_masi20
    }

def calculer_valeur_portefeuille(constituents, historique, date_index=-1):
    """
    Calcule la valeur actuelle du portefeuille théorique
    """
    valeur_totale = 0
    
    for constituant in constituents:
        ticker = constituant['ticker']
        poids = constituant['poids']
        prix_actuel = historique[ticker]['prix'][date_index]
        valeur_totale += poids * prix_actuel
    
    return valeur_totale * 1000  # Multiplicateur pour avoir une valeur réaliste en MAD

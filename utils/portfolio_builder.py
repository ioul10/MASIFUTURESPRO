# ============================================
# PORTFOLIO BUILDER - MASI20 Constituents
# Données Mockées pour Développement
# ============================================

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_masi20_constituents():
    """
    Récupère la liste des constituants MASI20 avec leurs poids, cours et dividendes
    Données mockées réalistes pour le développement
    """
    constituents = [
        {'ticker': 'ATW', 'nom': 'Attijariwafa Bank', 'poids': 0.185, 'secteur': 'Banque', 
         'cours': 485.0, 'dividende_annuel': 18.0},
        {'ticker': 'BCP', 'nom': 'Banque Populaire', 'poids': 0.125, 'secteur': 'Banque', 
         'cours': 142.5, 'dividende_annuel': 2.5},
        {'ticker': 'IAM', 'nom': 'Maroc Telecom', 'poids': 0.105, 'secteur': 'Télécom', 
         'cours': 128.0, 'dividende_annuel': 7.5},
        {'ticker': 'OCP', 'nom': 'OCP Group', 'poids': 0.085, 'secteur': 'Chimie', 
         'cours': 7850.0, 'dividende_annuel': 120.0},
        {'ticker': 'LAF', 'nom': 'LafargeHolcim Maroc', 'poids': 0.065, 'secteur': 'Ciment', 
         'cours': 1650.0, 'dividende_annuel': 180.0},
        {'ticker': 'SNG', 'nom': 'Sonasid', 'poids': 0.055, 'secteur': 'Sidérurgie', 
         'cours': 850.0, 'dividende_annuel': 25.0},
        {'ticker': 'MNG', 'nom': 'Managem', 'poids': 0.045, 'secteur': 'Mines', 
         'cours': 1250.0, 'dividende_annuel': 8.0},
        {'ticker': 'CIH', 'nom': 'CIH Bank', 'poids': 0.040, 'secteur': 'Banque', 
         'cours': 245.0, 'dividende_annuel': 3.5},
        {'ticker': 'BNA', 'nom': 'Bank Al-Maghrib', 'poids': 0.038, 'secteur': 'Banque', 
         'cours': 625.0, 'dividende_annuel': 45.0},
        {'ticker': 'SID', 'nom': 'Sidérurgie Nationale', 'poids': 0.035, 'secteur': 'Sidérurgie', 
         'cours': 485.0, 'dividende_annuel': 15.0},
        {'ticker': 'TIS', 'nom': 'Titan Cement', 'poids': 0.032, 'secteur': 'Ciment', 
         'cours': 285.0, 'dividende_annuel': 4.5},
        {'ticker': 'WAA', 'nom': 'Wafa Assurance', 'poids': 0.030, 'secteur': 'Assurance', 
         'cours': 4850.0, 'dividende_annuel': 90.0},
        {'ticker': 'SAB', 'nom': 'SABIC Morocco', 'poids': 0.028, 'secteur': 'Chimie', 
         'cours': 1150.0, 'dividende_annuel': 20.0},
        {'ticker': 'DAM', 'nom': 'Delta Holding', 'poids': 0.025, 'secteur': 'Divers', 
         'cours': 1250.0, 'dividende_annuel': 20.0},
        {'ticker': 'HPS', 'nom': 'HPS Group', 'poids': 0.022, 'secteur': 'Technologie', 
         'cours': 8500.0, 'dividende_annuel': 15.0},
        {'ticker': 'LUX', 'nom': 'Luxembourg Telecom', 'poids': 0.020, 'secteur': 'Télécom', 
         'cours': 1850.0, 'dividende_annuel': 30.0},
        {'ticker': 'MAM', 'nom': 'Marsa Maroc', 'poids': 0.018, 'secteur': 'Transport', 
         'cours': 165.0, 'dividende_annuel': 2.8},
        {'ticker': 'NEH', 'nom': 'Nehad Group', 'poids': 0.015, 'secteur': 'Divers', 
         'cours': 95.0, 'dividende_annuel': 1.2},
        {'ticker': 'OUL', 'nom': 'Oulmes', 'poids': 0.012, 'secteur': 'Agroalimentaire', 
         'cours': 685.0, 'dividende_annuel': 6.0},
        {'ticker': 'RES', 'nom': 'Residence', 'poids': 0.010, 'secteur': 'Immobilier', 
         'cours': 485.0, 'dividende_annuel': 4.0}
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

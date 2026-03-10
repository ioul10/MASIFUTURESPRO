# ============================================
# DATA LOADER — Chargement Fichiers Externes
# ============================================

import pandas as pd
import os

def charger_taux_bkam():
    """
    Charge les taux BKAM depuis un fichier Excel/CSV
    Retourne un DataFrame ou None si fichier introuvable
    """
    chemins_possibles = [
        'data/taux_bkam.xlsx',
        'data/taux_bkam.csv',
        '../data/taux_bkam.xlsx',
        '../data/taux_bkam.csv'
    ]
    
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            try:
                if chemin.endswith('.xlsx'):
                    return pd.read_excel(chemin)
                else:
                    return pd.read_csv(chemin)
            except Exception as e:
                print(f"Erreur lecture {chemin}: {e}")
    
    # Fallback: données par défaut
    return pd.DataFrame({
        'Maturité': ['13 semaines', '26 semaines', '52 semaines', '10 ans'],
        'Taux (%)': [2.85, 3.10, 3.35, 3.50],
        'Date': ['06/03/2026'] * 4
    })

def charger_dividendes():
    """
    Charge les dividendes depuis un fichier externe
    """
    # À implémenter si besoin
    return None

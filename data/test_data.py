# =============================================================================
# DONNÉES DE TEST — MASI Futures Pro
# Données mockées pour tester les formules de pricing et backtesting
# =============================================================================

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# =============================================================================
# 1. TAUX ZÉRO-COUPON (r) — Bank Al-Maghrib
# Format : date_spot | date_maturity | zc (taux en %)
# =============================================================================

def get_taux_zc_mock():
    """
    Génère un tableau mocké de taux ZC pour testing
    Période : 3 mois d'historique + données futures
    """
    
    # Dates de publication BKAM (hebdomadaire)
    dates_publication = [
        datetime(2026, 1, 1),
        datetime(2026, 1, 8),
        datetime(2026, 1, 15),
        datetime(2026, 1, 22),
        datetime(2026, 1, 29),
        datetime(2026, 2, 5),
        datetime(2026, 2, 12),
        datetime(2026, 2, 19),
        datetime(2026, 2, 26),
        datetime(2026, 3, 5),
        datetime(2026, 3, 12),
        datetime(2026, 3, 19),
        datetime(2026, 3, 26),
        datetime(2026, 4, 2),
        datetime(2026, 4, 9),
        datetime(2026, 4, 16),
        datetime(2026, 4, 23),
        datetime(2026, 4, 30),
        datetime(2026, 5, 7),
        datetime(2026, 5, 14),
    ]
    
    # Maturités standards (en mois à partir de la date de publication)
    maturites_mois = [3, 6, 12]  # 3 mois, 6 mois, 12 mois
    
    # Taux de base (réalistes pour le Maroc)
    taux_base = {
        3: 2.85,   # ZC 3 mois
        6: 3.10,   # ZC 6 mois
        12: 3.35,  # ZC 12 mois
    }
    
    # Générer les données
    data = []
    
    for date_pub in dates_publication:
        # Petite variation aléatoire pour chaque publication (±0.02%)
        variation = np.random.uniform(-0.02, 0.02)
        
        for maturite in maturites_mois:
            # Date de maturity = date publication + X mois
            date_maturity = date_pub + timedelta(days=maturite * 30)
            
            # Taux avec légère tendance haussière
            taux = taux_base[maturite] + variation + (maturite * 0.05)
            
            data.append({
                'date_spot': date_pub,
                'date_maturity': date_maturity,
                'zc': round(taux, 3)
            })
    
    df = pd.DataFrame(data)
    return df


# =============================================================================
# 2. DIVIDENDES MASI20 (q)
# Format : ticker | poids | cours | frequence | dividende_annuel | 
#          taux_yield_annuel | prochaine_date_ex | statut
# =============================================================================

def get_dividendes_masi20_mock():
    """
    Génère un tableau mocké des dividendes des 20 constituants MASI20
    """
    
    # Données réalistes pour les principales valeurs MASI20
    dividendes_data = [
        # Ticker, Poids, Cours, Fréquence, Div Annuel, Prochaine Date Ex, Statut
        ('ATW', 0.185, 485.0, 'semestriel', 18.0, '2026-03-15', 'annonce'),
        ('BCP', 0.125, 142.5, 'annuel', 2.5, '2026-05-20', 'annonce'),
        ('IAM', 0.105, 128.0, 'semestriel', 7.5, '2026-04-10', 'annonce'),
        ('OCP', 0.080, 7850.0, 'annuel', 120.0, '2026-07-15', 'estime'),
        ('CIH', 0.065, 245.0, 'annuel', 6.0, '2026-06-01', 'estime'),
        ('CFG', 0.055, 165.0, 'annuel', 3.5, '2026-05-15', 'annonce'),
        ('WAFACASH', 0.050, 185.0, 'annuel', 5.0, '2026-06-20', 'estime'),
        ('MARWAH', 0.045, 95.0, 'annuel', 2.0, '2026-04-25', 'annonce'),
        ('LAFARGE', 0.040, 725.0, 'annuel', 22.0, '2026-05-30', 'estime'),
        ('COSUMAR', 0.038, 165.0, 'annuel', 4.5, '2026-06-15', 'estime'),
        ('SONASID', 0.035, 850.0, 'annuel', 25.0, '2026-07-01', 'estime'),
        ('SNI', 0.032, 920.0, 'annuel', 28.0, '2026-06-25', 'estime'),
        ('BMCE', 0.030, 195.0, 'annuel', 5.5, '2026-05-10', 'annonce'),
        ('BMCI', 0.028, 565.0, 'annuel', 16.0, '2026-05-25', 'annonce'),
        ('ALLIANS', 0.025, 1250.0, 'annuel', 35.0, '2026-06-10', 'estime'),
        ('SIDER', 0.022, 485.0, 'annuel', 12.0, '2026-07-20', 'estime'),
        ('TIMAR', 0.020, 625.0, 'annuel', 18.0, '2026-06-05', 'estime'),
        ('DISWAY', 0.018, 145.0, 'annuel', 3.0, '2026-05-15', 'annonce'),
        ('JET', 0.015, 950.0, 'annuel', 28.0, '2026-06-30', 'estime'),
        ('HPS', 0.012, 6850.0, 'annuel', 195.0, '2026-07-10', 'estime'),
    ]
    
    # Créer le DataFrame
    data = []
    for ticker, poids, cours, frequence, div_annuel, date_ex, statut in dividendes_data:
        # Calculer le taux de rendement annuel
        taux_yield = (div_annuel / cours) * 100
        
        data.append({
            'ticker': ticker,
            'poids': poids,
            'cours': cours,
            'frequence': frequence,
            'dividende_annuel': div_annuel,
            'taux_yield_annuel': round(taux_yield, 3),
            'prochaine_date_ex': datetime.strptime(date_ex, '%Y-%m-%d'),
            'statut': statut
        })
    
    df = pd.DataFrame(data)
    return df


# =============================================================================
# 3. DONNÉES DE PRIX MASI20 (pour backtesting)
# Format : date | spot_masi20 | prix_future_reel (optionnel)
# =============================================================================

def get_historique_masi20_mock(jours=90):
    """
    Génère un historique mocké des prix MASI20 pour backtesting
    Utilise une marche aléatoire géométrique réaliste
    """
    
    # Prix de départ réaliste
    spot_initial = 1876.54
    
    # Paramètres réalistes pour le MASI20
    rendement_moyen_journalier = 0.0002  # ~5% annualisé
    volatilite_journaliere = 0.008       # ~12.7% annualisé
    
    # Générer les dates (jours de bourse : Lundi-Vendredi)
    date_debut = datetime.now() - timedelta(days=jours)
    dates = []
    current_date = date_debut
    
    while len(dates) < jours:
        if current_date.weekday() < 5:  # Lundi à Vendredi
            dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Générer les prix avec marche aléatoire
    np.random.seed(42)  # Pour reproductibilité
    rendements = np.random.normal(
        rendement_moyen_journalier, 
        volatilite_journaliere, 
        jours
    )
    
    prix = [spot_initial]
    for r in rendements[1:]:
        nouveau_prix = prix[-1] * (1 + r)
        prix.append(nouveau_prix)
    
    # Créer le DataFrame
    df = pd.DataFrame({
        'date': dates[:jours],
        'spot_masi20': [round(p, 2) for p in prix[:jours]]
    })
    
    # Ajouter un prix future simulé (avec une base réaliste)
    df['prix_future_reel'] = df.apply(
        lambda row: round(
            row['spot_masi20'] * (1 + 0.001 * (jours - list(df.index).index(row.name)) / 30),
            2
        ),
        axis=1
    )
    
    return df


# =============================================================================
# 4. FONCTIONS DE CHARGEMENT UNIFIÉES
# =============================================================================

def charger_donnees_test(nom_donnees):
    """
    Charge les données de test selon le nom
    
    Args:
        nom_donnees: 'taux_zc', 'dividendes', ou 'historique_masi20'
    
    Returns:
        DataFrame pandas
    """
    
    if nom_donnees == 'taux_zc':
        return get_taux_zc_mock()
    
    elif nom_donnees == 'dividendes':
        return get_dividendes_masi20_mock()
    
    elif nom_donnees == 'historique_masi20':
        return get_historique_masi20_mock()
    
    else:
        raise ValueError(f"Données inconnues: {nom_donnees}")


# =============================================================================
# 5. EXEMPLES D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DES DONNÉES MOCKÉES")
    print("=" * 60)
    
    # Test 1: Taux ZC
    print("\n📊 TAUX ZÉRO-COUPON (r)")
    df_taux = get_taux_zc_mock()
    print(f"Nombre de lignes: {len(df_taux)}")
    print(f"Colonnes: {list(df_taux.columns)}")
    print("\nAperçu:")
    print(df_taux.head(10))
    
    # Test 2: Dividendes
    print("\n💰 DIVIDENDES MASI20 (q)")
    df_div = get_dividendes_masi20_mock()
    print(f"Nombre d'actions: {len(df_div)}")
    print(f"Colonnes: {list(df_div.columns)}")
    print("\nTop 5 par poids:")
    print(df_div.nlargest(5, 'poids')[['ticker', 'poids', 'dividende_annuel', 'taux_yield_annuel']])
    
    # Test 3: Historique
    print("\n📈 HISTORIQUE MASI20")
    df_hist = get_historique_masi20_mock(90)
    print(f"Nombre de jours: {len(df_hist)}")
    print(f"Colonnes: {list(df_hist.columns)}")
    print("\nAperçu:")
    print(df_hist.head(10))
    print(f"\nPrix initial: {df_hist['spot_masi20'].iloc[0]:.2f}")
    print(f"Prix final: {df_hist['spot_masi20'].iloc[-1]:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ TESTS TERMINÉS")
    print("=" * 60)

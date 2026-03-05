# ============================================
# BOURSE DE CASABLANCA SCRAPER
# Récupération des données officielles MASI20
# ============================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from cachetools import TTLCache
import config

# Cache pour éviter de scraper trop souvent (24h)
cache_masi20 = TTLCache(maxsize=100, ttl=86400)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

def get_masi20_constituents_officiels():
    """
    Scraper la composition officielle du MASI20 depuis la Bourse de Casablanca
    Returns: Liste des constituants avec ticker, nom, poids, cours actuel
    """
    
    # Vérifier le cache
    if 'constituents' in cache_masi20:
        return cache_masi20['constituents']
    
    try:
        # URL de la composition des indices
        url = "https://www.casablanca-bourse.com/bourseweb/Indices-Composition"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Parser le tableau des constituants MASI20
        constituents = []
        
        # Chercher le tableau (adapter les sélecteurs selon la structure réelle)
        table = soup.find('table', {'id': 'masi20-table'})
        
        if table:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    try:
                        ticker = cols[0].text.strip()
                        nom = cols[1].text.strip()
                        poids = float(cols[2].text.strip().replace('%', '')) / 100
                        cours = float(cols[3].text.strip().replace(' ', '').replace(',', '.'))
                        
                        constituents.append({
                            'ticker': ticker,
                            'nom': nom,
                            'poids': poids,
                            'cours': cours,
                            'dividende_annuel': 0  # Sera rempli par get_dividendes_actions
                        })
                    except (ValueError, IndexError) as e:
                        continue
        
        # Sauvegarder dans le cache
        cache_masi20['constituents'] = constituents
        
        return constituents
        
    except Exception as e:
        print(f"❌ Erreur scraping Bourse de Casablanca: {e}")
        # Fallback sur données mockées en cas d'erreur
        return get_masi20_constituents_mock()

def get_dividendes_actions(tickers):
    """
    Scraper les dividendes des actions depuis Ilboursa
    Returns: Dict {ticker: dividende_annuel}
    """
    
    dividendes = {}
    
    for ticker in tickers:
        try:
            # URL Ilboursa pour l'action
            url = f"https://www.ilboursa.com/fiche-valeur/{ticker}"
            
            response = requests.get(url, headers=HEADERS, timeout=5)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Chercher l'information de dividende
            # (adapter selon la structure réelle du site)
            div_tag = soup.find('div', class_='dividend-yield')
            
            if div_tag:
                # Extraire le dividende (ex: "18.00 MAD")
                div_text = div_tag.text.strip()
                dividende = float(div_text.replace('MAD', '').replace(' ', '').replace(',', '.'))
                dividendes[ticker] = dividende
            else:
                dividendes[ticker] = 0
                
        except Exception as e:
            print(f"⚠️ Erreur scraping dividende pour {ticker}: {e}")
            dividendes[ticker] = 0
    
    return dividendes

def get_masi20_constituents_mock():
    """
    Données mockées en cas d'erreur de scraping
    """
    return [
        {'ticker': 'ATW', 'nom': 'Attijariwafa Bank', 'poids': 0.185, 'cours': 485.0, 'dividende_annuel': 18.0},
        {'ticker': 'BCP', 'nom': 'Banque Populaire', 'poids': 0.125, 'cours': 142.5, 'dividende_annuel': 2.5},
        {'ticker': 'IAM', 'nom': 'Maroc Telecom', 'poids': 0.105, 'cours': 128.0, 'dividende_annuel': 7.5},
        {'ticker': 'OCP', 'nom': 'OCP Group', 'poids': 0.085, 'cours': 7850.0, 'dividende_annuel': 120.0},
        {'ticker': 'LAF', 'nom': 'LafargeHolcim Maroc', 'poids': 0.065, 'cours': 1650.0, 'dividende_annuel': 180.0},
        {'ticker': 'SNG', 'nom': 'Sonasid', 'poids': 0.055, 'cours': 850.0, 'dividende_annuel': 25.0},
        {'ticker': 'MNG', 'nom': 'Managem', 'poids': 0.045, 'cours': 1250.0, 'dividende_annuel': 8.0},
        {'ticker': 'CIH', 'nom': 'CIH Bank', 'poids': 0.040, 'cours': 245.0, 'dividende_annuel': 3.5},
        {'ticker': 'BNA', 'nom': 'Bank Al-Maghrib', 'poids': 0.038, 'cours': 625.0, 'dividende_annuel': 45.0},
        {'ticker': 'SID', 'nom': 'Sidérurgie Nationale', 'poids': 0.035, 'cours': 485.0, 'dividende_annuel': 15.0},
        {'ticker': 'TIS', 'nom': 'Titan Cement', 'poids': 0.032, 'cours': 285.0, 'dividende_annuel': 4.5},
        {'ticker': 'WAA', 'nom': 'Wafa Assurance', 'poids': 0.030, 'cours': 4850.0, 'dividende_annuel': 90.0},
        {'ticker': 'SAB', 'nom': 'SABIC Morocco', 'poids': 0.028, 'cours': 1150.0, 'dividende_annuel': 20.0},
        {'ticker': 'DAM', 'nom': 'Delta Holding', 'poids': 0.025, 'cours': 1250.0, 'dividende_annuel': 20.0},
        {'ticker': 'HPS', 'nom': 'HPS Group', 'poids': 0.022, 'cours': 8500.0, 'dividende_annuel': 15.0},
        {'ticker': 'LUX', 'nom': 'Luxembourg Telecom', 'poids': 0.020, 'cours': 1850.0, 'dividende_annuel': 30.0},
        {'ticker': 'MAM', 'nom': 'Marsa Maroc', 'poids': 0.018, 'cours': 165.0, 'dividende_annuel': 2.8},
        {'ticker': 'NEH', 'nom': 'Nehad Group', 'poids': 0.015, 'cours': 95.0, 'dividende_annuel': 1.2},
        {'ticker': 'OUL', 'nom': 'Oulmes', 'poids': 0.012, 'cours': 685.0, 'dividende_annuel': 6.0},
        {'ticker': 'RES', 'nom': 'Residence', 'poids': 0.010, 'cours': 485.0, 'dividende_annuel': 4.0}
    ]

def calculer_taux_dividende_masi20(constituents=None):
    """
    Calcule le taux de dividende de l'indice MASI20
    Selon la formule BAM: d = Σ(Pi × Di/Ci)
    
    Args:
        constituents: Liste des constituants (si None, utilise le scraping)
    
    Returns:
        taux_dividende: Taux de dividende annualisé
        details: DataFrame avec le détail du calcul
    """
    
    if constituents is None:
        constituents = get_masi20_constituents_officiels()
    
    taux_dividende_total = 0
    details = []
    
    for constituant in constituents:
        ticker = constituant['ticker']
        poids = constituant['poids']  # Pi
        dividende = constituant.get('dividende_annuel', 0)  # Di
        cours = constituant.get('cours', 1)  # Ci
        
        # Dividend yield du titre: Di/Ci
        dividend_yield = dividende / cours if cours > 0 else 0
        
        # Contribution pondérée: Pi × (Di/Ci)
        contribution = poids * dividend_yield
        
        taux_dividende_total += contribution
        
        details.append({
            'Ticker': ticker,
            'Nom': constituant['nom'],
            'Poids (Pi)': f"{poids*100:.2f}%",
            'Cours (Ci)': f"{cours:,.2f} MAD",
            'Dividende (Di)': f"{dividende:,.2f} MAD",
            'Dividend Yield (Di/Ci)': f"{dividend_yield*100:.2f}%",
            'Contribution (Pi×Di/Ci)': f"{contribution*100:.4f}%"
        })
    
    df_details = pd.DataFrame(details)
    
    return taux_dividende_total, df_details

def get_cours_cloture_masi20():
    """
    Récupère le cours de clôture du MASI20
    Selon l'instruction BAM: cours du fixing de clôture
    """
    
    try:
        url = "https://www.casablanca-bourse.com/bourseweb/Indices-Cotation"
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Chercher le MASI20 dans le tableau
        # (adapter selon la structure réelle)
        table = soup.find('table')
        
        if table:
            rows = table.find_all('tr')
            for row in rows:
                if 'MASI20' in row.text:
                    cols = row.find_all('td')
                    # Extraire le cours de clôture
                    cours = float(cols[1].text.strip().replace(' ', '').replace(',', '.'))
                    return cours
        
        return None
        
    except Exception as e:
        print(f"❌ Erreur récupération cours MASI20: {e}")
        return None

def update_constituents_with_dividendes():
    """
    Met à jour les constituants avec les dividendes scrapés
    """
    constituents = get_masi20_constituents_officiels()
    tickers = [c['ticker'] for c in constituents]
    
    dividendes = get_dividendes_actions(tickers)
    
    for constituant in constituents:
        ticker = constituant['ticker']
        constituant['dividende_annuel'] = dividendes.get(ticker, 0)
    
    return constituents

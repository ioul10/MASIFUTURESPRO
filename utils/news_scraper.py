# ============================================
# NEWS SCRAPER - MASI Futures Pro
# Version Allégée pour Widget
# ============================================

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from cachetools import TTLCache
import config

# Cache pour les news
news_cache = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['news'])

def get_all_news(force_refresh=False, max_total=5):
    """
    Récupère les actualités (version simplifiée Alpha)
    
    Returns:
        DataFrame avec les actualités ou DataFrame vide
    """
    
    import pandas as pd
    
    # Vérifier le cache
    if not force_refresh and 'news_data' in news_cache:
        return news_cache['news_data']
    
    # Pour l'Alpha, données mockées réalistes
    # En production, implémenter le vrai scraping Ilboursa
    news_data = [
        {
            'source': 'Ilboursa',
            'titre': 'Le MASI progresse de 0,45% en séance',
            'resume': 'Le marché marocain affiche une progression portée par les valeurs bancaires...',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.ilboursa.com',
            'categorie': 'Marché'
        },
        {
            'source': 'Bourse de Casablanca',
            'titre': 'Introduction des futures sur indices MASI',
            'resume': 'Lancement officiel des contrats futures pour moderniser le marché...',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.casablanca-bourse.com',
            'categorie': 'Produits'
        },
        {
            'source': 'Ilboursa',
            'titre': 'BKAM maintient son taux directeur à 3%',
            'resume': 'La banque centrale conserve sa politique monétaire accommodante...',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.ilboursa.com',
            'categorie': 'Économie'
        }
    ]
    
    df_news = pd.DataFrame(news_data[:max_total])
    
    # Mettre en cache
    news_cache['news_data'] = df_news
    
    return df_news

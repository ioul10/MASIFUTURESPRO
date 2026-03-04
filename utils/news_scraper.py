from datetime import datetime
from cachetools import TTLCache
import config
import pandas as pd

news_cache = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['news'])

def get_all_news(force_refresh=False, max_total=5):
    """Récupère les actualités"""
    
    if not force_refresh and 'news_data' in news_cache:
        return news_cache['news_data']
    
    # Données mockées pour l'Alpha
    news_data = [
        {
            'source': 'Ilboursa',
            'titre': 'Le MASI progresse de 0,45% en séance',
            'resume': 'Le marché marocain affiche une progression...',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.ilboursa.com',
            'categorie': 'Marché'
        },
        {
            'source': 'Bourse de Casablanca',
            'titre': 'Introduction des futures sur indices MASI',
            'resume': 'Lancement officiel des contrats futures...',
            'date': datetime.now().strftime('%d/%m/%Y'),
            'url': 'https://www.casablanca-bourse.com',
            'categorie': 'Produits'
        }
    ]
    
    df_news = pd.DataFrame(news_data[:max_total])
    news_cache['news_data'] = df_news
    
    return df_news

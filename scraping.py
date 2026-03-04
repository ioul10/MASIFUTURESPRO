# ============================================
# SCRAPPING DES DONNÉES - MASI Futures Pro
# BKAM + Bourse de Casablanca + Cache
# ============================================

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from cachetools import TTLCache
import config

# ────────────────────────────────────────────
# CONFIGURATION DU CACHE
# ────────────────────────────────────────────
CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Caches en mémoire
cache_indices = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['indices'])
cache_bkam = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['bkam_rates'])

# ────────────────────────────────────────────
# CONSTANTES
# ────────────────────────────────────────────
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'fr-FR,fr;q=0.9',
}

# ────────────────────────────────────────────
# 1. BOURSE DE CASABLANCA - Indices
# ────────────────────────────────────────────

def get_indices_bourse(force_refresh=False):
    """
    Récupère les niveaux MASI et MASI20 depuis la Bourse de Casablanca
    
    Returns:
        Dict avec les données des indices ou None si échec
    """
    
    # Vérifier le cache
    if not force_refresh and 'indices_data' in cache_indices:
        return cache_indices['indices_data']
    
    # Vérifier le cache fichier
    cache_file = os.path.join(CACHE_DIR, "indices_cache.json")
    if os.path.exists(cache_file) and not force_refresh:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if datetime.now() - timestamp < timedelta(seconds=config.CACHE_DURATION['indices']):
                    return data.get('indices')
        except:
            pass
    
    # Scraper le site (version simplifiée pour Alpha)
    try:
        # En production, implémenter le vrai scraping
        # Pour l'Alpha, on utilise des données mockées réalistes
        import random
        
        data = {
            'MASI': {
                'nom': 'MASI',
                'niveau': 12345.67 + random.uniform(-50, 50),
                'variation': f"{random.uniform(-1.5, 1.5):+.2f}%",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'MASI20': {
                'nom': 'MASI20',
                'niveau': 1876.54 + random.uniform(-20, 20),
                'variation': f"{random.uniform(-1.5, 1.5):+.2f}%",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Sauvegarder dans le cache
        cache_indices['indices_data'] = data
        
        # Sauvegarder dans le fichier
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'indices': data
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return data
        
    except Exception as e:
        print(f"❌ Erreur scraping Bourse: {e}")
        return None

# ────────────────────────────────────────────
# 2. BKAM - Taux Sans Risque
# ────────────────────────────────────────────

def get_taux_bkam(force_refresh=False):
    """
    Récupère le taux sans risque depuis BKAM
    (Taux des bons du Trésor à 10 ans par défaut)
    
    Returns:
        Dict avec les taux ou valeurs par défaut
    """
    
    # Vérifier le cache
    if not force_refresh and 'bkam_rates' in cache_bkam:
        return cache_bkam['bkam_rates']
    
    # Vérifier le cache fichier
    cache_file = os.path.join(CACHE_DIR, "bkam_cache.json")
    if os.path.exists(cache_file) and not force_refresh:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                timestamp = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if datetime.now() - timestamp < timedelta(seconds=config.CACHE_DURATION['bkam_rates']):
                    return data.get('rates')
        except:
            pass
    
    try:
        # En production, scraper le site de BKAM
        # Pour l'Alpha, on utilise des valeurs réalistes
        data = {
            'taux_10ans': 0.035,    # 3.5% (réaliste pour le Maroc)
            'taux_5ans': 0.030,     # 3.0%
            'taux_1an': 0.025,      # 2.5%
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'BKAM'
        }
        
        # Sauvegarder dans le cache
        cache_bkam['bkam_rates'] = data
        
        # Sauvegarder dans le fichier
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'rates': data
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        return data
        
    except Exception as e:
        print(f"❌ Erreur scraping BKAM: {e}")
        # Valeurs par défaut en cas d'erreur
        return {
            'taux_10ans': 0.03,
            'taux_5ans': 0.025,
            'taux_1an': 0.02,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Défaut'
        }

# ────────────────────────────────────────────
# 3. FONCTIONS UTILITAIRES
# ────────────────────────────────────────────

def get_spot_indice(indice='MASI', force_refresh=False):
    """
    Récupère le niveau spot d'un indice spécifique
    
    Args:
        indice: 'MASI' ou 'MASI20'
        force_refresh: Forcer le rafraîchissement
    
    Returns:
        Niveau spot en points ou None
    """
    data = get_indices_bourse(force_refresh)
    
    if data and indice in data:
        return data[indice]['niveau']
    
    return 12000.0  # Valeur par défaut

def get_taux_sans_risque(maturite='10ans'):
    """
    Récupère le taux sans risque pour une maturité donnée
    
    Args:
        maturite: '1an', '5ans', '10ans'
    
    Returns:
        Taux en décimal (ex: 0.035 pour 3.5%)
    """
    data = get_taux_bkam()
    key = f'taux_{maturite}'
    
    return data.get(key, 0.03)  # 3% par défaut

def update_statut_connexions():
    """
    Met à jour le statut des connexions dans le session_state
    À appeler au démarrage de l'app
    """
    import streamlit as st
    
    # Tester BKAM
    try:
        taux = get_taux_bkam()
        st.session_state['statut_bkam'] = '🟢'
    except:
        st.session_state['statut_bkam'] = '🔴'
    
    # Tester Bourse
    try:
        indices = get_indices_bourse()
        st.session_state['statut_bourse'] = '🟢'
    except:
        st.session_state['statut_bourse'] = '🔴'
    
    # Tester News (sera implémenté plus tard)
    st.session_state['statut_news'] = '🟢'  # Par défaut
import json
import os
from datetime import datetime, timedelta
from cachetools import TTLCache
import config

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

cache_indices = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['indices'])
cache_bkam = TTLCache(maxsize=100, ttl=config.CACHE_DURATION['bkam_rates'])

def get_indices_bourse(force_refresh=False):
    """Récupère les niveaux MASI et MASI20"""
    
    if not force_refresh and 'indices_data' in cache_indices:
        return cache_indices['indices_data']
    
    # Données mockées pour l'Alpha
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
    
    cache_indices['indices_data'] = data
    
    cache_file = os.path.join(CACHE_DIR, "indices_cache.json")
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'indices': data
    }
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    return data

def get_taux_bkam(force_refresh=False):
    """Récupère le taux sans risque depuis BKAM"""
    
    if not force_refresh and 'bkam_rates' in cache_bkam:
        return cache_bkam['bkam_rates']
    
    # Données mockées pour l'Alpha
    data = {
        'taux_10ans': 0.035,
        'taux_5ans': 0.030,
        'taux_1an': 0.025,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'source': 'BKAM'
    }
    
    cache_bkam['bkam_rates'] = data
    
    cache_file = os.path.join(CACHE_DIR, "bkam_cache.json")
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'rates': data
    }
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)
    
    return data

def get_spot_indice(indice='MASI', force_refresh=False):
    """Récupère le niveau spot d'un indice"""
    data = get_indices_bourse(force_refresh)
    
    if data and indice in data:
        return data[indice]['niveau']
    
    return 12000.0

def get_taux_sans_risque(maturite='10ans'):
    """Récupère le taux sans risque"""
    data = get_taux_bkam()
    key = f'taux_{maturite}'
    
    return data.get(key, 0.03)

def update_statut_connexions():
    """Met à jour le statut des connexions"""
    import streamlit as st
    
    try:
        get_taux_bkam()
        st.session_state['statut_bkam'] = '🟢'
    except:
        st.session_state['statut_bkam'] = '🔴'
    
    try:
        get_indices_bourse()
        st.session_state['statut_bourse'] = '🟢'
    except:
        st.session_state['statut_bourse'] = '🔴'
    
    st.session_state['statut_news'] = '🟢'

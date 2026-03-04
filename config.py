# ============================================
# CONFIGURATION - MASI Futures Pro
# Version Alpha
# ============================================

# Informations Application
APP_NAME = "MASI Futures Pro"
APP_VERSION = "1.0.0-alpha"
APP_AUTHOR = "CDG Capital - Document de Référence"

# Logo (chemin relatif)
LOGO_PATH = "assets/logo.png"  # À ajouter plus tard

# Palette de Couleurs Professionnelle
COLORS = {
    'primary': '#1E3A5F',          # Bleu marine
    'secondary': '#2E5C8A',        # Bleu moyen
    'accent': '#3E7CAD',           # Bleu clair
    'success': '#10B981',          # Vert
    'warning': '#F59E0B',          # Orange
    'danger': '#EF4444',           # Rouge
    'info': '#3B82F6',             # Bleu info
    'background': '#F5F7FA',       # Gris clair
    'card': '#FFFFFF',             # Blanc
    'text': '#1F2937',             # Gris foncé
    'text_muted': '#6B7280',       # Gris moyen
}

# Constantes MASI/MASI20 (Document §4.1)
MULTIPLICATEUR = 10  # MAD/point
DEVISE = "MAD"

# Indices Disponibles
INDICES = ["MASI", "MASI20"]

# Sources de Données
SOURCES = {
    'bkam': 'https://www.bkam.ma',
    'bourse': 'https://www.casablanca-bourse.com',
    'news': 'https://www.ilboursa.com'
}

# Cache Configuration
CACHE_DURATION = {
    'indices': 300,      # 5 minutes
    'bkam_rates': 3600,  # 1 heure
    'news': 1800,        # 30 minutes
}

# Paramètres par Défaut pour Pricing
DEFAULT_PRICING = {
    'r': 0.03,      # 3% (taux sans risque)
    'q': 0.025,     # 2.5% (dividendes)
    'jours': 90,    # 3 mois
}
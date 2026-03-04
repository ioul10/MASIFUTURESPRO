# ============================================
# CONFIGURATION - MASI Futures Pro
# ============================================

APP_NAME = "MASI Futures Pro"
APP_VERSION = "1.0.0-alpha"

COLORS = {
    'primary': '#1E3A5F',
    'secondary': '#2E5C8A',
    'accent': '#3E7CAD',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    'background': '#F5F7FA',
    'card': '#FFFFFF',
    'text': '#1F2937',
    'text_muted': '#6B7280',
}

MULTIPLICATEUR = 10
DEVISE = "MAD"
INDICES = ["MASI", "MASI20"]

CACHE_DURATION = {
    'indices': 300,
    'bkam_rates': 3600,
    'news': 1800,
}

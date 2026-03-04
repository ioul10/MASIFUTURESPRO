# ============================================
# MASI Futures Pro - Version Alpha
# Point d'Entrée Principal
# ============================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions

# ────────────────────────────────────────────
# CONFIGURATION DE LA PAGE
# ────────────────────────────────────────────
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────
# INITIALISATION
# ────────────────────────────────────────────
# Mettre à jour le statut des connexions
update_statut_connexions()

# ────────────────────────────────────────────
# SIDEBAR (Toutes les pages)
# ────────────────────────────────────────────
page = render_sidebar()

# ────────────────────────────────────────────
# HEADER (Toutes les pages)
# ────────────────────────────────────────────
marche_ouvert = render_header()

# ────────────────────────────────────────────
# NOTE : La navigation est gérée automatiquement
# par Streamlit via le dossier pages/
# Pas besoin de st.switch_page()
# ────────────────────────────────────────────

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
render_footer()

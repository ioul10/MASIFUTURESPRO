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
# ROUTING VERS LES PAGES
# ────────────────────────────────────────────
# Streamlit gère automatiquement le routing via le dossier pages/
# Ce fichier sert principalement pour la sidebar et le header communs

# Afficher un message si on est sur la page principale
if page == "🏠 Accueil":
    st.switch_page("pages/01_🏠_Accueil.py")
elif page == "🧮 Pricing":
    st.switch_page("pages/02_🧮_Pricing.py")
elif page == "📊 Indices":
    st.switch_page("pages/03_📊_Indices.py")

# ────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────
render_footer()
# ============================================
# MASI Futures Pro - Version Alpha
# ============================================

import streamlit as st
import config
from components.sidebar import render_sidebar
from components.header import render_header
from components.footer import render_footer
from utils.scraping import update_statut_connexions

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

update_statut_connexions()

render_sidebar()
render_header()
render_footer()

import streamlit as st
from utils.news_scraper import get_all_news

def render_news_widget(max_news=5):
    """Affiche un widget compact avec les dernières news"""
    
    st.markdown("### 📰 Actualités MASI")
    
    with st.spinner("Chargement des actualités..."):
        df_news = get_all_news(force_refresh=False, max_total=max_news)
    
    if not df_news.empty:
        for idx, row in df_news.iterrows():
            with st.expander(f"📌 {row['titre']} — {row['source']}"):
                if row.get('resume'):
                    st.markdown(f"*{row['resume'][:150]}...*")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"Catégorie: {row.get('categorie', 'N/A')}")
                with col2:
                    if row.get('url'):
                        st.markdown(f"[🔗 Lire]({row['url']})")
                
                st.divider()
    else:
        st.info("ℹ️ Aucune actualité disponible pour le moment.")

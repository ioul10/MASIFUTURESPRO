import streamlit as st
import config
from utils.scraping import get_indices_bourse
import pandas as pd

st.title("📊 Indices MASI & MASI20")

st.markdown("### Niveaux Actuels")

indices_data = get_indices_bourse()

if indices_data:
    col1, col2 = st.columns(2)
    
    for idx_name, idx_data in indices_data.items():
        with col1 if idx_name == 'MASI' else col2:
            st.markdown(f"""
                <div style='padding: 30px; background: {config.COLORS["card"]}; 
                            border-radius: 16px; margin-bottom: 20px;
                            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                            border-left: 6px solid {config.COLORS["primary"]};'>
                    <h2 style='margin: 0 0 15px 0; color: {config.COLORS["primary"]};'>
                        🇲 {idx_data['nom']}
                    </h2>
                    <p style='margin: 0; font-size: 2.5em; font-weight: 700; 
                              color: {config.COLORS["text"]};'>
                        {idx_data['niveau']:,.2f}
                    </p>
                    <p style='margin: 10px 0 0 0; font-size: 1.2em; font-weight: 600; 
                              color: {config.COLORS["success"] if "+" in idx_data["variation"] else config.COLORS["danger"]};'>
                        {idx_data['variation']}
                    </p>
                    <p style='margin: 15px 0 0 0; color: {config.COLORS["text_muted"]}; 
                              font-size: 0.85em;'>
                        MAJ: {idx_data['timestamp']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("❌ Impossible de récupérer les données")

st.divider()

st.markdown("### 📋 Caractéristiques des Contrats")

specs = pd.DataFrame({
    "Paramètre": ["Sous-jacent", "Multiplicateur", "Règlement", "Échéances", "Devise"],
    "Valeur": ["MASI/MASI20", f"{config.MULTIPLICATEUR} MAD/pt", "Cash settlement", "Mensuelles/Trimestrielles", config.DEVISE]
})

st.dataframe(specs, use_container_width=True, hide_index=True)

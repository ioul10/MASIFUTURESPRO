# ============================================
# PAGE 3: INDICES - MASI Futures Pro
# Niveaux et Graphiques
# ============================================

import streamlit as st
import config
from utils.scraping import get_indices_bourse

st.title("📊 Indices MASI & MASI20")

st.markdown("### Niveaux Actuels des Indices")

# Récupération des données
indices_data = get_indices_bourse()

if indices_data:
    col1, col2 = st.columns(2)
    
    for idx_name, idx_data in indices_data.items():
        with st.container():
            st.markdown(f"""
                <div style='padding: 30px; background: {config.COLORS["card"]}; 
                            border-radius: 16px; margin-bottom: 20px;
                            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                            border-left: 6px solid {config.COLORS["primary"]};'>
                    <h2 style='margin: 0 0 15px 0; color: {config.COLORS["primary"]};'>
                        🇲 {idx_data['nom']}
                    </h2>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <p style='margin: 0; font-size: 2.5em; font-weight: 700; 
                                      color: {config.COLORS["text"]};'>
                                {idx_data['niveau']:,.2f}
                            </p>
                            <p style='margin: 10px 0 0 0; color: {config.COLORS["text_muted"]};'>
                                points
                            </p>
                        </div>
                        <div style='text-align: right;'>
                            <p style='margin: 0; font-size: 1.5em; font-weight: 600; 
                                      color: {config.COLORS["success"] if "+" in idx_data["variation"] else config.COLORS["danger"]};'>
                                {idx_data['variation']}
                            </p>
                            <p style='margin: 5px 0 0 0; color: {config.COLORS["text_muted"]}; 
                                      font-size: 0.9em;'>
                                vs clôture précédente
                            </p>
                        </div>
                    </div>
                    <p style='margin: 15px 0 0 0; color: {config.COLORS["text_muted"]}; 
                              font-size: 0.85em;'>
                        MAJ: {idx_data['timestamp']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("❌ Impossible de récupérer les données des indices")

st.divider()

# Caractéristiques des contrats
st.markdown("### 📋 Caractéristiques des Contrats Futures")

specs_data = {
    "Paramètre": [
        "Sous-jacent",
        "Multiplicateur",
        "Règlement",
        "Échéances",
        "Devise",
        "Tick Size"
    ],
    "Valeur": [
        "MASI / MASI20",
        f"{config.MULTIPLICATEUR} MAD/point",
        "Cash settlement (règlement en espèces)",
        "Mensuelles / Trimestrielles",
        config.DEVISE,
        "0.01 point"
    ]
}

import pandas as pd
df_specs = pd.DataFrame(specs_data)

st.dataframe(
    df_specs,
    use_container_width=True,
    hide_index=True
)

# Info box
st.markdown(f"""
    <div style='padding: 20px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); 
                border-left: 5px solid {config.COLORS["primary"]};
                border-radius: 12px; margin: 20px 0;'>
        <strong>💡 Le saviez-vous ?</strong><br>
        Le MASI (Moroccan All Shares Index) représente la performance de l'ensemble des actions 
        cotées à la Bourse de Casablanca, tandis que le MASI20 se concentre sur les 20 valeurs 
        les plus liquides du marché.
    </div>
""", unsafe_allow_html=True)

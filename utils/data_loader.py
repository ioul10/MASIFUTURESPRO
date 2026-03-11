# =============================================================================
# DATA LOADER — MASI Futures Pro
# Chargement et validation des données (CSV uploadés ou mockées)
# Version 0.3
# =============================================================================

import pandas as pd
import streamlit as st
from datetime import datetime
import os

# Import des données mockées
from data.test_data import (
    get_taux_zc_mock,
    get_dividendes_masi20_mock,
    get_historique_masi20_mock
)


# =============================================================================
# 1. CHARGEMENT DES TAUX ZC (r)
# =============================================================================

def charger_taux_zc_csv(uploaded_file):
    """
    Charge un fichier CSV de taux ZC uploadé par l'utilisateur
    
    Format attendu:
        date_spot,date_maturity,zc
        2026-01-01,2026-04-01,2.85
        2026-01-01,2026-07-01,3.10
    
    Args:
        uploaded_file: Fichier uploadé via st.file_uploader
    
    Returns:
        DataFrame pandas ou None si erreur
    """
    try:
        # Détection automatique CSV/Excel
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validation des colonnes requises
        colonnes_requises = ['date_spot', 'date_maturity', 'zc']
        colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
        
        if colonnes_manquantes:
            st.error(f"❌ Colonnes manquantes: {', '.join(colonnes_manquantes)}")
            st.info(f"💡 Colonnes attendues: {', '.join(colonnes_requises)}")
            return None
        
        # Conversion des dates
        df['date_spot'] = pd.to_datetime(df['date_spot'], errors='coerce')
        df['date_maturity'] = pd.to_datetime(df['date_maturity'], errors='coerce')
        
        # Vérification des dates invalides
        if df['date_spot'].isna().any() or df['date_maturity'].isna().any():
            st.warning("⚠️ Certaines dates n'ont pas pu être converties")
        
        # Conversion du taux (gestion % ou décimal)
        # Si les valeurs sont > 1, on suppose que c'est en % (ex: 2.85)
        if df['zc'].max() > 1:
            df['zc'] = df['zc'] / 100
        
        # Tri par date
        df = df.sort_values(['date_spot', 'date_maturity']).reset_index(drop=True)
        
        # Statistiques
        nb_lignes = len(df)
        nb_dates_pub = df['date_spot'].nunique()
        nb_maturites = df['date_maturity'].nunique()
        
        st.success(f"✅ {nb_lignes} taux chargés ({nb_dates_pub} dates de publication, {nb_maturites} maturités)")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {str(e)}")
        return None


def charger_taux_zc(uploaded_file=None, utiliser_mock=True):
    """
    Fonction unifiée pour charger les taux ZC
    
    Args:
        uploaded_file: Fichier uploadé (optionnel)
        utiliser_mock: Si True et pas de fichier, utilise les données mockées
    
    Returns:
        DataFrame pandas
    """
    # Priorité 1: Fichier uploadé
    if uploaded_file is not None:
        df = charger_taux_zc_csv(uploaded_file)
        if df is not None:
            return df
    
    # Priorité 2: Données mockées
    if utiliser_mock:
        st.info("ℹ️ Utilisation des données mockées pour les taux ZC")
        return get_taux_zc_mock()
    
    # Priorité 3: Fichier par défaut (si existe)
    chemins_possibles = [
        'data/taux_zc.csv',
        'data/taux_zc.xlsx',
        '../data/taux_zc.csv',
        '../data/taux_zc.xlsx'
    ]
    
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            try:
                if chemin.endswith('.csv'):
                    return pd.read_csv(chemin)
                else:
                    return pd.read_excel(chemin)
            except:
                pass
    
    # Échec total
    st.error("❌ Aucune source de données disponible pour les taux ZC")
    return None


# =============================================================================
# 2. CHARGEMENT DES DIVIDENDES (q)
# =============================================================================

def charger_dividendes_csv(uploaded_file):
    """
    Charge un fichier CSV de dividendes uploadé
    
    Format attendu (colonnes minimales):
        ticker,poids,cours,dividende_annuel
        ATW,0.185,485.0,18.0
        BCP,0.125,142.5,2.5
    
    Format complet:
        ticker,poids,cours,frequence,dividende_annuel,prochaine_date_ex,statut
    
    Args:
        uploaded_file: Fichier uploadé via st.file_uploader
    
    Returns:
        DataFrame pandas ou None si erreur
    """
    try:
        # Détection automatique CSV/Excel
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validation des colonnes requises (minimum)
        colonnes_minimales = ['ticker', 'poids', 'cours', 'dividende_annuel']
        colonnes_manquantes = [col for col in colonnes_minimales if col not in df.columns]
        
        if colonnes_manquantes:
            st.error(f"❌ Colonnes manquantes: {', '.join(colonnes_manquantes)}")
            st.info(f"💡 Colonnes requises: {', '.join(colonnes_minimales)}")
            return None
        
        # Colonnes optionnelles
        colonnes_optionnelles = ['frequence', 'prochaine_date_ex', 'statut', 'nom', 'taux_yield_annuel']
        
        # Ajouter les colonnes manquantes avec valeurs par défaut
        for col in colonnes_optionnelles:
            if col not in df.columns:
                if col == 'frequence':
                    df[col] = 'annuel'
                elif col == 'statut':
                    df[col] = 'estime'
                elif col == 'nom':
                    df[col] = df['ticker']
                elif col == 'prochaine_date_ex':
                    df[col] = None
                elif col == 'taux_yield_annuel':
                    df[col] = (df['dividende_annuel'] / df['cours'] * 100).round(3)
        
        # Calcul du taux de rendement si pas fourni
        if 'taux_yield_annuel' not in df.columns or df['taux_yield_annuel'].isna().all():
            df['taux_yield_annuel'] = (df['dividende_annuel'] / df['cours'] * 100).round(3)
        
        # Conversion des dates si présentes
        if 'prochaine_date_ex' in df.columns:
            df['prochaine_date_ex'] = pd.to_datetime(df['prochaine_date_ex'], errors='coerce')
        
        # Validation des poids (doivent sommer à ~1)
        total_poids = df['poids'].sum()
        if abs(total_poids - 1.0) > 0.05:  # Tolérance 5%
            st.warning(f"⚠️ La somme des poids est {total_poids:.3f} (devrait être ~1.0)")
        
        # Tri par poids décroissant
        df = df.sort_values('poids', ascending=False).reset_index(drop=True)
        
        # Statistiques
        nb_actions = len(df)
        total_poids = df['poids'].sum()
        yield_moyen = df['taux_yield_annuel'].mean()
        
        st.success(f"✅ {nb_actions} actions chargées (Poids total: {total_poids:.1%}, Yield moyen: {yield_moyen:.2f}%)")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des dividendes: {str(e)}")
        return None


def charger_dividendes(uploaded_file=None, utiliser_mock=True):
    """
    Fonction unifiée pour charger les dividendes
    
    Args:
        uploaded_file: Fichier uploadé (optionnel)
        utiliser_mock: Si True et pas de fichier, utilise les données mockées
    
    Returns:
        DataFrame pandas ou liste de dicts
    """
    # Priorité 1: Fichier uploadé
    if uploaded_file is not None:
        df = charger_dividendes_csv(uploaded_file)
        if df is not None:
            return df
    
    # Priorité 2: Données mockées
    if utiliser_mock:
        st.info("ℹ️ Utilisation des données mockées pour les dividendes")
        return get_dividendes_masi20_mock()
    
    # Priorité 3: Fichier par défaut
    chemins_possibles = [
        'data/dividendes_masi20.csv',
        'data/dividendes_masi20.xlsx',
        '../data/dividendes_masi20.csv'
    ]
    
    for chemin in chemins_possibles:
        if os.path.exists(chemin):
            try:
                if chemin.endswith('.csv'):
                    return pd.read_csv(chemin)
                else:
                    return pd.read_excel(chemin)
            except:
                pass
    
    # Échec total
    st.error("❌ Aucune source de données disponible pour les dividendes")
    return None


# =============================================================================
# 3. CHARGEMENT DE L'HISTORIQUE MASI20 (pour backtesting)
# =============================================================================

def charger_historique_masi20_csv(uploaded_file):
    """
    Charge un fichier CSV d'historique MASI20
    
    Format attendu:
        date,spot_masi20,prix_future_reel
        2026-01-15,1876.54,1878.42
        2026-01-16,1878.20,1880.15
    
    Args:
        uploaded_file: Fichier uploadé
    
    Returns:
        DataFrame pandas ou None
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Colonnes requises
        colonnes_requises = ['date', 'spot_masi20']
        colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
        
        if colonnes_manquantes:
            st.error(f"❌ Colonnes manquantes: {', '.join(colonnes_manquantes)}")
            return None
        
        # Conversion dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Tri par date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Prix future réel (optionnel)
        if 'prix_future_reel' not in df.columns:
            st.info("ℹ️ Colonne 'prix_future_reel' absente — backtesting limité")
        
        st.success(f"✅ {len(df)} jours de données historiques chargés")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        return None


def charger_historique_masi20(uploaded_file=None, jours=90, utiliser_mock=True):
    """
    Fonction unifiée pour charger l'historique MASI20
    
    Args:
        uploaded_file: Fichier uploadé (optionnel)
        jours: Nombre de jours si génération mock
        utiliser_mock: Utiliser données mockées si pas de fichier
    
    Returns:
        DataFrame pandas
    """
    # Priorité 1: Fichier uploadé
    if uploaded_file is not None:
        df = charger_historique_masi20_csv(uploaded_file)
        if df is not None:
            return df
    
    # Priorité 2: Données mockées
    if utiliser_mock:
        st.info(f"ℹ️ Génération de {jours} jours de données mockées")
        return get_historique_masi20_mock(jours)
    
    return None


# =============================================================================
# 4. TEMPLATE DE FICHIERS CSV
# =============================================================================

def telecharger_template_taux_zc():
    """
    Génère un template CSV pour les taux ZC
    """
    df_template = pd.DataFrame({
        'date_spot': ['2026-01-01', '2026-01-01', '2026-01-08'],
        'date_maturity': ['2026-04-01', '2026-07-01', '2026-04-08'],
        'zc': [2.85, 3.10, 2.87]
    })
    return df_template.to_csv(index=False).encode('utf-8')


def telecharger_template_dividendes():
    """
    Génère un template CSV pour les dividendes
    """
    df_template = pd.DataFrame({
        'ticker': ['ATW', 'BCP', 'IAM'],
        'nom': ['Attijariwafa Bank', 'Banque Populaire', 'Maroc Telecom'],
        'poids': [0.185, 0.125, 0.105],
        'cours': [485.0, 142.5, 128.0],
        'frequence': ['semestriel', 'annuel', 'semestriel'],
        'dividende_annuel': [18.0, 2.5, 7.5],
        'prochaine_date_ex': ['2026-03-15', '2026-05-20', '2026-04-10'],
        'statut': ['annonce', 'annonce', 'estime']
    })
    return df_template.to_csv(index=False).encode('utf-8')


# =============================================================================
# 5. WIDGET STREAMLIT POUR UPLOAD
# =============================================================================

def widget_upload_taux_zc():
    """
    Affiche un widget Streamlit complet pour uploader les taux ZC
    """
    st.markdown("### 🏦 Import des Taux ZC (Bank Al-Maghrib)")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choisissez un fichier CSV ou Excel",
            type=['csv', 'xlsx'],
            help="Format: date_spot, date_maturity, zc"
        )
    
    with col2:
        if st.button("📥 Télécharger Template", type="secondary"):
            csv_template = telecharger_template_taux_zc()
            st.download_button(
                label="📄 CSV Template",
                data=csv_template,
                file_name="template_taux_zc.csv",
                mime="text/csv"
            )
    
    if uploaded_file:
        df = charger_taux_zc(uploaded_file, utiliser_mock=False)
        if df is not None:
            with st.expander("📊 Aperçu des données", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            return df
    else:
        st.info("💡 Ou utilisez les données mockées (défaut)")
        return None
    
    return None


def widget_upload_dividendes():
    """
    Affiche un widget Streamlit complet pour uploader les dividendes
    """
    st.markdown("### 💰 Import des Dividendes MASI20")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choisissez un fichier CSV ou Excel",
            type=['csv', 'xlsx'],
            help="Format: ticker, poids, cours, dividende_annuel, ..."
        )
    
    with col2:
        if st.button("📥 Télécharger Template", type="secondary"):
            csv_template = telecharger_template_dividendes()
            st.download_button(
                label="📄 CSV Template",
                data=csv_template,
                file_name="template_dividendes.csv",
                mime="text/csv"
            )
    
    if uploaded_file:
        df = charger_dividendes(uploaded_file, utiliser_mock=False)
        if df is not None:
            with st.expander("📊 Aperçu des données", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            return df
    else:
        st.info("💡 Ou utilisez les données mockées (défaut)")
        return None
    
    return None


# =============================================================================
# 6. EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DU DATA LOADER")
    print("=" * 60)
    
    # Test chargement mock
    print("\n1. Chargement données mockées:")
    df_taux = charger_taux_zc(utiliser_mock=True)
    print(f"   Taux ZC: {len(df_taux)} lignes")
    
    df_div = charger_dividendes(utiliser_mock=True)
    print(f"   Dividendes: {len(df_div)} actions")
    
    df_hist = charger_historique_masi20(utiliser_mock=True, jours=90)
    print(f"   Historique: {len(df_hist)} jours")
    
    print("\n✅ Test terminé")

# ============================================
# GUIDE INTERACTIF - INSTRUCTION BAM N° IN-2026-01
# Modalités de détermination des cours de clôture
# ============================================

import streamlit as st
from datetime import datetime

def render_guide_complet():
    """Affiche le guide complet de l'instruction BAM"""
    
    st.title("📚 Instruction Bank Al-Maghrib N° IN-2026-01")
    st.caption("Modalités de détermination des cours de clôture des instruments financiers à terme")
    
    st.divider()
    
    # ────────────────────────────────────────────
    # OBJET ET RÉFÉRENCES
    # ────────────────────────────────────────────
    st.markdown("### 🎯 Objet de l'Instruction")
    
    st.info("""
        **Objectif :** Définir les modalités de détermination des cours de clôture 
        des instruments financiers à terme sur le marché à terme marocain.
    """)
    
    st.markdown("### 📋 Références Réglementaires")
    
    st.markdown("""
        - **Vu** le dahir N°1-14-96 du 20 Rejeb 1435 (20 Mai 2014) portant promulgation 
          de la loi n°42-12 relative au marché à terme d'instruments financiers, et notamment l'article 9
          
        - **Vu** les dispositions du Règlement Général de la société gestionnaire du marché à terme, 
          approuvé par l'arrêté du ministre de l'économie et des finances n°2582-22 du premier 
          rabii I 1444 (27 septembre 2022) notamment son article 58
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # ARTICLE 1 : COURS DE CLÔTURE
    # ────────────────────────────────────────────
    st.markdown("### 📌 Article 1 — Détermination du Cours de Clôture")
    
    st.markdown("""
        Le cours de clôture d'un instrument financier à terme est déterminé selon la hiérarchie suivante :
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **1️⃣ Cours du Fixing de Clôture**
            
            Priorité au cours officiel de clôture
            
            ✅ **Première option**
        """)
    
    with col2:
        st.markdown("""
            **2️⃣ Dernier Cours Traité**
            
            En l'absence de fixing de clôture
            
            ⚠️ **Deuxième option**
        """)
    
    with col3:
        st.markdown("""
            **3️⃣ Cours Théorique**
            
            En l'absence de tout cours traité
            
            📐 **Troisième option**
        """)
    
    st.success("""
        **Hiérarchie de détermination :**  
        Fixing de Clôture → Dernier Cours Traité → Cours Théorique
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # ARTICLE 2 : COURS THÉORIQUE
    # ────────────────────────────────────────────
    st.markdown("### 📐 Article 2 — Calcul du Cours Théorique")
    
    st.markdown("""
        #### Formule Générale pour les Futures sur Indice
    """)
    
    st.markdown("""
        <div style='padding: 30px; background: linear-gradient(135deg, #1E3A5F 0%, #2E5C8A 100%); 
                    border-radius: 12px; text-align: center; color: white; margin: 20px 0;'>
            <p style='font-size: 1.8em; font-weight: 700; margin: 0;'>
                Cours théorique = S × e<sup>(r-d)t</sup>
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Variables de la formule
    st.markdown("#### Variables de la Formule")
    
    col_s, col_r = st.columns(2)
    
    with col_s:
        st.markdown("""
            **S — Prix Spot (Cash)**
            
            • Valeur de l'indice cash au moment du calcul  
            • Correspond au niveau de l'indice sous-jacent  
            • Source : Bourse de Casablanca
        """)
    
    with col_r:
        st.markdown("""
            **r — Taux d'Intérêt Sans Risque**
            
            • Taux des bons du Trésor  
            • Maturité adaptée à l'échéance du future  
            • Source : Bank Al-Maghrib (BKAM)
        """)
    
    col_d, col_t = st.columns(2)
    
    with col_d:
        st.markdown("""
            **d — Taux de Dividende**
            
            • Dividend yield de l'indice  
            • Calculé selon formule spécifique (voir ci-dessous)  
            • Reflète les dividendes attendus des constituants
        """)
    
    with col_t:
        st.markdown("""
            **t — Temps jusqu'à l'Échéance**
            
            • t = Nombre de jours / 360  
            • Inclure tous les jours de la semaine (week-ends inclus)  
            • Convention de base 360 jours
        """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # CALCUL DU TAUX DE DIVIDENDE
    # ────────────────────────────────────────────
    st.markdown("#### Calcul du Taux de Dividende de l'Indice")
    
    st.markdown("""
        Le taux de dividende (dividend yield) de l'indice est calculé selon la formule suivante :
    """)
    
    st.markdown("""
        <div style='padding: 25px; background: #f0f9ff; border-left: 5px solid #1E3A5F; 
                    border-radius: 8px; margin: 20px 0;'>
            <p style='font-size: 1.5em; font-weight: 600; margin: 0; text-align: center;'>
                d = Σ (Pi × Di / Ci)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### Composantes du Calcul")
    
    st.markdown("""
        | Symbole | Signification | Détails |
        |---------|---------------|---------|
        | **i** | Les actions qui constituent l'indice | Somme sur tous les constituants (ex: 20 pour MASI20) |
        | **Di** | Dividende par action i | Dividende annuel attendu ou déclaré |
        | **Ci** | Cours de l'action i | Prix de l'action au moment du calcul |
        | **Pi** | Poids du titre i dans l'indice | Pondération officielle dans l'indice |
    """)
    
    # Exemple de calcul
    st.markdown("#### Exemple de Calcul (Illustratif)")
    
    st.markdown("""
        Pour un indice composé de 3 actions :
        
        | Action | Poids (Pi) | Cours (Ci) | Dividende (Di) | Di/Ci | Pi × (Di/Ci) |
        |--------|------------|------------|----------------|-------|--------------|
        | A | 50% | 100 MAD | 5 MAD | 5% | 0.50 × 0.05 = 0.025 |
        | B | 30% | 200 MAD | 8 MAD | 4% | 0.30 × 0.04 = 0.012 |
        | C | 20% | 150 MAD | 6 MAD | 4% | 0.20 × 0.04 = 0.008 |
        
        **Taux de dividende de l'indice :** d = 0.025 + 0.012 + 0.008 = **0.045 = 4.5%**
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # APPLICATION PRATIQUE
    # ────────────────────────────────────────────
    st.markdown("### 🔧 Application Pratique")
    
    st.markdown("#### Cas du MASI20")
    
    st.markdown("""
        Pour le calcul du cours théorique d'un future sur le MASI20 :
        
        1. **Récupérer le niveau spot du MASI20** (S)  
           → Source : Bourse de Casablanca (cours de clôture)
        
        2. **Déterminer le taux sans risque** (r)  
           → Source : BKAM (taux des bons du Trésor à 10 ans)
        
        3. **Calculer le taux de dividende** (d)  
           → Somme pondérée des dividend yields des 20 constituants  
           → Utiliser les poids officiels du MASI20
        
        4. **Calculer le temps jusqu'à l'échéance** (t)  
           → t = Nombre de jours restants / 360  
           → Inclure tous les jours (week-ends inclus)
        
        5. **Appliquer la formule**  
           → Cours théorique = S × e^((r-d)t)
    """)
    
    # Exemple numérique complet
    st.markdown("#### Exemple Numérique Complet — Future MASI20")
    
    st.markdown("""
        **Données d'entrée :**
        - S = 1 876.54 points (niveau spot MASI20)
        - r = 3.5% = 0.035 (taux BKAM)
        - d = 2.8% = 0.028 (dividend yield calculé)
        - Jours restants = 90 jours
        - t = 90/360 = 0.25
        
        **Calcul :**
        ```
        Cours théorique = 1 876.54 × e^((0.035 - 0.028) × 0.25)
                        = 1 876.54 × e^(0.007 × 0.25)
                        = 1 876.54 × e^(0.00175)
                        = 1 876.54 × 1.001751
                        = 1 879.82 points
        ```
        
        **Résultat :** Le cours théorique du future MASI20 est de **1 879.82 points**
        
        **Base :** 1 879.82 - 1 876.54 = **+3.28 points (+0.17%)**
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # FONDAMENT THÉORIQUE
    # ────────────────────────────────────────────
    st.markdown("### 🎓 Fondement Théorique")
    
    st.markdown("""
        #### Le Principe d'Absence d'Opportunité d'Arbitrage
        
        La formule du cours théorique repose sur le principe fondamental suivant :
        
        > **À l'équilibre du marché, aucun trader ne peut réaliser un profit sans risque 
        > en exploitant la différence entre le future et le spot.**
    """)
    
    st.markdown("""
        #### Stratégies d'Arbitrage
        
        **Cas 1 : Future surévalué**  
        Si `Prix Marché > Cours Théorique`
        
        → Stratégie : Vendre Future + Acheter Spot (Cash-and-Carry)  
        → Résultat : Profit sans risque jusqu'à convergence
        
        **Cas 2 : Future sous-évalué**  
        Si `Prix Marché < Cours Théorique`
        
        → Stratégie : Acheter Future + Vendre Spot (Reverse Cash-and-Carry)  
        → Résultat : Profit sans risque jusqu'à convergence
        
        **À l'équilibre :**  
        `Prix Marché = Cours Théorique`  
        → Aucune opportunité d'arbitrage possible
    """)
    
    st.info("""
        **Pourquoi cette formule est-elle importante ?**
        
        1. ✅ **Référence objective** : Prix calculable par tous, indépendant des opinions
        2. ✅ **Transparence du marché** : Tous les acteurs utilisent la même méthode
        3. ✅ **Détection d'anomalies** : Permet d'identifier les déviations de prix
        4. ✅ **Conformité réglementaire** : Respect des exigences de Bank Al-Maghrib
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # ARTICLE 3 : ENTRÉE EN APPLICATION
    # ────────────────────────────────────────────
    st.markdown("### 📅 Article 3 — Entrée en Application")
    
    st.warning("""
        Les dispositions de la présente instruction entrent en application à partir du :  
        **------** (Date à compléter)
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # RÉSUMÉ EXÉCUTIF
    # ────────────────────────────────────────────
    st.markdown("### 📋 Résumé Exécutif")
    
    st.markdown("""
        #### Points Clés à Retenir
        
        1. **Hiérarchie des cours de clôture :**
           - Priorité au fixing de clôture
           - À défaut, dernier cours traité
           - À défaut, cours théorique
        
        2. **Formule du cours théorique :**
           - `Cours théorique = S × e^((r-d)t)`
           - Base 360 jours (convention marocaine)
           - Week-ends inclus dans le calcul du temps
        
        3. **Calcul du taux de dividende :**
           - Formule : `d = Σ(Pi × Di / Ci)`
           - Somme sur tous les constituants de l'indice
           - Utiliser les poids officiels
        
        4. **Sources des données :**
           - S : Bourse de Casablanca
           - r : Bank Al-Maghrib (BKAM)
           - d : Calculé à partir des constituants
           - t : Calculé en jours/360
        
        5. **Conformité :**
           - Instruction BAM N° IN-2026-01
           - Basée sur la loi n°42-12 du marché à terme
           - Applicable à tous les futures sur indice
    """)
    
    st.success("""
        ✅ **Cette application respecte intégralement les dispositions de l'Instruction 
        BAM N° IN-2026-01 pour le calcul des cours théoriques des futures sur indice.**
    """)
    
    st.divider()
    
    # ────────────────────────────────────────────
    # MÉTA-INFORMATIONS
    # ────────────────────────────────────────────
    st.caption(f"""
        **Document de référence :** Instruction Bank Al-Maghrib N° IN-2026-01  
        **Date de publication :** 2026  
        **Autorité émettrice :** Bank Al-Maghrib (Banque Centrale du Maroc)  
        **Cadre légal :** Loi n°42-12 relative au marché à terme d'instruments financiers  
        **Génééré le :** {datetime.now().strftime('%d/%m/%Y à %H:%M')}
    """)


def render_guide_compact():
    """Version compacte pour intégration dans les pages existantes"""
    
    with st.expander("📘 Guide Complet — Instruction BAM N° IN-2026-01"):
        render_guide_complet()

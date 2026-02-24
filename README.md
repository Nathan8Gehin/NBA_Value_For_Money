# 🏀 NBA Analytics - Performance vs Salary

Ce projet est une application de Business Intelligence appliquée à la NBA. Elle permet d'évaluer le "Value for Money" (VFM) des joueurs pour la saison 2025-2026 en comparant leur production statistique réelle à leur rémunération.

# 👥 Équipe Projet
* Nathan GEHIN

* Kevin KONAN

* Marius HAVAN


## 🌟 Points importants du projet

* **Algorithme de Scoring Adaptatif** : Contrairement aux modèles classiques, notre impact défensif valorise la protection de cercle (Contres 50%) et la présence physique (Rebonds 35%), rendant justice aux profils plus défensifs
* **Matching de Données Robuste** : Système de fusion (Merge) intelligent capable de réconcilier les noms accentués (*Dončić*) et les formats abrégés (*V. Wembanyama*).
* **Interface Intuitive** : Dashboard complet avec 6 sections d'analyse (Stats, Efficacité, Défense, Performance %, Impacts et Contrat).
* **Automatisation** : Script de scraping intégré avec mise à jour automatique des données si le fichier local est obsolète.

## 📊 Méthodologie d'Analyse

Le projet repose sur trois piliers de calcul (situés dans `Scripts/utils_nba.py`) :

### 1. Score de Performance Global
Calculé sur une base normalisée (0 à 1) par rapport aux leaders de la ligue, avec des coefficients de rareté :
* **Défense (Steals/Blocks)** : Coeff 2.5
* **Création (Assists)** : Coeff 1.5
* **Scoring (Points)** : Coeff 1.0

### 2. Évaluation des Impacts
* **Offensif** : Équilibre entre points et passes.
* **Défensif** : Modèle pondéré pour éviter de surévaluer les meneurs qui interceptent mais ne protègent pas le cercle.

### 3. Diagnostic de Valeur
* 🟢 **Sous-payé** : Le joueur produit bien plus que ce que son salaire suggère.
* 🟡 **Bien payé** : Le salaire est en adéquation avec la production statistique.
* 🔴 **Sur-payé** : La production statistique ne justifie pas le salaire actuel.

## 🛠️ Installation et Utilisation

### Prérequis
* Python 3.10 ou supérieur
* Pip (gestionnaire de paquets)

### Installation
1.  **Cloner le projet**
    ```bash
    git clone [https://github.com/ton-nom-utilisateur/NBA_Value_for_money.git](https://github.com/ton-nom-utilisateur/NBA_Value_for_money.git)
    cd NBA_Value_for_money
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Lancer l'application**
    ```bash
    python nba_app.py
    ```
    *L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse `http://127.0.0.1:5000`.*

## 📁 Structure du Repository

* `nba_app.py` : Serveur Flask et interface utilisateur.
* `Scripts/` : Cœur algorithmique (fusion et calculs).
* `Scrapers/` : Scripts de récupération des données NBA.
* `data/` : Stockage des fichiers Excel sources et finaux.
* `requirements.txt` : Liste des bibliothèques nécessaires (Pandas, Flask, Openpyxl).

## 📄 Licence
Ce projet est distribué sous la **Licence MIT**. Voir le fichier `LICENSE` pour plus de détails.

---
*Projet réalisé dans le cadre du Master 1 DS2E - 2026*

# Rennes Traffic - Application de Surveillance du Trafic Routier

> **Environnement** : Ce projet a été développé et testé sous **WSL2 (Windows Subsystem for Linux)** avec Ubuntu 24.

> **Avertissement** : Ce repo est réalisé dans un cadre pédagogique (E5 - Cas Pratique). Le code original contenait des bugs volontaires qui ont été corrigés et l'application a été monitorée dans le cadre de cet exercice.

## Présentation

Application web Flask permettant de visualiser en temps réel l'état du trafic routier de l'agglomération de Rennes, à partir des données ouvertes de Rennes Métropole. Elle intègre un modèle de Machine Learning pour prédire l'état du trafic (Libre / Dense / Bloqué) en fonction de l'heure saisie par l'utilisateur.

---

## Fonctionnalités

- Carte interactive du trafic en temps réel (Plotly)
- Prédiction de l'état du trafic par un modèle Keras
- Mise à jour automatique des données toutes les 30 minutes (APScheduler)
- Monitoring applicatif via Flask Monitoring Dashboard
- Journalisation des erreurs avec horodatage (module `logging`)
- Alertes email automatiques en cas d'erreur (SMTPHandler)
- Variables d'environnement sécurisées via `.env`

---

## Stack technique

- Python 3.11
- Flask
- Keras / TensorFlow
- Plotly
- Flask Monitoring Dashboard
- APScheduler
- python-dotenv

---

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/TON_USERNAME/rennes_traffic.git
cd rennes_traffic
```

### 2. Créer et activer l'environnement virtuel

**Avec conda :**
```bash
conda create -n rennes_env python=3.11
conda activate rennes_env
```

**Ou avec pip :**
```bash
python -m venv rennes_env
source rennes_env/bin/activate  # Linux/Mac
rennes_env\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Installer Flask Monitoring Dashboard depuis GitHub

> Le package PyPI de flask_monitoringdashboard ne contient pas les assets frontend compilés (app.js, main.css). Il faut builder manuellement depuis le repo GitHub.

```bash
# Installer nodejs et npm si nécessaire
sudo apt update && sudo apt install nodejs npm -y

# Cloner le repo
git clone https://github.com/flask-dashboard/Flask-MonitoringDashboard.git

# Builder le frontend Vue.js
cd Flask-MonitoringDashboard/flask_monitoringdashboard/frontend
npm install
npm run build

# Revenir à la racine et installer le package
cd ../../..
pip install .

# Copier les assets buildés dans le package installé
cp -r Flask-MonitoringDashboard/flask_monitoringdashboard/static/* \
$(python3 -c "import os, flask_monitoringdashboard; print(os.path.dirname(flask_monitoringdashboard.__file__))")/static/
```

### 5. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```ini
MAIL_FROM=ton_email@gmail.com
MAIL_TO=ton_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

> Pour `MAIL_PASSWORD` : utiliser un **mot de passe applicatif Gmail** (Google Account → Sécurité → Mots de passe des applications), et non votre mot de passe principal.

### 6. Configurer le monitoring

Le fichier `config.cfg` est déjà présent à la racine :

```ini
[dashboard]
MONITOR_LEVEL=3
OUTLIER_DETECTION_CONSTANT=3
SAMPLING_PERIOD=1
ENABLE_LOGGING=True
DATABASE=sqlite:///flask_monitoringdashboard.db
CUSTOM_LINK=dashboard

[visualization]
TIMEZONE=Europe/Paris

[telemetry]
TELEMETRY=False

[metrics]
CPU_USAGE=True
MEMORY_USAGE=True
REQUESTS=True
RESPONSE_TIMES=True
EXCEPTIONS=True
```

---

## Lancement

```bash
python3 app.py
```

- Application : [http://localhost:5000](http://localhost:5000)
- Dashboard monitoring : [http://localhost:5000/dashboard](http://localhost:5000/dashboard)
  - Login : `admin` / Password : `admin`

---

## Structure du projet

```
rennes_traffic/
├── app.py                  # Application Flask principale
├── config.cfg              # Configuration Flask Monitoring Dashboard
├── .env                    # Variables d'environnement (non versionné)
├── .gitignore
├── requirements.txt
├── model.h5                # Modèle Keras (non versionné)
├── logs/
│   └── app.log             # Fichier de journalisation des erreurs
├── src/
│   ├── get_data.py         # Récupération et traitement des données API
│   └── utils.py            # Fonctions utilitaires (figure, prédiction, alerte)
└── templates/
    └── index.html          # Template HTML
```

---

## Bugs corrigés

| Fichier | Bug | Correction |
|---|---|---|
| `app.py` | `prediction_from_model()` appelé avec 1 argument au lieu de 2 | Ajout de l'argument `selected_hour` |
| `app.py` | `render_template("home.html")` fichier inexistant | Remplacé par `index.html` |
| `get_data.py` | Crochet fermant manquant sur le filtre `res_df` | Ajout du `]` manquant |
| `get_data.py` | Clé `traffic_status` inexistante dans le JSON de l'API | Remplacée par `trafficstatus` |
| `get_data.py` | Clé `lattitude` (faute de frappe) | Remplacée par `lat` |
| `get_data.py` | Clé `longitude` (faute de frappe) | Remplacée par `lon` |
| `utils.py` | `zoom=10` sans virgule dans `create_figure()` | Ajout de la virgule |
| `utils.py` | Tableau `np.array([0]*25)` au lieu de 24 heures | Corrigé en `np.array([0]*24)` |

---

## Monitoring

Le dashboard Flask Monitoring Dashboard est accessible sur `/dashboard` et permet de surveiller :

- **Temps de réponse** par endpoint
- **Nombre de requêtes** (aujourd'hui, 7 derniers jours, total)
- **Exceptions** levées
- **Outliers** (requêtes anormalement lentes)
- **Utilisation CPU et mémoire**

### Seuils d'alerte définis

| Métrique | Seuil alerte |
|---|---|
| Temps de réponse | > 2 secondes |
| Volume données API | < 10 enregistrements |
| Erreur applicative | Toute exception non gérée |

En cas de dépassement, une alerte email est envoyée automatiquement.

---

## Journalisation

Les erreurs sont enregistrées dans `logs/app.log` avec horodatage :

```
2026-04-15 14:32:01 - ERROR - Erreur route / : KeyError 'hour'
2026-04-15 14:35:22 - ERROR - Erreur récupération données API : JSONDecodeError
```

---

## Source des données

[API Open Data Rennes Métropole - État du trafic en temps réel](https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-du-trafic-en-temps-reel/)
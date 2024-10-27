# Projet de Scraping en Python
Ce projet utilise Python pour scraper des données web à l'aide de BeautifulSoup, Requests, et Selenium. Le script extrait des informations spécifiques de sites web et génère des rapports visuels et PDF à partir des données récoltées.

## Prérequis
Assurez-vous d'avoir Python 3.7+ installé sur votre machine. Utilisez pip pour installer les packages nécessaires.

## Installation des dépendances
Les dépendances pour ce projet sont listées dans le fichier requirements.txt. Pour les installer, exécutez la commande suivante :

```bash
pip install -r requirements.txt
```

## Packages inclus
Le fichier ```requirements.txt``` inclut les versions suivantes des packages :
- ```beautifulsoup4==0.0.2``` : pour analyser et extraire des données du HTML.
- ```requests==2.32.3``` : pour faire des requêtes HTTP.
- ```selenium==4.25.0``` : pour l'automatisation du navigateur, nécessaire pour scraper les sites nécessitant JavaScript.
- ```matplotlib==3.9.2``` : pour générer des graphiques à partir des données récoltées.
- ```reportlab==4.2.5``` : pour générer des rapports PDF.

## Utilisation
Exécution du script : Lancez le script de scraping en exécutant la commande suivante dans le terminal :

```bash
python script.py
```


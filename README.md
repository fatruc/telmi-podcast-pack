# Podcast Downloader

Ce projet permet de télécharger des podcast volumineux et de les mettre dans un format importable dans telmisync

## Fonctionnalités

- Télécharge les épisodes d'un podcast depuis un flux RSS.
- Télécharge et redimensionne les images de couverture des podcasts.
- Regroupe les épisodes par 8, et créer une image contenant la liste des épisodes de chaque partie

## Prérequis

Avant de commencer, assurez-vous que vous avez installé les outils suivants :

- **Python 3.x** : Assurez-vous d'avoir Python 3 installé sur votre machine. :

  ```bash
  python3 --version
  ```
- **pip** : Le gestionnaire de paquets Python pour installer les dépendances. Vous pouvez vérifier que pip est installé avec la commande :
```bash
  pip --version
```

- **git** :  système de contrôle de version distribué. Vous pouvez vérifier que pip est installé avec la commande :
```bash
  git --version
```

## Installation

- Clonez ce dépôt sur votre machine :

```bash
  git clone https://github.com/fatruc/telmi-podcast-pack.git
  cd /telmi-podcast-pack
```

- Créez un environnement virtuel (optionnel mais recommandé) :

```bash
  python3 -m venv venv
  source venv/bin/activate  # Sur Linux/MacOS
  venv\Scripts\activate     # Sur Windows
```

- Installez les dépendances requises :

```bash
  pip install -r requirements.txt
```

## Exécution du script

Exécutez le script Python en fournissant l'URL du flux RSS du podcast que vous souhaitez télécharger. Voici un exemple d'exécution :

```bash
  python3 download_podcast.py <RSS_URL>
```

Remplacez <RSS_URL> par l'URL du flux RSS du podcast. Par exemple :

```bash
  python3 download_podcast.py https://example.com/podcast/rss
```

Le script va télécharger les fichiers MP3 et les mettre en forme pour telmisync
# Contributions
Si vous souhaitez contribuer à ce projet, n'hésitez pas à soumettre des pull requests. Vous pouvez également ouvrir des issues pour signaler des bugs ou des suggestions d'amélioration.

# Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.


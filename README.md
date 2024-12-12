# Large Podcast Downloader

Ce projet permet de télécharger des podcast volumineux et de les mettre dans un format importable dans telmisync.

Il s'accompagne de scrapper pour récupérer les vignettes des histoires sur les sites des éditeurs

## Fonctionnalités

- Télécharge les épisodes d'un podcast depuis un flux RSS.
- Télécharge et redimensionne les images de couverture des podcasts.
- Regroupe les épisodes par 8, et créer une image contenant la liste des épisodes de chaque partie. Ce groupement n'a lieu que si le pack comporte au moins 27 images.

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

Vous pouvez également passer les paramètres suivants pour modifier le comportement par défaut:
- reverse_order pour traiter les épisodes dans l'ordre inverse (du plus ancien au plus récent)
- clean_strings pour modifier les titres des épisodes afin de rendre la synthèse vocale plus correcte
- generate_audio pour utiliser la synthèse vocale de google plutôt que celle utilisée par telmi sync
- disable_grouping pour empêcher la création automatique de groupes
- add_episode_title pour ajouter le titre des épisodes sur la vignette des épisodes

Remplacez <RSS_URL> par l'URL du flux RSS du podcast. Par exemple :

```bash
  python3 download_podcast.py https://example.com/podcast/rss
```

Le script va télécharger les fichiers MP3 et les mettre en forme pour telmisync

## Exemple d'utilisation pour un podcast de RF

Chercher un podcast sur le site: https://radio-france-rss.aerion.workers.dev/

Par exemple:

![image](https://github.com/user-attachments/assets/6e72f137-f598-490e-8cba-d045b1d03f49)

1- Copier le lien émission puis exécuter

```bash
  python3 scrapper_radiofrance.py <URL_Emission>
```

Le script va créer un dossier images avec les vignettes des épisodes, ainsi qu'un fichier mapping.csv. Pour chaque vignette, le fichier contient le nom de l'épisode. A ce stade vous pouvez modifier le nom de l'épisode dans la deuxième colonne du fichier

2- Copier le lien Flux RSS puis exécuter

```bash
  python3 download_podcast.py <RSS_URL>
```

S'ils existent, le script va utiliser le dossier images et le fichier mapping.csv pour créer un pack sous forme d'un fichier zip importable dans telmisync

Voici les commandes à exécuter pour quelques podcasts libre

### pomme d'api
```bash
python my-telmi-podcast.py https://feed.ausha.co/B6r8OclKP6gn  generate_audio clean_strings add_episode_title
```

### une histoire et oli
```bash
python scrapper_radiofrance.py https://www.radiofrance.fr/franceinter/podcasts/une-histoire-et-oli
python my-telmi-podcast.py https://radio-france-rss.aerion.workers.dev/rss/d555ed4e-dbe5-4908-912e-b3169f9ceede clean_strings generate_audio
```

### les odyssés
```bash
python scrapper_radiofrance.py https://www.radiofrance.fr/franceinter/podcasts/les-odyssees
python my-telmi-podcast.py https://radio-france-rss.aerion.workers.dev/rss/c361798b-d6e3-4282-ba0a-ebb051b9e424 clean_strings generate_audio
```

# Contributions
Si vous souhaitez contribuer à ce projet, n'hésitez pas à soumettre des pull requests. Vous pouvez également ouvrir des issues pour signaler des bugs ou des suggestions d'amélioration.

# Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.


# Podcast Downloader

Ce projet permet de télécharger et de gérer des podcasts en téléchargeant les fichiers audio (MP3) et en générant des images avec des titres d'épisodes.

## Fonctionnalités

- Télécharge les épisodes d'un podcast depuis un flux RSS.
- Télécharge et redimensionne les images de couverture des podcasts.
- Crée des images avec des titres d'épisodes.
- Gère les titres de manière uniforme, en ajustant la taille du texte et en répartissant les lignes sur toute la hauteur de l'image.
- Génère des images avec des couleurs de fond pastel tournantes.

## Prérequis

Avant de commencer, assurez-vous que vous avez installé les outils suivants :

- **Python 3.x** : Assurez-vous d'avoir Python 3 installé sur votre machine. Vous pouvez vérifier cela avec la commande :
  ```bash
  python3 --version
pip : Le gestionnaire de paquets Python pour installer les dépendances. Vous pouvez vérifier que pip est installé avec la commande :
bash
Copier le code
pip --version
Installation
Clonez ce dépôt sur votre machine :

bash
Copier le code
git clone https://github.com/<votre-nom-utilisateur>/podcast-downloader.git
cd podcast-downloader
Créez un environnement virtuel (optionnel mais recommandé) :

bash
Copier le code
python3 -m venv venv
source venv/bin/activate  # Sur Linux/MacOS
venv\Scripts\activate     # Sur Windows
Installez les dépendances requises :

bash
Copier le code
pip install -r requirements.txt
Le fichier requirements.txt contient les bibliothèques nécessaires pour exécuter le script, telles que :

txt
Copier le code
requests
feedparser
Pillow
Utilisation
Exécution du script
Exécutez le script Python en fournissant l'URL du flux RSS du podcast que vous souhaitez télécharger. Voici un exemple d'exécution :

bash
Copier le code
python3 download_podcast.py <RSS_URL>
Remplacez <RSS_URL> par l'URL du flux RSS du podcast. Par exemple :

bash
Copier le code
python3 download_podcast.py https://example.com/podcast/rss
Le script va télécharger les fichiers MP3 des épisodes et générer des images avec les titres, en les enregistrant dans un dossier structuré sur votre machine.

Exemple de structure de répertoire
Après l'exécution du script, la structure des fichiers sera organisée comme suit :

bash
Copier le code
<nom_du_podcast>/
├── main-title.png      # Image principale du podcast
├── cover.png           # Image de couverture
├── 0/                  # Dossier pour la première page
│   ├── title.txt       # Texte de la première page
│   ├── title.png       # Image avec le titre
│   └── 0/              # Dossier pour les épisodes de la première partie
│       └── story.mp3   # Fichier MP3 de l'épisode
└── 1/                  # Dossier pour la deuxième page
    ├── title.txt       # Texte de la deuxième page
    ├── title.png       # Image avec le titre
    └── 0/              # Dossier pour les épisodes de la deuxième partie
        └── story.mp3   # Fichier MP3 de l'épisode
Chaque dossier contient des fichiers MP3 pour les épisodes, des fichiers title.txt avec les titres, et des images avec des fonds de couleurs pastel.

Contributions
Si vous souhaitez contribuer à ce projet, n'hésitez pas à soumettre des pull requests. Vous pouvez également ouvrir des issues pour signaler des bugs ou des suggestions d'amélioration.

Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus d'informations.

python
Copier le code

### Explications supplémentaires :

- **Instructions d'installation des dépendances** : Le fichier `README.md` contient des instructions détaillées sur la façon d'installer Python, de créer un environnement virtuel et d'installer les dépendances nécessaires pour exécuter le script.
  
- **Exécution du script** : Un exemple d'exécution du script est fourni, ainsi qu'une explication sur la structure des répertoires générée après le téléchargement des podcasts.

- **Contributions** : Vous encouragez les autres à contribuer en soumettant des *pull requests* ou en signalant des bugs/suggestions d'amélioration.

### Fichier `requirements.txt`

N'oubliez pas de créer un fichier `requirements.txt` avec les bibliothèques Python nécessaires :

requests feedparser Pillow

markdown
Copier le code

Cela permettra aux utilisateurs de facilement installer toutes les dépendances via `pip`.

### Licence

Le fichier `README.md` fait référence à une licence MIT (vous pouvez ajuster cela en fonction de la licence que vous souhaitez utiliser pour votre projet).

Avec ce `README.md`, les utilisateurs pourront facilement comprendre comment installer et utiliser votre script sur leur machine !

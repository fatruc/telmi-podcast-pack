import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import csv
import argparse
import re

# Dossiers pour les images et les fichiers audio
os.makedirs('images', exist_ok=True)


def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name)
    """Remplace les caractères interdits dans les noms de fichiers et dossiers par un '-'"""
    """return re.sub(r'[<>:"/\\|?*]', '-', name)"""


def file_exists(title, file_type):
    """Vérifie si un fichier (image ou audio) existe déjà."""
    safe_title = sanitize_filename(title)
    file_path = f'{file_type}/{safe_title}.jpg'
    return os.path.isfile(file_path)

def download_image(url, save_path):
    """Télécharge une image depuis une URL et la sauvegarde à l'emplacement donné si elle n'existe pas déjà."""
    if os.path.exists(save_path):
        print(f"Image déjà existante: {save_path}, téléchargement ignoré.")
        return True
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return True
    except requests.RequestException as e:
        print(f"Erreur lors du téléchargement de l'image {url}: {e}")
        return False

def download_episodes(base_url):
    """Étape 1 : Téléchargement des images et des audios des épisodes."""
    page_number = 1
    total_file_count = 0
    encountered_titles = set()  # Ensemble pour suivre les titres rencontrés

    while True:
        # Construire l'URL de la page en cours
        url = f"{base_url}{page_number}"
        print(f"Traitement de la page {page_number}...")

        # Effectuer une requête GET pour récupérer le contenu de la page
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver la liste des épisodes
        episodes = soup.find('ul', class_='Collection-section-items')

        # Si aucune épisode n'est trouvé, sortir de la boucle
        if not episodes:
            break

        # Parcourir chaque épisode
        for item in episodes.find_all('li', class_='Collection-section-items-item'):
            picture = item.find('picture')
            img_src = picture.find('source')['srcset'] if picture else None
            
            title_span = item.find('span', class_='CardTitle')
            title = title_span.find('a').text.strip() if title_span and title_span.find('a') else None
            
            if img_src and title:
                # Si le titre a déjà été rencontré, arrêter complètement le traitement
                if title in encountered_titles:
                    print(f"Le titre '{title}' a déjà été rencontré. Arrêt complet.")
                    return  # Arrêter la boucle principale
                
                encountered_titles.add(title)  # Ajouter le titre à l'ensemble

                # Créer une version sécurisée du titre pour le nom de fichier
                safe_title = sanitize_filename(title)

                # Vérifier et télécharger l'image
                img_filename = f'output/images/{safe_title}.jpg'
                if not os.path.isfile(img_filename):
                    download_image(img_src, img_filename)

        page_number += 1

    print(f"Total de fichiers traités : {total_file_count}")

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Scrape un site pour télécharger des podcasts.")
    parser.add_argument("base_url", type=str, help="URL de base pour scraper les épisodes (exemple : 'https://www.radiofrance.fr/franceinter/podcasts/les-odyssees?p=')")
    args = parser.parse_args()

    print("Début du script.")
    # Télécharger les épisodes
    download_episodes(args.base_url+"?p=")
    print("Script terminé.")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import csv
import argparse

# Dossiers pour les images et les fichiers audio
os.makedirs('images', exist_ok=True)
os.makedirs('audio', exist_ok=True)

# Nom du fichier de mapping
MAPPING_FILE = 'mapping.csv'

def initialize_mapping_file():
    """Crée le fichier de mapping s'il n'existe pas, avec encodage UTF-8 BOM pour compatibilité avec Excel."""
    if not os.path.isfile(MAPPING_FILE):
        with open(MAPPING_FILE, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(['Nom modifié', 'Nom original'])  # Créer l'en-tête avec les colonnes 'Nom modifié' et 'Nom original'

def add_to_mapping_file(safe_title, original_title):
    """Ajoute une ligne au fichier de mapping si le fichier n'existe pas déjà."""
    with open(MAPPING_FILE, mode='r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=';')
        existing_files = {row['Nom modifié'] for row in reader}

    if safe_title not in existing_files:
        with open(MAPPING_FILE, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([safe_title, original_title])  # Ajouter la ligne avec le nom modifié et le nom original

def file_exists(title, file_type):
    """Vérifie si un fichier (image ou audio) existe déjà."""
    safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
    file_extension = 'jpg' if file_type == 'image' else 'mp3'
    file_path = f'{file_type}/{safe_title}.{file_extension}'
    return os.path.isfile(file_path)

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
                safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()

                # Vérifier et télécharger l'image
                img_filename = f'images/{safe_title}.jpg'
                if not file_exists(title, 'image'):
                    img_response = requests.get(img_src)
                    img = Image.open(BytesIO(img_response.content))

                    # Convertir l'image en RGB si elle est en mode RGBA
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')

                    # Redimensionner l'image tout en maintenant le ratio
                    frame_width, frame_height = 640, 480
                    aspect_ratio = img.width / img.height

                    if aspect_ratio > (frame_width / frame_height):
                        # L'image est plus large que le cadre : ajuster à la largeur
                        new_width = frame_width
                        new_height = int(new_width / aspect_ratio)
                    else:
                        # L'image est plus haute ou carrée : ajuster à la hauteur
                        new_height = frame_height
                        new_width = int(new_height * aspect_ratio)

                    img = img.resize((new_width, new_height), Image.LANCZOS)

                    # Créer une image de fond noir
                    canvas = Image.new("RGB", (frame_width, frame_height), (0, 0, 0))

                    # Centrer l'image redimensionnée sur le fond
                    x_offset = (frame_width - new_width) // 2
                    y_offset = (frame_height - new_height) // 2
                    canvas.paste(img, (x_offset, y_offset))

                    # Sauvegarder l'image finale
                    canvas.save(img_filename, "JPEG", quality=100)
                    
                    print(f"Téléchargé : {img_filename}")
                    total_file_count += 1

                    # Ajouter au fichier de mapping avec le nom sécurisé et le titre original
                    add_to_mapping_file(safe_title, title)

        page_number += 1

    print(f"Total de fichiers traités : {total_file_count}")

def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Scrape un site pour télécharger des podcasts.")
    parser.add_argument("base_url", type=str, help="URL de base pour scraper les épisodes (exemple : 'https://www.radiofrance.fr/franceinter/podcasts/les-odyssees?p=')")
    args = parser.parse_args()

    print("Début du script.")
    # Initialiser le fichier de mapping
    initialize_mapping_file()
    # Télécharger les épisodes
    download_episodes(args.base_url+"?p=")
    print("Script terminé.")

if __name__ == "__main__":
    main()

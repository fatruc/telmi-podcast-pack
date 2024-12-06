import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import xml.etree.ElementTree as ET

# Définition des URL de manière statique
RSS_URL = "https://radio-france-rss.aerion.workers.dev/rss/d555ed4e-dbe5-4908-912e-b3169f9ceede"
BASE_URL = "https://www.radiofrance.fr/franceinter/podcasts/une-histoire-et-oli?p="

# Dossiers pour les images et les fichiers audio
os.makedirs('images', exist_ok=True)
os.makedirs('audio', exist_ok=True)

def file_exists(title, file_type):
    """Vérifie si un fichier (image ou audio) existe déjà."""
    safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
    file_extension = 'jpg' if file_type == 'image' else 'mp3'
    file_path = f'{file_type}/{safe_title}.{file_extension}'
    return os.path.isfile(file_path)

def get_audio_info_from_rss(rss_url):
    """Récupère les informations audio depuis un flux RSS."""
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    audio_info = {}
    
    for item in root.findall('.//item'):
        title = item.find('title').text
        audio_url = item.find('enclosure').attrib['url']
        audio_info[title] = audio_url
    
    return audio_info

def download_episodes(rss_url):
    """Étape 1 : Téléchargement des images et des audios des épisodes."""
    page_number = 1
    total_file_count = 0
    encountered_titles = set()  # Ensemble pour suivre les titres rencontrés

    # Obtenir les informations audio à partir du flux RSS
    audio_info = get_audio_info_from_rss(rss_url)

    while True:
        # Construire l'URL de la page en cours
        url = f"{BASE_URL}{page_number}"
        print(f"Traitement de la page {page_number}...")

        # Effectuer une requête GET pour récupérer le contenu de la page
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Trouver la liste des épisodes
        episodes = soup.find('ul', class_='Collection-section-items')

        # Si aucune épisode n'est trouvé, sortir de la boucle
        if not episodes:
            break

        page_file_count = 0  # Compteur de fichiers pour cette page

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

                safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()

                # Vérifier et télécharger l'image
                img_filename = f'images/{safe_title}.jpg'
                if not file_exists(title, 'image'):
                    img_response = requests.get(img_src)
                    img = Image.open(BytesIO(img_response.content))

                    # Redimensionner l'image
                    aspect_ratio = img.width / img.height
                    new_height = 480
                    new_width = int(aspect_ratio * new_height)
                    img = img.resize((new_width, new_height), Image.LANCZOS)

                    # Tronquer l'image si la largeur dépasse 640px
                    if new_width > 640:
                        left = (new_width - 640) // 2
                        right = left + 640
                        img = img.crop((left, 0, right, new_height))

                    img.save(img_filename, 'JPEG', quality=100)
                    print(f"Téléchargé : {img_filename}")
                    total_file_count += 1

                # Vérifier et télécharger l'audio
                audio_url = audio_info.get(title)
                audio_filename = f'audio/{safe_title}.mp3'
                if audio_url and not file_exists(title, 'audio'):
                    audio_response = requests.get(audio_url)
                    with open(audio_filename, 'wb') as audio_file:
                        audio_file.write(audio_response.content)
                    print(f"Téléchargé audio : {audio_filename}")
                    total_file_count += 1

        print(f"Nombre de fichiers traités sur la page {page_number} : {page_file_count}")
        page_number += 1

    print(f"Total de fichiers traités : {total_file_count}")

def get_podcast_info(rss_url):
    """Extrait le titre et l'image principale du podcast depuis le flux RSS."""
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    channel = root.find('channel')

    if channel is None:
        raise ValueError("Le flux RSS ne contient pas d'élément <channel>.")

    # Récupérer le titre
    title_element = channel.find('title')
    title = title_element.text if title_element is not None else "Podcast sans titre"

    # Récupérer l'URL de l'image (si disponible)
    image_element = channel.find('image')
    if image_element is not None:
        url_element = image_element.find('url')
        image_url = url_element.text if url_element is not None else None
    else:
        image_url = None

    return title, image_url

 

def setup_podcast_folder(rss_url):
    """Étape 2 : Crée le dossier principal du podcast et les fichiers nécessaires."""
    podcast_title, podcast_image_url = get_podcast_info(rss_url)
    safe_podcast_title = f"0+] {podcast_title}"

    # Créer le dossier principal du podcast
    os.makedirs(safe_podcast_title, exist_ok=True)
    print(f"Dossier du podcast créé : {safe_podcast_title}")

    # Créer les fichiers `title.txt` et `main-title.txt`
    title_file_path = os.path.join(safe_podcast_title, "title.txt")
    main_title_file_path = os.path.join(safe_podcast_title, "main-title.txt")

    for file_path in [title_file_path, main_title_file_path]:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(podcast_title)
    print(f"Fichiers 'title.txt' et 'main-title.txt' créés dans {safe_podcast_title}")

    # Télécharger et sauvegarder l'image du podcast si elle existe
    if podcast_image_url:
        response = requests.get(podcast_image_url)
        img = Image.open(BytesIO(response.content))

        # Sauvegarder l'image en tant que `main-title.png` et `cover.png`
        main_title_image_path = os.path.join(safe_podcast_title, "main-title.png")
        cover_image_path = os.path.join(safe_podcast_title, "cover.png")

        for image_path in [main_title_image_path, cover_image_path]:
            img.save(image_path, "PNG")
        print(f"Images 'main-title.png' et 'cover.png' créées dans {safe_podcast_title}")
    else:
        print("Aucune image disponible pour ce podcast.")

    # Créer le dossier "0" (dossier de choix)
    choice_folder_path = os.path.join(safe_podcast_title, "0")
    os.makedirs(choice_folder_path, exist_ok=True)
    print(f"Dossier de choix créé : {choice_folder_path}")


def main():
    """Point d'entrée principal."""
    print("Début du script.")
    # Étape 1 : Télécharger les épisodes
    download_episodes(RSS_URL)

    # Étape 2 : Créer le dossier du podcast
    setup_podcast_folder(RSS_URL)
    print("Script terminé.")

if __name__ == "__main__":
    main()

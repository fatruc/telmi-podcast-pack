import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import os
import sys
import xml.etree.ElementTree as ET

# Dossier pour les images et les fichiers audio
os.makedirs('images', exist_ok=True)
os.makedirs('audio', exist_ok=True)

# Fonction pour vérifier si l'image ou l'audio existe déjà
def file_exists(title, file_type):
    safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
    file_extension = 'jpg' if file_type == 'image' else 'mp3'
    file_path = f'{file_type}/{safe_title}.{file_extension}'
    return os.path.isfile(file_path)

# Télécharger le flux RSS et extraire les titres et les URLs audio
def get_audio_info_from_rss(rss_url):
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    audio_info = {}
    
    for item in root.findall('.//item'):
        title = item.find('title').text
        audio_url = item.find('enclosure').attrib['url']
        audio_info[title] = audio_url
    
    return audio_info

# Initialiser le numéro de page et le compteur de fichiers
page_number = 1
total_file_count = 0

# Obtenir les informations audio à partir du flux RSS
rss_url = "https://radio-france-rss.aerion.workers.dev/rss/d555ed4e-dbe5-4908-912e-b3169f9ceede"
audio_info = get_audio_info_from_rss(rss_url)

while True:
    # URL de la page à scraper
    url = f"https://www.radiofrance.fr/franceinter/podcasts/une-histoire-et-oli?p={page_number}"
    
    # Afficher le numéro de la page en cours de traitement
    print(f"Traitement de la page {page_number}...")

    # Effectuer une requête GET pour récupérer le contenu de la page
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trouver la liste des épisodes
    episodes = soup.find('ul', class_='Collection-section-items')

    # Si aucune épisode n'est trouvé, sortir de la boucle
    if not episodes:
        break

    # Initialiser le compteur de fichiers pour cette page
    page_file_count = 0

    # Parcourir chaque épisode
    for item in episodes.find_all('li', class_='Collection-section-items-item'):
        # Extraire l'image
        picture = item.find('picture')
        img_src = picture.find('source')['srcset'] if picture else None
        
        # Extraire le titre
        title_span = item.find('span', class_='CardTitle')
        title = title_span.find('a').text.strip() if title_span and title_span.find('a') else None
        
        if img_src and title:
            # Vérifier si l'image ou l'audio existe déjà
            if file_exists(title, 'image') or file_exists(title, 'audio'):
                print(f"L'image ou l'audio pour '{title}' existe déjà. Arrêt du scraping.")
                print(f"Total de fichiers traités : {total_file_count}")
                sys.exit()  # Arrêter complètement le programme
            
            # Télécharger l'image
            img_response = requests.get(img_src)
            
            # Ouvrir l'image
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
            
            # Créer un nom de fichier valide pour l'image
            safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
            img_filename = f'images/{safe_title}.jpg'
            
            # Sauvegarder l'image avec une qualité maximale
            img.save(img_filename, 'JPEG', quality=100)
            total_file_count += 1  # Incrémenter le compteur total de fichiers
            page_file_count += 1  # Incrémenter le compteur de fichiers pour cette page
            print(f"Téléchargé : {img_filename}")

            # Télécharger le fichier audio
            audio_url = audio_info.get(title)
            if audio_url:
                audio_response = requests.get(audio_url)
                audio_filename = f'audio/{safe_title}.mp3'
                with open(audio_filename, 'wb') as audio_file:
                    audio_file.write(audio_response.content)
                total_file_count += 1  # Incrémenter le compteur total de fichiers pour l'audio
                print(f"Téléchargé audio : {audio_filename}")

    # Afficher le nombre de fichiers traités pour cette page
    print(f"Nombre de fichiers traités sur la page {page_number} : {page_file_count}")

    # Incrémenter le numéro de page
    page_number += 1

# Afficher le nombre total de fichiers traités
print(f"Total de fichiers traités : {total_file_count}")

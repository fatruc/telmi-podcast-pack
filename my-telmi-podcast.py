import os
import shutil
import requests
import feedparser
import unicodedata
import re
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont

def zip_folder(folder_path, output_path):
    """Crée une archive zip à partir d'un dossier."""
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        print(f"Dossier zippé avec succès : {output_path}")
    except Exception as e:
        print(f"Erreur lors de la création du fichier zip : {e}")

def clean_filename(title):
    nfkd_form = unicodedata.normalize('NFKD', title)
    ascii_title = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    cleaned_title = re.sub(r'[<>:"/\\|?*]', '-', ascii_title)
    cleaned_title = re.sub(r'[^a-zA-Z0-9\-]', '-', cleaned_title)
    cleaned_title = cleaned_title.lower()
    cleaned_title = re.sub(r'-+$', '', cleaned_title)
    return cleaned_title

def download_file(url, filename):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Fichier téléchargé : {filename}")
        else:
            print(f"Erreur lors du téléchargement de {url}")
    except Exception as e:
        print(f"Erreur: {e}")

def resize_image(input_path, output_path, size=(640, 480)):
    try:
        with Image.open(input_path) as img:
            target_height = size[1]
            img_ratio = img.width / img.height
            new_width = int(img_ratio * target_height)
            img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            background = Image.new("RGB", size, (240, 240, 240))  # Couleur pastel
            x_offset = (size[0] - new_width) // 2
            background.paste(img, (x_offset, 0))
            background.save(output_path)
    except Exception as e:
        print(f"Erreur lors du redimensionnement de l'image : {e}")

def create_text_image(output_path, text, size=(640, 480), font_path="Pacifico-Regular.ttf", color_index=0):
    # Liste des couleurs pastel
    pastel_colors = [
        (255, 255, 204),  # Conditioner
        (255, 204, 153),  # Peach Orange
        (255, 204, 204),  # Lusty-Gallant
        (255, 153, 204),  # Himalayan Balsam
        (255, 204, 255),  # Sugar Chic
        (204, 153, 255),  # Lilás
        (204, 204, 255),  # Lavender Blue
        (153, 204, 255),  # Apocyan
        (204, 255, 255),  # Dawn Departs
        (153, 255, 204),  # —
        (204, 255, 204),  # Distilled Moss
        (204, 255, 153),  # —
    ]

    try:
        # Sélectionner la couleur actuelle de la liste
        background_color = pastel_colors[color_index % len(pastel_colors)]
        
        # Créer l'image avec la couleur de fond choisie
        img = Image.new("RGB", size, background_color)  # Couleur pastel
        draw = ImageDraw.Draw(img)

        # Taille de la police
        font = ImageFont.truetype(font_path, size=36)

        margin = 19  # 0.5 cm ~ 19px
        text_lines = text.split('\n')

        # Hauteur totale disponible pour le texte
        available_height = size[1] - 2 * margin

        # Hauteur de chaque ligne d'espacement
        line_height = 36  # Hauteur de la ligne
        total_text_height = line_height * len(text_lines)

        # Si le texte dépasse la hauteur de l'image, ajustez la taille de la police
        if total_text_height > available_height:
            font_size = int(font.size * available_height / total_text_height)
            font = ImageFont.truetype(font_path, font_size)
            line_height = font_size
            total_text_height = line_height * len(text_lines)

        # Calculer l'offset vertical pour que les lignes de texte soient ventilées
        # Calcule l'espacement entre les lignes
        spacing = (available_height - total_text_height) / (len(text_lines) + 1)
        
        # Initialiser l'offset vertical (commencer après la marge)
        y_offset = margin + spacing  # L'espacement au début

        # Dessiner chaque ligne de texte avec la couleur noire
        for line in text_lines:
            draw.text((margin, y_offset), line, font=font, fill="black")
            y_offset += line_height + spacing  # Incrémenter par la hauteur de ligne et l'espacement

        # Sauvegarder l'image
        img.save(output_path)

    except Exception as e:
        print(f"Erreur lors de la création de l'image : {e}")





def clean_title(title):
    # Supprimer le texte avant le premier "-" ou ":" dans le titre
   # title = re.split(r'[:\-]', title, maxsplit=1)[-1].strip()
    return title

def download_podcast(rss_url):
    feed = feedparser.parse(rss_url)
    podcast_title = feed.feed.title
    podcast_image_url = feed.feed.image.href if 'image' in feed.feed else None
    main_dir = clean_filename(podcast_title)
    
    # Supprimer le dossier principal existant s'il existe
    if os.path.exists(main_dir):
        shutil.rmtree(main_dir)
    
    os.makedirs(main_dir)

    # Ajouter un fichier main-title.txt contenant le nom du podcast
    main_title_path = os.path.join(main_dir, 'main-title.txt')
    with open(main_title_path, 'w', encoding='utf-8') as f:
        f.write(podcast_title)
    
    # Liste pour stocker tous les titres d'épisodes
    all_episode_titles = []

    main_image_path = os.path.join(main_dir, 'main-title.png')
    cover_image_path = os.path.join(main_dir, 'cover.png')
    if podcast_image_url:
        download_file(podcast_image_url, main_image_path)
        resize_image(main_image_path, cover_image_path)
    
    zero_dir = os.path.join(main_dir, '0')
    os.makedirs(zero_dir, exist_ok=True)
    with open(os.path.join(zero_dir, 'title.txt'), 'w', encoding='utf-8') as f:
        f.write("Quelle histoire veux-tu écouter ?")
    shutil.copy(cover_image_path, os.path.join(zero_dir, 'title.png'))
    
    episodes = feed.entries
    groups = [episodes[i:i + 8] for i in range(0, len(episodes), 8)]
    
    for group_index, group in enumerate(groups):
        group_dir = os.path.join(zero_dir, str(group_index))
        os.makedirs(group_dir, exist_ok=True)
        with open(os.path.join(group_dir, 'title.txt'), 'w', encoding='utf-8') as f:
            f.write(f"partie {group_index + 1}")
        episode_titles = "\n".join([clean_title(ep.title) for ep in group])
        
        # Ajouter les titres des épisodes à la liste principale
        all_episode_titles.extend([clean_title(ep.title) for ep in group])

        # Créer l'image avec la liste des épisodes
        create_text_image(os.path.join(group_dir, 'title.png'), episode_titles, font_path="Pacifico-Regular.ttf", color_index=group_index)
        
        for episode_index, entry in enumerate(group):
            mp3_url = next((link.href for link in entry.links if link.type == 'audio/mpeg'), None)
            if not mp3_url:
                continue
            episode_subdir = os.path.join(group_dir, str(episode_index))
            os.makedirs(episode_subdir, exist_ok=True)
            with open(os.path.join(episode_subdir, 'title.txt'), 'w', encoding='utf-8') as f:
                f.write(clean_title(entry.title))
            mp3_path = os.path.join(episode_subdir, 'story.mp3')
           # download_file(mp3_url, mp3_path)

            # Télécharger l'image spécifique à cet épisode
            episode_image_url = entry.get('image', {}).get('href')
            if episode_image_url:
                episode_image_path = os.path.join(episode_subdir, 'title.png')
                download_file(episode_image_url, episode_image_path)
                resize_image(episode_image_path, episode_image_path)  # Redimensionner l'image de l'épisode

    # Créer un fichier episodes.txt contenant la liste de tous les épisodes
    episodes_path = os.path.join(main_dir, 'episodes.txt')
    with open(episodes_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_episode_titles))

    # Créer un fichier zip du dossier principal
    zip_path = f"{main_dir}.zip"
    zip_folder(main_dir, zip_path)

    # Supprimer le dossier source après zippage
    try:
        #shutil.rmtree(main_dir)
        print(f"Dossier supprimé après zippage : {main_dir}")
    except Exception as e:
        print(f"Erreur lors de la suppression du dossier : {e}")



# Récupérer l'URL du podcast depuis la ligne de commande
if len(sys.argv) != 2:
    print("Usage: python my-telmi-podcast.py <RSS_URL>")
    sys.exit(1)

rss_url = sys.argv[1]
download_podcast(rss_url)

import os
import shutil
import requests
import feedparser
import unicodedata
import re
import sys
import zipfile
from PIL import Image, ImageDraw, ImageFont
import csv
from gtts import gTTS  # Importer gTTS pour la synthèse vocale

# Variable globale pour stocker le mapping
_mapping_cache = None

def charger_mapping(chemin_fichier="mapping.csv"):
    global _mapping_cache
    if _mapping_cache is None:
        try:
            with open(chemin_fichier, mode="r", encoding="utf-8-sig") as fichier_csv:
                dialect = csv.Sniffer().sniff(fichier_csv.read(1024))
                fichier_csv.seek(0)
                lecteur = csv.reader(fichier_csv, delimiter=dialect.delimiter)
                _mapping_cache = {ligne[0]: ligne[1] for ligne in lecteur if len(ligne) >= 2}
        except FileNotFoundError:
            _mapping_cache = {}
        except Exception as e:
            print(f"Erreur lors du chargement du fichier : {e}")
            _mapping_cache = {}

def traduire(chaine, chemin_fichier="mapping.csv"):
    global _mapping_cache
    if _mapping_cache is None:
        charger_mapping(chemin_fichier)
    return _mapping_cache.get(chaine, chaine)

def nombre_en_lettres(n):
    if not (0 <= n <= 999):
        return "Nombre hors limite (doit être entre 0 et 999)"
    
    unite = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    dizaine = ["", "dix", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    special = {
        10: "dix", 11: "onze", 12: "douze", 13: "treize", 14: "quatorze", 
        15: "quinze", 16: "seize", 70: "soixante-dix", 71: "soixante et onze",
        90: "quatre-vingt-dix", 91: "quatre-vingt-onze"
    }

    if n in special:
        return special[n]
    
    if n >= 100:
        centaine, reste = divmod(n, 100)
        centaine_txt = f"{unite[centaine]} cent" if centaine > 1 else "cent"
        if reste == 0:
            return centaine_txt
        return f"{centaine_txt} {nombre_en_lettres(reste)}"
    
    if n >= 17:
        dizaine_index, unite_index = divmod(n, 10)
        dizaine_txt = dizaine[dizaine_index]
        if unite_index == 1 and (dizaine_index not in {8, 7}):
            return f"{dizaine_txt} et {unite[unite_index]}"
        elif dizaine_index == 8:
            dizaine_txt += "s" if unite_index == 0 else ""
        return f"{dizaine_txt} {unite[unite_index]}".strip()
    
    return unite[n]

def zip_folder(folder_path, output_path):
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

def clean_title(title):
    return title

def clean_filename(title):
    nfkd_form = unicodedata.normalize('NFKD', title)
    ascii_title = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    cleaned_title = re.sub(r'[<>:"/\\|?*]', '-', ascii_title)
    cleaned_title = re.sub(r'[^a-zA-Z0-9\-]', '-', cleaned_title)
    cleaned_title = cleaned_title.lower()
    cleaned_title = re.sub(r'-+$', '', cleaned_title)
    return cleaned_title

def clean_string(s):
    # Remplacer X/Y par X sur Y
    s = re.sub(r'(\d+)/(\d+)', r'\1 sur \2', s)
    # Conserver les caractères alphanumériques, les espaces, les accents, les tirets et les virgules
    return re.sub(r'[^a-zA-Z0-9\sÀ-ÿ,\'-]', '', s)


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
            background = Image.new("RGB", size, (240, 240, 240))
            x_offset = (size[0] - new_width) // 2
            background.paste(img, (x_offset, 0))
            background.save(output_path)
    except Exception as e:
        print(f"Erreur lors du redimensionnement de l'image : {e}")

def create_text_image(output_path, text, size=(640, 480), font_path="Pacifico-Regular.ttf", color_index=0):
    pastel_colors = [
        (255, 255, 204),
        (255, 204, 153),
        (255, 204, 204),
        (255, 153, 204),
        (255, 204, 255),
        (204, 153, 255),
        (204, 204, 255),
        (153, 204, 255),
        (204, 255, 255),
        (153, 255, 204),
        (204, 255, 204),
        (204, 255, 153),
    ]

    try:
        background_color = pastel_colors[color_index % len(pastel_colors)]
        img = Image.new("RGB", size, background_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, size=36)

        margin = 19
        text_lines = text.split('\n')
        available_height = size[1] - 2 * margin
        line_height = 36
        total_text_height = line_height * len(text_lines)

        if total_text_height > available_height:
            font_size = int(font.size * available_height / total_text_height)
            font = ImageFont.truetype(font_path, font_size)
            line_height = font_size
            total_text_height = line_height * len(text_lines)

        spacing = (available_height - total_text_height) / (len(text_lines) + 1)
        y_offset = margin

        for line in text_lines:
            draw.text((margin, y_offset), line, font=font, fill="black")
            y_offset += line_height + spacing

        img.save(output_path)

    except Exception as e:
        print(f"Erreur lors de la création de l'image : {e}")

def generate_audio_file(text, output_path):
    print(f"Génération de l'audio pour : {text}")
    try:
        tts = gTTS(text=text, lang='fr')
        tts.save(output_path)
        print(f"Fichier audio généré : {output_path}")
    except Exception as e:
        print(f"Erreur lors de la génération de l'audio : {e}")

def create_groups_dir(feed, choice_dir, reverse_order=False, clean_strings=False, generate_audio=False):
    episodes = feed.entries
    if reverse_order:
        episodes = episodes[::-1]
    total_episodes = len(episodes)

    if total_episodes > 26:
        groups = [episodes[i:i + 8] for i in range(0, total_episodes, 8)]
    else:
        groups = [episodes]
    
    is_single_group = len(groups) == 1

    for group_index, group in enumerate(groups):
        if is_single_group:
            group_dir = choice_dir
        else:
            group_dir = os.path.join(choice_dir, str(group_index))
            os.makedirs(group_dir, exist_ok=True)
        
            title_text = f"Partie, {nombre_en_lettres(group_index + 1)}"
            if clean_strings:
                title_text = clean_string(title_text)

            if generate_audio:
                generate_audio_file(title_text, os.path.join(group_dir, 'title.mp3'))
            else:
                with open(os.path.join(group_dir, 'title.txt'), 'w', encoding='utf-8') as f:
                    f.write(title_text)
        
            episode_titles = "\n".join([traduire(ep.title) for ep in group])
            if clean_strings:
                episode_titles = clean_string(episode_titles)

            create_text_image(os.path.join(group_dir, 'title.png'), episode_titles, font_path="Pacifico-Regular.ttf", color_index=group_index)
        
        for episode_index, entry in enumerate(group):
            mp3_url = next((link.href for link in entry.links if link.type == 'audio/mpeg'), None)
            if not mp3_url:
                continue
            
            episode_subdir = os.path.join(group_dir, str(episode_index))
            os.makedirs(episode_subdir, exist_ok=True)
            
            title_text = traduire(entry.title)
            if clean_strings:
                title_text = clean_string(title_text)

            if generate_audio:
                generate_audio_file(title_text, os.path.join(episode_subdir, 'title.mp3'))
            else:
                with open(os.path.join(episode_subdir, 'title.txt'), 'w', encoding='utf-8') as f:
                    f.write(title_text)
            
            mp3_path = os.path.join(episode_subdir, 'story.mp3')
            download_file(mp3_url, mp3_path)

            local_file_name = "".join(x for x in entry.title if x.isalnum() or x in (" ", "_")).rstrip()
            local_file_path = f'images/{local_file_name}.jpg'

            if os.path.isfile(local_file_path):
                shutil.copy(local_file_name, os.path.join(episode_subdir, 'title.png'))
            else:
                episode_image_url = entry.get('image', {}).get('href')
                if episode_image_url:
                    episode_image_path = os.path.join(episode_subdir, 'title.png')
                    download_file(episode_image_url, episode_image_path)
                    resize_image(episode_image_path, episode_image_path)

def create_choice_dir(feed, main_dir, cover_image_path, reverse_order=False, clean_strings=False, generate_audio=False):
    choice_dir = os.path.join(main_dir, '0')
    os.makedirs(choice_dir, exist_ok=True)
    title_text = "Quelle épisode veux-tu écouter ?"

    if generate_audio:
        generate_audio_file(title_text, os.path.join(choice_dir, 'choice.mp3'))
    else:
        with open(os.path.join(choice_dir, 'title.txt'), 'w', encoding='utf-8') as f:
            f.write(title_text)
    
    shutil.copy(cover_image_path, os.path.join(choice_dir, 'title.png'))
    
    create_groups_dir(feed, choice_dir, reverse_order, clean_strings, generate_audio)

def download_podcast(rss_url, reverse_order=False, clean_strings=False, generate_audio=False):
    feed = feedparser.parse(rss_url)
    podcast_title = feed.feed.title
    podcast_image_url = feed.feed.image.href if 'image' in feed.feed else None
    main_dir = clean_filename(podcast_title)
    
    if os.path.exists(main_dir):
        shutil.rmtree(main_dir)
    
    os.makedirs(main_dir)

    main_title_text = podcast_title
    if clean_strings:
        main_title_text = clean_string(main_title_text)

    if generate_audio:
        generate_audio_file(main_title_text, os.path.join(main_dir, 'main-title.mp3'))
    else:
        main_title_path = os.path.join(main_dir, 'main-title.txt')
        with open(main_title_path, 'w', encoding='utf-8') as f:
            f.write(main_title_text)
    
    main_image_path = os.path.join(main_dir, 'main-title.png')
    cover_image_path = os.path.join(main_dir, 'cover.png')
    if podcast_image_url:
        download_file(podcast_image_url, main_image_path)
        resize_image(main_image_path, main_image_path)
        resize_image(main_image_path, cover_image_path)
    
    create_choice_dir(feed, main_dir, cover_image_path, reverse_order, clean_strings, generate_audio)

    zip_path = f"{main_dir}.zip"
    zip_folder(main_dir, zip_path)

    try:
        shutil.rmtree(main_dir)
        print(f"Dossier supprimé après zippage : {main_dir}")
    except Exception as e:
        print(f"Erreur lors de la suppression du dossier : {e}")

# Récupérer l'URL du podcast depuis la ligne de commande
if len(sys.argv) < 2:
    print("Usage: python my-telmi-podcast.py <RSS_URL> [options]")
    sys.exit(1)

rss_url = sys.argv[1]
reverse_order = 'reverse_order' in sys.argv
clean_strings = 'clean_strings' in sys.argv
generate_audio = 'generate_audio' in sys.argv

download_podcast(rss_url, reverse_order, clean_strings, generate_audio)

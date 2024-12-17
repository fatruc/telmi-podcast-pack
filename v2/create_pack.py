
import csv
import os
from collections import defaultdict
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS  # Importer gTTS pour la synthèse vocale
import textwrap

screen_size = (640, 480)
cover_size = (480, 480)
font_path="Pacifico-Regular.ttf"
pastel_colors = [
    (255, 255, 204), (255, 204, 153), (255, 204, 204),
    (255, 153, 204), (255, 204, 255), (204, 153, 255),
    (204, 204, 255), (153, 204, 255), (204, 255, 255),
    (153, 255, 204), (204, 255, 204), (204, 255, 153),
]

def find_first_available_integer(directory):
    """
    Parcourt les noms des dossiers dans le répertoire donné, 
    et retourne le premier entier disponible en partant de 0.

    :param directory: Chemin du répertoire à analyser
    :return: Le premier entier disponible
    """
    try:
        # Récupérer les noms des dossiers dans le répertoire
        folder_names = [
            int(name) for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name)) and name.isdigit()
        ]
        
        # Trier les entiers pour identifier les lacunes
        folder_names.sort()
        
        # Trouver le premier entier manquant
        expected = 0
        for folder in folder_names:
            if folder != expected:
                return expected
            expected += 1
        
        # Si aucun entier n'est manquant, le prochain disponible est celui après le dernier
        return f"{expected}"
    except Exception as e:
        raise RuntimeError(f"Une erreur est survenue : {e}")

def read_txt_file(file_path):
 
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            return " ".join(line.strip() for line in file)  # Supprime les espaces inutiles

    except FileNotFoundError:
        print(f"Le fichier '{file_path}' n'existe pas.")

def generate_audio_file(text, output_path):
    print(f"Génération de l'audio pour : {text}")
    try:
        tts = gTTS(text=text, lang='fr')
        tts.save(output_path)
        print(f"Fichier audio généré : {output_path}")
    except Exception as e:
        print(f"Erreur lors de la génération de l'audio : {e}")

def resize_image(input_path, output_path, size, text=None):
    global font_path
    with Image.open(input_path) as img:
        # Calcul du ratio de l'image et du cadre cible
        img_ratio = img.width / img.height
        target_ratio = size[0] / size[1]

        # Redimensionner pour s'adapter au cadre cible tout en respectant les proportions
        if img_ratio > target_ratio:
            # L'image est plus large que le cadre cible : ajuster en largeur
            new_width = size[0]
            new_height = int(size[0] / img_ratio)
        else:
            # L'image est plus haute que le cadre cible : ajuster en hauteur
            new_height = size[1]
            new_width = int(size[1] * img_ratio)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Créer un fond noir pour le cadre cible
        background = Image.new("RGB", size, (0, 0, 0))

        # Centrer l'image dans le fond
        x_offset = (size[0] - new_width) // 2
        y_offset = (size[1] - new_height) // 2
        background.paste(img, (x_offset, y_offset))
    
        if text is not None:
            draw = ImageDraw.Draw(background)
            font = ImageFont.truetype(font_path, 36)

            # Calculer la taille du texte
            wrapped_text = textwrap.fill(text, width=45)  # Ajustez la largeur selon vos besoins
            bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            padding = 10
            box_width = 640
            box_height = text_height + padding * 2

            # Créer un cadre semi-transparent
            transparency = 200
            box = Image.new("RGBA", (box_width, box_height), (255, 255, 255, transparency))
            draw_box = ImageDraw.Draw(box)
            draw_box.rectangle([0, 0, box_width, box_height], fill=(255, 255, 255, transparency))
          

            # Ajouter le cadre à l'image
            box_x = size[0] // 2 - box_width // 2
            box_y = size[1] - box_height - 20
            background.paste(box, (box_x, box_y), box)

            # Ajouter le texte centré dans le cadre
            text_x = size[0] // 2 - text_width // 2
            text_y = box_y
            draw.text((text_x, text_y), wrapped_text, fill="black", font=font)

        background.save(output_path)



def create_group_image(output_path, text, group_number):
    global pastel_colors
    global screen_size
    global font_path

    try:
        background_color = pastel_colors[group_number % len(pastel_colors)]
        img = Image.new("RGB", screen_size, background_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, size=26)

        margin = 19
        max_width = 640  # Largeur maximale en pixels pour une ligne de texte
        available_height = screen_size[1] - 2 * margin
        line_height = 36

        # Fonction pour ajuster le texte en fonction de la largeur maximale
        def wrap_text(text, max_width, font):
            wrapped_lines = []
            words = text.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] > (max_width - 2 * margin):  # Vérifie si la largeur dépasse max_width
                    wrapped_lines.append(line)
                    line = word  # Démarre une nouvelle ligne avec le mot actuel
                else:
                    line = test_line
            if line:  # Ajoute la dernière ligne si elle existe
                wrapped_lines.append(line)
            return wrapped_lines

        # Découpe le texte pour qu'il tienne dans la largeur spécifiée
        text_lines = []
        for line in text.split('\n'):
            text_lines.extend(wrap_text(line, max_width, font))

        # Calcule la hauteur totale et ajuste la taille de la police si nécessaire
        total_text_height = line_height * len(text_lines)
        if total_text_height > available_height:
            font_size = int(font.size * available_height / total_text_height)
            font = ImageFont.truetype(font_path, font_size)
            line_height = font_size
            total_text_height = line_height * len(text_lines)

        # Calcule l'espacement vertical entre les lignes
        spacing = (available_height - total_text_height) / (len(text_lines) + 1)
        y_offset = margin

        # Dessine le texte sur l'image
        for line in text_lines:
            draw.text((margin, y_offset), line, font=font, fill="black")
            y_offset += line_height + spacing

        # Sauvegarde l'image générée
        img.save(output_path)

    except Exception as e:
        print(f"Erreur lors de la création de l'image : {e}")

def create_pack(pack_title):
    global cover_size
    global screen_size

    base_dir = os.path.join(os.getcwd(), f"output/{pack_title}")
    csv_path = os.path.join(base_dir, f"{pack_title}.csv")
    pack_path = os.path.join(base_dir, pack_title)
    pack_image_path = os.path.join(base_dir, "podcast.jpg")
    
    if os.path.exists(pack_path):
        shutil.rmtree(pack_path)
    os.makedirs(pack_path)
    
    resize_image(pack_image_path, os.path.join(pack_path, "cover.jpg"), cover_size)
    resize_image(pack_image_path, os.path.join(pack_path, "main-title.jpg"), screen_size)
    
    generate_audio_file(read_txt_file(os.path.join(base_dir, "podcast.txt")), os.path.join(pack_path, "main-title.mp3"))
    
    choice_dir =  os.path.join(pack_path, find_first_available_integer(pack_path))
    os.makedirs(choice_dir)
    resize_image(pack_image_path, os.path.join(choice_dir, "title.jpg"), screen_size)
    generate_audio_file("Que veux tu écouter ?", os.path.join(choice_dir, "title.mp3"))
    
    # Dictionnaire pour regrouper les lignes par numéro de groupe
    groupes = defaultdict(list)

    with open(csv_path, mode='r', newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        
        # Ignorer les en-têtes
        next(reader, None)

        for row in reader:
            if len(row) < 5:  # S'assurer que la ligne a au moins 5 colonnes
                continue

            try:
                # Extraction des numéros de groupe (colonne 4) et d'épisode (colonne 5)
                numero_groupe = int(row[3])  # Index 3 pour la colonne 4
                numero_episode = int(row[4])  # Index 4 pour la colonne 5
            except ValueError:
                continue  # Ignorer les lignes avec des valeurs non valides

            # Ajouter la ligne au groupe correspondant
            groupes[numero_groupe].append((numero_episode, row))

    group_folders = {}

    # Trier les groupes par numéro de groupe croissant
    for numero_groupe in sorted(groupes.keys()):
        # Trier les épisodes au sein du groupe par numéro d'épisode croissant
        episodes_tries = sorted(groupes[numero_groupe], key=lambda x: x[0])
        
        if not numero_groupe in group_folders:
            group_folders[numero_groupe] = find_first_available_integer(choice_dir)
        
        
        #print(f"Groupe {numero_groupe}:")
        
       
        for _, ligne in episodes_tries:
        
            no_group = not ligne[2].strip()
            groupe_path = choice_dir if no_group else os.path.join(choice_dir, f"{group_folders[numero_groupe]}")
            
            if not no_group:
                if not os.path.exists(groupe_path):
                    os.makedirs(groupe_path)
                    generate_audio_file(ligne[2], os.path.join(groupe_path, "title.mp3"))
                    group_image_path = os.path.join(groupe_path, "title.png")
                    if os.path.exists(os.path.join(base_dir,f"images/groupes/{numero_groupe}.jpg")):
                        resize_image(os.path.join(base_dir,f"images/groupes/{numero_groupe}.jpg"), group_image_path, screen_size, ligne[2])
                    else:
                        texte = "- " + "\n- ".join([ligne[1] for _, ligne in episodes_tries])
                        create_group_image(group_image_path, texte, numero_groupe)
            
            episode_path =  os.path.join(groupe_path, f"{find_first_available_integer(groupe_path)}")
            os.makedirs(episode_path)
            resize_image(os.path.join(base_dir,f"images/episodes/{ligne[0]}.jpg"), os.path.join(episode_path, "title.png"), screen_size, ligne[1])
            generate_audio_file(ligne[1], os.path.join(episode_path, "title.mp3"))
            shutil.copy(os.path.join(base_dir,f"audios/{ligne[0]}.mp3"), os.path.join(episode_path, "story.mp3"))
            
            

            #print(f"  - Episode {ligne[4]}: {ligne}")
            

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <rss_feed_url>")
        sys.exit(1)

    pack_title = sys.argv[1]
    create_pack(pack_title)
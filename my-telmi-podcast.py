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
import textwrap

class PodcastDownloader:
    # Variables de classe
    rss_url = None
    reverse_order = False
    clean_strings = False
    generate_audio = False
    disable_grouping = False
    add_episode_title = False
    csv_only = False
    font_path="Pacifico-Regular.ttf"

    screen_size = (640, 480)
    cover_size = (480, 480)
    pastel_colors = [
        (255, 255, 204), (255, 204, 153), (255, 204, 204),
        (255, 153, 204), (255, 204, 255), (204, 153, 255),
        (204, 204, 255), (153, 204, 255), (204, 255, 255),
        (153, 255, 204), (204, 255, 204), (204, 255, 153),
    ]

    main_dir = None
    mapping_cache = None
    
    @classmethod
    def charger_mapping(self):
        chemin_fichier = f"{self.main_dir}.csv"
        
        if self.mapping_cache is None:
            try:
                with open(chemin_fichier, mode="r", encoding="utf-8-sig") as fichier_csv:
                    dialect = csv.Sniffer().sniff(fichier_csv.read(1024))
                    fichier_csv.seek(0)
                    lecteur = csv.reader(fichier_csv, delimiter=dialect.delimiter)
                    self.mapping_cache = {ligne[0]: ligne[1] for ligne in lecteur if len(ligne) >= 2}
            except FileNotFoundError:
                self.mapping_cache = {}
            except Exception as e:
                print(f"Erreur lors du chargement du fichier : {e}")
                self.mapping_cache = {}

    @classmethod
    def traduire(self, chaine):
    
        chemin_fichier = f"{self.main_dir}.csv"
        title = self.clean_string(chaine)
        safe_title = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
            
        if self.mapping_cache is None:
            self.charger_mapping()
        
        # Vérifier si la chaîne est dans le mapping
        if safe_title in self.mapping_cache:
            return self.mapping_cache[safe_title]
        
        # Si la chaîne n'est pas trouvée, l'ajouter au fichier CSV et au cache
        try:
            with open(chemin_fichier, mode="a", encoding="utf-8-sig", newline='') as fichier_csv:
                writer = csv.writer(fichier_csv, delimiter=';')
                writer.writerow([safe_title, title])  # Ajouter la chaîne dans les deux colonnes
                
                # Ajouter au self.mapping_cache
                self.mapping_cache[safe_title] = title
        except Exception as e:
            print(f"Erreur lors de l'ajout au fichier CSV : {e}")
        
        return title  # Retourner la chaîne d'origine si elle n'est pas trouvée

    @staticmethod
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
            return f"{centaine_txt} {self.nombre_en_lettres(reste)}"
        
        if n >= 17:
            dizaine_index, unite_index = divmod(n, 10)
            dizaine_txt = dizaine[dizaine_index]
            if unite_index == 1 and (dizaine_index not in {8, 7}):
                return f"{dizaine_txt} et {unite[unite_index]}"
            elif dizaine_index == 8:
                dizaine_txt += "s" if unite_index == 0 else ""
            return f"{dizaine_txt} {unite[unite_index]}".strip()
        
        return unite[n]

    @classmethod
    def zip_folder(self):
        try:
            zip_path = f"{self.main_dir}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.main_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.main_dir)
                        zipf.write(file_path, arcname)
            print(f"Dossier zippé avec succès : {zip_path}")
        except Exception as e:
            print(f"Erreur lors de la création du fichier zip : {e}")
    
        
    @staticmethod
    def clean_filename(title):
        nfkd_form = unicodedata.normalize('NFKD', title)
        ascii_title = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
        cleaned_title = re.sub(r'[<>:"/\\|?*]', '-', ascii_title)
        cleaned_title = re.sub(r'[^a-zA-Z0-9\-]', '-', cleaned_title)
        cleaned_title = cleaned_title.lower()
        cleaned_title = re.sub(r'-+$', '', cleaned_title)
        return cleaned_title
    @staticmethod
    def clean_string(s):
        # Remplacer X/Y par X sur Y
        s = re.sub(r'(\d+)/(\d+)', r'\1 sur \2', s)
        # Conserver les caractères alphanumériques, les espaces, les accents, les tirets et les virgules
        return re.sub(r'[^a-zA-Z0-9\sÀ-ÿ,\'-]', '', s)

    @classmethod
    def download_file(self, url, filename):
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



    @classmethod
    def resize_image(self, input_path, output_path, size, text):
        try:
            with Image.open(input_path) as img:
                target_height = size[1]
                img_ratio = img.width / img.height
                new_width = int(img_ratio * target_height)
                img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                background = Image.new("RGB", size, (0, 0, 0))
                x_offset = (size[0] - new_width) // 2
                background.paste(img, (x_offset, 0))
                if text is not None:
                    draw = ImageDraw.Draw(background)
                    font = ImageFont.truetype(self.font_path, 36)

                    # Calculer la taille du texte
                    wrapped_text = textwrap.fill(text, width=30)  # Ajustez la largeur selon vos besoins
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
        except Exception as e:
            print(f"Erreur lors du redimensionnement de l'image : {e}")


    @classmethod
    def create_text_image(self, output_path, text, color_index=0):

        try:
            background_color = self.pastel_colors[color_index % len(self.pastel_colors)]
            img = Image.new("RGB", self.screen_size, background_color)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(self.font_path, size=26)

            margin = 19
            max_width = 640  # Largeur maximale en pixels pour une ligne de texte
            available_height = self.screen_size[1] - 2 * margin
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
                font = ImageFont.truetype(self.font_path, font_size)
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

    @classmethod
    def generate_audio_file(self, text, output_path):
        print(f"Génération de l'audio pour : {text}")
        try:
            tts = gTTS(text=text, lang='fr')
            tts.save(output_path)
            print(f"Fichier audio généré : {output_path}")
        except Exception as e:
            print(f"Erreur lors de la génération de l'audio : {e}")

    @classmethod
    def create_groups_dir(self, feed, choice_dir):
        episodes = feed.entries
        if self.reverse_order:
            episodes = episodes[::-1]
        total_episodes = len(episodes)

        if not self.disable_grouping and total_episodes > 26:
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
            
                title_text = f"Partie, {self.nombre_en_lettres(group_index + 1)}"
                if self.clean_strings:
                    title_text = self.clean_string(title_text)

                if not self.csv_only:
                    if self.generate_audio:
                        self.generate_audio_file(title_text, os.path.join(group_dir, 'title.mp3'))
                    else:
                        with open(os.path.join(group_dir, 'title.txt'), 'w', encoding='utf-8') as f:
                            f.write(title_text)
            
                episode_titles = "\n- ".join([self.traduire(ep.title) for ep in group])
                episode_titles = f"- {episode_titles}"

                if self.clean_strings:
                    episode_titles = self.clean_string(episode_titles)

                self.create_text_image(os.path.join(group_dir, 'title.png'), episode_titles, color_index=group_index)
            
            for episode_index, entry in enumerate(group):
                mp3_url = next((link.href for link in entry.links if link.type == 'audio/mpeg'), None)
                if not mp3_url:
                    continue
                
                episode_subdir = os.path.join(group_dir, str(episode_index))
                os.makedirs(episode_subdir, exist_ok=True)
                
                title_text = self.traduire(entry.title)
                if self.clean_strings:
                    title_text = self.clean_string(title_text)
                
                if not self.csv_only:
                    if self.generate_audio:
                        self.generate_audio_file(title_text, os.path.join(episode_subdir, 'title.mp3'))
                    else:
                        with open(os.path.join(episode_subdir, 'title.txt'), 'w', encoding='utf-8') as f:
                            f.write(title_text)
                
                mp3_path = os.path.join(episode_subdir, 'story.mp3')
                if not self.csv_only:
                    self.download_file(mp3_url, mp3_path)

                local_file_name = "".join(x for x in entry.title if x.isalnum() or x in (" ", "_")).rstrip()
                local_file_path = f'images/{local_file_name}.jpg'

                if os.path.isfile(local_file_path):
                    target_path = os.path.join(episode_subdir, 'title.png')
                    shutil.copy(local_file_path, target_path)
                    self.resize_image(target_path, target_path, self.screen_size, title_text if self.add_episode_title else None)
                else:
                    episode_image_url = entry.get('image', {}).get('href')
                    if episode_image_url:
                        episode_image_path = os.path.join(episode_subdir, 'title.png')
                        self.download_file(episode_image_url, episode_image_path)
                        self.resize_image(episode_image_path, episode_image_path, self.screen_size, title_text if self.add_episode_title else None)

    @classmethod
    def create_choice_dir(self, feed, title_image_path):
        choice_dir = os.path.join(self.main_dir, '0')
        os.makedirs(choice_dir, exist_ok=True)
        title_text = "Quelle épisode veux-tu écouter ?"

        if not self.csv_only:
            if self.generate_audio:
                self.generate_audio_file(title_text, os.path.join(choice_dir, 'choice.mp3'))
            else:
                with open(os.path.join(choice_dir, 'title.txt'), 'w', encoding='utf-8') as f:
                    f.write(title_text)
        
            shutil.copy(title_image_path, os.path.join(choice_dir, 'title.png'))
        
        self.create_groups_dir(feed, choice_dir)

    @classmethod
    def download_podcast(self):

        feed = feedparser.parse(self.rss_url)
        podcast_title = feed.feed.title
        podcast_image_url = feed.feed.image.href if 'image' in feed.feed else None
        self.main_dir = self.clean_filename(podcast_title)
        
        if os.path.exists(self.main_dir):
            shutil.rmtree(self.main_dir)
        
        os.makedirs(self.main_dir)

        main_title_text = podcast_title
        if self.clean_strings:
            main_title_text = self.clean_string(main_title_text)


        main_image_path = os.path.join(self.main_dir, 'main-title.png')
        cover_image_path = os.path.join(self.main_dir, 'cover.png')
        
        if not self.csv_only:
            if self.generate_audio:
                self.generate_audio_file(main_title_text, os.path.join(self.main_dir, 'main-title.mp3'))
            else:
                main_title_path = os.path.join(self.main_dir, 'main-title.txt')
                with open(main_title_path, 'w', encoding='utf-8') as f:
                    f.write(main_title_text)

            if podcast_image_url:
                self.download_file(podcast_image_url, main_image_path)
                self.resize_image(main_image_path, main_image_path, self.screen_size, None)
                self.resize_image(main_image_path, cover_image_path, self.cover_size, None)
        
        self.create_choice_dir(feed, main_image_path)

        self.zip_folder()

        try:
            shutil.rmtree(self.main_dir)
            print(f"Dossier supprimé après zippage : {self.main_dir}")
        except Exception as e:
            print(f"Erreur lors de la suppression du dossier : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python podcast_downloader.py <RSS_URL> [options]")
        sys.exit(1)

    PodcastDownloader.rss_url = sys.argv[1]
    PodcastDownloader.reverse_order = 'reverse_order' in sys.argv
    PodcastDownloader.clean_strings = 'clean_strings' in sys.argv
    PodcastDownloader.generate_audio = 'generate_audio' in sys.argv
    PodcastDownloader.disable_grouping = 'disable_grouping' in sys.argv
    PodcastDownloader.add_episode_title = 'add_episode_title' in sys.argv
    PodcastDownloader.csv_only = 'csv_only' in sys.argv
    PodcastDownloader.download_podcast()

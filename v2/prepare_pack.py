import os   
import csv
import requests
import feedparser
import sys
import re
import shutil

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name)
    """Remplace les caractères interdits dans les noms de fichiers et dossiers par un '-'"""
    """return re.sub(r'[<>:"/\\|?*]', '-', name)"""
    
def download_image(url, save_path):
    """Télécharge une image depuis une URL et la sauvegarde à l'emplacement donné."""
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

def valeurs_dernier_groupe_et_episode(csv_path):

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Le fichier {csv_path} n'existe pas.")

    max_groupe = 0  # Maximum dans la colonne 3
    max_episode = 1  # Maximum dans la colonne 5 pour max_groupe

    with open(csv_path, mode='r', newline='', encoding='utf-8-sig') as csv_file:
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')
        
        # Ignorer les en-têtes
        next(reader, None)  

        for row in reader:
            print(f"row= {row}")
            if len(row) < 5:  # S'assurer que la ligne a au moins 5 colonnes
                continue

            # Extraire les valeurs de la colonne 3 et 5
            try:
                groupe = int(row[3])  # Index 2 pour la colonne 3
                episode = int(row[4])  # Index 4 pour la colonne 5
                print(f"groupe= {groupe}, episode={episode}")
            except ValueError:
                continue  # Ignorer les lignes avec des valeurs non entières

            # Trouver la valeur maximale dans la colonne 3
            if groupe > max_groupe:
                max_groupe = groupe
                max_episode = episode  # Réinitialiser max_episode pour ce max_groupe
            elif groupe == max_groupe:
                # Si égalité, mettre à jour max_episode
                if episode > max_episode:
                    max_episode = episode

    if max_episode == 8:
        return max_groupe + 1, 1

    return max_groupe, max_episode

def process_rss_feed(rss_url):
    """Traite un flux RSS et génère un fichier CSV avec les informations demandées."""
    # Analyse du flux RSS
    feed = feedparser.parse(rss_url)
    podcast_title = sanitize_filename(feed.feed.title)

    # Création des répertoires
    base_dir = os.path.join(os.getcwd(), f"output/{podcast_title}")
    episodes_dir = os.path.join(base_dir, "images/episodes")
    groups_dir = os.path.join(base_dir, "images/groupes")
    audios_dir = os.path.join(base_dir, "audios")
    os.makedirs(episodes_dir, exist_ok=True)
    os.makedirs(groups_dir, exist_ok=True)
    os.makedirs(audios_dir, exist_ok=True)

    podcast_image_path = os.path.join(base_dir, "podcast.jpg")
    if not os.path.exists(podcast_image_path):
        podcast_image_url = feed.feed.image.href if 'image' in feed.feed else None
        download_image(podcast_image_url,podcast_image_path)
    
    podcat_title_path = os.path.join(base_dir, "podcast.txt")
    if not os.path.exists(podcat_title_path):
        with open(podcat_title_path, mode='w', encoding='utf-8') as file:
            file.write(feed.feed.title)

    # Fonction pour vérifier si une valeur existe déjà dans la première colonne
    def ligne_existe_deja(valeur):
        csv_path = os.path.join(base_dir, f"{podcast_title}.csv")
        if not os.path.isfile(csv_path):  # Si le fichier n'existe pas encore
            return False
        with open(csv_path, mode='r', newline='', encoding='utf-8-sig') as csv_file:
            reader = csv.reader(csv_file, delimiter=';', quotechar='"')
            for row in reader:
                if row and row[0] == valeur:  # Vérifie si la première colonne contient la valeur
                    return True
        return False

    # Création du fichier CSV
    csv_path = os.path.join(base_dir, f"{podcast_title}.csv")
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode='a', newline='', encoding='utf-8-sig') as csv_file:  # Compatible avec Excel
        writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        reader = csv.reader(csv_file, delimiter=';', quotechar='"')

        # Écriture des en-têtes uniquement si le fichier est vide
        if not file_exists or os.stat(csv_path).st_size == 0:
            writer.writerow(["Nom de fichier", "Nom de l'épisode","Nom du groupe", "Numéro Groupe", "Numéro de l'épisode"])


        # Initialisation des groupes et des compteurs
        group_number, episode_number = valeurs_dernier_groupe_et_episode(csv_path)
        
        print(f"dernier groupe: {group_number}, dernier épisode: {episode_number}")
        
        group_image_path = os.path.join(groups_dir, f"{group_number}.jpg")

        # Parcours des épisodes du flux RSS
        for index, entry in enumerate(feed.entries):
            safe_title = sanitize_filename(entry.title)
            print(f"Processing episode: {entry.title}")
            
            episode_image_path = os.path.join(episodes_dir,f"{safe_title}.jpg")
            
            # gestion de l'image de l'épisode
            if not os.path.exists(episode_image_path):
            
                scrapped_file_path = os.path.join("output/images", f"{safe_title}.jpg")
                
                print(f"... search scrapped image {scrapped_file_path}")
                if os.path.exists(scrapped_file_path):
                    print(f"... scrapped image found")
                    shutil.copy(scrapped_file_path, episode_image_path)
                else:
                    print(f"... not found => download image from rss feed")
                    episode_image_url = entry.image.get('href') if 'image' in entry else None
                    print(f"... url: {episode_image_url}")
                    if episode_image_url:
                        download_image(episode_image_url, episode_image_path)

            # gestion de l'audio de l'épisode
            episode_audio_path = os.path.join(audios_dir,f"{safe_title}.mp3")
            
            if not os.path.exists(episode_audio_path):
                mp3_url = next((link.href for link in entry.links if link.type == 'audio/mpeg'), None)
                if mp3_url:
                    download_image(mp3_url, episode_audio_path)

            #gestion du csv
            
            if not ligne_existe_deja(safe_title):
                # Changement de groupe tous les 8 épisodes
                if (index % 8 == 0) and index != 0:
                    group_number += 1
                    episode_number = 1
                    group_image_path = os.path.join(groups_dir, f"{group_number}.jpg")
    
                    if not os.path.exists(group_image_path):

                        # Téléchargement de l'image du groupe (facultatif, ici exemple statique)
                        group_image_url = feed.feed.image.get('href') if 'image' in feed.feed else None
                        if group_image_url:
                            download_image(group_image_url, group_image_path)

                # Ajout de la ligne au fichier CSV
                writer.writerow([
                    safe_title,
                    entry.title,
                    f"Partie {group_number+1}",
                    group_number,
                    episode_number
                ])

                episode_number += 1

    print(f"Traitement terminé. Les données sont sauvegardées dans {csv_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <rss_feed_url>")
        sys.exit(1)

    rss_feed_url = sys.argv[1]
    process_rss_feed(rss_feed_url)

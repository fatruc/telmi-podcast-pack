import os
import shutil
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PIL import Image
from io import BytesIO

# Chemin du dossier contenant les fichiers MP3
source_folder = os.getcwd()  # Dossier courant, vous pouvez changer cela si besoin

# URL de base pour télécharger les images
image_base_url = "https://static.bayard.io/presse/audio"

# Liste des fichiers MP3 respectant le format spécifié
mp3_files = [f for f in os.listdir(source_folder) if f.endswith('.mp3') and '_' in f]

# Fonction pour positionner une image sur un fond blanc 640x480
def create_canvas_with_image(image_data, output_path, canvas_size=(640, 480)):
    with Image.open(image_data) as img:
        # Ajuster la hauteur tout en conservant les proportions
        aspect_ratio = img.width / img.height
        new_height = canvas_size[1]
        new_width = int(new_height * aspect_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Créer un fond blanc
        canvas = Image.new("RGB", canvas_size, "white")

        # Calculer les coordonnées pour centrer l'image
        x_offset = (canvas_size[0] - new_width) // 2
        y_offset = 0  # Centré uniquement horizontalement
        canvas.paste(img_resized, (x_offset, y_offset))

        # Sauvegarder l'image sur le fond
        canvas.save(output_path, format="PNG")

# Parcourir les fichiers et effectuer les opérations
for index, file_name in enumerate(mp3_files):
    # Extraire le code et le titre
    code, title = file_name.split('_', 1)
    title = title.rsplit('.mp3', 1)[0]

    # Créer un dossier pour ce fichier
    target_folder = os.path.join(source_folder, str(index))
    os.makedirs(target_folder, exist_ok=True)

    # Copier et renommer le fichier MP3 dans le dossier
    source_file_path = os.path.join(source_folder, file_name)
    target_file_path = os.path.join(target_folder, 'story.mp3')
    shutil.copy2(source_file_path, target_file_path)

    # Créer le fichier title.txt avec le titre
    title_file_path = os.path.join(target_folder, 'title.txt')
    with open(title_file_path, 'w', encoding='utf-8') as title_file:
        title_file.write(title)

    # Télécharger l'image depuis l'URL
    image_path = os.path.join(target_folder, 'title.png')
    image_url = f"{image_base_url}/{code}/{code}_Couv.png"

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_data = BytesIO(response.content)  # Charger les données de l'image dans un objet BytesIO
            create_canvas_with_image(image_data, image_path)
        else:
            print(f"Image introuvable à l'URL : {image_url}, utilisez une image par défaut.")
            image_data = default_image_path
            create_canvas_with_image(image_data, image_path)
    except Exception as e:
        print(f"Erreur lors du téléchargement ou du traitement de l'image pour '{file_name}': {e}")
        image_data = default_image_path
        create_canvas_with_image(image_data, image_path)

print("Traitement terminé. Les dossiers ont été créés.")

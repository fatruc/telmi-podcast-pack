import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# Créez le dossier si nécessaire
output_folder = "mpjl"
os.makedirs(output_folder, exist_ok=True)

# Couleur de fond
background_color = (249, 226, 20)  # Code couleur F9E214

# URL de base
base_url = "https://i.hello-merlin.com/insecure/fill/480/480/ce/1/plain/https://static.bayard.io/presse/audio/MPRN0{index}/MPRN0{index}_Couv.png"

# Itération sur les indices
for index in range(1, 261):  # 1 à 260 inclus
    try:
        # Générer l'URL
        url = base_url.format(index=str(index).zfill(3))  # Ajoute les zéros à gauche pour avoir trois chiffres
        print(f"Téléchargement de l'image {index} : {url}")

        # Télécharger l'image
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi

        # Charger l'image
        original_image = Image.open(BytesIO(response.content))

        # Créer une nouvelle image de fond
        background = Image.new("RGB", (640, 480), background_color)

        # Centrer l'image sur le fond
        offset = ((640 - original_image.width) // 2, (480 - original_image.height) // 2)
        background.paste(original_image, offset)

        # Enregistrer l'image finale
        output_path = os.path.join(output_folder, f"{index}.png")
        background.save(output_path)
        print(f"Image {index} enregistrée avec succès à {output_path}")
    
    except Exception as e:
        print(f"Erreur lors du traitement de l'image {index} : {e}")

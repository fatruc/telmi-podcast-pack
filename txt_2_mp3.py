import os
import sys
from gtts import gTTS

def text_to_speech_in_directory(directory):
    if not os.path.isdir(directory):
        print(f"Le chemin spécifié n'est pas un répertoire valide : {directory}")
        return

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                txt_file_path = os.path.join(root, file)
                mp3_file_path = os.path.splitext(txt_file_path)[0] + ".mp3"

                try:
                    with open(txt_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if content.strip():
                        tts = gTTS(content, lang='fr')  # Utiliser le français comme langue par défaut
                        tts.save(mp3_file_path)
                        print(f"Fichier converti : {txt_file_path} -> {mp3_file_path}")
                    else:
                        print(f"Le fichier est vide, ignoré : {txt_file_path}")

                    os.remove(txt_file_path)
                    print(f"Fichier supprimé : {txt_file_path}")
                except Exception as e:
                    print(f"Erreur lors du traitement du fichier {txt_file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : python script.py <dossier>")
    else:
        directory = sys.argv[1]
        text_to_speech_in_directory(directory)

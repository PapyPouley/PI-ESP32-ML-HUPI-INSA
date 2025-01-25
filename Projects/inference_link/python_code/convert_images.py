import os
from PIL import Image

def resize_images_in_folder(input_folder, output_folder, target_size=(240, 240)):
    """
    Redimensionne toutes les images JPEG d'un dossier en 240x240 et les sauvegarde dans un dossier de sortie.

    :param input_folder: Chemin du dossier contenant les images d'entrée.
    :param output_folder: Chemin du dossier où les images converties seront sauvegardées.
    :param target_size: Taille cible des images (largeur, hauteur), par défaut (240, 240).
    """
    # Vérifier si le dossier de sortie existe, sinon le créer
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Parcourir toutes les images du dossier
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                # Ouvrir l'image et la redimensionner
                with Image.open(input_path) as img:
                    img = img.convert("RGB")  # Assure que l'image est en RGB
                    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    img_resized.save(output_path, "JPEG", quality=90)  # Sauvegarde en JPEG avec qualité élevée
                    print(f"Image convertie : {filename} -> {output_path}")
            except Exception as e:
                print(f"Erreur lors du traitement de l'image {filename} : {e}")

# Exemple d'utilisation
input_folder = "hupi"  # Dossier contenant les images d'entrée
output_folder = "hupi_resized"  # Dossier où sauvegarder les images converties
resize_images_in_folder(input_folder, output_folder)

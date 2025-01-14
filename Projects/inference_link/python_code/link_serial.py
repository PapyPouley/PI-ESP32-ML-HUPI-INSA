import numpy as np
import cv2
import matplotlib.pyplot as plt
import serial
import json
import os
import re

original_width = 240
original_height = 240

inference_width = 196
inference_height = 196
offset_width = 0

# Fonction pour envoyer une commande à l'ESP32 et attendre une réponse
def send_command(ser, command, expected_response):
    try:
        ser.write(command.encode())  # Envoyer la commande
        print(f"Commande envoyée : {command}")
        if expected_response=="":
            return True
        response = ser.read(1).decode()  # Lire une réponse d'un octet
        print(f"Réponse reçue : {response}")
        
        return response == expected_response
    except Exception as e:
        print(f"Erreur lors de l'envoi de la commande {command} : {e}")
        return False


# Fonction pour lire une image depuis le port série
def read_image_from_serial(ser):
    try:
        print("En attente de l'image...")
        image_data = b''
        receiving_image = False

        while True:
            chunk = ser.read(1024)  # Lire un bloc de données (1024 octets)
            if not chunk:
                continue

            # Début de l'image
            if b'<start_image>' in chunk:
                receiving_image = True
                image_data = b''  # Réinitialiser les données
                chunk = chunk.split(b'<start_image>')[1]

            # Fin de l'image
            if b'<end_image>' in chunk:
                chunk = chunk.split(b'<end_image>')[0]
                image_data += chunk
                print("Image reçue avec succès.")
                break

            if receiving_image:
                image_data += chunk

        # Décoder l'image JPEG
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Erreur : Impossible de décoder l'image.")
        return image

    except Exception as e:
        print(f"Erreur lors de la lecture de l'image : {e}")
        return None


# Fonction pour lire les boîtes de détection depuis le port série
def read_boxes_from_serial(ser):
    try:
        print("En attente des boîtes...")
        boxes_data = ""
        receiving_boxes = False
        num_boxes = 0

        while True:
            chunk = ser.read(1024).decode("utf-8", errors="ignore")
            if not chunk:
                continue

            print("Données reçues:", chunk)  # Affiche toutes les données reçues

            # Début des boîtes
            if "<start_box>" in chunk:
                receiving_boxes = True
                boxes_data = ""  # Réinitialiser les données
                chunk = chunk.split("<start_box>")[1]  # Enlever le marqueur de début
                print("Début des boîtes détecté.")

            # Fin des boîtes
            if "<end_box>" in chunk:
                chunk = chunk.split("<end_box>")[0]  # Enlever le marqueur de fin
                boxes_data += chunk
                print("Boîtes reçues avec succès.")
                break

            if receiving_boxes:
                boxes_data += chunk

        # Vérification du contenu de boxes_data
        print("Données des boîtes :", boxes_data)
        
        if not boxes_data.strip():
            print("Erreur : Aucune boîte détectée entre <start_box> et <end_box>.")
            return []

        # Traitement des boîtes
        boxes = []
        lines = boxes_data.strip().split("\n")

        # Extraire le nombre de boîtes
        try:
            # Le nombre de boîtes est entre <start_box> et >
            num_boxes_str = re.findall(r'<(\d+)>', lines[0])
            num_boxes = int(num_boxes_str[0])
            print(f"Nombre de boîtes détectées : {num_boxes}")
            if num_boxes == 0:
                print("Aucune boîte à traiter.")
                return []  # Aucune boîte à traiter
        except ValueError:
            print("Erreur lors de la lecture du nombre de boîtes.")
            return []

        # Si le nombre de boîtes est supérieur à 0, on traite les boîtes
        if num_boxes > 0:
            # Extraire les boîtes
            for line in lines[1:]:  # Ignorer la première ligne qui contient le nombre de boîtes
                if "(" in line and "[" in line:
                    try:
                        # Exemple de ligne : "label1 (0.95) [x: 10, y: 20, width: 50, height: 60]"
                        parts = line.split("[")
                        label_and_confidence = parts[0].strip().split("(")
                        label = label_and_confidence[0].strip()
                        confidence = float(label_and_confidence[1].replace(")", "").strip())

                        coords = parts[1].replace("]", "").strip().split(",")
                        x = int(coords[0].split(":")[1].strip())
                        y = int(coords[1].split(":")[1].strip())
                        width = int(coords[2].split(":")[1].strip())
                        height = int(coords[3].split(":")[1].strip())

                        boxes.append({
                            "label": label,
                            "confidence": confidence,
                            "x": x,
                            "y": y,
                            "width": width,
                            "height": height
                        })
                    except Exception as e:
                        print(f"Erreur lors de l'analyse d'une boîte : {e}")

        return boxes

    except Exception as e:
        print(f"Erreur lors de la lecture des boîtes : {e}")
        return 0


# Fonction pour afficher l'image et les boîtes
def display_image_with_boxes(image, boxes):
    # Chemin du dossier pour sauvegarder les résultats
    output_folder = "./images_box"
    os.makedirs(output_folder, exist_ok=True)

    # Générer un nom unique pour les fichiers
    timestamp = str(int(cv2.getTickCount()))  # Utilise un compteur pour des noms uniques
    image_filename = os.path.join(output_folder, f"{timestamp}_image.jpg")
    json_filename = os.path.join(output_folder, f"{timestamp}_boxes.json")
    annotated_image_filename = os.path.join(output_folder, f"{timestamp}_annotated_image.jpg")

    # Sauvegarder l'image brute
    cv2.imwrite(image_filename, image)

    # Sauvegarder les boîtes dans un fichier JSON
    with open(json_filename, "w") as json_file:
        json.dump(boxes, json_file, indent=4)

    # Dessiner les boîtes sur l'image
    annotated_image = image.copy()
    for box in boxes:
        label = box["label"]
        confidence = box["confidence"]
        x = (box["x"] * original_width) // inference_width + offset_width
        y = (box["y"] * original_height) // inference_height
        width = (box["width"] * original_width) // inference_width
        height = (box["height"] * original_height) // inference_height

        print(f"Label: {label}, Confiance: {confidence:.2f}, x: {x}, y: {y}, Largeur: {width}, Hauteur: {height}")

        # Ajouter la boîte sur l'image
        color = (255, 0, 0)  # Rouge
        thickness = 1
        start_point = (x, y)
        end_point = (x + width, y + height)
        annotated_image = cv2.rectangle(annotated_image, start_point, end_point, color, thickness)

        # Ajouter le label et la confiance
        text = f"{confidence:.2f}"
        font_scale = 0.5
        font_color = (0, 255, 0)  # Vert
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_position = (x, y - 10 if y - 10 > 10 else y + 10)
        annotated_image = cv2.putText(annotated_image, text, text_position, font, font_scale, font_color, thickness)

    # Sauvegarder l'image annotée
    cv2.imwrite(annotated_image_filename, annotated_image)

    # Afficher l'image annotée avec Matplotlib
    plt.figure(figsize=(10, 8))
    annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    plt.imshow(annotated_image_rgb)
    plt.axis("off")
    plt.show()

    print(f"Image brute sauvegardée dans : {image_filename}")
    print(f"Boîtes sauvegardées dans : {json_filename}")
    print(f"Image annotée sauvegardée dans : {annotated_image_filename}")


if __name__ == "__main__":
    # Configurer votre port série et vitesse de communication
    serial_port = "/dev/tty.usbmodem1101"  # Remplacez par le port série correct
    baud_rate = 115200

    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)

        # Étape 1 : Envoyer 0 pour démarrer l'inférence
        if not send_command(ser, "0", "1"):
            print("Erreur : L'inférence a échoué ou aucune réponse reçue.")
            ser.close()
            exit()

        # Étape 2 : Envoyer 1 pour recevoir l'image
        if not send_command(ser, "1", ""):
            print("Erreur : Impossible de recevoir l'image.")
            ser.close()
            exit()

        image = read_image_from_serial(ser)
        if image is None:
            print("Erreur : L'image reçue est invalide.")
            ser.close()
            exit()

        # Étape 3 : Envoyer 2 pour recevoir les boîtes
        if not send_command(ser, "2", ""):
            print("Erreur : Impossible de recevoir les boîtes.")
            ser.close()
            exit()

        boxes = read_boxes_from_serial(ser)
        if boxes == 0:
            print("Erreur : Aucune boîte reçue.")
            ser.close()
            exit()

        # Étape 4 : Afficher l'image avec les boîtes
        display_image_with_boxes(image, boxes)

    except Exception as e:
        print(f"Erreur : {e}")

# Description: This script is used to communicate with the ESP board via the serial port.
# It sends commands to the ESP board to start the inference, receive the image and the boxes.
# The image is displayed and saved with the boxes detected.
# Made by: Valentin FAUCHEUX
# Date: 2025-01-20

import numpy as np
import cv2
import matplotlib.pyplot as plt
import serial
import json
import os
import re

# Constants
# Original image size take by the camera
original_width = 240
original_height = 240

# Image size used for the inference
inference_width = 230
inference_height = 230

# Offset width if we need to crop the image
offset_width = 0

# Index of the image infered
index = 0

# Path to store the images
output_folder = "./images_box"

# Function to send a command to the serial port
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


# Function to read an image from the serial port
def read_image_from_serial(ser):
    try:
        print("En attente de l'image...")
        image_data = b''
        receiving_image = False

        while True:
            chunk = ser.read(1024)  # Read 1 KB at a time
            if not chunk:
                continue

            # Detect the start of the image
            if b'<start_image>' in chunk:
                receiving_image = True
                image_data = b''  # Réinitialiser les données
                chunk = chunk.split(b'<start_image>')[1]

            # Detect the end of the image
            if b'<end_image>' in chunk:
                chunk = chunk.split(b'<end_image>')[0]
                image_data += chunk
                print("Image got with success.")
                break

            if receiving_image:
                image_data += chunk

        # Décoder l'image JPEG
        
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Error decoding the image.")
        return image

    except Exception as e:
        print(f"Error during the reading of the image: {e}")
        return None


# Function to read boxes from the serial port
def read_boxes_from_serial(ser):
    try:
        print("Waiting for boxes...")
        boxes_data = ""
        receiving_boxes = False
        num_boxes = 0

        while True:
            chunk = ser.read(2048).decode("utf-8", errors="ignore")
            if not chunk:
                continue

            print("Data recieved", chunk)  # Print the data received

            # Start of the boxes
            if "<start_box>" in chunk:
                receiving_boxes = True
                boxes_data = ""  # Reset the data
                chunk = chunk.split("<start_box>")[1]  # Remove the start marker
                print("Boxes data started.")

            # Detect the end of the boxes
            if "<end_box>" in chunk:
                chunk = chunk.split("<end_box>")[0]  # Remove the end marker
                boxes_data += chunk
                print("Boxes data ended.")
                break

            if receiving_boxes:
                boxes_data += chunk

        # Verify if any box was detected
        print("Data box: ", boxes_data)
        
        if not boxes_data.strip():
            print("Error: No box detected between <start_box> and <end_box>.") 
            return []

        # Extract the boxes
        boxes = []
        lines = boxes_data.strip().split("\n")

        # Extract the number of boxes
        try:
            # Number of boxes is in the first line
            num_boxes_str = re.findall(r'<(\d+)>', lines[0])
            num_boxes = int(num_boxes_str[0])
            print(f"Nombre de boîtes détectées : {num_boxes}")
            if num_boxes == 0:
                print("Aucune boîte à traiter.")
                return [] # No boxes to process
        except ValueError:
            print("Error reading the number of boxes.")
            return []

        # If there are boxes
        if num_boxes > 0:
            # Extract the boxes
            for line in lines[1:]:  # Ignore the first line
                if "(" in line and "[" in line:
                    try:
                        # Line example: "label1 (0.95) [x: 10, y: 20, width: 50, height: 60]"
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


# Function to display an store image with boxes
def display_image_with_boxes(image, boxes):
    os.makedirs(output_folder, exist_ok=True)

    # Generate unique filenames
    image_filename = os.path.join(output_folder, f"image{index}.jpg")
    json_filename = os.path.join(output_folder, f"boxes{index}.json")
    annotated_image_filename = os.path.join(output_folder, f"annotated_image{index}.jpg")

    # Save the image
    cv2.imwrite(image_filename, image)

    # Save the boxes in a JSON file
    with open(json_filename, "w") as json_file:
        json.dump(boxes, json_file, indent=4)

    # Draw the boxes on the image
    ratio = original_width / inference_width
    print(ratio)

    annotated_image = image.copy()
    for box in boxes:
        label = box["label"]
        confidence = box["confidence"]
        x = int(round(box["x"] * ratio + offset_width, 0))
        y = int(round(box["y"] * ratio, 0))
        width = int(round(box["width"] * ratio, 0))
        height = int(round(box["height"] * ratio, 0))

        print(f"Label: {label}, Confiance: {confidence:.2f}, x: {x}, y: {y}, Largeur: {width}, Hauteur: {height}")

        # Add the box to the image
        if confidence<0.8:
            color = (0, 0, 255)  # Red
        elif confidence>=0.8 and confidence<0.9:
            color = (0, 165, 255)  # Orange
        else:
            color = (0, 255, 0) # Green
        thickness = 1
        center_point = (x + (width//2), y + (height//2))
        annotated_image = cv2.circle(annotated_image, center_point, 6, color, thickness)

        # Add the confidence label to the image
        text = f"{confidence:.2f}"
        font_scale = 0.3
        # Display the confidence in different colors
        if confidence<0.8:
            font_color = (0, 0, 255)   # Red
        elif confidence>=0.8 and confidence<0.9:
            font_color = (0, 165, 255)  # Orange
        else:
            font_color = (0, 255, 0) # Green

        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

        # Center the text
        text_x = center_point[0] - (text_size[0] // 2)  
        text_y = center_point[1] + (text_size[1] // 2) - 10  

        text_position = (text_x, text_y) # Position of the text
        if text_x < 0:
            text_x = 0
        if text_y < text_size[1]:
            text_y = center_point[1] + (text_size[1] // 2) + 10
        if text_x + text_size[0] > original_width:
            text_x = original_width - text_size[0]
        if text_y + text_size[1] > original_height:
            text_y = original_height - text_size[1]

        text_position = (text_x, text_y)
        #annotated_image = cv2.putText(annotated_image, text, text_position, font, font_scale, font_color, thickness)

    # Save the annotated image
    cv2.imwrite(annotated_image_filename, annotated_image)

    # Print the annotated image on matplotlib
    #plt.figure(figsize=(10, 8))
    #annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    #plt.imshow(annotated_image_rgb)
    #plt.axis("off")
    #plt.show()

    print(f"Image saved in : {image_filename}")
    print(f"Boxes saved in : {json_filename}")
    print(f"Images with boxes saved in : {annotated_image_filename}")


if __name__ == "__main__":
    # Configure the serial port
    serial_port = "/dev/tty.usbmodem1101"  # Serial port
    baud_rate = 115200 # Baud rate

    # Loop to process the 11 images
    for i in range(1, 12):
        index = i
        try:
            ser = serial.Serial(serial_port, baud_rate, timeout=2)

            # Step 1: Send 0 to start the inference
            if not send_command(ser, "0", "1"):
                print("Erreur : L'inférence a échoué ou aucune réponse reçue.")
                ser.close()
                exit()

            # Step 2: Send 1 to receive the image
            if not send_command(ser, "1", ""):
                print("Erreur : Impossible de recevoir l'image.")
                ser.close()
                exit()

            image = read_image_from_serial(ser)
            if image is None:
                print("Erreur : L'image reçue est invalide.")
                ser.close()
                exit()

            # Step 3: Send 2 to receive the boxes
            if not send_command(ser, "2", ""):
                print("Erreur : Impossible de recevoir les boîtes.")
                ser.close()
                exit()

            boxes = read_boxes_from_serial(ser)
            if boxes == 0:
                print("Erreur : Aucune boîte reçue.")
                ser.close()
                exit()

            # Step 4: Display and save the image with the boxes
            display_image_with_boxes(image, boxes)

        except Exception as e:
            print(f"Erreur : {e}")

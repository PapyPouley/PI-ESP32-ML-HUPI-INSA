# Description: This script counts the number of boxes with confidence >= 0.8 in all JSON files in a folder.
# Made by: Valentin FAUCHEUX
# Date: 2025-01-23

import json
import os

# Path of the main folder containing the JSON files
main_folder_path = "/Users/valentinfaucheux/Documents/EII/5A/S9/PI/PI-ESP32-ML-HUPI-INSA/Projects/Inference_link/python_code/Dataset/EYE"

# Init global counters
global_high_confidence_count = 0
global_total_boxes = 0

# Browse all files in the main folder
for root, dirs, files in os.walk(main_folder_path):
    for file in files:
        # Check if the file is a JSON file
        if file.endswith(".json"):
            file_path = os.path.join(root, file)

            # Load the JSON file
            with open(file_path, "r") as json_file:
                try:
                    data = json.load(json_file)

                    # Init local counters
                    high_confidence_count = 0
                    total_boxes = 0

                    # Compute the number of boxes with confidence > 0.8
                    for box in data:
                        total_boxes += 1
                        if box.get("confidence", 0) >= 0.8:
                            high_confidence_count += 1

                    # Add local counters to global counters
                    global_high_confidence_count += high_confidence_count
                    global_total_boxes += total_boxes

                    # Print the results
                    print(f"Fichier : {file_path}")
                    print(f"  Nombre total de boîtes : {total_boxes}")
                    print(f"  Boîtes avec confiance > 0.8 : {high_confidence_count}\n")

                except json.JSONDecodeError:
                    print(f"Erreur : Impossible de lire le fichier JSON {file_path}\n")

# Print the global results
print("Résultats globaux :")
print(f"Nombre total de boîtes : {global_total_boxes}")
print(f"Boîtes avec confiance > 0.8 : {global_high_confidence_count}")
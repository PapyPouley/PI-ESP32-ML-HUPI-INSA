# Computer Vision on ESP32 _ HUPI INSA RENNES

This project is part of the industrial project at INSA Rennes. Its objective is to integrate computer vision models into an ESP32 microcontroller.

---

### Prerequisites

Using PlatformIO is highly recommended to ensure compatibility and ease of development.

---

## Getting Started

### Project Organization  
The main folder is divided into three parts:  
- **BoardsInfo**: Contains additional information and JSON files required for implementing the ESP32-EYE.  
- **LIB**: Includes all model libraries in `.zip` format and pre-trained `.tflite` files.  
- **Projects**: Subdivided into two distinct projects:  
   - **Inference**: The default program that performs inference using the model, captures data from the camera, and sends results to the serial monitor.  
   - **Inference_link**: A program designed to retrieve and store inference results from the ESP32. Requires the **ESP3-SERIAL** module to be loaded onto the boards.  

---

## Built With

Most of the models were developed using **[EdgeImpulse](https://studio.edgeimpulse.com/)**.  
Relevant models can be found here:  
- [Dataset4-model](https://studio.edgeimpulse.com/public/553109/live)  
- [COCO-model](https://studio.edgeimpulse.com/public/575392/live)  

Development was carried out using the PlatformIO extension for Visual Studio Code. To use ESP32 S3 Eye, it's required to put the file esp32-s3-devkitc1-n8r8.json from https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/blob/main/BoardsInfo/EYE/esp32-s3-devkitc1-n8r8.json or in available in the folder ./boardInfo folder to : Mac/linux ~/.platformio/platforms/espressif32/boards or Win C:\Users\<UserName>\.platformio\platforms\espressif32\boards

---

## Authors  

This project was created by: [Contributors](https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/contributors)  
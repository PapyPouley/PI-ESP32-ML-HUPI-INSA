# Computer Vision on ESP32 _ HUPI INSA RENNES

This project is part of the industrial project at INSA Rennes. Its objective is to integrate object detection models into an ESP32 microcontroller. In order to study this, we have worked on the use case of counting the number of cars in a parking lot.

This repository contains a part of all the models we trained for the project.

---

### Prerequisites

An ESP32 with its associated camera. Models have been tested with 3 differents boards : ESP32-CAM, ESP-S3-EYE and ESP-S3-SENSE.

Using VS code extension [PlatformIO](https://platformio.org/) is highly recommended to ensure compatibility and ease of development.

Using [SenseCraft ToolKit](https://seeed-studio.github.io/SenseCraft-Web-Toolkit/#/setup/process) can be useful for quick deploymenent on ESP-S3-SENSE only from the libraries in .tflite.

---

## Getting Started

### Project Organization  

The main folder is divided into three parts:  
- **BoardsInfo**: Contains additional information and JSON files required for implementing the ESP32-S3-EYE.  
- **LIB**: Includes model libraries in `.zip` format and pre-trained `.tflite` files.
   - Every model is entitled as follow : `size of training images_nb of epochs_learning rate_batch size_base model_dataset`
   - 4 datasets have been used for training all these models, there are different subsets of the [CNR Park dataset](http://cnrpark.it/)
     - DS2 : ~80 images of subjective "high quality"
     - DS4 : ~1000 images without any manual sorting
- **Projects**: Subdivided into two distinct projects:  
   - **Inference**: The default program that performs inference using the model, captures data from the camera, and sends results to the serial monitor.  
   - **Inference_link**: A program designed to retrieve and store inference results from the ESP32. Requires the **ESP3-SERIAL** module to be loaded onto the boards.  

The model with the best performance is : 196x196_80_0.005_32_FOMO 035_DS4. 

Among all these models, some cannot be deployed on an ESP32 : models trained with other base model than FOMO, and some cannot run an inference on the ESP32 (models with image sizes above 230x230 pixels or working with float32).

---

## Built With

Most of the models were developed using **[EdgeImpulse](https://studio.edgeimpulse.com/)**.  
Relevant models can be found here:  
- [Dataset4-model](https://studio.edgeimpulse.com/public/575010/live)
- [COCO-model](https://studio.edgeimpulse.com/public/575392/live)  

Development was carried out using the PlatformIO extension for Visual Studio Code. To use ESP32 S3 EYE, it's required to put the file esp32-s3-devkitc1-n8r8.json from https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/blob/main/BoardsInfo/EYE/esp32-s3-devkitc1-n8r8.json or in available in the folder ./boardInfo folder to : Mac/linux `~/.platformio/platforms/espressif32/boards` or Win `C:\Users\<UserName>\.platformio\platforms\espressif32\boards`

The configuration of both projects (inference and inference_link) is controlled by the file : PI-ESP32-ML-HUPI-INSA/Project/[project]/platformio.ini. This file allows an user to select the board and the model them want to deploy in it. To select a library, modify the library path in the platformio.ini file, line 15 (lib_deps = ...).

---

## Authors  

This project was created by: [Contributors](https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/contributors)  

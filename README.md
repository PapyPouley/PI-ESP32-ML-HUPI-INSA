# Computer Vision on ESP32 _ HUPI INSA RENNES

This project is part of the industrial project of INSA Rennes. Its goal is to integrate computer vision models into an ESP32 microcontroller.

### Prerequisites

Using the PlatformIO is recommended.

## Getting Started

### Project organization
The main folder is separated into three part : 
- BoardsInfo : Further information and json files for implementing ESP 32 EYE
- LIB : Contains all models librairies in .zip and tflite
- Projects : Divided in two projects:
   - Inference : Default program who infere model from camera and send results into the serial monitor
   - Inference_link : Project to get and store the result infered by the ESP. Need to load ESP3-SERIAL on boards.

## Built With

Most of the models were developed using * [EdgeImpulse](https://studio.edgeimpulse.com/).  
Most of the models are from this link :
- [Dataset4](https://studio.edgeimpulse.com/public/553109/live)
- [COCO](https://studio.edgeimpulse.com/public/575392/live)

Additionally, the PlatformIO extension for VSCode was used. To use ESP32 S3 Eye, it's required to put the file esp32-s3-devkitc1-n8r8.json from https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/blob/main/BoardsInfo/EYE/esp32-s3-devkitc1-n8r8.json or in available in the folder ./boardInfo folder to : Mac/linux ~/.platformio/platforms/espressif32/boards or Win C:\Users\<UserName>\.platformio\platforms\espressif32\boards

## Authors

This project was created by: https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/contributors  

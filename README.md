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
Relevant datasets can be found here:  
- [Dataset4](https://studio.edgeimpulse.com/public/553109/live)  
- [COCO](https://studio.edgeimpulse.com/public/575392/live)  

Development was carried out using the PlatformIO extension for Visual Studio Code.

---

## Authors  

This project was created by: [Contributors](https://github.com/PapyPouley/PI-ESP32-ML-HUPI-INSA/contributors)  
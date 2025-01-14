/* Includes ---------------------------------------------------------------- */
#include <Arduino.h>
#include <a1000-frames_inferencing.h>
#include "edge-impulse-sdk/dsp/image/image.hpp"

//#define USED_SD
#ifdef USED_SD
    #include <SD_MMC.h>
#endif

#include "esp_camera.h"

#define CONFIG_ESP32_CAMERA_DEBUG 1
#define THRESHOLD 0.9

//Define default : 
#define PWDN_GPIO_NUM     0
#define RESET_GPIO_NUM    0
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     0
#define SIOC_GPIO_NUM     0

#define Y9_GPIO_NUM       0
#define Y8_GPIO_NUM       0
#define Y7_GPIO_NUM       0
#define Y6_GPIO_NUM       0
#define Y5_GPIO_NUM       0
#define Y4_GPIO_NUM       0
#define Y3_GPIO_NUM       0
#define Y2_GPIO_NUM       0

#define VSYNC_GPIO_NUM    0
#define HREF_GPIO_NUM     0
#define PCLK_GPIO_NUM     0

#ifdef EYE
    #define PWDN_GPIO_NUM    -1
    #define RESET_GPIO_NUM   -1
    #define XCLK_GPIO_NUM    15
    #define SIOD_GPIO_NUM    4
    #define SIOC_GPIO_NUM    5

    #define Y9_GPIO_NUM      16
    #define Y8_GPIO_NUM      17
    #define Y7_GPIO_NUM      18
    #define Y6_GPIO_NUM      12
    #define Y5_GPIO_NUM      10
    #define Y4_GPIO_NUM      8
    #define Y3_GPIO_NUM      9
    #define Y2_GPIO_NUM      11

    #define VSYNC_GPIO_NUM   6
    #define HREF_GPIO_NUM    7
    #define PCLK_GPIO_NUM    13

#elif SENSE
    #define PWDN_GPIO_NUM -1
    #define RESET_GPIO_NUM -1
    #define XCLK_GPIO_NUM 10
    #define SIOD_GPIO_NUM 40
    #define SIOC_GPIO_NUM 39

    #define Y9_GPIO_NUM 48
    #define Y8_GPIO_NUM 11
    #define Y7_GPIO_NUM 12
    #define Y6_GPIO_NUM 14
    #define Y5_GPIO_NUM 16
    #define Y4_GPIO_NUM 18
    #define Y3_GPIO_NUM 17
    #define Y2_GPIO_NUM 15

    #define VSYNC_GPIO_NUM 38
    #define HREF_GPIO_NUM 47
    #define PCLK_GPIO_NUM 13

#elif CAM
    #define PWDN_GPIO_NUM     32
    #define RESET_GPIO_NUM    -1
    #define XCLK_GPIO_NUM      0
    #define SIOD_GPIO_NUM     26
    #define SIOC_GPIO_NUM     27

    #define Y9_GPIO_NUM       35
    #define Y8_GPIO_NUM       34
    #define Y7_GPIO_NUM       39
    #define Y6_GPIO_NUM       36
    #define Y5_GPIO_NUM       21
    #define Y4_GPIO_NUM       19
    #define Y3_GPIO_NUM       18
    #define Y2_GPIO_NUM        5

    #define VSYNC_GPIO_NUM    25
    #define HREF_GPIO_NUM     23
    #define PCLK_GPIO_NUM     22

#endif

/* Constant defines -------------------------------------------------------- */
#define EI_CAMERA_RAW_FRAME_BUFFER_COLS           240
#define EI_CAMERA_RAW_FRAME_BUFFER_ROWS           240
#define EI_CAMERA_FRAME_BYTE_SIZE                 3

/* Private variables ------------------------------------------------------- */
static bool debug_nn = false; // Set this to true to see e.g. features generated from the raw signal
static bool is_initialised = false;
uint8_t *snapshot_buf; //points to the output of the capture

camera_fb_t *fb = nullptr;
ei_impulse_result_t result = { 0 };

static camera_config_t camera_config = {
    .pin_pwdn = PWDN_GPIO_NUM,
    .pin_reset = RESET_GPIO_NUM,
    .pin_xclk = XCLK_GPIO_NUM,
    .pin_sscb_sda = SIOD_GPIO_NUM,
    .pin_sscb_scl = SIOC_GPIO_NUM,

    .pin_d7 = Y9_GPIO_NUM,
    .pin_d6 = Y8_GPIO_NUM,
    .pin_d5 = Y7_GPIO_NUM,
    .pin_d4 = Y6_GPIO_NUM,
    .pin_d3 = Y5_GPIO_NUM,
    .pin_d2 = Y4_GPIO_NUM,
    .pin_d1 = Y3_GPIO_NUM,
    .pin_d0 = Y2_GPIO_NUM,
    .pin_vsync = VSYNC_GPIO_NUM,
    .pin_href = HREF_GPIO_NUM,
    .pin_pclk = PCLK_GPIO_NUM,

    //XCLK 20MHz or 10MHz for OV2640 double FPS (Experimental)
    .xclk_freq_hz = 20000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG, //YUV422,GRAYSCALE,RGB565,JPEG
    .frame_size = FRAMESIZE_240X240,    //QQVGA-UXGA Do not use sizes above QVGA when not JPEG

    .jpeg_quality = 12, //0-63 lower number means higher quality
    .fb_count = 1,       //if more than one, i2s runs in continuous mode. Use only with JPEG
    .fb_location = CAMERA_FB_IN_PSRAM,
    .grab_mode = CAMERA_GRAB_WHEN_EMPTY,
};

/* Function definitions ------------------------------------------------------- */
bool ei_camera_init(void);
void ei_camera_deinit(void);
camera_fb_t * ei_camera_capture(uint32_t img_width, uint32_t img_height, uint8_t *out_buf) ;
static int ei_camera_get_data(size_t offset, size_t length, float *out_ptr);

void sendImage(uint8_t *buf);
void sendBox(ei_impulse_result_t result);
bool runInference();

/**
* @brief      Arduino setup function
*/
void setup()
{
    // put your setup code here, to run once:
    Serial.begin(115200);
    //comment out the below line to start inference immediately after upload
    while (!Serial);
    Serial.println("Edge Impulse Inferencing Demo");
    if (ei_camera_init() == false) {
        ei_printf("Failed to initialize Camera!\r\n");
    }
    else {
        ei_printf("Camera initialized\r\n");
    }

    #ifdef USED_SD
        // Configuration des broches SD
        if (!SD_MMC.setPins(39, 38, 40)) { // CLK = GPIO 39, CMD = GPIO 38, DATA0 = GPIO 40
            Serial.println("Erreur lors de la configuration des broches !");
            return;
        }
        
        // Initialisation de la carte SD en utilisant SD_MMC
        if (!SD_MMC.begin("/sdcard", true)) {
            Serial.println("Erreur d'initialisation de la carte SD !");
            while (1);
        }
        Serial.println("Carte SD initialisée avec succès.");
    #endif

    ei_printf("\nStarting now\n");
}

#ifdef USED_SD
void save_image_and_boxes(uint8_t *buf, ei_impulse_result_t result) {
    // Vérification de la carte SD
    if (!SD_MMC.begin()) {
        Serial.println("Erreur : Carte SD non détectée !");
        return;
    }

    String time = String(millis());
    // Générer un nom de fichier unique pour l'image
    String imageFileName = "/" + time + "_capture.jpg";
    File imageFile = SD_MMC.open(imageFileName.c_str(), FILE_WRITE);
    if (!imageFile) {
        Serial.println("Erreur lors de l'ouverture du fichier pour l'image !");
        return;
    }

    // Sauvegarder l'image capturée (au format JPEG)
    imageFile.write(buf, EI_CLASSIFIER_INPUT_WIDTH * EI_CLASSIFIER_INPUT_HEIGHT * EI_CAMERA_FRAME_BYTE_SIZE);
    imageFile.close();
    Serial.println("Image sauvegardée avec succès sur la carte SD : " + imageFileName);

    File jsonFile = SD_MMC.open("/" + time + "_boxes.json", FILE_WRITE);
    if (!jsonFile) {
        Serial.println("Erreur lors de la création du fichier JSON !");
    } else {
        jsonFile.print("[");
        for (uint32_t i = 0; i < result.bounding_boxes_count; i++) {
            ei_impulse_result_bounding_box_t bb = result.bounding_boxes[i];
            if (bb.value < THRESHOLD) {
                continue;
            }
            jsonFile.printf(
                "{\"label\": \"%s\", \"confidence\": %.2f, \"x\": %u, \"y\": %u, \"width\": %u, \"height\": %u}",
                bb.label, bb.value, bb.x, bb.y, bb.width, bb.height
            );
            if (i < result.bounding_boxes_count - 1) {
                jsonFile.print(",");
            }
        }
        jsonFile.print("]");
        jsonFile.close();
        Serial.println("Données sauvegardées dans boxes.json !");
    }
}
#endif

void serialEvent() {
    char inChar = (char)Serial.read();
    switch (inChar)
    {
    case '0':
        Serial.println(runInference());
        break;
    case '1':
        sendImage(fb->buf);
        break;
    case '2':
        sendBox(result);
        break;
    default:
        Serial.println("Run!");
        break;
    }
}

void sendImage(uint8_t *buf){
    // Ajouter un marqueur de début
    Serial.print("<start_image>");
    
    // Envoyer l'image en binaire
    Serial.write(buf, EI_CAMERA_RAW_FRAME_BUFFER_COLS * EI_CAMERA_RAW_FRAME_BUFFER_ROWS * EI_CAMERA_FRAME_BYTE_SIZE);

    // Ajouter un marqueur de fin
    Serial.print("<end_image>");
    esp_camera_fb_return(fb);
}

void sendBox(ei_impulse_result_t result){
    // Ajouter un marqueur de début
    Serial.print("<start_box>");
    Serial.print("<");
    Serial.print(result.bounding_boxes_count);
    Serial.println(">");

    for (uint32_t i = 0; i < result.bounding_boxes_count; i++) {
        ei_impulse_result_bounding_box_t bb = result.bounding_boxes[i];
        if (bb.value < THRESHOLD) {
            continue;
        }
        Serial.print("  ");
        Serial.print(bb.label);  // Affiche le label
        Serial.print(" (");
        Serial.print(bb.value, 2);  // Affiche la valeur avec 2 décimales
        Serial.print(") [ x: ");
        Serial.print(bb.x);
        Serial.print(", y: ");
        Serial.print(bb.y);
        Serial.print(", width: ");
        Serial.print(bb.width);
        Serial.print(", height: ");
        Serial.print(bb.height);
        Serial.println(" ]");  
    }
    // Ajouter un marqueur de fin
    Serial.print("<end_box>");
}

bool runInference(){
    esp_camera_fb_return(fb);
    snapshot_buf = (uint8_t*)malloc(EI_CAMERA_RAW_FRAME_BUFFER_COLS * EI_CAMERA_RAW_FRAME_BUFFER_ROWS * EI_CAMERA_FRAME_BYTE_SIZE);

    // check if allocation was successful
    if(snapshot_buf == nullptr) {
        ei_printf("ERR: Failed to allocate snapshot buffer!\n");
        return false;
    }

    ei::signal_t signal;
    signal.total_length = EI_CLASSIFIER_INPUT_WIDTH * EI_CLASSIFIER_INPUT_HEIGHT;
    signal.get_data = &ei_camera_get_data;

    if (!(fb = ei_camera_capture((size_t)EI_CLASSIFIER_INPUT_WIDTH, (size_t)EI_CLASSIFIER_INPUT_HEIGHT, snapshot_buf))) {
        ei_printf("Failed to capture image\r\n");
        free(snapshot_buf);
        return false;
    }

    // Run the classifier
    EI_IMPULSE_ERROR err = run_classifier(&signal, &result, debug_nn);
    if (err != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\n", err);
        return false;
    }
    free(snapshot_buf);
    return true;
}
/**
* @brief      Get data and run inferencing
*
* @param[in]  debug  Get debug info if true
*/
void loop()
{
    if (Serial.available() > 0) {  // Vérifie si des données sont disponibles sur le port série
        sleep(0.01);
        serialEvent();  // Exécute la fonction de gestion des événements série
    }
}

/**
 * @brief   Setup image sensor & start streaming
 *
 * @retval  false if initialisation failed
 */
bool ei_camera_init(void) {

    if (is_initialised) return true;

    //initialize the camera
    esp_err_t err = esp_camera_init(&camera_config);
    if (err != ESP_OK) {
      Serial.printf("Camera init failed with error 0x%x\n", err);
      return false;
    }

    sensor_t * s = esp_camera_sensor_get();
    // initial sensors are flipped vertically and colors are a bit saturated
    if (s->id.PID == OV3660_PID) {
      s->set_vflip(s, 1); // flip it back
      s->set_brightness(s, 1); // up the brightness just a bit
      s->set_saturation(s, 0); // lower the saturation
    }

    is_initialised = true;
    return true;
}

/**
 * @brief      Stop streaming of sensor data
 */
void ei_camera_deinit(void) {

    //deinitialize the camera
    esp_err_t err = esp_camera_deinit();

    if (err != ESP_OK)
    {
        ei_printf("Camera deinit failed\n");
        return;
    }

    is_initialised = false;
    return;
}


/**
 * @brief      Capture, rescale and crop image
 *
 * @param[in]  img_width     width of output image
 * @param[in]  img_height    height of output image
 * @param[in]  out_buf       pointer to store output image, NULL may be used
 *                           if ei_camera_frame_buffer is to be used for capture and resize/cropping.
 *
 * @retval     false if not initialised, image captured, rescaled or cropped failed
 *
 */
camera_fb_t * ei_camera_capture(uint32_t img_width, uint32_t img_height, uint8_t *out_buf) {
    bool do_resize = false;

    if (!is_initialised) {
        ei_printf("ERR: Camera is not initialized\r\n");
        return NULL;
    }

    camera_fb_t *fb = esp_camera_fb_get();

    if (!fb) {
        ei_printf("Camera capture failed\n");
        return NULL;
    }

   bool converted = fmt2rgb888(fb->buf, fb->len, PIXFORMAT_JPEG, snapshot_buf);

   if(!converted){
       ei_printf("Conversion failed\n");
       return NULL;
   }

    if ((img_width != EI_CAMERA_RAW_FRAME_BUFFER_COLS)
        || (img_height != EI_CAMERA_RAW_FRAME_BUFFER_ROWS)) {
        do_resize = true;
    }

    if (do_resize) {
        ei::image::processing::crop_and_interpolate_rgb888(
        out_buf, //input buffer
        EI_CAMERA_RAW_FRAME_BUFFER_COLS, //input width 320
        EI_CAMERA_RAW_FRAME_BUFFER_ROWS, //input height 240
        out_buf, //output buffer
        img_width,//output width 196
        img_height); //output height 196
    }


    return fb;
}

static int ei_camera_get_data(size_t offset, size_t length, float *out_ptr)
{
    // we already have a RGB888 buffer, so recalculate offset into pixel index
    size_t pixel_ix = offset * 3;
    size_t pixels_left = length;
    size_t out_ptr_ix = 0;

    while (pixels_left != 0) {
        // Swap BGR to RGB here
        // due to https://github.com/espressif/esp32-camera/issues/379
        out_ptr[out_ptr_ix] = (snapshot_buf[pixel_ix + 2] << 16) + (snapshot_buf[pixel_ix + 1] << 8) + snapshot_buf[pixel_ix];

        // go to the next pixel
        out_ptr_ix++;
        pixel_ix+=3;
        pixels_left--;
    }
    // and done!
    return 0;
}

#if !defined(EI_CLASSIFIER_SENSOR) || EI_CLASSIFIER_SENSOR != EI_CLASSIFIER_SENSOR_CAMERA
#error "Invalid model for current sensor"
#endif

#include <Arduino.h>
#include <WiFi.h>
#include <FirebaseESP32.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Provide the token generation process info.
#include <addons/TokenHelper.h>

// Provide the RTDB payload printing info and other helper functions.
#include <addons/RTDBHelper.h>

/* 1. Define the WiFi credentials */
#define WIFI_SSID "PennApps"
#define WIFI_PASSWORD "PASSWORD"

/* 2. Define the API Key */
#define API_KEY "SECRETKEYLOL"

/* 3. Define the RTDB URL */
#define DATABASE_URL "SECRET_URL_LOL"

/* 4. Define the user Email and password that already registered or added in your project */
#define USER_EMAIL "SECRETSECRET@gmail.com"
#define USER_PASSWORD "SECRETSECRET"

// Define Firebase Data object
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

unsigned long sendDataPrevMillis = 0;

Adafruit_MPU6050 mpu;

float accel_offset[3] = {0, 0, 0};
float prev_ax = 0, prev_ay = 0, prev_az = 0;
float threshold = 0.5; // Adjust this value based on your needs

void calibrateMPU6050() {
  float sum[3] = {0, 0, 0};
  for (int i = 0; i < 1000; i++) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    sum[0] += a.acceleration.x;
    sum[1] += a.acceleration.y;
    sum[2] += a.acceleration.z;
    delay(1);
  }
  // Calculate average offset
  accel_offset[0] = sum[0] / 1000.0;
  accel_offset[1] = sum[1] / 1000.0;
  accel_offset[2] = sum[2] / 1000.0 - 9.81; // Subtract 1g from the axis pointing downwards (assuming Z-axis)
  
  Serial.println("Calibration complete");
  Serial.print("Offsets: ");
  Serial.print(accel_offset[0]); Serial.print(", ");
  Serial.print(accel_offset[1]); Serial.print(", ");
  Serial.println(accel_offset[2]);
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Connected with IP: ");
  Serial.println(WiFi.localIP());

  Serial.printf("Firebase Client v%s\n\n", FIREBASE_CLIENT_VERSION);

  /* Assign the api key (required) */
  config.api_key = API_KEY;

  /* Assign the user sign in credentials */
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  /* Assign the RTDB URL (required) */
  config.database_url = DATABASE_URL;

  /* Assign the callback function for the long running token generation task */
  config.token_status_callback = tokenStatusCallback;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Additional Firebase settings
  Firebase.setDoubleDigits(5);
  Firebase.setReadTimeout(fbdo, 1000 * 60);
  Firebase.setwriteSizeLimit(fbdo, "tiny");

  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
  calibrateMPU6050();
}

void loop() {
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 5000 || sendDataPrevMillis == 0)) {
    sendDataPrevMillis = millis();

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Apply calibration offsets
    float ax = a.acceleration.x - accel_offset[0];
    float ay = a.acceleration.y - accel_offset[1];
    float az = a.acceleration.z - accel_offset[2];

    float delta_ax = abs(ax - prev_ax);
    float delta_ay = abs(ay - prev_ay);
    float delta_az = abs(az - prev_az);

    // Calculate total acceleration
    float totalAccel = sqrt(ax*ax + ay*ay + az*az);

    // Create a JSON object to hold all the data
    FirebaseJson json;
    json.set("totalAcceleration", totalAccel);
    json.set("accelerationX", ax);
    json.set("accelerationY", ay);
    json.set("accelerationZ", az);
    json.set("gyroX", g.gyro.x);
    json.set("gyroY", g.gyro.y);
    json.set("gyroZ", g.gyro.z);
    json.set("temperature", temp.temperature);

    // Send all data in a single update
    if (Firebase.updateNode(fbdo, "/motionData", json)) {
      Serial.println("Data sent successfully");
    } else {
      Serial.println("Failed to send data: " + fbdo.errorReason());
    }

    // Handle acceleration alert
    if (delta_ax > threshold + 8 || delta_ay > threshold + 8 || delta_az > threshold + 8) {
      Serial.println("Acceleration change detected!");
      Serial.print("Delta X: "); Serial.print(delta_ax);
      Serial.print(" Y: "); Serial.print(delta_ay);
      Serial.print(" Z: "); Serial.println(delta_az);

      if (Firebase.setBool(fbdo, "/motionData/accelerationAlert", true)) {
        Serial.println("Alert sent successfully");
      } else {
        Serial.println("Failed to send alert: " + fbdo.errorReason());
      }
    } else {
      // Reset the alert when no significant change is detected
      Firebase.setBool(fbdo, "/motionData/accelerationAlert", false);
    }

    prev_ax = ax;
    prev_ay = ay;
    prev_az = az;

    Serial.println("--------------------");
  }

  // Check WiFi connection and reconnect if needed
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost. Reconnecting...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("\nReconnected to WiFi");
  }
}

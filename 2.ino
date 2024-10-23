#include <Wire.h> 
#include <MPU6050.h>
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

MPU6050 mpu;

// Blynk credentials
#define BLYNK_TEMPLATE_ID "TMPL3tdzsZbqN"
#define BLYNK_TEMPLATE_NAME "ieee"
#define BLYNK_AUTH_TOKEN "J0BpK_Y7m9_tfYmy4hqAfaPN03gcjr7Y"

// WiFi credentials
char auth[] = "J0BpK_Y7m9_tfYmy4hqAfaPN03gcjr7Y";    // Blynk Auth Token
char ssid[] = "Garv";     // WiFi SSID
char pass[] = "12341234"; // WiFi Password

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Connect to Blynk
  Blynk.begin(auth, ssid, pass);

  Wire.begin();
  mpu.initialize();

  Serial.println("MPU6050 Initialized");
}

void loop() {
  Blynk.run(); // Keep Blynk connection alive

  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  // Get accelerometer and gyroscope readings
  mpu.getAcceleration(&ax, &ay, &az);
  mpu.getRotation(&gx, &gy, &gz);

  Serial.print(ax);
  Serial.print(",");
  Serial.print(ay);
  Serial.print(",");
  Serial.print(az);
  Serial.print(",");
  Serial.print(gx);
  Serial.print(",");
  Serial.print(gy);
  Serial.print(",");
  Serial.println(gz);

  // Upload data to Blynk using virtual pins
  Blynk.virtualWrite(V0, ax); // Accelerometer X
  Blynk.virtualWrite(V1, ay); // Accelerometer Y
  Blynk.virtualWrite(V2, az); // Accelerometer Z
  Blynk.virtualWrite(V3, gx); // Gyroscope X
  Blynk.virtualWrite(V4, gy); // Gyroscope Y
  Blynk.virtualWrite(V5, gz); // Gyroscope Z
  Blynk.virtualWrite(V7, 26.775495); // Gyroscope Z
  Blynk.virtualWrite(V8, 75.876831); // Gyroscope Z

  // Optional: Add temperature data if you wish to send it as well
  int16_t tempRaw = mpu.getTemperature();
  float tempC = tempRaw / 340.00 + 36.53; // Convert raw temperature to Celsius
  Blynk.virtualWrite(V6, tempC); // Temperature

  delay(100); // Adjust delay as needed
}







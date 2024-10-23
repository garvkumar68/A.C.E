#include <TinyGPSPlus.h>

TinyGPSPlus gps;

// Use Serial2 for GPS on ESP32 (GPIO 16 for RX and GPIO 17 for TX)
HardwareSerial gpsSerial(2);

void setup() {
  Serial.begin(115200);    // Debugging via USB
  gpsSerial.begin(9600, SERIAL_8N1, 16, 17); // GPS serial: baud rate 9600, RX pin 16, TX pin 17

  // Call the GPS calibration function
  GPS_calibration();
}

void GPS_calibration() {
  // Keep reading GPS data until we have valid location data
  while (!gps.location.isValid()) {
    smartDelay(1000);  // Delay with GPS processing
    if (millis() > 5000 && gps.charsProcessed() < 10) {
      Serial.println(F("No GPS data received: check wiring"));
      return;  // Exit function if no valid GPS data after 5 seconds
    }
  }

  // Print latitude and longitude once valid GPS data is received
  Serial.print("Latitude: ");
  Serial.print(gps.location.lat(), 6);
  Serial.print(", Longitude: ");
  Serial.println(gps.location.lng(), 6);

  // Enter an infinite loop to prevent further execution
  while (true) {
    // Do nothing, just stay in this loop indefinitely
  }
}

void loop() {
  // Empty loop as all functionality is contained within the GPS_calibration function
}

static void smartDelay(unsigned long ms) {
  unsigned long start = millis();
  do {
    while (gpsSerial.available()) {
      gps.encode(gpsSerial.read()); // Read data from GPS serial and encode it
    }
  } while (millis() - start < ms);
}

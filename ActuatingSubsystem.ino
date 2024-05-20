#include <ArduinoBLE.h>

const int ledPin = 9;
const int buzzerPin = 8;
BLEService distanceService("180F"); // BLE Service
BLEUnsignedCharCharacteristic distanceCharacteristic("2A19", BLERead | BLENotify | BLEWrite); // BLE Characteristic

void setup() {
  Serial.begin(9600);
  while (!Serial);

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  if (!BLE.begin()) {
    Serial.println("Starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("ActuatingSubsystem");
  BLE.setAdvertisedService(distanceService);
  distanceService.addCharacteristic(distanceCharacteristic);
  BLE.addService(distanceService);

  distanceCharacteristic.writeValue(0);
  BLE.advertise();

  Serial.println("BLE device is now advertising...");
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      if (distanceCharacteristic.written()) {
        int scaled_distance = distanceCharacteristic.value();
        Serial.print("Scaled distance received: ");
        Serial.println(scaled_distance);

        int original_distance = map(scaled_distance, 0, 255, 0, 500);
        Serial.print("Original distance approximated: ");
        Serial.println(original_distance);
        
        if (original_distance < 30) {
          analogWrite(ledPin, 255);
          digitalWrite(buzzerPin, HIGH);
          Serial.println("LED and Buzzer ON");
        } else {
          int led_brightness = map(original_distance, 30, 100, 0, 255);
          if (led_brightness > 100) led_brightness = 0;
          analogWrite(ledPin, led_brightness);
          digitalWrite(buzzerPin, LOW);
          Serial.print("LED brightness: ");
          Serial.println(led_brightness);
          Serial.println("Buzzer OFF");
        }
      }
      delay(1000);
    }
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}

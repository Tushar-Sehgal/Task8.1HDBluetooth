import time
from bluepy.btle import Peripheral, DefaultDelegate, BTLEException, UUID
import RPi.GPIO as GPIO

# GPIO setup
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setwarnings(False)

def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    
    return distance

def connect_to_device(address):
    while True:
        try:
            print(f"Connecting to {address}")
            peripheral = Peripheral(address, "public")
            return peripheral
        except BTLEException as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def main():
    arduino_address = "EC:62:60:81:68:DE"
    peripheral = connect_to_device(arduino_address)
    
    service_uuid = UUID("180F")
    char_uuid = UUID("2A19")
    service = peripheral.getServiceByUUID(service_uuid)
    char = service.getCharacteristics(char_uuid)[0]

    try:
        while True:
            try:
                distance = measure_distance()
                scaled_distance = int((distance / 500.0) * 255)
                scaled_distance = max(0, min(255, scaled_distance))
                print(f"Measured distance: {distance} cm, Scaled distance: {scaled_distance}")
                char.write(bytes([scaled_distance]), withResponse=True)
                print(f'Successfully sent distance: {scaled_distance}')
                time.sleep(1)
            except BTLEException as e:
                print(f'Error during communication: {e}')
                peripheral.disconnect()
                peripheral = connect_to_device(arduino_address)
                service = peripheral.getServiceByUUID(service_uuid)
                char = service.getCharacteristics(char_uuid)[0]
    except KeyboardInterrupt:
        GPIO.cleanup()
        peripheral.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()

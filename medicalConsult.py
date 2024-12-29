import time
import datetime
import RPi.GPIO as GPIO
from grove.display.jhd1802 import JHD1802
import Adafruit_DHT
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# Sensor configuration
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 22  # Temperature and humidity sensor
MIC_PIN = 26  # Sound sensor
TOUCH_PIN = 24  # Touch sensor
PROX_PIN = 16  # Proximity sensor
LED_PIN = 5  # LED
BUZZER_PIN = 18  # Buzzer
DISTANCE_THRESHOLD = 1.0  # Distance to start the process

# InfluxDB configuration
INFLUXDB_URL = "http://192.168.247.95:8086"  # InfluxDB server address
INFLUXDB_TOKEN = "U-19LssMKH4z6jiDwysJ9jPvfgLenIYRMRsUtfPDalr_HcYm4_5OrQulGEw-5N4FGJFAtzbATPiiL7nwN2p3CA=="
INFLUXDB_ORG = "iot_group_10"  # InfluxDB organization
INFLUXDB_BUCKET = "temp&Hum"  # InfluxDB bucket

# Initialize InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize GPIO pins and LCD display
GPIO.setmode(GPIO.BCM)
GPIO.setup(MIC_PIN, GPIO.IN)
GPIO.setup(TOUCH_PIN, GPIO.IN)
GPIO.setup(PROX_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize the LCD display
lcd = JHD1802()

def measure_distance():
    """Measure distance using the proximity sensor."""
    GPIO.setup(PROX_PIN, GPIO.OUT)
    GPIO.output(PROX_PIN, False)
    time.sleep(0.2)
    GPIO.output(PROX_PIN, True)
    time.sleep(0.00001)
    GPIO.output(PROX_PIN, False)
    GPIO.setup(PROX_PIN, GPIO.IN)
    pulse_start = time.time()
    while GPIO.input(PROX_PIN) == 0:
        pulse_start = time.time()
    while GPIO.input(PROX_PIN) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2
    return distance / 100  # Convert to meters

def measure_temp_humidity():
    """Read data from the temperature and humidity sensor."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        return None, None

def display_message(line1, line2="", duration=2):
    """Display a message on the LCD."""
    lcd.setCursor(0, 0)
    lcd.write(line1)
    lcd.setCursor(1, 0)
    lcd.write(line2)
    time.sleep(duration)  # Ensure the message is displayed for the specified time
    lcd.clear()

def send_to_influxdb(temperature, humidity):
    """Send data to InfluxDB in a single row with formatted date."""
    try:
        formatted_time = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M")
        point = (
            Point("environment_data")
            .tag("device", "raspberry_pi")
            .field("temperature", temperature)
            .field("humidity", humidity)
            .field("formatted_time", formatted_time)
        )
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"Data sent: Date={formatted_time}, Temp={temperature}°C, Hum={humidity}%")
    except Exception as e:
        print(f"Error sending data to InfluxDB: {e}")

def main_flow():
    """Run the main measurement and data sending process. Restart the cycle after each query."""
    while True:
        try:
            # Wait until the user is at the correct distance
            display_message("Get closer to", "start")
            while True:
                distance = measure_distance()
                print(f"Measured distance: {distance:.2f} m")  # For debugging
                if distance < DISTANCE_THRESHOLD:
                    display_message("Starting", "process...")
                    break
                time.sleep(0.5)

            # Keep "Touch to start" message until the user touches the sensor
            display_message("Touch to start")
            while GPIO.input(TOUCH_PIN) == GPIO.LOW:  # Loop until touch is detected
                time.sleep(0.1)  # Short pause to avoid CPU overload

            # Turn on the LED to indicate the process has started
            GPIO.output(LED_PIN, GPIO.LOW)
            display_message("Welcome!", "Measuring...")

            # Measure temperature and humidity
            temperature, humidity = measure_temp_humidity()
            if temperature is not None and humidity is not None:
                display_message(f"Temp: {temperature:.1f}C", f"Humidity: {humidity:.1f}%", 5)  # Show for 5 seconds
                send_to_influxdb(temperature, humidity)  # Send data to InfluxDB
            else:
                display_message("Error at", "reading data", 3)

            # Voice query
            display_message("Speak after", "the beep", 2)
            start_time = time.time()
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.25)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            listen_time = 10  # Listen for 10 seconds
            speaking = False

            while time.time() - start_time < listen_time:
                if GPIO.input(MIC_PIN) == GPIO.HIGH:
                    speaking = True
                    display_message("Voice detected", "confirmed", 1)
                    break
                time.sleep(0.1)

            # Final confirmation
            if speaking:
                display_message("Consult done", "Thanks! :)", 3)
            else:
                display_message("Calling 112", 3)

            # Turn off the LED after the process is completed
            GPIO.output(LED_PIN, GPIO.HIGH)

        except KeyboardInterrupt:
            print("Program terminated by the user")
            break
        finally:
            # Clear resources at the end of the complete cycle
            lcd.clear()

if __name__ == "__main__":
    main_flow()

    # Clean GPIO pins only at the end of the program
    GPIO.cleanup()
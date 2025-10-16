import time
import board
import busio
import RPi.GPIO as GPIO
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import paho.mqtt.client as mqtt
from utils.utils import get_cpu_temp  # your helper function

# ----- Config -----
BROKER = "localhost"         # MQTT broker IP
TOPIC_TEMP = "pi/temperature"
TOPIC_FAN = "pi/fan_state"
UPDATE_INTERVAL = 5             # seconds
ENABLE_PIN = 17                  # GPIO pin controlling the fan relay

# ----- GPIO -----
GPIO.setmode(GPIO.BCM)
GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=GPIO.LOW)
fan_on = False

# ----- OLED -----
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

# ----- MQTT -----

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT broker")
    client.subscribe(TOPIC_FAN)

def on_message(client, userdata, msg):
    global fan_on
    payload = msg.payload.decode().strip().upper()
    if payload == "ON" and not fan_on:
        GPIO.output(ENABLE_PIN, GPIO.HIGH)
        fan_on = True
        time.sleep(0.1)
    elif payload == "OFF":
        GPIO.output(ENABLE_PIN, GPIO.LOW)
        fan_on = False
        time.sleep(0.1)
        
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()

# ----- Main Loop -----
last_update = 0

try:
    while True:
        now = time.monotonic()
        if now - last_update < UPDATE_INTERVAL:
            time.sleep(0.1)  # Prevent CPU spinning
            continue

        # Read CPU temperature
        temp = get_cpu_temp() or 0.0
        client.publish(TOPIC_TEMP, f"{temp:.1f}")

        # OLED display
        oled.fill(0)
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)

        line1 = "CPU Temp"
        bbox1 = draw.textbbox((0, 0), line1, font=font)
        x1 = (oled.width - (bbox1[2] - bbox1[0])) // 2
        y1 = 10

        line2 = f"{temp:.1f} °C"
        bbox2 = draw.textbbox((0, 0), line2, font=font)
        x2 = (oled.width - (bbox2[2] - bbox2[0])) // 2
        y2 = y1 + bbox1[3] + 5

        line3 = "Fan: ON" if fan_on else "Fan: OFF"
        bbox3 = draw.textbbox((0, 0), line3, font=font)
        x3 = (oled.width - (bbox3[2] - bbox3[0])) // 2
        y3 = y2 + bbox2[3] + 5

        draw.text((x1, y1), line1, font=font, fill=255)
        draw.text((x2, y2), line2, font=font, fill=255)
        draw.text((x3, y3), line3, font=font, fill=255)

        oled.image(image)
        oled.show()

        print(f"Temp: {temp:.1f}oC | Fan: {'ON' if fan_on else 'OFF'}")

        last_update = now

except KeyboardInterrupt:
    GPIO.cleanup()
    GPIO.output(ENABLE_PIN, GPIO.LOW)  # Turn off fan
    client.loop_stop()
    client.disconnect()
    print("Stopped.")

import time
import board
import busio
import RPi.GPIO as GPIO
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
# import paho.mqtt.client as mqtt
from utils import get_cpu_temp  # your existing function

# --- Configuration ---
BROKER = "192.168.1.50"         # MQTT broker IP
TOPIC_TEMP = "pi/temperature"
TOPIC_FAN = "pi/fan_speed"
UPDATE_INTERVAL = 5             # seconds
FAN_PIN = 18                    # PWM pin for motor

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)
pwm = GPIO.PWM(FAN_PIN, 100)  # 100Hz
pwm.start(0)
fan_speed = 0

# --- OLED Setup ---
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

# --- MQTT Setup ---
# client = mqtt.Client()

# def on_connect(client, userdata, flags, rc):
#     print("Connected to MQTT broker")
#     client.subscribe(TOPIC_FAN)

# def on_message(client, userdata, msg):
#     global fan_speed
#     try:
#         fan_speed = int(msg.payload.decode())
#         pwm.ChangeDutyCycle(fan_speed)
#         print(f"Fan speed set to {fan_speed}%")
#     except ValueError:
#         print("Invalid fan speed payload")

# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(BROKER, 1883, 60)
# client.loop_start()

# --- Main Loop ---
last_update = time.monotonic()

while True:
    now = time.monotonic()
    if now - last_update < UPDATE_INTERVAL:
        continue

    # --- CPU Temp ---
    temp = get_cpu_temp() or 0.0
    # client.publish(TOPIC_TEMP, f"{temp:.1f}")

    # --- OLED Display ---
    oled.fill(0)
    oled.show()

    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw CPU temperature
    line1 = "CPU Temp"
    bbox1 = draw.textbbox((0, 0), line1, font=font)
    x1 = (oled.width - (bbox1[2]-bbox1[0])) // 2
    y1 = 10

    line2 = f"{temp:.1f} °C"
    bbox2 = draw.textbbox((0, 0), line2, font=font)
    x2 = (oled.width - (bbox2[2]-bbox2[0])) // 2
    y2 = y1 + bbox1[3] + 5

    draw.text((x1, y1), line1, font=font, fill=255)
    draw.text((x2, y2), line2, font=font, fill=255)

    # Draw fan speed at bottom
    line3 = f"Fan: {fan_speed}%"
    bbox3 = draw.textbbox((0, 0), line3, font=font)
    x3 = (oled.width - (bbox3[2]-bbox3[0])) // 2
    y3 = y2 + bbox2[3] + 5
    draw.text((x3, y3), line3, font=font, fill=255)

    oled.image(image)
    oled.show()

    print(f"Temp: {temp:.1f}°C | Fan: {fan_speed}%")

    last_update = now

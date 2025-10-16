import board
import busio
from digitalio import DigitalInOut
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
from utils import get_cpu_temp
import time

interval = 5  # Update interval in seconds
last_update = time.monotonic()

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

while True:
    now = time.monotonic()
    if now - last_update < interval:
        continue

    # Clear display
    oled.fill(0)
    oled.show()

    # Create image buffer
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Load default font
    font = ImageFont.load_default()
    text = f"CPU Temp: {get_cpu_temp():.1f}C"

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position for centered text
    x = (oled.width - text_width) // 2
    y = (oled.height - text_height) // 2

    # Draw text and show on OLED
    draw.text((x, y), text, font=font, fill=255)
    oled.image(image)
    oled.show()

    last_update = now
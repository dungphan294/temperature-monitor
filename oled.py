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
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)

    # Line 1: Label
    line1 = "CPU Temp:"
    bbox1 = draw.textbbox((0, 0), line1, font=font)
    w1 = bbox1[2] - bbox1[0]
    x1 = (oled.width - w1) // 2
    y1 = 10  # top padding

    # Line 2: Temperature with degree symbol
    temp = get_cpu_temp()
    line2 = f"{temp:.1f} °C"
    bbox2 = draw.textbbox((0, 0), line2, font=font)
    w2 = bbox2[2] - bbox2[0]
    x2 = (oled.width - w2) // 2
    y2 = y1 + bbox1[3] + 5  # spacing below first line
    text = f"CPU Temp \n\t{get_cpu_temp():.1f} °C"

    # Draw text and show on OLED
    draw.text((x1, y1), line1, font=font, fill=255)
    draw.text((x2, y2), line2, font=font, fill=255)
    oled.image(image)
    oled.show()

    last_update = now

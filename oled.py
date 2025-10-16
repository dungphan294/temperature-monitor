import board
import busio
from digitalio import DigitalInOut
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Clear display
oled.fill(0)
oled.show()

# Create image buffer
image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Load default font
font = ImageFont.load_default()
text = "Hello Dung!"

# Calculate text position
(text_width, text_height) = draw.textsize(text, font=font)

# Calculate position for centered text
x = (oled.width - text_width) // 2
y = (oled.height - text_height) // 2

# Draw text and show on OLED
draw.text((x, y), text, font=font, fill=255)
oled.image(image)
oled.show()

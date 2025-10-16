import time
import sys
import signal
import board
import busio
import RPi.GPIO as GPIO
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import paho.mqtt.client as mqtt

# ====== Config ======
BROKER = "localhost"
PORT = 1883
QOS = 1

TOPIC_TEMP = "pi/temperature"
TOPIC_FAN = "pi/fan_state"        # inbound: "ON"/"OFF"
TOPIC_STATUS = "pi/status"        # publishes "ONLINE"/"OFFLINE"

UPDATE_INTERVAL = 5.0             # seconds
OLED_REFRESH_HEARTBEAT = 60.0     # force-refresh OLED at least this often
TEMP_CHANGE_THRESHOLD = 0.5       # °C change to trigger OLED refresh
DEBOUNCE_SECONDS = 0.2            # ignore repeated ON/OFF flips inside this window

ENABLE_PIN = 4                    # TPS61023 EN pin (active HIGH)
GPIO_ACTIVE_LEVEL = GPIO.HIGH     # set to GPIO.LOW if your board is active-low
RETAIN_FAN_STATE = True           # publish current fan state as retained

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

# ====== Globals ======
fan_on = False
last_cmd_ts = 0.0
last_temp = None
last_oled_refresh = 0.0

# ====== Helpers ======
def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except Exception:
        pass
    sys.stdout.flush()

def read_cpu_temp():
    """
    Reads CPU temperature from sysfs. Returns float (°C) or None on failure.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except Exception as e:
        safe_print(f"[WARN] Error reading CPU temp: {e}")
        return None

def set_fan(state: bool):
    """
    Sets the fan state with proper GPIO level.
    """
    global fan_on
    try:
        level = GPIO_ACTIVE_LEVEL if state else (GPIO.LOW if GPIO_ACTIVE_LEVEL == GPIO.HIGH else GPIO.HIGH)
        GPIO.output(ENABLE_PIN, level)
        fan_on = state
        safe_print(f"[INFO] Fan {'ON' if fan_on else 'OFF'} (GPIO level={level})")
    except Exception as e:
        safe_print(f"[ERROR] GPIO write failed: {e}")

def load_font(size=20):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    # Fallback PIL bitmap font
    from PIL import ImageFont as _F
    safe_print("[WARN] TrueType font not found; using default PIL font.")
    return _F.load_default()

def draw_oled(oled, font, temp, fan_on):
    """
    Renders a simple centered status layout to the OLED.
    """
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    line1 = "CPU Temp"
    line2 = f"{temp:.1f} °C" if temp is not None else "N/A"
    line3 = "Fan: ON" if fan_on else "Fan: OFF"

    # Centering helpers
    def center_y(prev_bbox, pad=5):
        return prev_bbox[3] + pad

    # First line
    bbox1 = draw.textbbox((0, 0), line1, font=font)
    x1 = (oled.width - (bbox1[2] - bbox1[0])) // 2
    y1 = 8

    # Second line
    bbox2 = draw.textbbox((0, 0), line2, font=font)
    x2 = (oled.width - (bbox2[2] - bbox2[0])) // 2
    y2 = center_y((x1, y1, x1 + bbox1[2], y1 + (bbox1[3] - bbox1[1])))

    # Third line
    bbox3 = draw.textbbox((0, 0), line3, font=font)
    x3 = (oled.width - (bbox3[2] - bbox3[0])) // 2
    y3 = center_y((x2, y2, x2 + bbox2[2], y2 + (bbox2[3] - bbox2[1])))

    draw.text((x1, y1), line1, font=font, fill=255)
    draw.text((x2, y2), line2, font=font, fill=255)
    draw.text((x3, y3), line3, font=font, fill=255)

    oled.image(image)
    oled.show()

# ====== MQTT Callbacks ======
def on_connect(client, userdata, flags, reason_code, properties):
    safe_print(f"[MQTT] Connected: rc={reason_code}")
    client.subscribe(TOPIC_FAN, qos=QOS)
    # Announce ONLINE (retained) after connecting
    client.publish(TOPIC_STATUS, "ONLINE", qos=QOS, retain=True)
    # Also publish current fan state (retained if desired)
    client.publish(TOPIC_FAN, "ON" if fan_on else "OFF", qos=QOS, retain=RETAIN_FAN_STATE)

def on_disconnect(client, userdata, rc, properties=None):
    safe_print(f"[MQTT] Disconnected: rc={rc}")

def on_message(client, userdata, msg):
    global last_cmd_ts, fan_on
    try:
        payload = msg.payload.decode(errors="ignore").strip().upper()
    except Exception:
        payload = ""
    now = time.monotonic()
    # Debounce rapid repeats
    if now - last_cmd_ts < DEBOUNCE_SECONDS:
        return
    last_cmd_ts = now

    if payload == "ON" and not fan_on:
        set_fan(True)
        client.publish(TOPIC_FAN, "ON", qos=QOS, retain=RETAIN_FAN_STATE)
    elif payload == "OFF" and fan_on:
        set_fan(False)
        client.publish(TOPIC_FAN, "OFF", qos=QOS, retain=RETAIN_FAN_STATE)
    # else ignore duplicate command

# ====== Init Peripherals ======
def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=(GPIO.LOW if GPIO_ACTIVE_LEVEL == GPIO.HIGH else GPIO.HIGH))
    # Ensure known OFF state on boot
    set_fan(False)

def init_oled():
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
    font = load_font(20)
    return oled, font

def init_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Reconnect backoff
    client.reconnect_delay_set(min_delay=1, max_delay=60)

    # Last Will & Testament
    client.will_set(TOPIC_STATUS, "OFFLINE", qos=QOS, retain=True)

    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()
    return client

# ====== Shutdown Handling ======
_shutdown = False
def _handle_signal(signum, frame):
    global _shutdown
    _shutdown = True

for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, _handle_signal)

def cleanup(client):
    safe_print("[SYS] Cleaning up...")
    try:
        set_fan(False)
    except Exception:
        pass
    try:
        GPIO.cleanup()
    except Exception:
        pass
    try:
        # Announce offline and stop MQTT
        client.publish(TOPIC_STATUS, "OFFLINE", qos=QOS, retain=True)
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    safe_print("[SYS] Stopped.")

# ====== Main ======
def main():
    global last_temp, last_oled_refresh

    init_gpio()
    oled, font = init_oled()
    client = init_mqtt()

    # Initial OLED
    last_temp = read_cpu_temp()
    draw_oled(oled, font, last_temp if last_temp is not None else 0.0, fan_on)
    last_oled_refresh = time.monotonic()

    last_update = 0.0

    try:
        while not _shutdown:
            now = time.monotonic()
            if now - last_update >= UPDATE_INTERVAL:
                temp = read_cpu_temp()
                # Publish temperature (no retain)
                if temp is not None:
                    client.publish(TOPIC_TEMP, f"{temp:.1f}", qos=QOS, retain=False)
                else:
                    # Publish sentinel or skip; here we skip to avoid polluting the topic
                    pass

                # OLED refresh only if needed
                need_refresh = False
                if temp is None and last_temp is not None:
                    need_refresh = True
                elif temp is not None and (last_temp is None or abs(temp - last_temp) >= TEMP_CHANGE_THRESHOLD):
                    need_refresh = True

                if need_refresh or (now - last_oled_refresh >= OLED_REFRESH_HEARTBEAT):
                    draw_oled(oled, font, temp if temp is not None else (last_temp if last_temp is not None else 0.0), fan_on)
                    last_oled_refresh = now

                last_temp = temp if temp is not None else last_temp
                last_update = now

                safe_print(f"[RUN] Temp: {temp:.1f}°C | Fan: {'ON' if fan_on else 'OFF'}") if temp is not None else safe_print(f"[RUN] Temp: N/A | Fan: {'ON' if fan_on else 'OFF'}")

            time.sleep(0.05)  # keep CPU usage low

    finally:
        cleanup(client)

if __name__ == "__main__":
    main()

import RPi.GPIO as GPIO
import time

EN_PIN = 18  # or any free GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_PIN, GPIO.OUT)

def fan_on():
    GPIO.output(EN_PIN, GPIO.HIGH)   # enable TPS61023
    print("Fan ON")

def fan_off():
    GPIO.output(EN_PIN, GPIO.LOW)    # disable TPS61023
    print("Fan OFF")

try:
    fan_on()
    time.sleep(5)
    fan_off()
    time.sleep(50)
finally:
    GPIO.cleanup()

import RPi.GPIO as GPIO
import time

EN_PIN = 17  # moved off GPIO4

GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_PIN, GPIO.OUT, initial=GPIO.LOW)  # start OFF

def fan_on():
    GPIO.output(EN_PIN, GPIO.HIGH)   # EN=HIGH -> ON (TPS61023 is active-high)
    print("Fan ON")

def fan_off():
    GPIO.output(EN_PIN, GPIO.LOW)    # EN=LOW  -> OFF
    print("Fan OFF")

try:
    print("Start: Fan OFF for 3s")
    time.sleep(3)
    fan_on()
    time.sleep(5)
    fan_off()
    time.sleep(5)
finally:
    # Keep it OFF on exit
    GPIO.output(EN_PIN, GPIO.LOW)
    time.sleep(0.2)
    GPIO.cleanup()

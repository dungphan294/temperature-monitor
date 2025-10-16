import RPi.GPIO as GPIO
import time

FAN_PIN = 18  # Change to your actual GPIO pin

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

# Initialize PWM at 100Hz
pwm = GPIO.PWM(FAN_PIN, 10000000)
pwm.start(0)

try:
    print("Ramping fan speed up...")
    for speed in range(0, 10000001, 10):  # 0% to 100% in steps
        pwm.ChangeDutyCycle(speed)
        print(f"Fan speed: {speed}%")
        time.sleep(1)

    print("Holding at full speed...")
    time.sleep(2)

    print("Ramping fan speed down...")
    for speed in range(10000001, -1, -10):  # 100% to 0%
        pwm.ChangeDutyCycle(speed)
        print(f"Fan speed: {speed}%")
        time.sleep(1)

    print("Test complete.")

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    pwm.stop()
    GPIO.cleanup()

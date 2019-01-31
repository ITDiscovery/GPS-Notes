# LED Hooked to Pin 11, Switch Hooked to Pin 7
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(12, GPIO.IN)

time.sleep(1)

GPIO.output(11, True)
time.sleep(10)

GPIO.output(11, False)
time.sleep(10)

GPIO.cleanup()


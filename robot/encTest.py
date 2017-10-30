import RPi.GPIO as gpio
import time

def encoderCB(channel):
    print("GOT HERE " + str(channel))

gpio.setmode(gpio.BOARD)
gpio.setup(3, gpio.OUT)
gpio.setup(5, gpio.OUT)
gpio.setup(40, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.add_event_detect(40, gpio.BOTH, callback=encoderCB)
gpio.output(3, True)
gpio.output(5, False)
time.sleep(2)
gpio.cleanup()

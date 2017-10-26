import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(3, gpio.OUT)
    gpio.setup(5, gpio.OUT)
    gpio.setup(12, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(16, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(12, gpio.FALLING, callback=aFell)
    gpio.add_event_detect(16, gpio.FALLING, callback=bFell)

def aFell(channel):
    print("Falling edge on GPIO 18")

def bFell(channel):
    print("Falling edge on GPIO 23")


def cw(t):
    init()
    gpio.output(3, True)
    gpio.output(5, False)
    time.sleep(t)
    gpio.cleanup()

cw(3)

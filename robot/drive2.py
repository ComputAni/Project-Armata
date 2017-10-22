import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)
    gpio.setup(7, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(11, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(7, gpio.FALLING, callback=aFell)
    gpio.add_event_detect(11, gpio.FALLING, callback=bFell)

def aFell(channel):
    print("Falling edge on GPIO 7")

def bFell(channel):
    print("Falling edge on GPIO 11")


def cw(t):
    init()
    gpio.output(13, True)
    gpio.output(15, False)
    time.sleep(t)
    gpio.cleanup()

cw(3)

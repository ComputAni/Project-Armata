import RPi.GPIO as gpio
import time

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(7, gpio.OUT)
    gpio.setup(11, gpio.OUT)
    gpio.setup(13, gpio.OUT)
    gpio.setup(15, gpio.OUT)

def forward(duration):
    init()
    gpio.output(7, False)
    gpio.output(11, True)
    gpio.output(13, True)
    gpio.output(15, False)
    time.sleep(duration)
    gpio.cleanup()

def backward(duration):
    init()
    gpio.output(7, True)
    gpio.output(11, False)
    gpio.output(13, False)
    gpio.output(15, True)
    time.sleep(duration)
    gpio.cleanup()

def pivLeft(duration):
    init()
    gpio.output(7, False)
    gpio.output(11, True)
    gpio.output(13, False)
    gpio.output(15, True)
    time.sleep(duration)
    gpio.cleanup()

def pivRight(duration):
    init()
    gpio.output(7, True)
    gpio.output(11, False)
    gpio.output(13, True)
    gpio.output(15, False)
    time.sleep(duration)
    gpio.cleanup()

def ccw90():
    forward(0.15)
    pivLeft(1.07)

# ccw90()
def eqForward():
    for i in range(27):
        forward(0.088)
        pivLeft(0.012)


for i in range(5):
    eqForward()
    time.sleep(1)





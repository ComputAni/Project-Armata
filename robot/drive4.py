import RPi.GPIO as gpio
import time

'''
Citations:

1. Basic GPIO Set up
https://www.youtube.com/watch?v=pbCdNh0TiUo&list=PLQVvvaa0QuDeJlgD1RX9_49tMLUxvIxF4&index=3

2. PID Set up from 18-349 S17, PID Lecture and Lab 4

3. Callback help:
http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
http://raspi.tv/2014/rpi-gpio-update-and-detecting-both-rising-and-falling-edges
'''

curr = 0
dest = 2000
cutoff = 10
Kp = 1
Kd = 0.6
Ki = 0

def init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(3, gpio.OUT)
    gpio.setup(5, gpio.OUT)
    gpio.setup(12, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(16, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(12, gpio.FALLING, callback=encoderCB)
    gpio.add_event_detect(16, gpio.FALLING, callback=encoderCB)

def encoderCB(channel):
    global curr
    if channel == 12:
        if (gpio.input(12) ^ gpio.input(16) == 0):
            curr += 1
        else:
            curr -= 1
    if channel == 16:
        if (gpio.input(12) ^ gpio.input(16) == 1):
            curr += 1
        else:
            curr -= 1

def clip(diff):
    if diff > 100:
        return 100
    elif diff < -100:
        return -100
    else:
        return diff

def rot(duty):
    output13 = False
    output15 = False
    if duty == 0:
        return
    elif duty < 0:
        output13 = True
    else:
        output15 = True
    T = float(abs(duty)) / 1000
    gpio.output(3, output13)
    gpio.output(5, output15)
    time.sleep(T)
    gpio.output(3, False)
    gpio.output(5, False)
    time.sleep(0.1 - T) # 100% duty cycle, divided by 1000

def forward(steps):
    init()
    prevErr = 0
    iErr = 0
    while abs(curr - steps) > cutoff:
        pErr = steps - curr
        dErr = pErr - prevErr
        iErr += pErr
        pidOut = (Kp * pErr) + (Kd * dErr) + (Ki * iErr)
        clippedErr = clip(pidOut)
        rot(clippedErr)
        prevErr = pErr
    gpio.cleanup()

forward(dest)

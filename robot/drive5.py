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

curr1 = 0
dest1 = 500
curr1 = 0
dest1 = 500
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
    gpio.setup(7, gpio.OUT)
    gpio.setup(17, gpio.OUT)
    gpio.setup(18, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(18, gpio.FALLING, callback=encoderCB)
    gpio.add_event_detect(22, gpio.FALLING, callback=encoderCB)


def encoderCB(channel):
    global curr1
    global curr2
    if channel == 12:
        if (gpio.input(12) ^ gpio.input(16) == 0):
            curr1 += 1
        else:
            curr1 -= 1
    if channel == 16:
        if (gpio.input(12) ^ gpio.input(16) == 1):
            curr1 += 1
        else:
            curr1 -= 1
    if channel == 18:
        if (gpio.input(18) ^ gpio.input(22) == 0):
            curr2 += 1
        else:
            curr2 -= 1
    if channel == 22:
        if (gpio.input(18) ^ gpio.input(22) == 1):
            curr2 += 1
        else:
            curr2 -= 1

def clip(diff):
    if diff > 100:
        return 100
    elif diff < -100:
        return -100
    else:
        return diff

def rot(duty):
    output1p = False
    output1m = False
    if duty == 0:
        return
    elif duty < 0:
        output1p = True
    else:
        output1m = True
    T = float(abs(duty)) / 1000
    gpio.output(3, output1p)
    gpio.output(5, output1m)
    gpio.output(7, output1p)
    gpio.output(17, output1m)
    time.sleep(T)
    gpio.output(3, False)
    gpio.output(5, False)
    gpio.output(7, False)
    gpio.output(17, False)
    time.sleep(0.1 - T) # 100% duty cycle, divided by 1000

def forward(steps):
    init()
    prevErr1 = 0
    iErr1 = 0
    while abs(curr1 - steps) > cutoff and abs(curr2 - steps) > cutoff:
        pErr1 = steps - curr1
        dErr1 = pErr1 - prevErr1
        iErr1 += pErr1
        pidOut1 = (Kp * pErr1) + (Kd * dErr1) + (Ki * iErr1)
        clippedErr1 = clip(pidOut1)
        rot(clippedErr)
        prevErr = pErr
    gpio.cleanup()

forward(dest)

import RPi.GPIO as gpio
import time
import threading

'''
Citations:

1. Basic GPIO Set up
https://www.youtube.com/watch?v=pbCdNh0TiUo&list=PLQVvvaa0QuDeJlgD1RX9_49tMLUxvIxF4&index=3

2. PID Set up from 18-349 S17, PID Lecture and Lab 4

3. Callback help:
http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio-part-3
http://raspi.tv/2014/rpi-gpio-update-and-detecting-both-rising-and-falling-edges

4. Threading:
https://stackoverflow.com/questions/28201667/killing-or-stopping-an-active-thread

'''

cutoff = 20 
Kp = 1
Kd = 0.5
Ki = 0

driveThreshold = 70 # Higher the number, stronger the left motor
rotThreshold = 80

def forwardClip(diff, out1):
    if diff > 100:
        if (out1 == 18 or out1 == 38):
            return driveThreshold
        else:
            return 100
    elif diff < -100:
        if (out1 == 18 or out1 == 38):
            return -driveThreshold
        else:
            return -100
    else:
        return diff

def rotClip(diff, out1):
    if diff > 100:
        if (out1 == 18 or out1 == 38):
            return rotThreshold
        else:
            return 100
    elif diff < -100:
        if (out1 == 18 or out1 == 38):
            return -rotThreshold
        else:
            return -100
    else:
        return diff

class motor(object):
    def __init__(self, out1, out2, in1, in2, dest_ticks=5600):
        gpio.setup(out1, gpio.OUT)
        gpio.setup(out2, gpio.OUT)
        gpio.setup(in1, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.setup(in2, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(in1, gpio.BOTH, callback=self.encoderCB)
        gpio.add_event_detect(in2, gpio.BOTH, callback=self.encoderCB)
        self.out1 = out1
        self.out2 = out2
        self.in1 = in1
        self.in2 = in2
        self.curr_motor_pos = 0
        self.dest_motor_pos = dest_ticks

    def restartCnt(self):
        self.curr_motor_pos = 0

    def encoderCB(self, channel):
        if channel == self.in1:
            if (gpio.input(self.in1) ^ gpio.input(self.in2) == 0):
                self.curr_motor_pos += 1
            else:
                self.curr_motor_pos -= 1
        if channel == self.in2:
            if (gpio.input(self.in1) ^ gpio.input(self.in2) == 1):
                self.curr_motor_pos += 1
            else:
                self.curr_motor_pos -= 1

    def rot(self, duty):
        output1p = False
        output1m = False
        if duty == 0:
            return
        elif duty < 0:
            output1p = True
        else:
            output1m = True
        T = float(abs(duty)) / 1000
        gpio.output(self.out1, output1p)
        gpio.output(self.out2, output1m)
        time.sleep(T)
        gpio.output(self.out1, False)
        gpio.output(self.out2, False)
        time.sleep(0.1 - T)

    def workerMethod(self):
        prevErr = 0
        iErr = 0
        while (abs(self.curr_motor_pos - self.dest_motor_pos) > cutoff):
            self.pErr = self.dest_motor_pos - self.curr_motor_pos
            dErr = self.pErr - prevErr
            iErr += self.pErr 
            pidOut = (Kp * self.pErr) + (Kd * dErr) + (Ki * iErr)
            if self.isFoward:
                clippedErr = forwardClip(pidOut, self.out1)
            else:
                clippedErr = rotClip(pidOut, self.out1)
            self.rot(clippedErr)
            prevErr = self.pErr
            if (threading.activeCount() < 5):
                break


def forward(motorL, ticks=5600):
    threadL = []
    for mot in motorL:
        mot.restartCnt()
        mot.dest_motor_pos = ticks
        mot.isFoward = True
        t = threading.Thread(target=mot.workerMethod)
        threadL.append(t)
        t.start()
    for t in threadL:
        t.join()

def cw(motorL, ticks=2400):
    threadL = []
    motorL[0].dest_motor_pos = ticks
    motorL[1].dest_motor_pos = ticks
    motorL[2].dest_motor_pos = -ticks
    motorL[3].dest_motor_pos = -ticks
    for mot in motorL:
        mot.restartCnt()
        mot.isFoward = False
        t = threading.Thread(target=mot.workerMethod)
        threadL.append(t)
        t.start()
    for t in threadL:
        t.join()

import threadDrive
import RPi.GPIO as gpio
import time


gpio.setmode(gpio.BOARD)
a = threadDrive.motor(18, 22, 12, 16)
b = threadDrive.motor(38, 40, 32, 36)
c = threadDrive.motor(31, 33, 35, 37)
d = threadDrive.motor(3, 5, 7, 11)
motorL = [a, b, c, d]

# # Test 1: Move forward 10 steps
# for i in range(1):
#     print("Step number: " + str(i + 1))
#     threadDrive.forward(motorL, 5650)

# # Test 2: Rotations
# for i in range(5):
#     print("Starting rotation: " + str(i+1))
#     threadDrive.cw(motorL, 2400)
#     threadDrive.cw(motorL, -2400)

threadDrive.cw(motorL, 2250)
time.sleep(1)
threadDrive.cw(motorL, -2250)

gpio.cleanup()

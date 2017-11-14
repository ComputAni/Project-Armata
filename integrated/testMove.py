import threadDrive
import RPi.GPIO as gpio


gpio.setmode(gpio.BOARD)
a = threadDrive.motor(18, 22, 12, 16)
b = threadDrive.motor(38, 40, 32, 36)
c = threadDrive.motor(31, 33, 35, 37)
d = threadDrive.motor(3, 5, 7, 11)
motorL = [a, b, c, d]


threadDrive.forward(motorL)
# threadDrive.forward(motorL)
# threadDrive.forward(motorL)
# threadDrive.cw(motorL)
# threadDrive.cw(motorL)
# threadDrive.forward(motorL)
# threadDrive.ccw(motorL)
# threadDrive.forward(motorL)
# threadDrive.forward(motorL)

gpio.cleanup()
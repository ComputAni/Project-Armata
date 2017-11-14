import threadDrive
import RPi.GPIO as gpio


gpio.setmode(gpio.BOARD)
a = threadDrive.motor(22, 18, 16, 12)
# b = threadDrive.motor(7, 11, 18, 22)
# c = threadDrive.motor(15, 13, 26, 24)
# d = threadDrive.motor(21, 19, 36, 32)
# motorL = [a, b, c, d]
motorL = [a]


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
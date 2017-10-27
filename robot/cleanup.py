import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)
gpio.setup(3, gpio.OUT)
gpio.setup(5, gpio.OUT)
gpio.setup(12, gpio.IN)
gpio.setup(16, gpio.IN)
gpio.setup(7, gpio.OUT)
gpio.setup(11, gpio.OUT)
gpio.setup(18, gpio.IN)
gpio.setup(22, gpio.IN)
gpio.cleanup()

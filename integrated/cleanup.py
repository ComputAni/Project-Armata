import RPi.GPIO as gpio

def cleanUpRun():
	gpio.setmode(gpio.BOARD)
	gpio.setup(12, gpio.IN)
	gpio.setup(16, gpio.IN)
	gpio.setup(18, gpio.OUT)
	gpio.setup(22, gpio.OUT)
	gpio.setup(31, gpio.OUT)
	gpio.setup(33, gpio.OUT)
	gpio.setup(35, gpio.IN)
	gpio.setup(37, gpio.IN)
	gpio.setup(3, gpio.OUT)
	gpio.setup(5, gpio.OUT)
	gpio.setup(7, gpio.IN)
	gpio.setup(11, gpio.IN)
	gpio.setup(40, gpio.OUT)
	gpio.setup(38, gpio.OUT)
	gpio.setup(36, gpio.IN)
	gpio.setup(32, gpio.IN)
	gpio.cleanup()

if __name__ == "__main__":
	cleanUpRun()


import board
import busio

import time

import threading
from threading import Thread

import update

print('\n///////////////////////////////////')
print('Starting OLED Service...')
print('///////////////////////////////////')
print(' ')

###### Hostname Stuff
import socket

host = "host_not_set" #default invalid host
ipaddr = "0.0.0.0" #default invalid IP

def UpdateHost():
	print('Updating Hostname...')
	global host
	global ipaddr
	testIP = "8.8.8.8"
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((testIP, 0))
	ipaddr = s.getsockname()[0]
	host = socket.gethostname()
	print ("UpdateHost():", ipaddr, " Host:", host)

UpdateHost()

# Webserver (Synchronize this with twitch_onair_webserver.py)
SERVER_PORT = "8000"

print ('host_url: ' + ipaddr + ':' + SERVER_PORT )

###### Remote Procedure call
import rpyc

###### Draw Image, ssd1306 OLED Drivers
from PIL import Image, ImageDraw, ImageFont, ImageOps
import adafruit_ssd1306
import digitalio

# Define the Reset Pin
#oled_reset = digitalio.DigitalInOut(board.D4)
oled_reset = None

# Change these
# to the right size for your display!
WIDTH = 128
HEIGHT = 32  # Change to 64 if needed
BORDER = 1

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Initial State Machine
input_block = False
pressed = False

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
font = ImageFont.load_default()

###### Image Drawing Functions

# Draw Text With Border
def drawTextBorder(text, invert=False):
	global image
	global font

	textColor = 0

	# Create blank image for drawing.
	# Make sure to create image with mode '1' for 1-bit color.
	image = Image.new("1", (oled.width, oled.height))

	# Get drawing object to draw on image.
	draw = ImageDraw.Draw(image)

	# Draw a white background
	draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)

	# Draw a smaller inner rectangle
	if not invert:
		draw.rectangle(
			(BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
			outline=0,
			fill=0,
		)
		textColor = 255

	(font_width, font_height) = font.getsize(text)
	draw.text(
		(oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
		text,
		font=font,
		fill=textColor,
	)

# Clear OLED
def clearOLED(brightness=0):
	oled.fill(brightness)
	oled.show()


# Show OLED Image
def showImage():
	global image
	# Rotate Image 180 degrees, since it's mounted upside-down
	image = image.rotate(180)
	oled.image(image)
	oled.show()

# Cycle between IP / Hostname Display
def showHostURLLoop(displayTime=3.0, loops=5):
	i = 0
	UpdateHost()
	while i < loops:
		drawTextBorder(host + ':' + SERVER_PORT)
		showImage()
		time.sleep(displayTime)
		drawTextBorder(ipaddr + ':' + SERVER_PORT)
		showImage()
		time.sleep(displayTime)
		i += 1

def showHostURL():
	UpdateHost()
	drawTextBorder(host + ':' + SERVER_PORT)
	showImage()

def showHostIP():
	UpdateHost()
	drawTextBorder(ipaddr + ':' + SERVER_PORT)
	showImage()

def showVersion():
	drawTextBorder( 'Version:' + update.getVersion('VERSION') )
	showImage()

def fancyFlash(text, loops=4):
	x = 0
	while x < loops:
		drawTextBorder( text, invert = True )
		showImage()
		time.sleep(0.1)
		drawTextBorder( text, invert = False )
		showImage()
		time.sleep(0.1)
		x += 1

###### Startup Sequence
clearOLED()
ohayuu = ('Ohayuu! v.' + (update.getVersion('VERSION')))
fancyFlash( ohayuu )
fancyFlash('Press -> For IP.')
time.sleep(2)
clearOLED()

###### Tutorial: https://rpyc.readthedocs.io/en/latest/tutorial/tut3.html

class OledService(rpyc.Service):
	def on_connect(self, conn):
		# code that runs when a connection is created
		# (to init the service, if needed)
		pass

	def on_disconnect(self, conn):
		# code that runs after the connection has already closed
		# (to finalize the service, if needed)
		pass

	def exposed_get_answer(self): # this is an exposed method
		return 42

	exposed_the_real_answer_though = 43	 # an exposed attribute

	def get_question(self):  # while this method is not exposed
		return "what is the airspeed velocity of an unladen swallow?"

	def exposed_ExDrawTextBorder(self, text='No Text Passed', displayTime=3.0, clearAfter=True):
		drawTextBorder(text)
		showImage()
		time.sleep(displayTime)
		if clearAfter:
			clearOLED()

	def exposed_clear(self):
		clearOLED()

	def exposed_showHostIP(self):
		showHostIP()

	def exposed_showHostURL(self):
		showHostURL()

	def exposed_showVersion(self):
		showVersion()

	def exposed_drawTextBorder(self, text, invert=False):
		drawTextBorder(text, invert=invert)
		showImage()

if __name__ == "__main__":
	from rpyc.utils.server import ThreadedServer
	t = ThreadedServer(OledService, port=18861)
	t.daemon=True
	t.start()
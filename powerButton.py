# Press and release the button to reboot, press and hold the button to shutdown the pi safely

import os, sys, time
import RPi.GPIO as GPIO
import pid #Used to killing webserver / neopixel service

print('\n////////////////////////////////')
print('Starting Power Button Service...')
print('////////////////////////////////')
print(' ')

GPIO.setmode(GPIO.BCM) # Broadcom pin numbers
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Pin 26 = reset button

#######################################
############ CONFIGURATION ############
#######################################

###### neopixels section - just so we can shut it down if needed
import board
import neopixel
import json

######## Connect to OLED Service
import rpyc
oled_service_connected = False
try:
	c = rpyc.connect("localhost", 18861)
	oled_service_connected = True
except:
	pass

def tryOLedMessage(text, displayTime=1.0):
	global c
	global oled_service_connected
	try:
		c = rpyc.connect("localhost", 18861)
		oled_service_connected = True
		c.root.ExDrawTextBorder(text, displayTime)
	except:
		pass

SHUTDOWN_TIME = 5.0 # How long to hold for shutdown sequence

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

#max brightness to limit power consumption and heat - match with twitch_onair_neopixel.py
MAX_HARDWARE_BRIGHTNESS = 0.33

###### Defaults
num_pixels = "4"
led_brightness = 0.3

# Initial State Machine
input_block = False
pressed = False
press_time = -0.1
held_time = -1.0

#######################################
########## END CONFIGURATION ##########
#######################################

def tryLoadConfig():
    global num_pixels
    global led_brightness

    config_file_exists = os.path.isfile('config/twitch_onair_config.json')
    if config_file_exists:
        print ('Configuration file found. Loading config')
        with open('config/twitch_onair_config.json') as json_config_file:
            configData = json.load(json_config_file)
            num_pixels = int( configData['num_pixels'] )
            led_brightness = configData['led_brightness']

def pixelOff():
    tryLoadConfig()
    pixels = neopixel.NeoPixel(
        pixel_pin, int(num_pixels), brightness=float(led_brightness), auto_write=False, pixel_order=ORDER
        )
    pixels.fill((0,0,0))
    pixels.show()

def tryKillNeopixelService():
    print('powerButton: Killing Neopixel Service...')
    #pidResult = pid.tryReadPID('neopixel')
    #if pidResult >= 0:
    #    os.system('sudo kill ' + str(pidResult))
    #    pid.delPID('neopixel')
    #else:
    #    pass
    try:
        os.system('sudo systemctl stop twitch_onair_neopixel_service.service')
    except:
    	pass
    pixelOff()

def tryKillWebService():
    print('powerButton: Killing Web Service...')
    #pidResult = pid.tryReadPID('webserver')
    #if pidResult >= 0:
    #    os.system('sudo kill ' + str(pidResult))
    #    pid.delPID('webserver')
    #else:
    #    pass
    try:
        os.system('sudo systemctl stop twitch_onair_webserver_service.service')
    except:
    	pass

def killServices():
	tryKillWebService()
	tryKillNeopixelService()

###### end neopixels section

# System Shutdown / Restart functions
def restart():
	global input_block
	input_block	= True # Comment this out if testing button hold logic
	killServices()
	print('Restarting...')
	tryOLedMessage('Restarting...')
	time.sleep(1.0)
	#GPIO.cleanup()
	os.system('sudo shutdown -r now')
def shutdown():
	global input_block
	input_block = True # Comment this out if testing button hold logic
	killServices()
	print('Shutting Down...')
	tryOLedMessage('Shutting Down...')
	time.sleep(1.0)
	GPIO.cleanup()
	os.system('sudo shutdown -h now')

tryOLedMessage('PowerButton Started')

try:
	while not input_block:
		if GPIO.input(26) == GPIO.LOW:
			
			if not pressed:
				press_time = time.time()
				print('Power button pressed')
				tryOLedMessage('Pressed', displayTime=0.5)
			
			pressed = True

			held_time = time.time() - press_time
			remaining_time = round( (SHUTDOWN_TIME - held_time), 0 )

			if remaining_time < 0:
				shutdown()

			else:
				print('Hold power button for ' + str( abs(remaining_time) ) + ' more seconds to shutdown')
				tryOLedMessage('Hold ' + str(abs(remaining_time)) + 's to shutdown', displayTime=0.5)
				#oledString = ( str( abs(remaining_time) ) + "s to OFF" )
				#tryOLedMessage( oledString , 0.5 )

		else:
			if pressed:
				print('Power button Released')
				if held_time > 0:
					if held_time > SHUTDOWN_TIME:
						shutdown()
					else:
						restart()

			pressed = False

		time.sleep (0.1)

except KeyboardInterrupt:
	GPIO.cleanup()
	print('\npowerButton.py interrupted by user input')
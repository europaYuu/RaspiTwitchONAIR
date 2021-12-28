import os, sys, time

###### Multifunction Button
import RPi.GPIO as GPIO

print('\n////////////////////////////////')
print('Starting Function Button Service...')
print('////////////////////////////////')
print(' ')

GPIO.setmode(GPIO.BCM) # Broadcom pin numbers
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Pin 23 = Multifunction Button


import board

######## Connect to OLED Service
import rpyc
oled_service_connected = False
try:
    c = rpyc.connect("localhost", 18861)
    oled_service_connected = True
except:
    pass

def tryOLedMessage(text):
    global c
    global oled_service_connected
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        c.root.ExDrawTextBorder(text, displayTime=1.0)
    except:
        pass

# Initial State Machine
input_block = False
pressed = False

def tryExShowHostURL():
    global c
    global oled_service_connected
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        c.root.ExShowHOstURL()
    except:
        pass

tryOLedMessage('FunctionButton Started')

try:
	while not input_block:
		if GPIO.input(13) == GPIO.LOW:
			if not pressed:
				print('Function button pressed')
				tryExShowHostURL()

			pressed = True
		else:
			if pressed:
				print('Function button Released')

			pressed = False

		time.sleep (0.2)

except KeyboardInterrupt:
	GPIO.cleanup()
	print('\npowerButton.py interrupted by user input')
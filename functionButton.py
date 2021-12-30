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
import threading
from threading import Thread

######## Connect to OLED Service
import rpyc
oled_service_connected = False
try:
    c = rpyc.connect("localhost", 18861)
    oled_service_connected = True
except:
    pass

import json
from datetime import datetime

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

def getStreamer():
    with open('config/twitch_onair_config.json') as json_config_file:
        configData = json.load(json_config_file)
        try:
            return configData['user']
        except:
            'Config Not Set'

def tryExShowHostURL():
    global c
    global oled_service_connected
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        c.root.ExShowHOstURL()
    except:
        pass

def getCPUuse():
    return str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline())

def tryFunctionButton():
    global c
    global oled_service_connected
    global OLED_mode
    global cpu
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        if OLED_mode == 0:
            c.root.showHostURL()
        elif OLED_mode == 1:
            c.root.showHostIP()
        elif OLED_mode == 2:
            c.root.drawTextBorder( 'Streamer', invert=True )
            time.sleep(0.5)
            c.root.drawTextBorder( getStreamer() )
        #elif OLED_mode == 3:
            #c.root.drawTextBorder( 'Statistics', invert=True )
            #time.sleep(0.5)
        elif OLED_mode == 3:
            c.root.showVersion()
        else:
            c.root.showHostURL()
            OLED_mode = 0
    except:
        pass

def turnOffOLED():
    global c
    global oled_service_connected
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        c.root.clear()
    except:
        pass

oled_on = False
oled_timeout = 10.0
OLED_mode = 0
use = "00.0"
last_press_time = datetime.now()

class Main(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global input_block
        global GPIO
        global pressed
        global oled_on
        global OLED_mode
        global last_press_time
        while True:
            try:
                while not input_block:
                    if GPIO.input(13) == GPIO.LOW:
                        if not pressed:
                            print('Function button pressed at: ' + str(datetime.now()) )
                            last_press_time = datetime.now()
                            if oled_on:
                                OLED_mode += 1
                            tryFunctionButton()
                            oled_on = True

                        pressed = True
                    else:
                        if pressed:
                            print('Function button Released at: ' + str(datetime.now()) )

                        pressed = False

                    time.sleep (0.1)

            except KeyboardInterrupt:
                GPIO.cleanup()
                print('\npowerButton.py interrupted by user input')

class Async(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global oled_on
        global oled_timeout
        while True:
            try:
                if oled_on:
                    time_delta = int( ( datetime.now() - last_press_time ).seconds )
                    print('OLED timeout in: ' + str( oled_timeout - time_delta) )
                    if time_delta >= oled_timeout :
                        turnOffOLED()
                        oled_on = False
            except:
                pass
            time.sleep(0.5)

class StatsDraw(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global oled_on
        global use
        while True:
            try:
                time_delta = int( ( datetime.now() - last_press_time ).seconds )
                if oled_on and OLED_mode == 3 and time_delta > 0.5:
                    c.root.drawTextBorder( 'CPU: ' + use )
                else:
                    pass
            except:
                pass
            time.sleep(0.66)

class StatsThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global use
        while True:
            try:
                if OLED_mode == 3:
                    use = getCPUuse()
            except:
                pass
            time.sleep (0.33)

Main()
Async()
#StatsDraw()
#StatsThread()
while True:
    pass

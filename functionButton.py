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
import subprocess #for SSID

######## Connect to OLED Service
import rpyc
oled_service_connected = False
try:
    c = rpyc.connect("localhost", 18861)
    oled_service_connected = True
except:
    pass

######## Other libraries
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
    try:
        with open('config/twitch_onair_config.json') as json_config_file:
            configData = json.load(json_config_file)
            try:
                return configData['user']
            except:
                return 'Config Not Set'
    except:
        return 'Config Not Set'

def getYoutuber():
    try:
        with open('config/twitch_onair_config.json') as json_config_file:
            configData = json.load(json_config_file)
            try:
                return configData['yt_channel_id']
            except:
                return 'Config Not Set'
    except:
        return 'Config Not Set'

def tryExShowHostURL():
    global c
    global oled_service_connected
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        c.root.ExShowHOstURL()
    except:
        pass

def getSSID():
    try:
        output = subprocess.check_output(['sudo', 'iwgetid'])
        output = output.split()[1]
        output = output.strip()
        output = eval(output[6:])
        print('SSID:' + output)
        return output
    except:
        return 'error/not connected'

# Statistics
def getCPUuse():
    rawstring = str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline())
    return rawstring.strip()
    return psutil.cpu_percent()

def getRAMuse():
    total_memory, used_memory, free_memory = map(
    int, os.popen('free -t -m').readlines()[-1].split()[1:])
    return str( round((used_memory/total_memory) * 100,2) )

def boolToText(source):
    if source:
        return "[ON]"
    else:
        return "[OFF]"

def getTwitchEnable():
    try:
        with open('config/twitch_onair_config.json') as json_config_file:
            configData = json.load(json_config_file)
            try:
                if configData['enable_twitch']:
                    return boolToText( configData['enable_twitch'] )
                else:
                    return boolToText(False)
            except:
                return boolToText(False)
    except:
        return boolToText(False)

def getYoutubeEnable():
    try:
        with open('config/twitch_onair_config.json') as json_config_file:
            configData = json.load(json_config_file)
            try:
                if configData['enable_youtube']:
                    return boolToText(True)
                else:
                    return boolToText(False)
            except:
                return boolToText(False)
    except:
        return boolToText(False)

def tryFunctionButton():
    global c
    global oled_service_connected
    global OLED_mode
    try:
        c = rpyc.connect("localhost", 18861)
        oled_service_connected = True
        if OLED_mode == 0:
            c.root.showHostURL()
        elif OLED_mode == 1:
            c.root.showHostIP()
        elif OLED_mode == 2:
            c.root.drawTextBorder( ('Twitch' + getTwitchEnable()), invert=True )
            time.sleep(0.5)
            c.root.drawTextBorder( getStreamer() )
        elif OLED_mode == 3:
            c.root.drawTextBorder( ('Youtube' + getYoutubeEnable()), invert=True )
            time.sleep(0.5)
            c.root.drawTextBorder( getYoutuber() )
            time.sleep(0.5)
            pass
        elif OLED_mode == 4:
            c.root.drawTextBorder( 'WIFI SSID', invert=True )
            time.sleep(0.5)
            c.root.drawTextBorder( getSSID() )
        elif OLED_mode == 5:
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
oled_timeout = 30.0
OLED_mode = 0
use = "00.0"
ram = "00.00"
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
                time.sleep (0.1)

            except KeyboardInterrupt:
                GPIO.cleanup()
                print('\npowerButton.py interrupted by user input')

            time.sleep (0.5)

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
                        oled_on = False
                        turnOffOLED()
            except:
                pass
            time.sleep(1.0)

class DrawStats(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global oled_on
        global OLED_mode
        global use
        global ram
        while True:
            try:
                if oled_on and OLED_mode == 3:
                    c.root.drawTextBorder( ' CPU:' + use.zfill(4)+ ' MEM:' + ram.zfill(4) )
            except:
                pass
            time.sleep(1.0)

class GetStats(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global oled_on
        global OLED_mode
        global use
        global ram
        while True:
            try:
                if oled_on and OLED_mode == 3:
                    use = getCPUuse()
                    ram = getRAMuse()
            except:
                pass
            time.sleep(1.0)

Main()
Async()
#GetStats() #Disabled because ironically, it uses too much CPU
#DrawStats() #Disabled because ironically, it uses too much CPU
while True:
    time.sleep(0.5)

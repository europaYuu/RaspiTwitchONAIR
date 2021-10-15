# Launches the neopixel and webserver script simultaneously, only really used for debugging (launching from SSH terminal)

import threading
import os

def startWebserver():
	os.system('python3 twitch_onair_webserver.py')
def startNeopixels():
	os.system('python3 twitch_onair_neopixel.py')
def startPowerButton():
	os.system('python3 powerButton.py')

#Comment out this section if you want to disable the web server
t=threading.Thread(target=startWebserver)
t.daemon = True
t.start()

#Commment out this section if you want to disable the neopixels (y tho)
t2=threading.Thread(target=startNeopixels)
t2.daemon = True
t2.start()

#Comment out this section if you want to disable the Power Button
t3=threading.Thread(target=startPowerButton)
t3.daemon = True
t3.start()
import os

os.system('sudo apt-get install python3-pandas')
os.system('sudo apt-get install python3-pip')
os.system('sudo pip3 install --upgrade setuptools')
os.system('sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel')
os.system('sudo python3 -m pip install --force-reinstall adafruit-blinka')
os.system('sudo pip3 install RPi.GPIO')
os.system('sudo pip3 install flask')
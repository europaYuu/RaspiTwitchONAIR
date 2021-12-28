import os

path = os.getcwd()

print('\n/////////////////////////////////')
print('Installing Twitch ON AIR Services...')
print('/////////////////////////////////')
print(' ')
print('Current Path: ' + path)

print('\n/////////////////////////////////')
print('Installing Dependencies...')
print('/////////////////////////////////')
print(' ')
os.system('sudo apt-get install python3-pandas')
os.system('sudo apt-get install python3-pip')
os.system('sudo pip3 install --upgrade setuptools')
os.system('sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel')
os.system('sudo python3 -m pip install --force-reinstall adafruit-blinka')
os.system('sudo pip3 install RPi.GPIO')
os.system('sudo pip3 install flask')
os.system('sudo pip3 install adafruit-circuitpython-ssd1306')
os.system('sudo apt-get install i2c-tools')
os.system('sudo pip3 install rpyc')

print('\n/////////////////////////////////')
print('Cloning Files From Git...')
print('/////////////////////////////////')
print(' ')

# git doesn't like cloning into non-empty directories, so let's make sure this is empty first (in case of failed previous install?)
try:
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/')
except:
	pass

os.system('git clone https://github.com/europaYuu/RaspiTwitchONAIR.git')
os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.git/')
os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.gitignore')
print('\n/////////////////////////////////')
print('Moving Files To /home/pi...')
print('/////////////////////////////////')
print(' ')
os.system('mv -v ' + path + '/RaspiTwitchONAIR/* ' + path)
os.system('rm -rf ' + path + '/RaspiTwitchONAIR/')

print('\n/////////////////////////////////')
print('Installing Services...')
print('/////////////////////////////////')
print(' ')
os.system('sudo python3 twitch_install_services.py')
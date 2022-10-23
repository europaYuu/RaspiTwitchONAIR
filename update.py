import os

######## Connect to OLED Service
import time
import rpyc

def drawProgressBar(percent, text):
    try:
        c = rpyc.connect("localhost", 18861)
        c.root.drawProgressBar(percent, text)
    except:
        pass

def drawTextBorder(text):
    try:
        c = rpyc.connect("localhost", 18861)
        c.root.drawTextBorder(text)
    except:
        pass

def turnOffOLED():
    try:
        c = rpyc.connect("localhost", 18861)
        c.root.clear()
    except:
        pass

def getVersion(filename):
	with open(filename) as fp:
		line = fp.readline()
		return line.strip()

def tryMakeTempdir():
	current_path = os.getcwd()
	path = current_path + '/temp'
	try:
		os.mkdir(path, 0o777)
	except:
		pass

tryMakeTempdir()

def CheckUpdateNeeded():
	updateNeeded = False
	print('\n/////////////////////////////////')
	print('Checking For New Version...')
	print('/////////////////////////////////')
	print(' ')
	try:
		os.system('rm -f /home/pi/temp/VERSION')
	except:
		pass

	try:
		os.system('wget https://raw.githubusercontent.com/europaYuu/RaspiTwitchONAIR/main/VERSION -P /home/pi/temp/')
		version_local = getVersion('VERSION')
		version_remote = getVersion('temp/VERSION')

		if version_local != version_remote:
			print('New Version Available: ' + version_remote)
			updateNeeded = True
		else:
			print('No Update Needed. Current version: ' + version_local)

	except:
		print('Failed to get remote version. Update cancelled')

	return updateNeeded

def GetRemoteVersion():
	version_remote = '-1'
	try: 
		version_remote = getVersion('temp/VERSION')
	except:
		pass
	return version_remote

def CleanUpRemoteVersion():
	try:
		os.system('rm -f /home/pi/temp/VERSION')
	except:
		pass

path = os.getcwd()

def Update():
	global path

	os.system('sudo systemctl stop powerButton.service')
	os.system('sudo systemctl stop functionButton.service')

	drawProgressBar(0.0, 'update started')
	print('\n/////////////////////////////////')
	print('Updating Twitch ON AIR Services...')
	print('/////////////////////////////////')
	print(' ')
	print('Current Path: ' + path)

	drawProgressBar(0.02, 'apt-get update')
	print('\n/////////////////////////////////')
	print('Performing apt-get update')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo apt-get update')

	drawProgressBar(0.1, 'apt-get upgrade')
	print('\n/////////////////////////////////')
	print('Performing apt-get upgrade')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo apt-get upgrade')

	drawProgressBar(0.15, 'remove old folders...')
	print('\n/////////////////////////////////')
	print('Remove Old Folders......')
	print('/////////////////////////////////')
	print(' ')
	os.system('rm -rf ' + path + '/static/' )
	os.system('rm -rf ' + path + '/templates/' )

	drawProgressBar(0.2, 'cloning from git')
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
	drawProgressBar(0.4, 'file permissions')
	os.system('sudo chmod -R 777 ' + path + '/RaspiTwitchONAIR')
	drawProgressBar(0.45, 'setting file perms')
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.git/')
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.gitignore')
	drawProgressBar(0.5, 'cleaning up')
	print('\n/////////////////////////////////')
	print('Moving Files To /home/pi...')
	print('/////////////////////////////////')
	print(' ')
	drawProgressBar(0.7, 'moving files')
	os.system('mv -v -f ' + path + '/RaspiTwitchONAIR/* ' + path)
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/')

	drawProgressBar(0.8, 'updating dependencies')
	print('\n/////////////////////////////////')
	print('Updating Dependencies...')
	print('/////////////////////////////////')
	os.system('sudo python3 /home/pi/twitch_update_dependencies.py')

	drawProgressBar(0.9, 'install services')
	print('\n/////////////////////////////////')
	print('Installing Services...')
	print('/////////////////////////////////')
	os.system('sudo python3 /home/pi/twitch_install_services.py')
	drawProgressBar(1.0, 'update complete')
	time.sleep(3.0)

def RebootAfterUpdate():
	global path
	drawTextBorder( 'Rebooting...' )
	time.sleep(1.5)
	turnOffOLED()
	print('\n/////////////////////////////////')
	print('Rebooting...')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo reboot')
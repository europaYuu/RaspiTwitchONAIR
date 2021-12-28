import os

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
	print('\n/////////////////////////////////')
	print('Updating Twitch ON AIR Services...')
	print('/////////////////////////////////')
	print(' ')
	print('Current Path: ' + path)

	print('\n/////////////////////////////////')
	print('Performing apt-get update')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo apt-get update')

	print('\n/////////////////////////////////')
	print('Performing apt-get upgrade')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo apt-get upgrade')

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
	os.system('sudo chmod -R 777 ' + path + '/RaspiTwitchONAIR')
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.git/')
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/.gitignore')
	print('\n/////////////////////////////////')
	print('Moving Files To /home/pi...')
	print('/////////////////////////////////')
	print(' ')
	os.system('mv -v ' + path + '/RaspiTwitchONAIR/* ' + path)
	os.system('rm -rf ' + path + '/RaspiTwitchONAIR/')

def RebootAfterUpdate():
	global path
	print('\n/////////////////////////////////')
	print('Rebooting...')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo reboot')
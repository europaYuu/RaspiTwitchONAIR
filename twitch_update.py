import os

path = os.getcwd()

def UpdateTwitch():
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
	print('Installing Dependencies...')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo python3 twitch_install_dependencies')

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

def RebootAfterUpdate():
	global path
	print('\n/////////////////////////////////')
	print('Rebooting...')
	print('/////////////////////////////////')
	print(' ')
	os.system('sudo reboot')

UpdateTwitch()
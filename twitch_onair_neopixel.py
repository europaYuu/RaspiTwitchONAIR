# Get Stream Status from Twitch
#
# Requires registration of a Twitch Application. For more information, go to https://dev.twitch.tv/docs/api/ "Getting Started with the Twitch API". Leaving OAuth Redirect URL to http://localhost seems to work, but please let me know on twitter if this is bad practice.
# This script uses the OAuth Client Credentials Flow, which doesn't require a UI to authenticate
# Remember to set User (doesn't have to be the same as the dev account), client_id, and client_secret in config/twitch_onair_config.json (Or use the webserver to do so)

print('\n/////////////////////////////////')
print('Starting Twitch ON AIR Service...')
print('/////////////////////////////////')
print(' ')

##### This is to try to catch boot neopixel errors
import RPi.GPIO as GPIO
GPIO.cleanup()

import os
import requests #For making cURL requests
import datetime
import pandas as pd #Simple datetime formatting for checking if tokens are stale
import json
import time
import random
import traceback

###### store PID so it can be killed easily by the webserver
import pid #store PID in file so webserver can kill if needed

###### neopixels
import board
import neopixel

#######################################
############ CONFIGURATION ############
#######################################

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The number of NeoPixels
num_pixels = 30

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

###### Time and Date

# get the current datetime time and format it - created here just in case we forget to call updateTime() at run
a_datetime = datetime.datetime.now()
formatted_datetime = a_datetime.isoformat()
json_datetime = json.dumps(formatted_datetime)

#define here to make it global scope
app_access_token = ''

# Catching "Connection Refused" Errors
# How many seconds to wait if server refuses our connection?
CONNREFUSE_WAIT_TIME = 30
CONNREFUSE_MAX_LOOPS = 10
CONNREFUSE_Loop = 0 #Initialize the loop count

###### Defaults ######

client_id = 'CLIENT_ID'
client_secret = 'CLIENT_SECRET'

# default twitch token age is 60 days
token_stale_age = 30

# default update interval
update_interval = 30

#streamer to watch
user_login = 'europayuu'

#default light color when live
live_color = (255,255,255)

#max brightness to limit power consumption and heat - match with twitch_onair_webserver.py
MAX_HARDWARE_BRIGHTNESS = 0.33

#default configurable brightness
led_brightness = 0.3

# Used by some pixel effects
num_rows = 3
num_columns = 8

TARGET_FRAMERATE = 20 # For effects that take a time input

# Debug Log. set to True if you want debug file output
ENABLE_DEBUG_LOG = False
DEBUG_LOG_FILENAME = 'logs/twitch_onair_neopixel_log.txt'

#######################################
########## END CONFIGURATION ##########
#######################################

# Initial State machine
first_loop = True

######## DEBUG LOG ########
if ENABLE_DEBUG_LOG:
	import logging
	logging.basicConfig(filename=DEBUG_LOG_FILENAME, level=logging.DEBUG)

def timesStamp():
	current_time = datetime.datetime.now()
	return ( "[" + str( current_time ) + "] ")
	#formatted_datetime = a_datetime.isoformat()
	#json_datetime = json.dumps(formatted_datetime)

def printLog(message='',alsoprint=True,level='debug',include_timestamp=True):
	if include_timestamp:
		message = timesStamp() + message
	if ENABLE_DEBUG_LOG:
		if level == 'debug':
			logging.debug(message)
		elif level == 'info':
			logging.info(message)
		else:
			logging.warning(message)
	else:
		pass
	if alsoprint:
		print(message)

if ENABLE_DEBUG_LOG:
	separator = "********" + "\n" 
	printLog("\n" + separator + 'twitch_onair_neopixel.py debug Log enabled, writing to file ' + DEBUG_LOG_FILENAME + "\n" + separator )

def clamp(n, smallest, largest): return max(smallest, min(n, largest))
def saturate(n): return clamp(n, 0,255) # I miss HLSL

###### Load configuration File ######

def tryLoadConfig():
	global user_login
	global client_id
	global client_secret
	global token_stale_age
	global update_interval
	global num_pixels
	global live_color
	global led_brightness
	global pixels
	global MAX_HARDWARE_BRIGHTNESS

	json_read_error = 'Error reading key value. Default key value used for '

	config_file_exists = os.path.isfile('config/twitch_onair_config.json')
	if config_file_exists:
		printLog ('Configuration file found. Loading config')
		with open('config/twitch_onair_config.json') as json_config_file:
			configData = json.load(json_config_file)
			try:
				user_login = configData['user']
			except:
				printLog(json_read_error + 'user')
			
			try:
				client_id = configData['client_id']
			except:
				printLog(json_read_error + 'client_id')
			
			try:
				client_secret = configData['client_secret']
			except:
				printLog(json_read_error + 'client_secret')
			
			try:
				token_stale_age = int( configData['token_stale_age'] )
			except:
				printLog(json_read_error + 'token_stale_age')
			
			try: 
				update_interval = int( configData['update_interval'] )
			except:
				printLog(json_read_error + 'update_interval')
			
			try:
				num_pixels = int( configData['num_pixels'] )
			except:
				printLog(json_read_error + 'num_pixels')
			
			try:
				live_color = eval( str(configData['live_color'] ) )
			except:
				printLog(json_read_error + 'live_color')

			try:
				led_brightness = eval( configData['led_brightness'] )
			except:
				printLog(json_read_error + 'led_brightness')
			
			try:
				num_rows = int( configData['num_rows'] )
			except:
				printLog(json_read_error + 'num_rows')
			
			try:
				num_columns = int( configData['num_columns'] )
			except:
				printLog(json_read_error + 'num_columns')

		led_brightness= clamp( (led_brightness * MAX_HARDWARE_BRIGHTNESS), 0, MAX_HARDWARE_BRIGHTNESS )
		#printLog( 'Brightness set to ' + str(led_brightness) )

		pixels = neopixel.NeoPixel(
		    pixel_pin, num_pixels, brightness=led_brightness, auto_write=False, pixel_order=ORDER
			)

	else:
		printLog('ERROR: Configuration file not found, using default parameters. Will most likely break')

tryLoadConfig()

###### Instantiate Neopixels & Graphics

def pixelFlood(color):
	pixels.fill(color)
	pixels.show()

def pixelClear():
	pixels.fill((0,0,0))
	pixels.show()


### Convert screenspace to strip number ###
def isEven(num):
	return ( (num % 2) == 0 )

def screenPixelInRange( pos=(0.0,0.0) ):
	resultx = pos[0] >= 0.0 and pos[0] <= 1.0
	resulty = pos[1] >= 0.0 and pos[1] <= 1.0
	return resultx and resulty

def pixelScrToStrip( screenspace_pos=(0.0 ,0.0) ): #Converts normalized screen-space coordinates to nearest strip pixel. Check documentation for wiring setup.
	global num_pixels
	global num_rows
	global num_columns
	
	if screenPixelInRange(screenspace_pos):

		if isEven(num_columns):
			column = clamp(
				int( screenspace_pos[0] * float(num_columns) ),
				0,
				num_columns - 1
				)
		else:
			column = clamp(
				round( screenspace_pos[0] * float(num_columns) ),
				0,
				num_columns - 1
				)
		
		if isEven(num_rows): #I haven't actually tested this
			row = int( screenspace_pos[1] * float(num_rows) )
		else:
			row = round( screenspace_pos[1] * float(num_rows) )

		rowOffset = clamp( (row - 1), 0, num_rows ) * num_columns

		if isEven(row) and (row > 0):
			nearest_pixel = rowOffset + ( num_columns - column ) - 1
		else:
			nearest_pixel = rowOffset + column

		nearest_pixel = clamp( (nearest_pixel), 0, num_pixels - 1 )

		#print( 'row: ' + str(row) + ' rowOffset: ' + str(rowOffset) + ' column: ' + str(column) + ' nearest_pixel: ' + str(nearest_pixel) + 'isEven(): ' + str(isEven(row)) + ' row > 0: ' + str(row > 0) ) #uncomment this for debug

		return nearest_pixel
	else:
		return -1

def drawToScreen( color=(255,255,255), pos=(0.0,0.0) ): #Draws a color to the nearest strip pixel using screen-space coordinates
	nearest_pixel = pixelScrToStrip( screenspace_pos=pos )
	if nearest_pixel >= 0:
		try:
			pixels[nearest_pixel] = color
			pixels.show()
		except IndexError:
			pass
### End Convert screenspace to strip number ###

# Smooth fades
def pixelFadeIn(color,length):
	for x in range(0,256,16):
		output_color = (
			saturate( int( (x*color[0]) / 255 ) ),
			saturate( int( (x*color[1]) / 255 ) ),
			saturate( int( (x*color[2]) / 255 ) )
			)
		pixels.fill((output_color))
		pixels.show()
		time.sleep(length/TARGET_FRAMERATE)
	pixels.fill((color))
	pixels.show()

def pixelFadeOut(color,length):
	for x in range(256,0,-16):
		output_color = (
			saturate( int((x*color[0]) / 255) ),
			saturate( int((x*color[1]) / 255) ),
			saturate( int((x*color[2]) / 255) )
			)
		pixels.fill((output_color))
		pixels.show()
		time.sleep(length/TARGET_FRAMERATE)
	pixels.fill((0,0,0))
	pixels.show()

# Flash entire array
def pixelFlash(color=(255,255,255), numFlashes=4, onTime=0.1, offTime=0.1):
	i = 0
	while i < numFlashes:
		pixels.fill(color)
		pixels.show()
		time.sleep(onTime)
		pixels.fill((0,0,0))
		pixels.show()
		time.sleep(offTime)
		i += 1

# Random flashing
def pixelRandom( color=(255,255,255 ), numIterations=8, flashDots= 3, onTime=0.05, offTime=0.1 ):
	i = 0
	while i < numIterations:
		randomdots = random.sample( range( 0, (num_pixels-1) ), flashDots)
		for x in randomdots:
			try:
				pixels[x] = color
			except IndexError:
				pass
			pixels.show()
		i += 1
		
		time.sleep(onTime)
		pixelClear()
		time.sleep(offTime)

#sequential with a soft fade tail
def pixelSequential(color=(255,98,0), length=2.0, fadeLength=4, reverse=False, clearPrevious=True, hold=False):

	padding = fadeLength * 2
	start = 0 - padding
	stop = num_pixels + padding
	step = 1

	#Loop
	for x in range(start,stop,step):

		if reverse:
			x = ( num_pixels - x ) - 1
		else:
			pass

		fadeLength = clamp(fadeLength, 1, fadeLength)

		#Fade
		if fadeLength > 1:
			for y in range(fadeLength):
				brightnessScalar =  1.0 - ( float(y) / float(fadeLength) ) ** 0.5
				try:
					colorResult = [
						int( clamp( ( float( color[0] ) * brightnessScalar ), 0.0, 256.0 ) ),
						int( clamp( ( float( color[1] ) * brightnessScalar ), 0.0, 256.0 ) ),
						int( clamp( ( float( color[2] ) * brightnessScalar ), 0.0, 256.0 ) )
						]
					if not reverse:
						if 0 <= ( x - y ) < num_pixels:
							pixels[ x - y ] = colorResult
					else:
						if 0 <= x <= num_pixels:
							pixels[ x + y ] = colorResult
				except IndexError:
					pass
		else:
			pass

		#Brightest Pixel - the Fade also sets this so this overwrites that value
		try:
			if 0 <= x <= num_pixels:
				pixels[x] = color
			else:
				pass
		except IndexError:
			pass

		#Clear Previous
		if clearPrevious:
			try:
				if not reverse:
					pixels[ x - fadeLength] = (0,0,0)
				else:
					pixels[ x + fadeLength] = (0,0,0)
			except IndexError:
				pass
		else:
			pass

		pixels.show()
		time.sleep( ( 1 / num_pixels)  * length )
	if not hold:
		pixelClear()

def pixelDrawColumn(color=(255,255,255), posX=0.0 ):
	for y in range(num_rows):
			drawToScreen(color=color, pos=(posX, ( float(y) / float(num_rows-1) ) ))

# Horizontal Wipe
def pixelHorizontalWipe(color=(255,98,0), length=1.0, fadeLength=0.0, reverse=False, clearPrevious=False, hold=True): #I couldn't get fade length to work properly for this... maybe because it's converting floating point screenspace to integer and I'm not sure how python does this intrinsically?
	global num_columns
	global num_rows

	fadeLength = clamp(fadeLength, 0.01, fadeLength)

	padding = int((fadeLength * float(num_columns) )) * 2
	start = 0 - padding
	stop = num_columns + padding
	step = 1

	for x in range(start, stop, step):

		x2 = float(x) / float(num_columns-1)

		if reverse:
			x2 = 1 - x2
		else:
			pass

		if fadeLength > 0.01:
			for y in range( int( fadeLength + float(num_columns) ) ):
				brightnessScalar =  1.0 - ( (float(y) / num_columns) / fadeLength ) ** 0.1
				colorResult = [
					int( clamp( ( float( color[0] ) * brightnessScalar ), 0.0, 256.0 ) ),
					int( clamp( ( float( color[1] ) * brightnessScalar ), 0.0, 256.0 ) ),
					int( clamp( ( float( color[2] ) * brightnessScalar ), 0.0, 256.0 ) )
					]
				if not reverse:
					pixelDrawColumn( color=colorResult, posX=(x - y))
				else:
					pixelDrawColumn( color=colorResult, posX=(x + y))
		else:
			pass

		#Brightest Column - the Fade also sets this so this overwrites that value
		pixelDrawColumn(color=color, posX=x2)

		#Clear Previous
		if clearPrevious:
			if not reverse:
				pixelDrawColumn( color=(0,0,0), posX=( x2 - (fadeLength+(1/num_columns))) )
				pixelDrawColumn( color=(0,0,0), posX=( x2 - (fadeLength+(1/num_columns))) )
			else:
				pixelDrawColumn( color=(0,0,0), posX=( x2 + (fadeLength+(1/num_columns))) )
				pixelDrawColumn( color=(0,0,0), posX=( x2 + (fadeLength+(1/num_columns))) )
		else:
			pass

		time.sleep( (1 / (num_columns * 2) )  * length ) #this is probably wrong, length should be the length of the total animation but my brain is fried
	if not hold:
		pixelClear()

def pixelError():
	pixelFlash((255,0,0),6,0.25,0.1)

# Attempt to authenticate using Client ID and secret to obtain a token
def pixelAuth():
	pixelFlash((148,0,255),3,0.2,0.2)

def pixelAuthSuccess():
	pixelFlash((0,255,0),4,0.1,0.1)

# Stream went ONLINE but previously was offline
def pixelLiveChanged():
	pixelRandom( live_color, 8, 5, 0.05, 0.05 )
	time.sleep(0.5)
	pixelFadeIn( live_color, 1.0)

# Stream went OFFLINE but previously was online
def pixelOffChanged():
	pixelFlash(live_color, 1, 0.05, 0.5)
	pixelFadeOut( live_color, 1.0)

# Start sequence = the Fadein/Out acts as a full array self-test
def pixelStart():
	pixelRandom( (255,98,0), 4, 6, 0.15, 0.3 )
	time.sleep(0.5)
	pixelFadeIn( (255,255,255),1.0 )
	pixelFadeOut( (255,255,255),1.0 )

###### Function Definitions ######

#update datetime
def updateTime():
	# get the current datetime time and format it - we want to update our global variables for current time
	global a_datetime
	global formatted_datetime
	global json_datetime

	a_datetime = datetime.datetime.now()
	formatted_datetime = a_datetime.isoformat()
	json_datetime = json.dumps(formatted_datetime)

# does token exist?
def tokenFileExist():
	return os.path.isfile('config/twitch_appaccesstoken.json')

# open the token file
def openTokenFile(return_token):
	updateTime()
	with open('config/twitch_appaccesstoken.json') as json_file:
		data = json.load(json_file)
		for p in data['tokens']:

			# time difference
			current_time = pd.to_datetime(formatted_datetime)
			unformatted_stored_time = p['time']
			stored_time = pd.to_datetime(unformatted_stored_time,infer_datetime_format=True, errors='coerce')
			difference = current_time - stored_time

			#printLog( 'App Access Token: ' + p['token'])
			#printLog( 'Stored Time: ' + str(stored_time) )
			#printLog( 'Current Time: ' + str(current_time) )
			#printLog( 'Time Since Token: ' + str(difference) )
			#printLog( 'Days Since Token: ' + str(difference.days) )

			if return_token:
				return p['token']
			else:
				return int(difference.days)



def createTokenFile():
	pixelAuth()
	updateTime()
	data = {
	    'client_id': client_id,
	    'client_secret': client_secret,
	    'grant_type': 'client_credentials',
	}

	response = requests.post('https://id.twitch.tv/oauth2/token', data=data)

	ResponseJson = response.json()

	if 'access_token' in ResponseJson:
		ResponseToken = ResponseJson['access_token']
		ResponseTokenObfuscated = ResponseToken.replace( ( str(ResponseToken) )[0:26], 'xxxxxxxxxxxxxxxxxxxxxxxxxx' )

		printLog('Token fetched: ' + ResponseTokenObfuscated)
		pixelAuthSuccess()

		#store the current token and date into file

		# construct our data json
		data = {}
		data['tokens'] = []
		data['tokens'].append({
		    'token': ResponseToken,
		    'time': json_datetime.strip('\"'),
		})

		with open('config/twitch_appaccesstoken.json', 'w') as outfile:
		    json.dump(data, outfile)

	else:
		printLog(str(ResponseJson))
		printLog('createTokenFile(): Error Creating Token')
		#pixelError() main loop already calls this

	time.sleep(1.0) #delay this so the user can tell what's happening; no longer needed once we play a proper animation later

def checkConfigUpdate():
	changed = os.path.isfile('temp/twitch_onair_config_updated.txt')
	if changed:
		os.remove('temp/twitch_onair_config_updated.txt')
	return changed	

def isLive(user_login):
	global first_loop
	updateTime()
	token_file_exists = tokenFileExist()
	if token_file_exists:

		token_age = openTokenFile(0)

		if token_age <= token_stale_age:
			printLog('Access token is valid. Age: ' + str(token_age) + ' days')
			app_access_token = openTokenFile(1)
			if first_loop:
				pixelAuthSuccess()
				first_loop = False

		else:
			printLog('Token is stale, fetching new access token. age: ' + str(token_age) + ' days')
			createTokenFile()
			if tokenFileExist():
				app_access_token = openTokenFile(1)
				first_loop = False

	else:
		printLog('Token doesn\'t exist. fetching new access token')
		createTokenFile()
		if tokenFileExist():
			app_access_token = openTokenFile(1)
			first_loop = False

	if tokenFileExist():
		headers = {
		    'Authorization': 'Bearer ' + app_access_token,
		    'Client-Id': client_id,
		}

		url = 'https://api.twitch.tv/helix/streams?user_login=' + user_login
		try:
			response = requests.get(url, headers=headers)
			ResponseJson = response.json()

			if 'data' in ResponseJson:
				return len(ResponseJson['data'])
			else:
				return (-1)
		except:
			if CONNREFUSE_Loop < CONNREFUSE_MAX_LOOPS:
				printLog("Connection Refused by the server... Sleeping for " + CONNREFUSE_WAIT_TIME + "seconds. This is attempt " + CONNREFUSE_Loop + "/" + CONNREFUSE_MAX_LOOPS + ". Neopixel service will restart when CONNREFUSE_MAX_LOOPS is reached.")
				CONNREFUSE_Loop += 1
				
				# Extra careful here just in case user injects a bad time into this part
				wait_time = (CONNREFUSE_WAIT_TIME - clamp( update_interval, 0.5, update_interval+0.5 ))
				wait_time_clamped = clamp(wait_time, 0.5, wait_time)
				
				time.sleep( wait_time_clamped )
				printLog("Continuing with next connection...")
				return (-2)
			else:
				os.system('python3 twitch_onair_neopixel.py')

	else:
		return (-2)

###### State machine

live = 0
previous_live = 0

###### Debug Functions

def debugLive(user_login):
	global live
	live = isLive(user_login)
	if live == 1:
		printLog(user_login + ' is live')
	elif live == 0:
		printLog(user_login + ' is offline')
	else:
		printLog('main: Authentication Error')
		
###### Stop
def stopLive():
	printLog('')
	printLog('Stopping Twitch ON AIR Service...')
	pixelClear()

###### debug
# Uncomment below if you just want to print to terminal
#debugLive(twitch_user_login)

##### Startup

# Only allow a single instance of this
def tryKillNeopixelService():
    print('twitch_onair_neopixel: Killing Neopixel Service...')
    pidResult = pid.tryReadPID('neopixel')
    if pidResult >= 0:
        os.system('sudo kill ' + str(pidResult))
        pixelClear()
        pid.delPID('neopixel')
    else:
        pass

tryKillNeopixelService()

pid.writePID('neopixel') #filename is referenced by twitch_onair_webserver - make sure these are synchronized

pixelStart()

###### Main Loop
# Set below to false if you want to disable the main loop... for whatever reason (debug only?)
enable_main = True

if enable_main:
	try:
	    while True:
	        live = isLive(user_login)

	        if checkConfigUpdate():
	        	pixelClear()
	        	pixelHorizontalWipe(color=live_color,length=0.25)
	        	time.sleep(0.2)
	        	pixelFadeOut(color=live_color,length=0.25)
	        	time.sleep(0.5)

	        if live >= 1:
	        	printLog(user_login + ' is live')
	        	if previous_live != live: #Did our live status change from the last check?
	        		printLog('Live status has changed, calling pixelLiveChanged()')
	        		pixelLiveChanged()
	        	else:
	        		pixelFlood(live_color)
	        elif live == 0:
	        	printLog(user_login + ' is offline')
	        	if previous_live != live: #Did our live status change from the last check?
	        		printLog('Live Status changed, calling PixelOffChanged()')
	        		pixelOffChanged()
	        	else:
	        		pixelClear()
	        else:
	        	printLog('main(): Authentication Error')
	        	pixelError()

	        previous_live = live
	        update_interval = clamp(update_interval, 0.5, update_interval+0.5 ) # Clamp minimum to not kill CPu
	        
	        time.sleep(update_interval) # Delay in the loop to not kill CPU
	        
	        #printLog('Update Interval: ' + str(update_interval) + ' seconds')

	        tryLoadConfig();
	        print('Heartbeat, PID: ' + str(os.getpid())) # Debugging

	except KeyboardInterrupt:
		stopLive()
		pixelSequential(color=(255,98,0),reverse=True)
		printLog('Keyboard Interrupt')

	except Exception:
		print("Exception in twitch_onair_neopixel.py")
		print("-"*60)
		traceback.print_exc(file=sys.stdout)
		print("-"*60)
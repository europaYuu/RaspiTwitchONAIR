# Get Stream Status from Twitch - Webserver
#
# Requires registration of a Twitch Application. For more information, go to https://dev.twitch.tv/docs/api/ "Getting Started with the Twitch API". Leaving OAuth Redirect URL to http://localhost seems to work, but please let me know on twitter if this is bad practice.
# This script uses the OAuth Client Credentials Flow, which doesn't require a UI to authenticate

print('\n///////////////////////////////////')
print('Starting Twitch ON AIR WebServer...')
print('///////////////////////////////////')
print(' ')

###### store PID so it can be killed easily by the powerButton.py
import pid #store PID in file so webserver can kill if needed
pid.writePID('webserver') #filename is referenced by powerButton - make sure these are synchronized

import os
import datetime
from flask import Flask, render_template, request, url_for, redirect, send_from_directory
import json
import time
import socket
import pid
import update

import colorsys

###### neopixels - just so we can shut it down if needed
import board
import neopixel

###### Misc
def clamp(n, smallest, largest): return max(smallest, min(n, largest))
def saturate(n): return clamp(n, 0,255) # I miss HLSL
def lerp(a=1.0, b=1.0, f=0.5): return (a * (1.0 - f)) + (b * f);

### 2D Vector Distance
def distance2D(vec1=(0.0,0.0),vec2=(0.0,0.0)):
    vec1x = vec1[0]
    vec1y = vec1[1]
    vec2x = vec2[0]
    vec2y = vec2[1]

    a = (vec2x-vec1x) ** 2.0
    b = (vec2y-vec1y) ** 2.0
    ab = a + b
    abClamp = clamp(ab, 0.0001, ab)

    return math.sqrt(abClamp)

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

def rgb2hsv(r,g,b):
    rf = float(r)
    gf = float(g)
    bf = float(b)
    rgb = ( (rf / 255.0), (gf / 255.0), (bf / 255.0) )
    return colorsys.rgb_to_hsv( rgb[0], rgb[1], rgb[2] )

import socket
testIP = "8.8.8.8"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((testIP, 0))
ipaddr = s.getsockname()[0]
host = socket.gethostname()
print ("IP:", ipaddr, " Host:", host)

###### neopixels - just so we can shut it down if needed
import board
import neopixel

#######################################
############ CONFIGURATION ############
#######################################

# Webserver 
SERVER_PORT = "8000"
host_url = ipaddr + ':' + SERVER_PORT

# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18

# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

#max brightness to limit power consumption and heat - match with twitch_onair_neopixel.py
MAX_HARDWARE_BRIGHTNESS = 0.33

###### Defaults
user_login = "europayuu"
client_id = "<CLIENT_ID>"
client_secret = "<CLIENT_SECRET>"
token_stale_age = "30"
update_interval = "10"
num_pixels = "24"
live_color = "(255,0,0)"
off_color = "(0,0,0)"
led_brightness = "0.3"
placeholder_secret = "*****" #not stored
num_rows = "3"
num_columns = "8"
TARGET_FRAMERATE = 20 # For effects that take a time input

# Debug Log. set to True if you want debug file output
def tryMakeLogDir():
    current_path = os.getcwd()
    path = current_path + '/logs'
    try:
        os.mkdir(path, 0o777)
    except:
        pass

tryMakeLogDir()

ENABLE_DEBUG_LOG = False
DEBUG_LOG_FILENAME = 'logs/twitch_onair_webserver_log.txt'

#default config
pixels = neopixel.NeoPixel(
    board.D18,
    24,
    brightness=0.3,
    auto_write=False,
    pixel_order=ORDER
    )

def tryMakeConfigDir():
    current_path = os.getcwd()
    path = current_path + '/config'
    try:
        os.mkdir(path, 0o777)
    except:
        pass

#######################################
########## END CONFIGURATION ##########
#######################################

# Initial state machine
last_config_file_time = "-1"

# Defaults
def setDefaults():
    global user_login
    global client_id
    global client_secret
    global token_stale_age
    global update_interval
    global num_pixels
    global live_color
    global off_color
    global led_brightness
    global num_rows
    global num_columns

    user_login = "europayuu"
    client_id = "<CLIENT_ID>"
    client_secret = "<CLIENT_SECRET>"
    token_stale_age = "30"
    update_interval = "10"
    num_pixels = "24"
    live_color = "(255,0,0)"
    off_color = "(0,0,0)"
    led_brightness = "0.3"

######## DEBUG LOG ########
if ENABLE_DEBUG_LOG:
    import logging
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, level=logging.DEBUG)

def printLog(message='',alsoprint=True,level='debug'):
    if ENABLE_DEBUG_LOG:
        if level == 'debug':
            logging.info(message)
        elif level == 'info':
            logging.info(message)
        else:
            logging.warning(message)
    else:
        pass
    if alsoprint:
        print(message)

###### HEX <-> RGB conversions

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  
  return tuple(rgb)

def rgb_to_hex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

###### check for config file
def tryLoadConfig():
    global user_login
    global client_id
    global client_secret
    global token_stale_age
    global update_interval
    global num_pixels
    global live_color
    global off_color
    global led_brightness
    global num_rows
    global num_columns

    json_read_error = 'Webserver: Error reading key value. Default key value used for '

    tryMakeConfigDir()
    config_file_exists = os.path.isfile('config/twitch_onair_config.json')
    if config_file_exists:

        ### Did the file change from last time?
        global last_config_file_time
        config_moddate = os.stat('config/twitch_onair_config.json') [8] # there are 10 attributes this call returns and you want the next to last
        # format our timestamp
        timestamp = datetime.datetime.fromtimestamp(config_moddate).strftime('%Y-%m-%dT%H:%M:%S')
        # For debugging file modification detection
        #print('******** config file modified date: ' + timestamp + " ********")

        if timestamp != last_config_file_time:
            printLog ('Webserver: Configuration file found. Loading Config. Modified: ' + timestamp.replace("T", " ") )
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
                    off_color = eval( str(configData['off_color'] ) )
                except:
                    printLog(json_read_error + 'off_color')

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

                last_config_file_time = timestamp

        else:
            printLog('Webserver: No changes in configuration file. Config Load Skipped.')

    else: #create default config file
        print('Webserver: Configuration file doesn\'t exist. Creating...')
        writeConfig()
        print('Webserver: Default Configuration File Created.')

def writeChangeFile():
    f = open("temp/twitch_onair_config_updated.txt", "w")
    f.write("temp")
    f.close()

def writeConfig():
    data = {
        'user': user_login,
        'client_id': client_id,
        'client_secret': client_secret,
        'token_stale_age': token_stale_age,
        'update_interval': update_interval,
        'num_pixels': num_pixels,
        'live_color': live_color,
        'off_color': off_color,
        'led_brightness': led_brightness,
        'num_rows': num_rows,
        'num_columns': num_columns
    }
    with open('config/twitch_onair_config.json', 'w') as outfile:
        json.dump(data, outfile)
    print( 'Config Written')
    writeChangeFile()

def deleteConfig():
    try:
        os.remove('config/twitch_onair_config.json')
        print('Saved Config Deleted')
    except:
        print('Failed to delete Saved Config. Does it exist?')
        pass
    deleteToken()
    writeChangeFile()

def deleteToken():
    try:
        os.remove('config/twitch_appaccesstoken.json')
        print('App Access Token Deleted')
    except:
        print('Unable to delete App Access Token. Does it exist?')
        pass
    #writeChangeFile()

# Used to check even / odd rows of pixels since the wiring makes the X-direction alternate
def isEven(num): return ( (num % 2) == 0 )

def getTickLength(framerateDivider=1.0):
    global TARGET_FRAMERATE
    return 1.0 / ( float(TARGET_FRAMERATE) / framerateDivider )

### Pixel Index to Screen UV
# Returns normalized screen space coordinates from a pixel strip ID input
def stripToUV(pixel=0):
    global num_pixels
    global num_rows
    global num_columns

    fpixel = float(pixel)
    fnum_rows = float(num_rows)
    fnum_columns = float(num_columns)

    posy = ( fnum_rows / (fnum_rows - 1.0) ) * ( float( int(fpixel / num_columns) ) / fnum_rows )
    posx = ( ( fnum_columns / (fnum_columns - 1.0) ) * ( fpixel % fnum_columns ) ) / fnum_columns 
    
    row = int( int(posy * fnum_rows) )
    if row != num_rows:
        row += 1

    if isEven( row ):
        posx = 1.0 - posx

    return (posx,posy)

def pixelClear():
    tryLoadConfig()
    pixels = neopixel.NeoPixel(
        pixel_pin, int(num_pixels), brightness=float(led_brightness), auto_write=False, pixel_order=ORDER
        )
    pixels.fill((0,0,0))
    pixels.show()

def pixelSequential(color=(255,98,0), length=2.0, fadeLength=4, reverse=False, clearPrevious=True, hold=False): #copied from twitch_onair_neopixel

    tryLoadConfig()
    pixels = neopixel.NeoPixel(
        pixel_pin, int(num_pixels), brightness=float(led_brightness), auto_write=False, pixel_order=ORDER
        )

    padding = fadeLength * 2 #clamp(fadeLength, 2, (fadeLength+2))
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

        #Brightest Pixel
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

### Draw rainbow
# 0 = horizontal, 1 = vertical
def drawRainbow(offset=0.0,scale=1.0, direction=0):
    global num_pixels
    global num_rows
    direction = clamp(direction, 0, 1) #never trust the users, they are evil
    for x in range(num_pixels):
        u = ( stripToUV(x) )[direction]
        u = u / ( 1 + (1 / num_rows) )
        u = u * scale
        u = u + offset
        colorResult = hsv2rgb(u,1.0,1.0)
        pixels[x] = colorResult
    pixels.show()

### Scrolling Rainbow
def drawAnimateRainbow(length=1.0, framerateDivider=1.0, scale=1.0, reverse=False, direction=0):
    tick = getTickLength(framerateDivider=framerateDivider)
    loops = int( length / tick)
    for i in range(loops):
        a = float(i) / float(loops)
        if reverse:
            a = 1 - a
        drawRainbow(offset=a, scale=scale, direction=direction)
        time.sleep(tick)

def tryKillNeopixelService():
    print('twitch_onair_webserver: Killing Neopixel Service...')
    #pidResult = pid.tryReadPID('neopixel')
    #if pidResult >= 0:
    #    pid.killPIDWithScript(pidResult, script='twitch_onair_neopixel.py')
    #    pixelSequential(length=1.0, reverse=True)
    #    pixelClear()
    #    pid.delPID('neopixel')
    #else:
    #    pass
    try:
        os.system('sudo systemctl stop twitch_onair_neopixel_service.service')
        pixelSequential(length=1.0, reverse=True)
        pixelClear()
    except:
        pass

def startNeopixelService():
    print('twitch_onair_webserver: Starting Neopixel Service...')
    os.system('sudo python3 twitch_onair_neopixel.py &')

def restartSystemLED():
    tryKillNeopixelService()
    startNeopixelService()

###### Startup
tryLoadConfig()
version_local = update.getVersion('VERSION')

###### Flask webapp
app = Flask(__name__, static_url_path='',
    static_folder='static')

@app.route('/', methods=['GET', 'POST'])
def index():
    global user_login
    global client_id
    global client_secret
    global token_stale_age
    global update_interval
    global num_pixels
    global live_color
    global off_color
    global led_brightness
    global num_rows
    global num_columns

    if request.method == 'POST':
        user_login = request.form['user_login'][:30]
        client_id = request.form['client_id'][:60]
        
        # Only update client_secret if it's not the server-obfuscated value
        POST_secret = request.form['client_secret'][:60]

        if POST_secret != placeholder_secret:
            print('POST_secret updated. Updating client_secret and invalidating token...')
            client_secret = POST_secret
            deleteToken()
        else:
            print('No change to POST_secret. client_secret not updated.')
            pass
        
        token_stale_age = request.form['token_stale_age']
        update_interval = request.form['update_interval']
        num_pixels = request.form['num_pixels'][:9]
        
        led_brightness = request.form['led_brightness']

        # hex -> rgb
        live_color_picker_hex = ( request.form['live_color_picker'] )[1:]
        live_color = hex_to_rgb(live_color_picker_hex)
        live_color = (
            saturate( live_color[0] ),
            saturate( live_color[1] ),
            saturate( live_color[2] )
            )

        off_color_picker_hex = ( request.form['off_color_picker'] )[1:]
        off_color = hex_to_rgb(off_color_picker_hex)
        off_color = (
            saturate( off_color[0] ),
            saturate( off_color[1] ),
            saturate( off_color[2] )
            )

        writeConfig()
        tryLoadConfig()

        try:
            live_color_hex = rgb_to_hex( (live_color[0]),(live_color[1]),(live_color[2]) )
        except:
            live_color_hex = "#ff0000"

        try:
            off_color_hex = rgb_to_hex( (off_color[0]),(off_color[1]),(off_color[2]) )
        except:
            off_color_hex = "#000000"

        return render_template('index.html',
            user_login_value=user_login,
            client_id_value=client_id,
            client_secret_value=placeholder_secret,
            token_stale_age_value=token_stale_age,
            update_interval_value=update_interval,
            num_pixels_value=num_pixels,
            live_color_picker_value=live_color_hex,
            off_color_picker_value=off_color_hex,
            neon_color=live_color_hex,
            neon_color2=live_color_hex,
            brightness_value=led_brightness,
            num_rows_value=num_rows,
            num_columns_value=num_columns,
            version=version_local
            )

    else:
        tryLoadConfig()

        try:
            live_color_hex = rgb_to_hex( (live_color[0]),(live_color[1]),(live_color[2]) )
            #print(live_color_hex)
        except:
            live_color_hex = "#ff0000"

        try:
            off_color_hex = rgb_to_hex( (off_color[0]),(off_color[1]),(off_color[2]) )
        except:
            off_color_hex = "#000000"

        return render_template('index.html',
            user_login_value=user_login,
            client_id_value=client_id,
            client_secret_value=placeholder_secret,
            token_stale_age_value=token_stale_age,
            update_interval_value=update_interval,
            num_pixels_value=num_pixels,
            live_color_picker_value=live_color_hex,
            off_color_picker_value=off_color_hex,
            neon_color=live_color_hex,
            neon_color2=live_color_hex,
            brightness_value=led_brightness,
            num_rows_value=num_rows,
            num_columns_value=num_columns,
            version=version_local
            )

@app.route('/reset', methods=['GET', 'POST'])
def reset():

    deleteConfig()
    setDefaults()

    return render_template('bye.html', message="Configuration Reset")

@app.route('/restart', methods=['GET', 'POST'])
def restart():

    print('restart')
    tryKillNeopixelService()
    time.sleep(1.0)
    pixelClear()
    time.sleep(0.25)
    os.system('sudo shutdown -r now')

    return render_template('bye.html', message="Restarting...")

@app.route('/restartled', methods=['GET', 'POST'])
def restartLED():

    print('restart LEDs')
    restartSystemLED()

    return render_template('bye.html', message="Restarting LEDs...")

@app.route('/killled', methods=['GET', 'POST'])
def killLED():

    print('kill LEDs')
    tryKillNeopixelService()

    tryLoadConfig()

    try:
        live_color_hex = rgb_to_hex( (live_color[0]),(live_color[1]),(live_color[2]) )
    except:
            live_color_hex = "#ff0000"

    try:
        off_color_hex = rgb_to_hex( (off_color[0]),(off_color[1]),(off_color[2]) )
    except:
        off_color_hex = "#000000"

    return render_template('index.html',
        user_login_value=user_login,
        client_id_value=client_id,
        client_secret_value=placeholder_secret,
        token_stale_age_value=token_stale_age,
        update_interval_value=update_interval,
        num_pixels_value=num_pixels,
        live_color_picker_value=live_color_hex,
        off_color_picker_value=off_color_hex,
        neon_color=live_color_hex,
        neon_color2=live_color_hex,
        brightness_value=led_brightness,
        num_rows_value=num_rows,
        num_columns_value=num_columns,
        version=version_local
        )

@app.route('/deltoken', methods=['GET', 'POST'])
def deltoken():

    deleteToken()

    return render_template('bye.html', message="Refreshing Token...")

@app.route('/checkupdate', methods=['GET', 'POST'])
def checkUpdate():

    print('Checking for Updates...')
    if update.CheckUpdateNeeded():
        return render_template('update.html', message="New Version: " + update.GetRemoteVersion() + " Update Now?")

    else:
        return render_template('bye.html', message="No Update Needed")

@app.route('/update', methods=['GET', 'POST'])
def Update():
    return render_template('doupdate.html', message="Updating... Please don't refresh this page or go back in your browser.")

@app.route('/doupdate', methods=['GET', 'POST'])
def doUpdate():
    if update.CheckUpdateNeeded():
        tryKillNeopixelService()
        drawAnimateRainbow(length=3.0)
        pixelClear()
        os.system('sudo python3 doUpdate.py')
        os.system('sudo shutdown -r now')

    tryLoadConfig()

    try:
        live_color_hex = rgb_to_hex( (live_color[0]),(live_color[1]),(live_color[2]) )
    except:
            live_color_hex = "#ff0000"

    try:
        off_color_hex = rgb_to_hex( (off_color[0]),(off_color[1]),(off_color[2]) )
    except:
        off_color_hex = "#000000"

    return render_template('index.html',
        user_login_value=user_login,
        client_id_value=client_id,
        client_secret_value=placeholder_secret,
        token_stale_age_value=token_stale_age,
        update_interval_value=update_interval,
        num_pixels_value=num_pixels,
        live_color_picker_value=live_color_hex,
        off_color_picker_value=off_color_hex,
        neon_color=live_color_hex,
        neon_color2=live_color_hex,
        brightness_value=led_brightness,
        num_rows_value=num_rows,
        num_columns_value=num_columns,
        version=version_local
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT)
print('\nYoutube Channel Live Check...')

#https://www.youtube.com/channel/CHANNEL_ID/live

import requests #For making cURL requests
from bs4 import BeautifulSoup
import json
import time

######## Channel ID, NOT name
# Test IDs
# Europa Yuu: UC5Ejf_RIWMVDAjA4B-GV5Zg
# Amelia Watson: UCyl1z3jo3XHR1riLFKG5UAg (She happened to be online while I was working on this code. Thank you Amelia!)
# Lofi Girl: UCSJ4gkVC6NrvII8umztf0Ow

yt_channel_id = 'UCCzUftO8KOVkV4wQG1vkUvg'

yt_url = 'https://www.youtube.com/channel/' + yt_channel_id + '/live'

# Returns 1 if user_login is online, 0 if user_login is offline, and -1 if there was an authentication error
def yt_isLive(url):
	global yt_url
	yt_live = 0
	yt_response_text = requests.get(yt_url).text
	yt_soup = BeautifulSoup(yt_response_text, 'html.parser')
	try:
		yt_soup = str( yt_soup.find("link", {"rel": "canonical"}) ) #Parse the result of our HTML link for elements exclusive to streams that are live
		print(yt_soup) #debug
		if 'watch' in yt_soup:
			# Online
			yt_live = 1
		else:
			# Offline
			pass
	except:
		# Invalid Channel ID
		yt_live = -1

	return yt_live

print( yt_isLive(yt_url) )
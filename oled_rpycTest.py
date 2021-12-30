import time
import rpyc
import math
def clamp(n, smallest, largest): return max(smallest, min(n, largest))

oled_service_connected = False
try:
	c = rpyc.connect("localhost", 18861)
	oled_service_connected = True
except:
	pass

try:
	i = -0.1
	while i < 1.1:
		formatted_percent = str( round(clamp(i,0.0,1.0)*100) )
		text = 'Percent: ' + formatted_percent
		c.root.drawProgressBar( i, text )
		time.sleep(0.1)
		i += 0.05
	c.root.clear()
except:
	pass

import update
#update.Update()
#update.RebootAfterUpdate()
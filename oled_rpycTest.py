import rpyc
oled_service_connected = False
try:
	c = rpyc.connect("localhost", 18861)
	oled_service_connected = True
except:
	pass

try:
	c.root.ExDrawTextBorder('Ohayuu')
except:
	pass
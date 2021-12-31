import board
import busio
def scani2c():
	i2c = busio.I2C(board.SCL, board.SDA)
	i2c_addr = i2c.scan()
	i2c_addresses = [ hex(device_address) for device_address in i2c.scan() ]
	return i2c_addresses[0]

print( 'I2C Address: ' + str(scani2c() ) )
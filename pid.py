import os

def tryReadPID(filename):
	filename = ('temp/pid_' + filename + '.txt')
	print('attempting to read PID for ' + filename)
	file_exists = os.path.isfile(filename)
	if file_exists:
		file = open(filename, 'r')
		pid = file.readline()
		return int(pid)
	else:
		print(filename + ' doesn\'t exist.')
		return -1

def writePID(filename):
	delPID(filename) # delete if it already exists
	pid = os.getpid()
	print('Writing PID: ' + str(pid) + ' to pid_' + filename + '.txt')
	f = open('temp/pid_' + filename + '.txt', 'w')
	f.write( str(pid) )
	f.close()

def delPID(filename):
	filename_combined = ( 'temp/pid_' + filename + '.txt' )
	print('Attempting to delete ' + filename_combined)
	try:
		os.remove(filename_combined)
		print(filename_combined + ' deleted successfully')
	except:
		print(filename_combined + ' failed to delete. Does it exist?')
		pass
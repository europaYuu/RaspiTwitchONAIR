import os
import subprocess

def tryMakeTempdir():
	current_path = os.getcwd()
	path = current_path + '/temp'
	try:
		os.mkdir(path, 0o777)
	except:
		pass

def get_pname(id):
	tryMakeTempdir()
	p = subprocess.Popen(["ps -o cmd= {}".format(id)], stdout=subprocess.PIPE, shell=True)
	return str(p.communicate()[0])

def tryReadPID(filename):
	tryMakeTempdir()
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
	tryMakeTempdir()
	delPID(filename) # delete if it already exists
	pid = os.getpid()
	print('Writing PID: ' + str(pid) + ' to pid_' + filename + '.txt')
	f = open('temp/pid_' + filename + '.txt', 'w')
	f.write( str(pid) )
	f.close()

def delPID(filename):
	tryMakeTempdir()
	filename_combined = ( 'temp/pid_' + filename + '.txt' )
	print('Attempting to delete ' + filename_combined)
	try:
		os.remove(filename_combined)
		print(filename_combined + ' deleted successfully')
	except:
		print(filename_combined + ' failed to delete. Does it exist?')

def getProcessByPID(pid="0"):
	tryMakeTempdir()
	name = get_pname( pid )
	if len(name) > 3: #process found
		return name
	else: #process not found
		return -1

def killPIDWithScript(pid=0, name="python3", script="test.py"):
	tryMakeTempdir()
	separator = '\n******\n'
	processInfo = getProcessByPID(pid)
	if processInfo != -1:
		#format the result
		processInfo = processInfo[2:]
		processInfo = processInfo[:-3]
		processInfo = processInfo.split(" ", 1)

		if processInfo[0] == name and processInfo[1] == script:
			print(separator + 'killPIDWithScript() MATCHED name: ' + name + ", script: " + script + " and PID: " + str(pid) + ". Killing..." + separator)
			# os.kill(pid, 0) #not sure why this doesnt work
			os.system('sudo kill ' + str(pid))

		else:
			print(separator + 'killPIDWithScript() UNMATCHED for name: ' + name + ", script: " + script + " and PID: " + str(pid) + ". Skipping kill..." + separator)

	elif -1:
		print(separator + 'WARNING: killPIDWithScript() Failed. Process not found' + separator)
	else: print(separator + 'WARNING: killPIDWithScript() Failed. Unknown Error.' + separator)
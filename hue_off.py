import sys
import getopt
from phue import Bridge

def main(argv):

	# IP address of your Hue Bridge
	bridgeIP = "0"
	username = ""
	createuser = False
	off_lights = []
	run = True
		

	# How often (in seconds) to check the pwrstatd log for events
	check_interval = 60

	# Parse the options
	try:
		opts, args = getopt.getopt(argv,"hb:ci:u:",["bridge=","createuser=","interval=","username="])
	except getopt.GetoptError:
		optUsage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			optUsage()
			sys.exit()
		elif opt in ("-b", "--bridge"):
			bridgeIP = arg
		elif opt in ("-c", "--createuser"):
			createuser = True
		elif opt in ("-i", "--interval"):
			check_interval = arg
		elif opt in ("-u", "--username"):
			username = arg

	"""	
	# Debugging
	print "Bridge IP: %s" % bridgeIP
	print "Createuser: %s" % createuser
	print "Username: %s" % username
	raw_input("Press enter to continue")	
	"""	

	try:
		bridge = Bridge(bridgeIP)	
	except:
		print "Error, App not registered.  Press Bridge button and try again."	

	if createuser:
		print "You've requested to create a new user.  Creating..."
		print "Press the button on your Bridge, then press Enter."
		bridge.connect()
	
	print bridge.get_api()
	raw_input("Press a key to continue")

	# Main guts of the program
	# Start an endless loop
	#while run:
	
	try:
		lights_list = bridge.get_light_objects('list')

		# Store list of lights that are currently off
		for light in lights_list:
			if not light.on:
				off_lights.append(light)
	except:
		print "Bridge unavailable"
	"""
	# Print the name of the lights that are Off
	for light in off_lights:
		print(light.name)		
	"""

	raw_input("Press Enter")



def optUsage():
	# This function displays options usage information

	print "Options Usage:"
	print "    -b, --bridge | IP address of your Hue Bridge"
	print "    -c, --createuser | Create a new user on your Hue Bridge"
	print "    -i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60"
	print "    -u, --username | Username to be used for Hue Bridge API calls"
	return 0

def getLightstatus(bridge):
	# This function will get the current status of all the Hue lights (whether or not they are on or off)
	
	lights = bridge.lights
	print lights()
	

if __name__ == "__main__":
	main(sys.argv[1:])

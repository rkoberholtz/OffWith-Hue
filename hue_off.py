import sys
import getopt
from phue import Bridge
import commands
import time

def main(argv):

	# IP address of your Hue Bridge
	bridgeIP = "0"
	username = ""
	createuser = False
	off_lights = []
	powerfailure = False
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
			check_interval = float(arg)
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
	
	# Main guts of the program
	# Start an endless loop
	while run:
	
		try:
			lights_list = bridge.get_light_objects('list')

			# Store list of lights that are currently off
			off_lights = []
			for light in lights_list:
				if not light.on:
					off_lights.append(light)
		except:
			# Bridge unavailable, Power failure?
			print "Connection to Hue Bridge has failed... is the power out?"
			powerfailure = checkPowerOutage()
	
		# Check power status
		powerfailure = checkPowerOutage()
		
		if powerfailure:
			waitSetlights(off_lights,check_interval)
		
		time.sleep(check_interval)	
		
	# End of endless loop
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

def checkPowerOutage():
	# This function checks the current pwrstatd process to see if we're on utility power or not.

	pwrstatus = commands.getstatusoutput("pwrstat -status | grep 'Power Supply'")
        if "Utility" not in pwrstatus[1]:
	        # We have a power failure!
		print "%s:Mains power: FAILURE" % datestamp()
                return True
        else:
                # No power failure... some other problem.  Don't touch the lights.
		print "%s:Mains power: OK" % datestamp()
		return False
	
def waitSetlights(off_lights,check_interval):
	# Periodically check for return to Utility power, and then turn off lights that were off prior to event.
	
	while True:
		
		outage = checkPowerOutage()
		if not outage:
			for light in off_lights:
				light.on = False
	
		time.sleep(check_interval)
	return 0

def datestamp():
	# this function returns a date string formatted as YYYYMMDD-HHMMSS
	return strftime("%Y%m%d-%H%M%S", gmtime())	

if __name__ == "__main__":

	main(sys.argv[1:])

#!/bin/python

"""
  This program uses CyberPower's pwrstatd daemon and the Phue Python library to turn
    off your Hue lights after a brief power outage.

  The program routinely query's your Hue bridge to a list of lights and stores the ones
    that are currently off.  It also queries pwrstat to determine if we are running on
    MAINS or BATTERY power.  When it detects that we are running on BATTERY power, it
    waits for MAINS power to return, then turns off the Hue lights that were off prior
    to the outage.

  Created By: 
	Rich Oberholtzer
	rich@rickelobe.com
	https://gitlab.rickelobe.com

"""

import sys
import getopt
from phue import Bridge
import commands
import time

def main(argv):

	# IP address of your Hue Bridge
	bridgeIP = "0"
	createnew = False
	off_lights = []
	powerfailure = False

	# How often (in seconds) to check the pwrstatd log for events
	check_interval = 60

	# Parse the options
	try:
		opts, args = getopt.getopt(argv,"hb:ci:",["bridge=","createnew=","interval="])
	except getopt.GetoptError:
		optUsage()
		sys.exit(2)
	except ValueError:
		print "Incorrect option usage!"
		opUsage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			optUsage()
			sys.exit()
		elif opt in ("-b", "--bridge"):
			bridgeIP = arg
		elif opt in ("-c", "--createnew"):
			createnew = True
		elif opt in ("-i", "--interval"):
			check_interval = float(arg)
	"""	
	# Debugging
	print "Bridge IP: %s" % bridgeIP
	print "Createnew: %s" % createnew
	print "Username: %s" % username
	raw_input("Press enter to continue")	
	"""	
	
	"""	
	# Read in status from last time app ran
	# 
	try:
		with open("off.lights") as f:
			prev_status = f.readlines()
		f.close()
		
	except:
		print "Error reading file."

	# Print the read-in contents of file
	for line in prev_status:
		print(line)
	
	
	raw_input("Press Enter")
	print(prev_status[1])
	raw_input("Press Enter Again")
	#if prev_status[1] == bridge:
	
	"""		

	try:
		bridge = Bridge(bridgeIP)	
	except:
		print "Error, App not registered.  Press Bridge button and try again."	

	if createnew:
		print "You've requested to connect to a new Bridge.  Connecting..."
		print "Press the button on your Bridge, then press Enter."
		bridge.connect()
	
	# Main guts of the program
	# Start an endless loop
	while True:
		
		if checkPowerOutage():
			waitSetlights(off_lights,check_interval)
		
		try:
			lights_list = bridge.get_light_objects('list')
			lights_file = open("off.lights", 'w')
			lights_file.truncate()
			lights_file.write(datestamp())
			lights_file.write("\n")
			lights_file.write(bridgeIP)
			lights_file.write("\n")
			# Store list of lights that are currently off
			off_lights = []
			for light in lights_list:
				if not light.on:
					off_lights.append(light)
					lights_file.write(light.name)
					lights_file.write("\n")
			lights_file.close()
		except:
			# Unknown exception!
			print "%s: An unknown exception has appeared..." % datestamp()
	
		#Pause	
		time.sleep(check_interval)	
		
	# End of endless loop... hmm
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
	print "    -c, --createnew | Connect to a new Hue Bridge"
	print "    -i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60"
	return 0

def checkPowerOutage():
	# This function checks the current pwrstatd process to see if we're on utility power or not.

	pwrstatus = commands.getstatusoutput("pwrstat -status | grep 'Power Supply'")
        if "Utility" not in pwrstatus[1]:
	        # We have a power failure!
		print "%s:Mains power FAILURE" % datestamp()
                return True
        else:
                # No power failure... some other problem.  Don't touch the lights.
		print "%s:Mains power OK" % datestamp()
		return False
	
def waitSetlights(off_lights,check_interval):
	# Periodically check for return to Utility power, and then turn off lights that were off prior to event.
	while True:
		# Loop in here until mains power returns
		outage = checkPowerOutage()
		if not outage:
			# Turn off the lights that were off prior to the power outage
			print "%s: ... Mains power has returned, turning off lights that were not on prior to outage:" % datestamp()
			for light in off_lights:
				print "%s: Turning off %s" % (datestamp(), light.name)
				light.on = False
			return 0
		time.sleep(check_interval)
	return 0

def datestamp():
	# this function returns a date string formatted as YYYYMMDD-HHMMSS
	return time.strftime("%Y%m%d-%H%M%S")	

if __name__ == "__main__":

	main(sys.argv[1:])

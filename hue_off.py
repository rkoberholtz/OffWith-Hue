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

Copyright (c) 2017, Richard K. Oberholtzer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
import getopt
from phue import Bridge
import subprocess
import time

def main(argv):

	# IP address of your Hue Bridge
	bridgeIP = "0"
	createnew = False
	off_lights = []
	powerfailure = False
	prev_status = []	
	username = ""
	mode = ""	# Mode Options: cyberpower, nut

	# How often (in seconds) to check the pwrstatd log for events
	check_interval = 60

	# Parse the options
	try:
		opts, args = getopt.getopt(argv,"hb:ci:m:",["bridge=","createnew=","interval=","mode="])
	except getopt.GetoptError:
		optUsage()
		sys.exit(2)
	except ValueError:
		print("Incorrect option usage!")
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
		elif opt in ("-m", "--mode"):
			mode = arg.lower()	

	'''		
	# Debugging
	print ("Bridge IP: %s" % bridgeIP)
	print ("Createnew: %s" % createnew)
	print ("Username: %s" % username)
	print ("Mode: %s" % mode)
	input("Press enter to continue")	
	'''	
	# Read in status from last time app ran
	try:
		with open("off.lights") as f:
			prev_status = f.readlines()
		f.close()
	except:
		print("Error reading file.")
	
	# Check if prev_status contains items
	if prev_status:
		if prev_status[1] == bridgeIP:
			# Same bridge as before, apply the light status!
			lights_list = bridge.get_light_objects('list')
		
			# Since the only names in the file are lights that should be off
			#  let's turn any light name in the file off.
			print("Searching off.lights for lights that were previously off...")
			for light in lights_list:
				for line in prev_status:
					if light.name == line:
						light.on = "off"
						print("Turning off: %s" % line)				
	

	try:
		bridge = Bridge(bridgeIP)	
	except:
		print("Error, App not registered.  Press Bridge button and try again.")	

	if createnew:
		print("You've requested to connect to a new Bridge.  Connecting...")
		print("Press the button on your Bridge, then press Enter.")
		bridge.connect()
	
	# Main guts of the program
	# Start an endless loop
	while True:
		
		if checkCyberPowerOutage():
			waitSetlights(off_lights,check_interval,mode)
		
		try:
			lights_list = bridge.get_light_objects('list')
			#print "Got list of lights"
			lights_file = open("off.lights", 'w')
			#print "Opened off.lights"
			lights_file.truncate()
			#print "Truncated off.lights"
			lights_file.write(datestamp())
			#print "Wrote datestamp to file"
			lights_file.write("\n")
			#print "Wrote newline"
			lights_file.write(bridgeIP)
			#print "Wrote BridgeIP"
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
			print("%s: An unknown exception has appeared..." % datestamp())
	
		#Pause	
		time.sleep(check_interval)	
		
	# End of endless loop... hmm
	"""
	# Print the name of the lights that are Off
	for light in off_lights:
		print(light.name)		
	"""

	input("Press Enter")



def optUsage():
	# This function displays options usage information

	print("Options Usage:")
	print("    -b, --bridge | IP address of your Hue Bridge")
	print("    -c, --createnew | Connect to a new Hue Bridge")
	print("    -i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60")
	print("    -m, --mode | Set the mode for checking if there's a power outage")
        print("                 Options: 'cyberpower' or 'nut'")
	return 0

def checkCyberPowerOutage():
	# This function checks the current pwrstatd process to see if we're on utility power or not.

	pwrstatus = subprocess.getstatusoutput("pwrstat -status | grep 'Power Supply'")
	if "Utility" not in pwrstatus[1]:
		# We have a power failure!
		print("%s:Mains power FAILURE" % datestamp())
		return True
	else:
        	# No power failure... some other problem.  Don't touch the lights.
		print("%s:Mains power OK" % datestamp())
		return False
def checkNutOutage():
	# This function returns True if the Nut Server sends an outage alert.
	
	#placeholder return
	return True

def waitSetlights(off_lights,check_interval,mode):
	# Periodically check for return to Utility power, and then turn off lights that were off prior to event.
	while True:
		# Loop in here until mains power returns
		
		# Determine which mode we're operating in and check for power outage accordingly
		if mode == "cyberpower":
			outage = checkCyberPowerOutage()
		elif mode == "nut":
			outage = checkNutOutage()
		#
		if not outage:
			# Turn off the lights that were off prior to the power outage
			print("%s: ... Mains power has returned, turning off lights that were not on prior to outage:" % datestamp())
			for light in off_lights:
				print("%s: Turning off %s" % (datestamp(), light.name))
				light.on = False
			return 0
		time.sleep(check_interval)
	return 0

def datestamp():
	# this function returns a date string formatted as YYYYMMDD-HHMMSS
	return time.strftime("%Y%m%d-%H%M%S")	

if __name__ == "__main__":

	main(sys.argv[1:])

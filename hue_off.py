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
import gevent

def main(argv):

	# IP address of your Hue Bridge
	bridgeIP = "0"
	createnew = False
	global off_lights
	off_lights = []
	powerfailure = False
	prev_status = []	
	username = ""
	mode = ""	# Mode Options: cyberpower, nut
	logfile = ""

	# How often (in seconds) to check the pwrstatd log for events
	check_interval = 60

	# Parse the options
	try:
		opts, args = getopt.getopt(argv,"hb:c:i:m:l",["bridge=","createnew=","interval=","mode=","logfile="])
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
			bridgeIP = arg
		elif opt in ("-i", "--interval"):
			check_interval = float(arg)
		elif opt in ("-m", "--mode"):
			mode = arg.lower()
		elif opt in ("-l", "--logfile"):
			logfile	= arg

	'''			
	# Debugging
	print ("Bridge IP: %s" % bridgeIP)
	print ("Createnew: %s" % createnew)
	print ("Username: %s" % username)
	print ("Mode: %s" % mode)
	print ("Logfile: %s" % logfile)
	input("Press enter to continue")	
	'''

	try:
		bridge = Bridge(bridgeIP)	
	except:
		print("Error, App not registered.  Press Bridge button and try again.")	

	if createnew:
		print("You've requested to connect to a new Bridge.  Connecting...")
		print("Press the button on your Bridge, then press Enter.")
		bridge = Bridge(bridgeIP)
		try:
			bridge.connect()
		except:
			print("Bridge connect failed")
		bridge.get_api()
	
	# Turn off any lights listed in the off.lights file from last run
	turnOffLights(bridge)	
	
	# Main guts of the program
	cmd = ("python3 updateLightStatus.py -b " + str(bridgeIP))
	print(cmd)
	p = subprocess.Popen(str(cmd), shell=True)
	#p = subprocess.Popen('python3 updateLightStatus.py -b 10.3.0.120', shell=True)
	print("Spun off updateLightStatus process")
	
	# Start an endless loop
	while True:
		print("Waiting for power failure")
		state = checkForPowerOutage(mode,logfile)
		if state:
			waitSetlights(bridge,check_interval,mode,logfile)
		
		#Pause	
		time.sleep(check_interval)	
	# End of endless loop... hmm

def optUsage():
	# This function displays options usage information

	print("Options Usage:")
	print("    -b, --bridge | IP address of your Hue Bridge")
	print("    -c, --createnew | Connect to a new Hue Bridge")
	print("    -i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60")
	print("    -m, --mode | Set the mode for checking if there's a power outage")
	print("                 Options: 'cyberpower' or 'nut'")
	print("    --logfile | Specify the logfile to monitor if choosing 'nut' mode")
	return 0


def turnOffLights(bridge):
	
	try:
		with open("off.lights") as f:
			prev_status = f.readlines()
		f.close()
	except:
		print("Error reading file.")

	# Check if prev_status contains items
	if prev_status:
		# Same bridge as before, apply the light status!
		lights_list = bridge.get_light_objects('list')

		# Since the only names in the file are lights that should be off
		#  let's turn any light name in the file off.
		print("Searching off.lights for lights that were previously off...")
		for light in lights_list:
			for line in prev_status:
				if light.name == line[:-1]:
					light.on = False
					print("Turning off: %s" % line)
		
	return 0

def checkForPowerOutage(mode,logfile):
	if mode == "cyberpower":
		return checkCyberPowerOutage()
	else:
		return checkNutOutage(logfile)

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


def checkNutOutage(logfile):
	# This function returns True if the Nut Server sends an outage alert.
	
	#Search for "on battery"
	if watchLog("on battery","on line power",str(logfile)):
		print("%s:Mains power FAILURE" % datestamp())
		return True
	else:
		print("%s:Mains power OK" % datestamp())
		return False
	

def watchLog(watchfortrue,watchforfalse,watchfile):
	# This function will watch watchfile (path to file in filesystem) for watchfor (string)
	#   then return the line it found
	
	f = open(watchfile, "r")
	
	f.seek(0,2) # Go to the end of the file
	while True:
		line = f.readline()
		if not line:
			time.sleep(0.1) # Sleep briefly
			continue
		if line.find(watchfortrue) >= 0:
			f.close()
			return True
		elif line.find(watchforfalse) >= 0:
			f.close()
			return False

def waitSetlights(bridge,check_interval,mode,logfile):
	# Periodically check for return to Utility power, and then turn off lights that were off prior to event.
	print("Waiting for power to return")
	while True:
		# Loop in here until mains power returns
		
		outage = checkForPowerOutage(mode,logfile)
		
		#
		if not outage:
			# Turn off the lights that were off prior to the power outage
			print("%s: ... Mains power has returned, turning off lights that were not on prior to outage:" % datestamp())
			turnOffLights(bridge)
			'''
			for light in off_lights:
				print("%s: Turning off %s" % (datestamp(), light.name))
				light.on = False
			'''
			return 0
		time.sleep(check_interval)
	return 0

def datestamp():
	# this function returns a date string formatted as YYYYMMDD-HHMMSS
	return time.strftime("%Y%m%d-%H%M%S")	

if __name__ == "__main__":

	main(sys.argv[1:])

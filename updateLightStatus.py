#!/bin/python

import sys
from phue import Bridge
import getopt
import time

def main(argv):

	bridgeIP = "0"
	check_interval = 60
	
	try:
		opts, args = getopt.getopt(argv,"b:",["bridge="])
	except getopt.GetoptError:
		optUsage()
		sys.exit(2)
	except ValueError:
		print("ULS: Incorrect option usage!")
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-b", "--bridge"):
			bridgeIP = arg
		#elif opt in ("-i", "--interval"):
			#check_interval = float(arg)
	
	#print("ULS: Bridge IP Address: %s" % bridgeIP)

	try:	
		bridge = Bridge(bridgeIP)
	except:
		print("ULS: Woah there, and error appeared!")

	while True:
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
			#off_lights = [i]
			for light in lights_list:
				if not light.on:
					#off_lights.append(light)
					lights_file.write(light.name)
					lights_file.write("\n")
			lights_file.close()
		except Exception as e:
			# Exception!
			print("%s: ULS: An exception has appeared... %s" % (datestamp(), str(e)))
			bridge.get_api()
		time.sleep(check_interval)

def datestamp():
	# this function returns a date string formatted as YYYYMMDD-HHMMSS
	return time.strftime("%Y%m%d-%H%M%S")


if __name__ == "__main__":
	main(sys.argv[1:])

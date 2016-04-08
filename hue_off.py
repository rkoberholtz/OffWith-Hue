import sys
import getopt
from qhue import Bridge
from qhue import create_new_username

def main(argv):

	# IP address of your Hue Bridge
	bridge = "0"
	username = ""
	createuser = False
	
	# How often (in seconds) to check the pwrstatd log for events
	check_interval = 60

	# Parse the options
	try:
		opts, args = getopt.getopt(argv,"hb:ciu:",["bridge=","createuser=","interval=","username="])
	except getopt.GetoptError:
		optUsage()
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			optUsage()
			sys.exit()
		elif opt in ("-b", "--bridge"):
			bridge = arg
		elif opt in ("-c", "--createuser"):
			createuser = True
		elif opt in ("-i", "--interval"):
			check_interval = arg
		elif opt in ("-u", "--username"):
			username = arg

	# Display error if user did not specify a username or ask to create one
	if (username == "") & (createuser == False):
		print "Error: No username specified!"
		sys.exit(2)
	# Display error if user specified a username AND asked to create one
	elif (username != "") & (createuser == True):
		print "Error: Can't create new user when username is specified!"
		sys.exit(2)

	# Debugging
	#print "Bridge IP: %s" % bridge
	#print "Createuser: %s" % createuser
	#print "Username: %s" % username
	#raw_input("Press enter to continue")
	
	if createuser:
		username = createUsername(bridge)

def createUsername(bridge):
	# This function will create a new user account on the Hue bridge
	# only if the '-c' argument is passed
	
	username = create_new_username("192.168.0.45")
	print "Your Username is: %s" % username
	return username

def optUsage():
	# This function displays options usage information

	print "Options Usage:"
	print "    -b, --bridge | IP address of your Hue Bridge"
	print "    -c, --createuser | Create a new user on your Hue Bridge"
	print "    -i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60"
	print "    -u, --username | Username to be used for Hue Bridge API calls"
	return 0

if __name__ == "__main__":
	main(sys.argv[1:])

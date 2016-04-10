# Prerequisits
1. *nix machine
2. **Phue** python library. Install using pip
<pre>pip install phue</pre>
3. A CyberPower UPS device connected to your machine
4. CyberPower's pwrstatd daemon (PowerPanel)
    * Download here: http://www.cyberpower-eu.com/products/software/pp_linux.htm
    
# Description
  This program uses CyberPower's pwrstatd daemon and the Phue Python library to turn
    off your Hue lights after a brief power outage.

  The program routinely query's your Hue bridge to a list of lights and stores the ones
    that are currently off.  It also queries pwrstat to determine if we are running on
    MAINS or BATTERY power.  When it detects that we are running on BATTERY power, it
    waits for MAINS power to return, then turns off the Hue lights that were off prior
    to the outage.
    
# Usage
**Example #1:** Show help
```
# hue_off.py -h
Options Usage:
-b, --bridge | IP address of your Hue Bridge<br>
-c, --createuser | Create a new user on your Hue Bridge<br>
-i, --interval | Set how often (in seconds) to check the pwrstatd log. Defaults to 60
```

**Example #2:** Start and connect to Hue Bridge at IP 192.168.1.101
```
# hue_off.py -b 192.168.1.101
```

# Limitations
1. If the power outage lasts longer than the runtime of your UPS, OffWith-Hue will not be able to turn off the ligts when the power returns. 
    * This could be remedied by storing the list of lights to be turned off in a file.  Once the computer starts up (assuming the computer and script is set to autostart) the lights can be turned off

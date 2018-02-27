***This Project lives @ https://gitlab.rickelobe.com/Rich/OffWith-Hue ***

# Prerequisits
1. *nix machine
2. **[Phue](https://github.com/studioimaginaire/phue)** python library. Install using pip
<pre>pip install phue</pre>
3. A CyberPower UPS device connected to your machine OR Network UPS Tools configured device

<br>
CyberPower's pwrstatd daemon (PowerPanel) can be downloaded here: http://www.cyberpower-eu.com/products/software/pp_linux.htm <br>
<br>  
# Description
  This program will turn off lights that are controlled through your Philips Hue bridge after 
    a power outage.  To determine whether a power outage has occurred, it can use CyberPower's 
    pwrstatd daemon or monitor your system log for messages from NUT (Network UPS Tools) for
    status changes.

  The program routinely query's your Hue bridge for a list of lights, storing the ones
    that are currently off.  When the power goes out, it will wait for the power to return, then
    turn off all lights that were off prior to the power outage.
    
# Usage
**Example #1:** Show help
```
# hue_off.py -h
Options Usage:
-b, --bridge | IP address of your Hue Bridge
-c, --createuser | Create a new user on your Hue Bridge
-i, --interval | Set how often (in seconds) to check the pwrstatd log. 
    Defaults to 60, only used for CyberPower monitoring
-m, --mode | Set the mode for checking power status
    Options are 'cyberpower' or 'nut'
-l, --logfile | Specify the logfile to watch for NUT messages
    This only applies when mode is set to "nut"
    Typically "/var/log/syslog"
```

**Example #2:** Start and connect to Hue Bridge at IP 192.168.1.101
```
# hue_off.py -b 192.168.1.101
```

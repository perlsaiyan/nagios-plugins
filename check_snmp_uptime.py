#!/usr/bin/python

import plac
import sys
import re
from subprocess import Popen, PIPE
import datetime

SNMPGET_BIN = '/usr/bin/snmpget'
SNMP_ENGINE_OID = '.1.3.6.1.6.3.10.2.1.3.0'
SNMP_UPTIME_OID = '.1.3.6.1.2.1.1.3.0'


NAGIOS_OK       = 0
NAGIOS_WARNING  = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN  = 3

@plac.annotations(
	warning=('Warning value', 'option', 'w', int),
	critical=('Critical value', 'option', 'c', int),
	host=('Host/address', 'option', 'H'),
	port=("Port", 'option', 'P', int),
	#debug=("Debug", 'flag', 'd'),
	community=("Community", 'option', 'C'),
	)
def main(warning, critical, host='localhost', port=161, community='public'):

	# first search the SNMP engine time OID
	mycode, stdout = snmpget(host, port, community, SNMP_ENGINE_OID)

	match = re.search('INTEGER:\W*(\d+)\W*seconds', stdout)
	
	if match:
		uptime_sec = int(match.group(1))
		method = 'engine'
	else:
		# no match, continue on to using the SysUpTime OID
		mycode, stdout = snmpget(host, port, community, SNMP_UPTIME_OID)
		#print stdout
		
		match = re.search('Timeticks:\W*\((\d+)\)\W*', stdout)
		
		if match:
			uptime_sec = int(match.group(1)) / 100
			method = 'sysUptime'
		else:
			print 'CRITICAL: Unable to determine uptime'
			sys.exit(NAGIOS_CRITICAL)

	if uptime_sec < critical:
		print 'CRITICAL: Uptime less than %s: is currently %s (SNMP method: %s)' % (str(datetime.timedelta(seconds=critical)), str(datetime.timedelta(seconds=uptime_sec)), method)
		sys.exit(NAGIOS_CRITICAL)  
	elif uptime_sec < warning:
		print 'WARNING: Uptime less than %s: is currently %s (method: %s)' % (str(datetime.timedelta(seconds=warning)), str(datetime.timedelta(seconds=uptime_sec)), method)
		sys.exit(NAGIOS_WARNING)  
	else:
		print 'UPTIME OK: %s (method: %s)' % (str(datetime.timedelta(seconds=uptime_sec)), method)
		sys.exit(NAGIOS_OK)


def snmpget(host, port, community, oid):
	snmpe = Popen([SNMPGET_BIN,'-v','2c','-c',community,host + ':' + str(port),oid], stdout=PIPE)
	
	sout, serr = snmpe.communicate()
	
	return (snmpe.returncode, sout)


if __name__ == '__main__':
	plac.call(main)

# snmp engine
# .1.3.6.1.6.3.10.2.1.3.0

# sysUptime
# .1.3.6.1.2.1.1.3.0

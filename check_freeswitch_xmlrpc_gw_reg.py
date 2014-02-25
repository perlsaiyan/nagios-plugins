#!/usr/bin/python

import sys
import plac
from socket import error as socket_error
from xmlrpclib import ServerProxy

NAGIOS_OK       = 0
NAGIOS_WARNING  = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN  = 3

@plac.annotations(
	host=('XML-RPC hostname/address', 'option', 'H'),
	username=('XML-RPC username', 'option', 'w'),
	password=('XML-RPC password', 'option', 'i'),
	port=('XML-RPC port', 'option', 'p'),
	sipreg=('FreeSWITCH registration'))
def main(sipreg, host='localhost', username='freeswitch', password='works', port='8080'):

	url = 'http://%s:%s@%s:%s' % (username, password, host, port)

	s = ServerProxy(url)
	try:
		status = s.freeswitch.api('sofia', 'status')
	except socket_error, e:
		print 'CRITICAL: Error connecting: %s' % e.args[1]
		return NAGIOS_CRITICAL
	except:
		print 'CRITICAL: Unknown error connecting'
		return NAGIOS_CRITICAL

	for ln in status.splitlines():
		lnargs = ln.split()
		if len(lnargs) > 3 and lnargs[1].lower() == 'gateway' and lnargs[2].startswith('sip:') and lnargs[2].lower().endswith(sipreg.lower()):
			# these should be just gateways
			if lnargs[3] == 'REGED':
				print 'OK: Gateway %s %s' % (lnargs[2], lnargs[3])
				return NAGIOS_OK
			elif lnargs[3] == 'REGISTER':
				print 'WARNING: Gateway REGISTERING: %s %s' % (lnargs[2], ' '.join(lnargs[3:]))
				return NAGIOS_WARNING
			else:
				print 'CRITICAL: Gateway not REGED: %s %s' % (lnargs[2], ' '.join(lnargs[3:]))
				return NAGIOS_CRITICAL

	print 'CRITICAL: Gateway not found: %s' % sipreg
	return NAGIOS_CRITICAL

if __name__ == '__main__':
	sys.exit(plac.call(main))

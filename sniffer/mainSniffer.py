#!/bin/python2.7
from scapy.all import *
import datetime
import json
import socket

mac_useragent_map={}
ip_domain_map={}
start_time=time.time()
services=['facebook','twitter','flickr','instagram','whatsapp','skype']

def timestamp():
	'''Creates a formatted timestap string using the format 
	yearMonthDay Hour:Minute:Second.
	Takes:
	Nothing
	Returns:
	String
	'''
	dt =datetime.datetime.now()
	return dt.strftime('%y%m%d '+'%I:%M:%S')
	
def getHost(packet):
	'''Attempts to get a packet's destination's host name 
	using socket's get host by address.
	Takes:
	packet-> scapy packet
	'''
	if packet.haslayer(IP):
		address=packet[IP].dst
		try:
			hostname=socket.gethostbyaddr(address)[0]
		except socket.herror:
			hostname=packet[IP].dst
		return hostname
	else:
		return

def getUserAgent(rawLayer):
	'''Attempts to find a User-Agent string in a packet's
	raw layer load.
	Takes:
	rawLayer->Scapy packet's raw layer
	Returns:
	userAgent->str
	'''
	userAgent=''
	if 'User-Agent' in rawLayer.load:
		splitLoad=rawLayer.load.split('\n')
		for line in splitLoad:
			if 'User-Agent' in line:
				userAgent=line
			else:
				pass
	else:
		pass
	return userAgent
def submitReport(server,report):
	'''Writes a json packet report to the specified 
	server.
	Takes:
	server->str
	report->JSON
	Returns:
	Nothing
	'''
	pass
def analysis(packet):
	'''
	Runs a full analysis of the specified package, converts
	it JSON and posts it to the server. The report takes the format
	{timestamp,deviceAddress,packetId,domain,<userAgent> (if available)}
	'''
	proceed=0
	#<start information gathering>
	time=timestamp()
	deviceAddress=packet.src
	#Check for TCP layer
	if packet.haslayer(TCP):
		# print 'Haz TCP'
		# Check for IP layer
		if packet.haslayer(IP):
			# print 'haz IP'
			packetId=packet[IP].id
			if packet[IP].dst not in ip_domain_map.keys():
				#Get domain name from destination IP address
				ip_domain_map[packet[IP].dst]=getHost(packet)
			domain=ip_domain_map[packet[IP].dst]
			print domain
			#Is this connection relevant?
			host=domain
			for s in services:
				if s in domain:
					print domain
					host=s
					proceed=1
					break
				else:
					host=domain
			#Check for raw layer
				if packet.haslayer(Raw):
					# print 'Haz Raw'
					#Do we know this devices User-Agent?
					for s in services:
						if s in packet[Raw].load:
							host=s
							proceed=1
							break
						else:
							host=domain
					if deviceAddress not in mac_useragent_map.keys():
						userAgent=getUserAgent(packet[Raw])
						mac_useragent_map[deviceAddress]=userAgent
					elif mac_useragent_map[deviceAddress]=='':
						userAgent=getUserAgent(packet[Raw])
						mac_useragent_map[deviceAddress]=userAgent
					else:
						userAgent=mac_useragent_map[deviceAddress]
					#<end information gathering>
					#<start report packing>
					if proceed==1:
						packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':host,'user-agent':userAgent}
						jsonisedData=json.dumps(packetData)
						return jsonisedData
				else:
					if proceed==1:
						packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':host,'user-agent':''}
						jsonisedData=json.dumps(packetData)
						return jsonisedData
			else:
				pass
		else:
			pass
	else:
		pass
		
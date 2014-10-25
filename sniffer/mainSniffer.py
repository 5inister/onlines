#!/bin/python
#usage:sniff(iface='wlan0',prn=analysis)

from scapy.all import *
import datetime
import json
import socket
from ipwhois import IPWhois,IPDefinedError

mac_useragent_map={}
ip_domain_map={'local':'192.168.0'}
start_time=time.time()
services=['facebook','twitter','flickr','instagram','whatsapp','skype','youtube','fbcdn','fbstatic','twvid','twimg']

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
	
def getHostname(ip):
	'''Attempts to get a packet's destination's host name 
	using socket's get host by address.
	Takes:
	ip->str
        Returns:
        str
	'''
        if '192.168.0' not in ip:
                try:
                        hostname=socket.gethostbyaddr(ip)[0]
                        return hostname
                except socket.herror:
                        return ''
        else:
                return 'local'
                
def getWhois(ip,key=''):
        '''TODO Return parsed dictionary
        Looks for an ip address' whois information.
        Optionally returns only a the 'key' part of the whois information
        Takes:
        ip->str
        Returns:
        whois_result->dict/None
        '''
        if '192.168.0' in ip:
                return None
                
        else:
                try:
                        whoisObject=IPWhois(ip)
                        whois_result = whoisObject.lookup()
                except ValueError:
                        print "Value Error "+host
                        return None
                except IPDefinedError:
                        return None
        if key != '':
                try:
                        return {key:whois_result[key]}
                except KeyError:
                        return whois_result
        else:
                return whois_result
def getUserAgent(raw_load):
	'''Attempts to find a User-Agent string in a packet's
	raw layer load.
	Takes:
	rawLayer->Scapy packet's raw layer
	Returns:
	userAgent->str/None
	'''
	userAgent=None
	if 'User-Agent' in raw_load:
		splitLoad=raw_load.split('\n')
		for line in splitLoad:
			if 'User-Agent' in line:
				userAgent=line
			else:
				pass
	else:
		pass
	return userAgent
def getQname(packet):
        '''Checks if the service name appears in
        the DNSQR layer and returns qname
        Takes:
        packet-> scapy packet
        Returns:
        str / None
        '''
        if packet.haslayer(DNSQR):
                return packet[DNS][DNSQR].qname
        else:
                return None

def getRawLoad(packet):
        '''Checks if a packet has a Raw layer and looks for the
        service in it.
        Takes:
        packet-> scapy packet
        service->str
        Returns:
        packet[Raw].load->str or None
        ''' 
        if packet.haslayer(Raw):
                return packet[Raw].load
        else:
                return None
def serviceInWhois(whoIs,service,key=''):
        '''Checks if the service name appears in
        the whois information for the given ip.
        Can analyse specific keys of the whois dictionary.
        Takes:
        whois->dict
        service->str
        key->str
        Returns:
        bool
        '''
        if key=='': 
                try: #Do we have a nets key? Is the service in there?
                        nets=whoIs['nets'][0]
                        for v in nets.values():
                                if isinstance(v,str):
                                        if service in v.lower():
                                                return True
                except (KeyError,TypeError): #If it isn't analyse the entire whois
                        for v in whoIs.values():
                                if v != None:
                                        if isinstance(v,str):
                                                if service in v.lower():
                                                        return True
                                                else:
                                                        pass
                                        if isinstance(v,list):
                                                for i in v:
                                                        if isinstance(i,str):
                                                                if service in i.lower():
                                                                        return True
                                                        elif isinstance(i,dict):
                                                                for value in i.values():
                                                                        if isinstance(value,str):
                                                                                if service in value.lower():
                                                                                        return True
                                                        else:
                                                                pass
                                else:
                                        pass
                        return False
        else: #Is our service in the key section of whois?
                keyValue=whoIs[key]
                if isinstance(keyValue,str):#is our value a string?
                        if service in keyValue.lower():
                                return True
                        else:
                                return False
                elif isinstance(keyValue,list): #is it a list? If it is iterate it
                        if len(keyValue)==1:
                                keyValue=keyValue[0]
                                if isinstance(keyValue,dict):
                                        for value in keyValue.values():
                                                if isinstance(value,str):
                                                        if service in value.lower():
                                                                return True
                                elif isinstance(keyValue,str):
                                        if service in keyValue.lower():
                                                return True
                        else:
                                for item in keyValue:
                                        if isinstance(item,str):
                                                if service in item.lower():
                                                        return True
                                        elif isinstance(item,dict):
                                                for value in item.values():
                                                        if isinstance(item,str):
                                                                if service in item.lower():
                                                                        return True
        return False
                                                        
                                        
def submitReport(server,report): #TODO
	'''Writes a json packet report to the specified 
	server.
	Takes:
	server->str
	report->JSON
	Returns:
	Nothing
	'''
	pass
def analysis(packet): #TODO This is an ugly function, split it into several funcitons!
	'''
	Runs a full analysis of the specified package, converts
	it JSON and posts it to the server. The report takes the format
	{timestamp,deviceAddress,packetId,domain,<userAgent> (if available)}
	'''
	proceed=0
	#<start information gathering>
	time=timestamp()
	deviceAddress=packet.src
        remoteHost='local'
        rawLoad=getRawLoad(packet)# Attempt to get a Raw load.
        if packet.haslayer(IP): #Does our package have an IP layer?
                packetId=packet[IP].id
                if '192.168.0' not in packet[IP].src: # Is the source or destination remote?
                        remoteHost=packet[IP].src
                elif '192.168.0' not in packet[IP].dst:
                        remoteHost=packet[IP].dst
                else:
                        remoteHost='local'
        else:
                packetId=None
        if remoteHost not in ip_domain_map.keys(): #Attempt to map IP addresses to their services
                qname=getQname(packet)# Attempt to get DNSQR qname
                print "Generating ip-domain item"
                #Is our service in qname?
                if qname != None:
                        for s in services:
                                if s in qname:
                                        print s + " in qname"
                                        domain=s
                                        ip_domain_map[remoteHost]=s+'.com'
                                        proceed = 1
                                        break
                elif rawLoad != None: #Is it in our raw load?
                        if proceed==0:
                                for s in services:
                                        if s in rawLoad:
                                                print s + " in rawLoad"
                                                domain=s
                                                ip_domain_map[remoteHost]=s+'.com'
                                                proceed = 1
                                                break
                else:
                        pass

                if proceed==0: 
                        hostname=getHostname(remoteHost)# or is it in a hostname
                        for s in services:
                                if s in hostname:
                                        print s + " in hostname"
                                        domain=s
                                        ip_domain_map[remoteHost]=s+'.com'
                                        proceed = 1
                                        break
                if proceed==0:
                        whois=getWhois(remoteHost)# or do we need whois information?
                        for s in services:
                                if serviceInWhois(whois,s):
                                        print s + " in whois"
                                        domain=s
                                        ip_domain_map[remoteHost]=s+'.com'
                                        proceed = 1
                                        break
                if proceed==0:
                        ip_domain_map[remoteHost]=remoteHost
                        print "Irrelevant service"
                        proceed=0

        else:
                domain=ip_domain_map[remoteHost]
                if remoteHost == 'local':
                        proceed=0
                        return False
                elif domain != remoteHost:
                        print "In dictionary: "+remoteHost
                        proceed=1
                else:
                        pass
        
        if rawLoad != None:
                #Do we have a user agent on record?
                if deviceAddress not in mac_useragent_map.keys():
                        userAgent=getUserAgent(rawLoad)
                        mac_useragent_map[deviceAddress]=userAgent
                elif mac_useragent_map[deviceAddress]==None:
                        userAgent=getUserAgent(rawLoad)
                        mac_useragent_map[deviceAddress]=userAgent
                else:
                        userAgent=mac_useragent_map[deviceAddress]
                        #<end information gathering>
                        #<start report packing>
                        if proceed==1:
                                packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':userAgent}
                                jsonisedData=json.dumps(packetData)
                                return jsonisedData
                        else:
                                return False
        else:
                if proceed==1:
                        if deviceAddress in mac_useragent_map.keys():
                                userAgent=mac_useragent_map[deviceAddress]
                                packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':userAgent}
                                jsonisedData=json.dumps(packetData)
                                return jsonisedData
                                                
                        else:
                                packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':''}
                                jsonisedData=json.dumps(packetData)
                                return jsonisedData
                else:
                        return False

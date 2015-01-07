#!/bin/python
#usage:
# Full analysis: sniff(iface='wlan0',prn=analysis,store=0)
# Quick analysis: sniff(iface='wlan0',prn=PacketInstance.quickAnalysis,store=0)
import datetime
#from ipwhois import IPWhois,IPDefinedError
import json
import re
from scapy.all import *
import socket
import urllib
import urllib2

class Analysis():
        '''A class containing packet analysis tools
        to be used in a network sniffing scenario
        '''

        def __init__(self,routerMac,serverAddrs,serviceDic,user):
                '''Populates the classe's variables defined in
                config.py.
                Takes:
                self
                routerMac->str
                serverAddrs->str
                serviceDic->dict
                user->str
                Returns:
                Nothing
                '''
                self.mac_useragent_map={}
                self.ip_domain_map={'local':'192.168.0'}
                self.start_time=self.timestamp()
                self.services=serviceDic
                self.user=user
                self.server=serverAddrs
                self.router_mac=routerMac
        def timestamp(self):
                '''Creates a formatted timestap string using unix time
                format in milliseconds (JS friendly)
                Takes:
                self
                Nothing
                Returns:
                String
                '''
                dt =datetime.datetime.utcnow()
                epoch=datetime.datetime.utcfromtimestamp(0)
                delta = dt-epoch
                return delta.total_seconds()*1000

        def getHostname(self,ip):
                '''Attempts to get a packet's destination's host name 
                using socket's get host by address.
                Takes:
                self
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
                
        def getWhois(self,ip,key=''):
                '''TODO Return parsed dictionary
                Looks for an ip address' whois information.
                Optionally returns only a the 'key' part of the whois information
                Takes:
                self
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

        def getUserAgent(self,raw_load):
                '''Attempts to find a User-Agent string in a packet's
                raw layer load.
                Takes:
                self
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

        def getQname(self,packet):
                '''Checks if the service name appears in
                the DNSQR layer and returns qname
                Takes:
                self
                packet-> scapy packet
                Returns:
                str / None
                '''
                if packet.haslayer(DNSQR):
                        return packet[DNSQR].qname
                else:
                        return None

        def getRawLoad(self,packet):
                '''Checks if a packet has a Raw layer and looks for the
                service in it.
                Takes:
                self
                packet-> scapy packet
                service->str
                Returns:
                packet[Raw].load->str or None
                ''' 
                if packet.haslayer(Raw):
                        return packet[Raw].load
                else:
                        return None
        def serviceInWhois(self,whoIs,service,key=''):
                '''Checks if the service name appears in
                the whois information for the given ip.
                Can analyse specific keys of the whois dictionary.
                Takes:
                self
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


        def submitReport(self,report_php_path,user,report):
                '''Posts a report data to the specified php on server.
                Takes:
                self
                server_php->str
                report_php_path->str
                report->json
                Returns:
                Nothing
                '''
                data={'user':user,'json':report}
                post_data=urllib.urlencode(data)
                request=urllib2.Request(report_php_path,post_data)
                #request.add_header("Content-type", "application/x-www-form-urlencoded")
                page=urllib2.urlopen(request).read()
                return page
                # connection = httplib.HTTPConnection(server)
                # connection.request("POST",report_path,report,headers)
                # response = conn.getresponse()
                # print response.read()
                #return response.status()

                
        def quickAnalysis(self,packet):
                '''
                Runs only a qname and useragent analysis of the packet, converts the results to
                JSON and posts it to the server. It ignores packages with the router as source.
                The report takes the format {timestamp,deviceAddress,packetId,domain,<userAgent> 
                (if available)}
                '''
                proceed=0
                #<start information gathering>
                time=self.timestamp()
                deviceAddress=packet.src
                remoteHost='local'
                rawLoad=self.getRawLoad(packet)# Attempt to get a Raw load.
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
                qname=self.getQname(packet)# Attempt to get DNSQR qname
                if deviceAddress != self.router_mac:
                        #Is our service in qname?
                        if qname != None:
                                for s in self.services.keys():
                                        regEx=re.compile('^(?!accounts|www\.accounts).*?[.]?'+s+'.*$')
                                        if regEx.match(qname) != None:
                                                print regEx.match(qname).group() + " in qname"
                                                domain=self.services[s]
                                                proceed = 1
                                                break
                        else:
                                domain=remoteHost
                                proceed=0
                else:
                        proceed=0

                if rawLoad != None:
                        #Do we have a user agent on record?
                        if deviceAddress not in self.mac_useragent_map.keys():
                                if deviceAddress == self.router_mac:
                                        self.mac_useragent_map[deviceAddress]='rPi-router'
                                else:
                                        userAgent=self.getUserAgent(rawLoad)
                                        self.mac_useragent_map[deviceAddress]=userAgent
                        elif self.mac_useragent_map[deviceAddress]==None:
                                userAgent=self.getUserAgent(rawLoad)
                                self.mac_useragent_map[deviceAddress]=userAgent
                        else:
                                userAgent=self.mac_useragent_map[deviceAddress]
                                #<end information gathering>
                                #<start report packing>
                                if proceed==1:
                                        packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':userAgent}
                                        jsonisedData=json.dumps(packetData)
                                        self.submitReport(self.server+'report.php',self.user,jsonisedData)
                                        return jsonisedData
                                else:
                                        return qname
                else:
                        if proceed==1:
                                if deviceAddress in self.mac_useragent_map.keys():
                                        userAgent=self.mac_useragent_map[deviceAddress]
                                        packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':userAgent}
                                        jsonisedData=json.dumps(packetData)
                                        self.submitReport(self.server+'report.php',self.user,jsonisedData)
                                        return jsonisedData

                                else:
                                        packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':''}
                                        jsonisedData=json.dumps(packetData)
                                        self.submitReport(self.server+'report.php',self.user,jsonisedData)
                                        return jsonisedData
                        else:
                                return qname
"""THIS FUNCTION IS BROKEN AND NEEDS TO BE FIXED BY:
-INTEGRATING IT INTO THE CLASS
-ANALYSING LOCAL TRAFFIC FOR QNAMES

        def analysis(self,packet):
                '''
                Runs a full analysis of the package, converts
                it JSON and posts it to the server. The report takes the format
                {timestamp,deviceAddress,packetId,domain,<userAgent> (if available)}
                '''
                proceed=0
                #<start information gathering>
                time=timestamp()
                deviceAddress=packet.src
                routerMac='c0:4a:00:1e:42:76'
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
                                for s in services.keys():
                                        if s in qname:
                                                print s + " in qname"
                                                domain=services[s]
                                                ip_domain_map[remoteHost]=services[s]
                                                proceed = 1
                                                break
                        elif rawLoad != None: #Is it in our raw load?
                                if proceed==0:
                                        for s in services.keys():
                                                if s in rawLoad:
                                                        print s + " in rawLoad"
                                                        domain=services[s]
                                                        ip_domain_map[remoteHost]=services[s]
                                                        proceed = 1
                                                        break
                        else:
                                pass

                        if proceed==0: 
                                hostname=getHostname(remoteHost)# or is it in a hostname
                                for s in services.keys():
                                        if s in hostname:
                                                print s + " in hostname"
                                                domain=services[s]
                                                ip_domain_map[remoteHost]=services[s]
                                                proceed = 1
                                                break
                        if proceed==0:
                                whois=getWhois(remoteHost)# or do we need whois information?
                                if whois != None:
                                        for s in services.keys():
                                                if serviceInWhois(whois,s):
                                                        print s + " in whois"
                                                        domain=services[s]
                                                        ip_domain_map[remoteHost]=services[s]
                                                        proceed = 1
                                                        break
                                else:
                                        pass
                        if proceed==0:
                                ip_domain_map[remoteHost]=remoteHost
                                print "Irrelevant service"
                                proceed=0

                else:
                        domain=ip_domain_map[remoteHost]
                        if remoteHost == 'local':
                                proceed=0
                                return 'local'
                        elif domain != remoteHost:
                                print "In dictionary: "+remoteHost
                                proceed=1
                        else:
                                if packet.haslayer(DNSQR):
                                        qname=getQname(packet)# Attempt to get DNSQR qname
                                        print "Re-evaluating irrelevant"
                                        #Is our service in qname?
                                        if qname != None:
                                                for s in services.keys():
                                                        if s in qname:
                                                                print s + " in qname"
                                                                domain=services[s]
                                                                ip_domain_map[remoteHost]=services[s]
                                                                proceed = 1
                                                                break
                                        else:
                                                proceed=0
                                else:
                                        proceed=0


                if rawLoad != None:
                        #Do we have a user agent on record?
                        if deviceAddress not in mac_useragent_map.keys():
                                if deviceAddress == routerMac:
                                        mac_useragent_map[deviceAddress]='rPi-router'
                                else:
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
                                        submitReport('relevant.json',jsonisedData)
                                        return jsonisedData
                                else:
                                        return remoteHost
                else:
                        if proceed==1:
                                if deviceAddress in mac_useragent_map.keys():
                                        userAgent=mac_useragent_map[deviceAddress]
                                        packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':userAgent}
                                        jsonisedData=json.dumps(packetData)
                                        submitReport('relevant.json',jsonisedData)
                                        return jsonisedData

                                else:
                                        packetData={'time':time,'HWaddr':deviceAddress,'pId':packetId,'domain':domain,'user-agent':''}
                                        jsonisedData=json.dumps(packetData)
                                        submitReport('relevant.json',jsonisedData)
                                        return jsonisedData
                        else:
                                return remoteHost

"""

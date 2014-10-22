import datetime
import json
import datetime
import random

services=['facebook','twitter','flickr','instagram','whatsapp','skype']
outfile='sample.json'
deviceAddress='40:61:86:1a:8f:7b' 
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
time=timestamp()
print time
# try:
with open(outfile,mode='r') as feeds_json:
    feeds=json.load(feeds_json)
    print feeds
with open(outfile,mode='w') as feeds_json:
    entry={'time':time,'HWaddr':deviceAddress,'pId':random.randint(0,150),'domain':random.choice(services),'user-agent':''}
    feeds.append(entry)
    print feeds
    json.dump(feeds,feeds_json)
# except:
#     pass

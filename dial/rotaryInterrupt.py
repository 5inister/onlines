#!/usr/local/bin/python

import RPi.GPIO as GPIO
import json
import stomp_config
from stompest.config import StompConfig
from stompest.sync import Stomp

#Setup R-Pi GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN,pull_up_down=GPIO.PUD_UP)         # PinA is on GPIO 16
GPIO.setup(18, GPIO.IN,pull_up_down=GPIO.PUD_UP)         # PinB is on GPIO 18
GPIO.setup(11,GPIO.IN,pull_up_down=GPIO.PUD_UP)          # Toggle button 11

#Global variabes
encoderPinA,encoderPinB = GPIO.input(16), GPIO.input(18)
encoderPinA = GPIO.input(16)
oldPinA=encoderPinA
encoderPinB = GPIO.input(18)
oldPinB=encoderPinB
sequence=""
clockwise=[11,45,52,18,180,210,75]
anticlockwise=[7,30,56,33,120,225,135]
lastTurns=[0,0,0]
position=0
previousPosition=0
#STOMP Client Setup
CONFIG = StompConfig(stomp_config.server, stomp_config.login,stomp_config.passcode)
QUEUE = stomp_config.queue
client = Stomp(CONFIG)

def encoderCallback(channel):
    global sequence
    encoderPinA,encoderPinB = GPIO.input(16), GPIO.input(18)
    sequence+=str(encoderPinA)+str(encoderPinB)
    if len(sequence)==8:
        calculatePosition()

def calculatePosition(inc=10):
    global sequence
    global position
    global previousPosition
    direction=evaluateSequence(sequence,False)
    position += inc*direction
    print sequence
    sequence=""
    if position !=previousPosition:
        writeJson(["aggregate",direction],'stomp')
        previousPosition=position
def evaluateSequence(sequence,subs=True):
    '''Analyses the sequence of values and defines
    if the rotary encoder turned clock or anti-clockwise
    '''
    global clockwise
    global anticlockwise
    global lastTurns
    
    if int(sequence,2) in clockwise:
        lastTurns=shiftAppend(lastTurns,1)
        return 1
    elif int(sequence,2) in anticlockwise:
        lastTurns=shiftAppend(lastTurns,-1)
        return -1
    else:
        if int(sequence[0:-2],2) in clockwise or int(sequence[2:],2) in clockwise:
            lastTurns=shiftAppend(lastTurns,1)
            return 1
        elif int(sequence[0:-2],2) in anticlockwise or int(sequence[2:],2) in anticlockwise:
            lastTurns=shiftAppend(lastTurns,-1)
            return -1
        else:
            if sum(lastTurns)>0:
                return 1
            else:
                return -1

def shiftAppend(array,value):
    '''Shifts the array one position to the left dumping the
    first value and adds <value> to the end of it.
    Takes:
    array -> list
    value -> *
    Returns
    list
    '''
    shifted=array[1:]
    shifted.append(value)
    return shifted
def writeJson(value,*argv):
    '''Writes the specified value to an output file
    Takes:
    value-> List or Dict
    *argv: Available options:
       'stomp'
       'post'
       'outfile'
    Returns:
    none
    '''
    outJson=json.dumps(value)
    print outJson
    if 'outfile' in argv:
        with open(outfile,'w') as jsonFile:
            jsonFile.write(outJson)
    elif 'stomp' in argv:
        global client
        global QUEUE
        client.connect()
        client.send(QUEUE, outJson)
        client.disconnect()
    elif 'post' in argv:
        #TODO Post to php server
        pass

def toggleCallback(channel):
    writeJson(["switch_view"],'stomp')

GPIO.add_event_detect(11,GPIO.FALLING,callback=toggleCallback,bouncetime=200)
GPIO.add_event_detect(16,GPIO.BOTH,callback=encoderCallback)
GPIO.add_event_detect(18,GPIO.BOTH,callback=encoderCallback)

while __name__ == '__main__':
    pass
#     encoderPolling()

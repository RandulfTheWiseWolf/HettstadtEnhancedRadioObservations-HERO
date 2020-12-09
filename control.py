# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 19:09:06 2019

@author: Raoul
"""

import serial


port = None

#Coordinate offset for calibrate()
#We define the offsets as the difference between the positions
#of the measured solar maximum and the user supplied solar coordinates
deltaAz = 0
deltaEl = 0

###Flag to check if telescope is moving
driving_flag = False


###Connect with the ACU
def connect(port_):
    global port
    port = serial.Serial(port_, 19200, timeout=1)


###Send commands to the ACU
def send(data):
    if port is None:
        print("No connection")
    else:
        port.write(data.encode())
    
    
##Drive the telescope to the given Az, El coordinates
def drive(az, el):
        global driving_flag
        driving_flag = True
        #Uncomment this line when calibrate() is implemented
        #send(f"<120/AZ_{az + deltaAz},EL_{el + deltaEl}")
        send(f"<120/AZ_{az},EL_{el}")
    
    
###Stop the telescope
def stop():
        global driving_flag
        driving_flag=False
        az, el, status = readdata()
    
        drive(az, el)
        
        
###Park the telescope at El = 90°
def park():
    send('<120/AZ_,EL_90.00')
        
    
###Check the coordinates are in the accessible limits of the telescope 
def checkLimits(az, el, offset=0.0):
    if az + offset > 322 or az - offset < 42 or el + offset > 90 or el - offset < 22:
       raise ValueError


###Read out the status of the ACU
def readdata():
        #Must query the status before reading out the port
        send("<120/STATUS_?")
        data = port.read_until(b'|')
        
        #Try except for double check if the readout failed
        try:
            az = float(data[len(data)-45:len(data)-39].decode())
            el = float(data[len(data)-35:len(data)-29].decode())
            status = data[len(data)-4:len(data)-1].decode()
            
            #return az - deltaAz, el - deltaEl, status
            return az, el, status
            
        except:
            send("<120/STATUS_?")
            data = port.read_until(b'|')
            
            az = float(data[len(data)-45:len(data)-39].decode())
            el = float(data[len(data)-35:len(data)-29].decode())
            status = data[len(data)-4:len(data)-1].decode()
            
            #return az - deltaAz, el - deltaEl, status
            return az, el, status
    

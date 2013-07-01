#!/usr/bin/python
killAllHumans = 0

import serial
import time
import binascii
from sys import argv

#initialization and open the port
#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

commandList = [\
['\x80\x70\xc0\x3f', 'Power On'     , ''],\
['\x80\x70\x9f\x60', 'Power Off'    , ''],\
['\x80\x70\x87\x78', '1'            , ''],\
['\x80\x70\x88\x77', '2'            , ''],\
['\x80\x70\x89\x76', '3'            , ''],\
['\x80\x70\x8a\x75', '4'            , ''],\
['\x80\x70\x8b\x74', '5'            , ''],\
['\x80\x70\x8c\x73', '6'            , ''],\
['\x80\x70\x8d\x72', '7'            , ''],\
['\x80\x70\x8e\x71', '8'            , ''],\
['\x80\x70\x9d\x62', '9'            , ''],\
['\x80\x70\x9e\x61', '0'            , ''],\
['\x82\x72\x9a\x65', 'Down<down>'   , 'Downward directional movement when navigating through OSD menus'],\
['\x82\x72\xc1\x3e', 'Left<left>'   , 'Left directional movement when navigating through OSD menus'],\
['\x82\x72\x84\x7b', 'SET'          , ''],\
['\x82\x72\xc2\x3d', 'Right<right>' , 'Right directional movement when navigating through OSD menus'],\
['\x82\x72\x99\x66', 'Up<up>'       , 'Upward directional movement when navigating through OSD menus'],\
['\x80\x70\xc0\x3f', 'AVR Power On' , ''],\
['\x80\x70\xd0\x2f', 'DVD'          , ''],\
['\x80\x70\xc4\x3b', 'CD'           , ''],\
['\x80\x70\xcc\x33', 'TAPE'         , ''],\
['\x82\x72\x9b\x64', 'Stereo'       , ''],\
['\x80\x70\xc1\x3e', 'Mute'         , ''],\
['\x80\x70\xca\x35', 'VID1(VCR)'    , ''],\
['\x80\x70\xcb\x34', 'VID2(TV)'     , ''],\
['\x80\x70\xce\x31', 'VID3(CBL/SAT)', ''],\
['\x80\x70\xd1\x2e', 'VID4'         , ''],\
['\x80\x70\x81\x7e', 'AM/FM'        , ''],\
['\x82\x72\x5d\xa2', 'Channel Guide', 'Access the Channel Trim Settings menu'],
['\x82\x72\xdb\x24', '6CH / 8CH'    , 'The first transmission of this code shows the current mode.  Subsequent transmissions step through the available modes.'],
['\x82\x72\x9a\x65', 'Level - Down' , 'Decreases the channel trim level'],
['\x82\x72\x99\x66', 'Level - Up  ' , 'Increaces the channel trim level'],
['\x80\x70\xdb\x24', 'Sleep'        , ''],\
['\x82\x72\x8c\x73', 'Test Tone'    , ''],\
['\x80\x70\xc7\x38', 'Volume Up'    , ''],\
['\x82\x72\x58\xa7', 'Surr'         , 'Initates surround mode and displays current mode'],\
['\x82\x72\x86\x79', 'Surr Down'    , 'Scroll down through surround choices (down arrow)'],\
['\x82\x72\x85\x7a', 'Surr Up'      , 'Scroll up through surround choices (up arrow)'],\
['\x82\x72\x96\x69', 'Night'        , ''],\
['\x82\x72\xdf\x20', 'Multiroom'    , 'Accesses the Multiroom menu and displays current status'],\
['\x82\x72\x5f\xa0', 'MRmulti<down>', 'Scroll down through multiroom choices (down arrow)'],\
['\x82\x72\x5e\xa1', 'MRmulti<up>  ', 'Scroll up through multiroom choices (up arrow)'],\
['\x80\x70\xc8\x37', 'Volume Down'  , ''],\
['\x82\x72\x53\xac', 'Speaker Menu' , 'Accesses the Speaker Configuration menu'],\
['\x82\x72\x8f\x70', 'Speaker<down>', 'Scrolls down through the speaker configuration choices'],\
['\x82\x72\x8e\x71', 'Speaker<up>'  , 'Scrolls up through the speaker configuration choices'],\
['\x82\x72\x54\xab', 'Digital/Exit' , 'Accesses Digital Input menu and displays input for current source'],\
['\x82\x72\x56\xa9', 'Digital<down>', 'Scrolls down through the list of digital inputs'],\
['\x82\x72\x57\xa8', 'Digital<up>+' , 'Scrolls up through the list of digital inputs'],\
['\x82\x72\x52\xad', 'Delay'        , 'Accesses delay settings'],\
['\x82\x72\x8b\x74', 'Delay<down>-' , 'Scrolls down through the list of digital inputs'],\
['\x82\x72\x8a\x75', 'Delay<up>+'   , 'Scrolls up through the list of digital inputs'],\
['\x80\x70\x85\x7a', 'Tuning Down -', ''],\
['\x82\x72\x5c\xa3', 'OSD'          , 'On Screen Display'],\
['\x82\x72\xdd\x22', 'RDS'          , 'Radio Data System (EU)'],\
['\x82\x72\xd1\x2e', 'Preset Down'  , ''],\
['\x82\x72\x50\xaf', 'Dolby'        , 'To access a Surround Mode group, first use one of these commands to select the desired mode group.  Issue the command again, as needed, to scroll through the list of available modes.'],\
['\x82\x72\xa0\x5f', 'DTS Surround' , ''],\
['\x82\x72\xa1\x5e', 'DTS NEO:6'    , ''],\
['\x82\x72\xa2\x5d', 'Logic 7'      , ''],\
['\x80\x70\x93\x6c', 'TUN/M'        , ''],\
['\x80\x70\x86\x79', 'Memory'       , ''],\
['\x80\x70\x84\x7b', 'Tuning Up'    , ''],\
['\x80\x70\x9b\x64', 'Direct'       , ''],\
['\x82\x72\xd9\x26', 'Clear'        , ''],\
['\x82\x72\xd0\x2f', 'Preset Up +'  , '']]

def sendAVR(command, listen = False):
    print ':: Attempting to connect to AVR3650...'
    ser = serial.Serial()
    ser.port = '/dev/ttyUSB0'
    ser.baudrate = 57600                # found after exhaustive testing, FUCK
    ser.bytesize = serial.EIGHTBITS     #number of bits per bytes
    ser.parity = serial.PARITY_NONE     #set parity check: no parity
    ser.stopbits = serial.STOPBITS_ONE  #number of stop bits
    #ser.timeout = None                  #block read
    #ser.timeout = 0                     #non-block read
    #ser.timeout = 2                     #timeout block read
    #ser.xonxoff = False                 #disable software flow control
    #ser.rtscts = False                  #disable hardware (RTS/CTS) flow control
    #ser.dsrdtr = True                   #disable hardware (DSR/DTR) flow control
    #ser.writeTimeout = 2                #timeout for write

    try: 
        ser.open()
    except Exception, msg:
        print ':: error open serial port: ', msg
        exit()

    if ser.isOpen():
        try:
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput()#flush output buffer, aborting current output 

            # Packet Structure & Example (taken from 'RS232 Protocol.pdf')
            # Transmission Type + Data Type + Packet Length + Command + Checksum
            # PCSEND            + 2         + 4             + XXXX    + CC

            c1 = int(binascii.hexlify(command[0][0]),16) ^ int(binascii.hexlify(command[0][2]),16)
            c2 = int(binascii.hexlify(command[0][1]),16) ^ int(binascii.hexlify(command[0][3]),16)
            checksum = chr(c1)+chr(c2)

            #print len('PCSEND\x02\x04'+command[0]+checksum),len('PCSEND\x02\x04'),len(command[0]),len(checksum)
            ser.write('PCSEND\x02\x04'+command[0]+checksum)
            
            print '   sending',command[1],'to AVR3650'
            
            if listen:
                time.sleep(.2)  #give the serial port sometime to receive the data
                numOfLines = 0
                while True:
                    response = ser.readline()
                    print('read data: ' + response)
                    numOfLines = numOfLines + 1
                    if (numOfLines >= 5):
                        break
            ser.close()
            print ':: Done'
        except Exception, msg:
            print ':: error communicating...:',msg
    else:
        print ':: cannot open serial port'
    ser.close()
    
if __name__ == '__main__':
    if len(argv) == 2:
        command = int(argv[1])
        sendAVR(commandList[command])
    else:
        print '   List of possible commands:'
        for idx, command in enumerate(zip(*commandList)[1]):
            print '  ',idx, '\t', command
        print '   Send using ./avr3650 <command>'
    


#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
This program as it stands controls a Harman Kardon AVR3650 receiver over RS-232 on any serial port.
Make sure the receiver has 'RS-232 Control' set to 'On' in the main menu.
'''
from __future__ import print_function, division
import serial
import time
from sys import argv, exit

#initialization and open the port
#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

# I should really make this a dictionary. It was transcribed from the C version and still looks bad...
commandList = [\
[b'\x80\x70\xc0\x3f', 'Power On'     , ''],\
[b'\x80\x70\x9f\x60', 'Power Off'    , ''],\
[b'\x80\x70\x87\x78', '1'            , ''],\
[b'\x80\x70\x88\x77', '2'            , ''],\
[b'\x80\x70\x89\x76', '3'            , ''],\
[b'\x80\x70\x8a\x75', '4'            , ''],\
[b'\x80\x70\x8b\x74', '5'            , ''],\
[b'\x80\x70\x8c\x73', '6'            , ''],\
[b'\x80\x70\x8d\x72', '7'            , ''],\
[b'\x80\x70\x8e\x71', '8'            , ''],\
[b'\x80\x70\x9d\x62', '9'            , ''],\
[b'\x80\x70\x9e\x61', '0'            , ''],\
[b'\x82\x72\x9a\x65', 'Down<down>'   , 'Downward directional movement when navigating through OSD menus'],\
[b'\x82\x72\xc1\x3e', 'Left<left>'   , 'Left directional movement when navigating through OSD menus'],\
[b'\x82\x72\x84\x7b', 'SET'          , ''],\
[b'\x82\x72\xc2\x3d', 'Right<right>' , 'Right directional movement when navigating through OSD menus'],\
[b'\x82\x72\x99\x66', 'Up<up>'       , 'Upward directional movement when navigating through OSD menus'],\
[b'\x80\x70\xc0\x3f', 'AVR Power On' , ''],\
[b'\x80\x70\xd0\x2f', 'DVD'          , ''],\
[b'\x80\x70\xc4\x3b', 'CD'           , ''],\
[b'\x80\x70\xcc\x33', 'TAPE'         , ''],\
[b'\x82\x72\x9b\x64', 'Stereo'       , ''],\
[b'\x80\x70\xc1\x3e', 'Mute'         , ''],\
[b'\x80\x70\xca\x35', 'VID1(VCR)'    , ''],\
[b'\x80\x70\xcb\x34', 'VID2(TV)'     , ''],\
[b'\x80\x70\xce\x31', 'VID3(CBL/SAT)', ''],\
[b'\x80\x70\xd1\x2e', 'VID4'         , ''],\
[b'\x80\x70\x81\x7e', 'AM/FM'        , ''],\
[b'\x82\x72\x5d\xa2', 'Channel Guide', 'Access the Channel Trim Settings menu'],
[b'\x82\x72\xdb\x24', '6CH / 8CH'    , 'The first transmission of this code shows the current mode.  Subsequent transmissions step through the available modes.'],
[b'\x82\x72\x9a\x65', 'Level - Down' , 'Decreases the channel trim level'],
[b'\x82\x72\x99\x66', 'Level - Up  ' , 'Increaces the channel trim level'],
[b'\x80\x70\xdb\x24', 'Sleep'        , ''],\
[b'\x82\x72\x8c\x73', 'Test Tone'    , ''],\
[b'\x80\x70\xc7\x38', 'Volume Up'    , ''],\
[b'\x82\x72\x58\xa7', 'Surr'         , 'Initates surround mode and displays current mode'],\
[b'\x82\x72\x86\x79', 'Surr Down'    , 'Scroll down through surround choices (down arrow)'],\
[b'\x82\x72\x85\x7a', 'Surr Up'      , 'Scroll up through surround choices (up arrow)'],\
[b'\x82\x72\x96\x69', 'Night'        , ''],\
[b'\x82\x72\xdf\x20', 'Multiroom'    , 'Accesses the Multiroom menu and displays current status'],\
[b'\x82\x72\x5f\xa0', 'MRmulti<down>', 'Scroll down through multiroom choices (down arrow)'],\
[b'\x82\x72\x5e\xa1', 'MRmulti<up>  ', 'Scroll up through multiroom choices (up arrow)'],\
[b'\x80\x70\xc8\x37', 'Volume Down'  , ''],\
[b'\x82\x72\x53\xac', 'Speaker Menu' , 'Accesses the Speaker Configuration menu'],\
[b'\x82\x72\x8f\x70', 'Speaker<down>', 'Scrolls down through the speaker configuration choices'],\
[b'\x82\x72\x8e\x71', 'Speaker<up>'  , 'Scrolls up through the speaker configuration choices'],\
[b'\x82\x72\x54\xab', 'Digital/Exit' , 'Accesses Digital Input menu and displays input for current source'],\
[b'\x82\x72\x56\xa9', 'Digital<down>', 'Scrolls down through the list of digital inputs'],\
[b'\x82\x72\x57\xa8', 'Digital<up>+' , 'Scrolls up through the list of digital inputs'],\
[b'\x82\x72\x52\xad', 'Delay'        , 'Accesses delay settings'],\
[b'\x82\x72\x8b\x74', 'Delay<down>-' , 'Scrolls down through the list of digital inputs'],\
[b'\x82\x72\x8a\x75', 'Delay<up>+'   , 'Scrolls up through the list of digital inputs'],\
[b'\x80\x70\x85\x7a', 'Tuning Down -', ''],\
[b'\x82\x72\x5c\xa3', 'OSD'          , 'On Screen Display'],\
[b'\x82\x72\xdd\x22', 'RDS'          , 'Radio Data System (EU)'],\
[b'\x82\x72\xd1\x2e', 'Preset Down'  , ''],\
[b'\x82\x72\x50\xaf', 'Dolby'        , 'To access a Surround Mode group, first use one of these commands to select the desired mode group.  Issue the command again, as needed, to scroll through the list of available modes.'],\
[b'\x82\x72\xa0\x5f', 'DTS Surround' , ''],\
[b'\x82\x72\xa1\x5e', 'DTS NEO:6'    , ''],\
[b'\x82\x72\xa2\x5d', 'Logic 7'      , ''],\
[b'\x80\x70\x93\x6c', 'TUN/M'        , ''],\
[b'\x80\x70\x86\x79', 'Memory'       , ''],\
[b'\x80\x70\x84\x7b', 'Tuning Up'    , ''],\
[b'\x80\x70\x9b\x64', 'Direct'       , ''],\
[b'\x82\x72\xd9\x26', 'Clear'        , ''],\
[b'\x82\x72\xd0\x2f', 'Preset Up +'  , '']]

def sendAVR(command, listen = False, port='/dev/ttyUSB0'):
    command_bytes, command_str, command_desc = command
    print(':: Sending {} to AVR3650...'.format(command_str))
    
    ser = serial.Serial()
    ser.port = port
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
        assert ser.isOpen()
    except serial.SerialException as e:
        print("SerialException: {0}".format(e))
        exit(1)
    except AssertionError as e:
        print("AssertionError: {0}".format(e))
        exit(1)

    ser.flushInput() 	#flush input buffer, discarding all its contents
    ser.flushOutput()	#flush output buffer, aborting current output 

    ### Create Packet
    # Packet Structure & Example (taken from 'RS232 Protocol.pdf')
    # Transmission Type + Data Type + Packet Length + Command + Checksum
    # PCSEND            + 2         + 4             + XXXX    + CC
    # 6 Bytes (ASCII)   + 1 Byte    + 1 Bytes       + Data    + 2 Bytes
    header = b'PCSEND\x02\x04'
    checksum0,checksum1 = 0,0
    for b in command_bytes[::2]: checksum0 ^= b
    for b in command_bytes[1::2]: checksum1 ^= b
    checksum0 = bytes([checksum0])
    checksum1 = bytes([checksum1])
    packet = header + command_bytes + checksum0 + checksum1
    
    ### Write Packet
    printhex = ''.join(hex(x)[2:] for x in packet)
    print('  ','writing {} to AVR3650'.format(printhex))
    ser.write(packet)
    
    if listen:
        time.sleep(.2)  #give the serial port sometime to receive the data
        numOfLines = 0
        while True:
            response = ser.readline()
            print(('read data: ' + response))
            numOfLines = numOfLines + 1
            if (numOfLines >= 5):
                break
    
    ### AVR Status Check (Unimplemented)
    # Sending the following poll will return AVR Display Data
    #status_bytes = b'MPSEND' + b'\x03\x48' + bytes([0]*48) + bytes([0]*2)
    #ser.write(status_bytes)
    #time.sleep(.4)
    #print(ser.inWaiting())
    #print(ser.readline())
    
    ser.close()
    print('::','Done')

if __name__ == '__main__':
    command_idx = int(argv[1])
    sendAVR(commandList[command_idx])


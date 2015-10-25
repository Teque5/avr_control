# avr_control
Serial interface control for Harman Kardon AVR home theater receivers.

# Dependencies
python3 : pySerial
python2 : binascii

# Usage
```
$ python3 avr_control3.py 22
  :: Sending Mute to AVR3650...
     writing 504353454e44248070c13e414e to AVR3650
  :: Done.
```

## File List
#### avr_control2.py
This python2 version will control any modern Harman Kardon receiver including mine, the AVR3650.

#### avr_control3.py
This python3 version will control any modern Harman Kardon receiver including mine, the AVR3650.

#### c_version/
Contains a historical version I used as a prototype but was outdated with an older incorrect message format.

#### harmankardonPDFs/
Contains some official documentation I found reguarding the interface. It does contain additional information about pushing data from your receiver to your PC if you like.

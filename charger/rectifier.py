#!/opt/solar-controller/venv/bin/python

import sys
import can
import struct
import subprocess
import time
import argparse

ARBITRATION_ID = 0x0607FF83
BITRATE = 125000

# 62.5A is the nominal current of Emerson/Vertiv R48-3000e and corresponds to 121%
OUTPUT_CURRENT_RATED_VALUE = 62.5
OUTPUT_CURRENT_RATED_PERCENTAGE_MIN = 10
OUTPUT_CURRENT_RATED_PERCENTAGE_MAX = 121
OUTPUT_CURRENT_RATED_PERCENTAGE = 121
OUTPUT_VOLTAGE_MIN = 41.0
OUTPUT_VOLTAGE_MAX = 58.5

# needs root/sudo access, or configure this part on the OS
def config(channel):
    subprocess.call(['ip', 'link', 'set', 'down', channel])
    subprocess.call(['ip', 'link', 'set', channel, 'type', 'can', 'bitrate', str(BITRATE), 'restart-ms', '1500'])
    subprocess.call(['ip', 'link', 'set', 'up', channel])

# To convert floating point units to 4 bytes in a bytearray
def float_to_bytearray(f):
    value = hex(struct.unpack('<I', struct.pack('<f', f))[0])
    return bytearray.fromhex(value.lstrip('0x').rstrip('L'))

# Get the bus and send data to the specified CAN bus
def send_can_message(channel, data):
    try:
        with can.interface.Bus(bustype='socketcan', channel=channel, bitrate=BITRATE) as bus:
            msg = can.Message(arbitration_id=ARBITRATION_ID, data=data, is_extended_id=True)
            bus.send(msg)
            print(f"Command sent on {bus.channel_info}")
    except can.CanError:
        print("Command NOT sent")

# Set the output voltage to the new value.
# The 'fixed' parameter
#  - if True makes the change permanent ('offline command')
#  - if False the change is temporary (30 seconds per command received, 'online command', repeat at 15 second intervals).
# Voltage between 41.0 and 58.5V - fan will go high below 48V!
def set_voltage(channel, voltage, fixed=False):
    if 41.0 <= voltage <= 58.5:
        b = float_to_bytearray(voltage)
        p = 0x21 if not fixed else 0x24
        data = [0x03, 0xF0, 0x00, p, *b]
        send_can_message(channel, data)
    else:
        print('Voltage should be between 41.0V and 58.5V')

# The output current is set in percent to the rated value of the rectifier written in the manual
# Possible values for 'current': 10% - 121% (rated current in the datasheet = 121%)
# The 'fixed' parameter
#  - if True makes the change permanent ('offline command')
#  - if False the change is temporary (30 seconds per command received, 'online command', repeat at 15 second intervals).
def set_current_percentage(channel, current, fixed=False):
    if 10 <= current <= 121:
        limit = current / 100
        b = float_to_bytearray(limit)
        p = 0x22 if not fixed else 0x19
        data = [0x03, 0xF0, 0x00, p, *b]
        send_can_message(channel, data)
    else:
        print('Current should be between 10% and 121%')

# The output current is set in percent to the rated value of the rectifier written in the manual
# Possible values for 'current': 10% - 121% (rated current in the datasheet = 121%)
# The 'fixed' parameter
#  - if True makes the change permanent ('offline command')
#  - if False the change is temporary (30 seconds per command received, 'online command', repeat at 15 second intervals).
def set_current_value(channel, current, fixed=False):
    percentage = current/OUTPUT_CURRENT_RATED_VALUE*OUTPUT_CURRENT_RATED_PERCENTAGE # 62.5A is the nominal current of Emerson/Vertiv R48-3000e and corresponds to 121%

    current_min = OUTPUT_CURRENT_RATED_PERCENTAGE_MIN*(OUTPUT_CURRENT_RATED_VALUE/OUTPUT_CURRENT_RATED_PERCENTAGE)
    current_max = OUTPUT_CURRENT_RATED_PERCENTAGE_MAX*(OUTPUT_CURRENT_RATED_VALUE/OUTPUT_CURRENT_RATED_PERCENTAGE)

    print(current)
    print(percentage)

    if OUTPUT_CURRENT_RATED_PERCENTAGE_MIN <= percentage <= OUTPUT_CURRENT_RATED_PERCENTAGE_MAX:
        set_current_percentage(channel , percentage, fixed)
    else:
        print(f"Current should be between {current_min} [ADC] and {current_max} [ADC]")


# Time to ramp up the rectifiers output voltage to the set voltage value, and enable/disable
def walk_in(channel, time=0, enable=False):
    if not enable:
        data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00]
    else:
        data = [0x03, 0xF0, 0x00, 0x32, 0x00, 0x01, 0x00, 0x00]
        b = float_to_bytearray(time)
        data.extend(b)
    send_can_message(channel, data)

# AC input current limit (called Diesel power limit): gives the possibility to reduce the overall power of the rectifier
def limit_input(channel, current):
    b = float_to_bytearray(current)
    data = [0x03, 0xF0, 0x00, 0x1A, *b]
    send_can_message(channel, data)

# Restart after overvoltage enable/disable
def restart_overvoltage(channel, state=False):
    if not state:
        data = [0x03, 0xF0, 0x00, 0x39, 0x00, 0x00, 0x00, 0x00]
    else:
        data = [0x03, 0xF0, 0x00, 0x39, 0x00, 0x01, 0x00, 0x00]
    send_can_message(channel, data)


if __name__ == "__main__":
#    config('can0')
#    set_voltage(sys.argv[1], float(sys.argv[2]), False)
#    set_voltage('can0', 56.0, False)
#    set_voltage('can1', 56.0, True)
    #set_current('can0', 10.0, False)
    #walk_in('can0', False)
    #limit_input('can0', 10.0)
    #restart_overvoltage('can0', False)

    parser = argparse.ArgumentParser(description='Set/Get Parameters from Emerson/Vertiv Rectifiers.')

    parser.add_argument('-m', '--mode' , default="set" ,
                    help='Mode of Operation (set/get)')

    parser.add_argument('-v', '--voltage' , type=float , default=52.0 ,
                    help='Voltage Set Point of the Charger [VDC]')

    parser.add_argument('-c', '--current' , type=float , default=50 ,
                    help='Current Set Point of the Charger [ADC]')

    parser.add_argument('-p', '--permanent', default=False ,
                    help='Settings Permanent [True/False]')

    parser.add_argument('-I', '--interface', default="can0" ,
                    help='Adapter Interface (can0, can1, ...)')

    args = parser.parse_args()

    if args.mode == "set":
       # Set Parameters
       set_voltage(args.interface , args.voltage , args.permanent)
       set_current_value(args.interface , args.current , args.permanent)
    elif args.mode == "get":
       # Get Data
       # ...
       set_voltage(args.interface , args.voltage , args.permanent)
       set_current_value(args.interface , args.current , args.permanent)

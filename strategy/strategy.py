# import calendar
import time
from datetime import datetime
import pandas as pd
import os
import pathlib
import random
import json
import pprint

# Import paho-mqtt to interact with BMS / Inverter
from paho.mqtt import client as mqtt_client

# Determine Base Path of the current file
basepath = pathlib.Path(__file__).parent.resolve()
# print(basepath)

# Determine Root Path of the Project
rootpath = basepath.parent.resolve()
# print(rootpath)

# Determine Configuration Path
configpath = os.getenv("STRATEGY_CONFIG_PATH")
if configpath is None:
    configpath = basepath / "config"

# Determine Write Path
tmppath = os.getenv("STRAGEY_TMP_PATH")
if tmppath is None:
    tmppath = rootpath / "tmp"

# Generate a Client ID with the subscribe prefix.
MQTT_CLIENT_ID = f'solarstrategy-subscribe-{random.randint(0, 100)}'

# MQTT Settings
MQTT_BROKER = '192.168.4.10'
MQTT_PORT = 1883
MQTT_USERNAME = ''
MQTT_PASSWORD = ''

# History Settings
HISTORY_LENGTH = 10
HISTORY_FILEPATH = f"{tmppath}/history.json"

SET_VOLTAGE_FILEPATH = f"{tmppath}/set_voltage"
SET_CURRENT_FILEPATH = f"{tmppath}/set_current"

# Battery Settings
CHARGE_PROTECTION_VOLTAGE_SLEW_RATE_MAX_PER_ITERATION = 0.1  # [VDC/iteration]
CHARGE_PROTECTION_VOLTAGE_SLEW_RATE_MAX_PER_SECOND = 0.1/60.0  # [VDC/iteration]

CHARGE_PROTECTION_CURRENT_SLEW_RATE_MAX_PER_ITERATION = 10  # [ADC/iteration]
CHARGE_PROTECTION_CURRENT_SLEW_RATE_MAX_PER_SECOND = 10/60.0  # [ADC/iteration]

# Data <---> MQTT Topics Mappings
MQTT_TOPICS = dict()

# Define Controller Requested Charge Voltage Topic
MQTT_TOPICS["jk-bms-bat02_requested_charge_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_requested_charge_voltage/state'

# Define Controller Requested Charge Current Topic
MQTT_TOPICS["jk-bms-bat02_requested_charge_current"] = 'jk-bms-bat02/sensor/jk-bms-bat02_requested_charge_current/state'

# Define BMS Measurements
MQTT_TOPICS["jk-bms-bat01_min_cell_voltage"] = 'jk-bms-bat01/sensor/jk-bms-bat01_min_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat02_min_cell_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_min_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat03_min_cell_voltage"] = 'jk-bms-bat03/sensor/jk-bms-bat03_min_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat04_min_cell_voltage"] = 'jk-bms-bat04/sensor/jk-bms-bat04_min_cell_voltage/state'

MQTT_TOPICS["jk-bms-bat01_max_cell_voltage"] = 'jk-bms-bat01/sensor/jk-bms-bat01_max_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat02_max_cell_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_max_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat03_max_cell_voltage"] = 'jk-bms-bat03/sensor/jk-bms-bat03_max_cell_voltage/state'
MQTT_TOPICS["jk-bms-bat04_max_cell_voltage"] = 'jk-bms-bat04/sensor/jk-bms-bat04_max_cell_voltage/state'

MQTT_TOPICS["jk_bms_bat01_total_voltage"] = 'jk-bms-bat01/sensor/jk-bms-bat01_total_voltage/state'
MQTT_TOPICS["jk_bms_bat02_total_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_total_voltage/state'
MQTT_TOPICS["jk_bms_bat03_total_voltage"] = 'jk-bms-bat03/sensor/jk-bms-bat03_total_voltage/state'
MQTT_TOPICS["jk_bms_bat04_total_voltage"] = 'jk-bms-bat04/sensor/jk-bms-bat04_total_voltage/state'

MQTT_TOPICS["jk-bms-bat01_state_of_charge"] = 'jk-bms-bat01/sensor/jk-bms-bat01_state_of_charge/state'
MQTT_TOPICS["jk-bms-bat02_state_of_charge"] = 'jk-bms-bat02/sensor/jk-bms-bat02_state_of_charge/state'
MQTT_TOPICS["jk-bms-bat03_state_of_charge"] = 'jk-bms-bat03/sensor/jk-bms-bat03_state_of_charge/state'
MQTT_TOPICS["jk-bms-bat04_state_of_charge"] = 'jk-bms-bat04/sensor/jk-bms-bat04_state_of_charge/state'

# Define Requested Charge Voltage Variable
# bms_requested_charge_voltage = 51.0 # VDC (Default Value)
bms_requested_charge_voltage_offset_value = -0.2   # VDC (Fixed)
# bms_requested_charge_voltage_offset_value = 0.0  # VDC (Fixed)


# Get data Mapping from Topic
def get_key_from_topic(topic) -> str:
    for key in MQTT_TOPICS:
        if MQTT_TOPICS.get(key) == topic:
            return key

    # Not Found
    return None

# Connect to MQTT broker
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Old Paho MQTT Version 1.x
    # client = mqtt_client.Client(MQTT_CLIENT_ID)

    # New Paho MQTT Version 2.x
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, MQTT_CLIENT_ID)

    # client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT)
    return client


def subscribe(client: mqtt_client , data):
    def on_message(client, userdata, msg):
        # Do nothing
        # pass
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # print(data)
        topic_name = msg.topic
        print(topic_name)
        data_field = get_key_from_topic(topic_name)
        topic_value = float(msg.payload.decode("UTF-8"))

        data[data_field] = topic_value

        # Echo
        print(f'Received {topic_name}: {topic_value}')





        # requestedchargevoltage = float(msg.payload.decode("UTF-8"))
        # data['jk-bms-bat02_requested_charge_voltage'] = requestedchargevoltage
        # print(f'Requested Charge Voltage: {requestedchargevoltage}')

        # key = topic_name.replace(prefix + '_' , "")
        # key = key.replace(prefix , "")
        # key = key.replace('/state' , "")
        # key = key.replace('/debug' , "") # Ignore debug messages
        # key = key.lstrip('/')
        # ###print(key)
        # s = re.split(r'/', key)
        # ###print(s)

        # if len(s) == 2:
        #     t = s[0]
        #     k = s[1]
        # #####print(t)
        # #####print(k)
        #     if k in data:
        #         pass
        #     else:
        #         data[k] = init_signal()
        #         data[k]['ID'] = k
        # 
        #     data[k]['Type'] = t
        #     data[k]['Value'] = msg.payload.decode()
        #     data[k]['Battery_Description'] = prefix
        #     data[k]['Battery_Number'] = int(prefix.replace(battery_txt , ''))
        # 
        #     if "voltage" in k:
        #          data[k]['Unit'] = "VDC"
        #     elif "current" in k:
        #         data[k]['Unit'] = "ADC"
        #     elif "power" in k:
        #         data[k]['Unit'] = "W"
        #     elif "temperature" in k:
        #         data[k]['Unit'] = "°C"
        #     elif "state_of_charge" in k:
        #         data[k]['Unit'] = "%"
        #     elif "capacity" in k:
        #        data[k]['Unit'] = "Ah"
        #     elif "total_runtime" in k and "formatted" not in k:
        #         data[k]['Unit'] = "s"
        #     elif "resistance" in k:
        #         data[k]['Unit'] = "mOhm"
        #     else:
        #         data[k]['Unit'] = "none"
        #         #data[k]['Value'] = msg.payload.decode("UTF-8")
        #

    # Subscribe to all MQTT Topics
    for key in MQTT_TOPICS:
        topic_name = MQTT_TOPICS[key]
        client.subscribe(topic_name)

    # Define Handler to store Responses
    client.on_message = on_message


# Initilize Scheme for Measurements
def init_measurement_scheme() -> None:
    # Initialize Data as an Empty Dictionary
    data = { }

    # Add Fields

    # Controller Reference Voltage
    data['jk-bms-bat02_requested_charge_voltage'] = float(51.2)

    # Controller Reference Current
    data['jk-bms-bat02_requested_charge_current'] = float(50.0)

    # BMS Measurements
    data['jk-bms-bat01_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat02_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat03_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat04_min_cell_voltage'] = float(2.50)

    data['jk-bms-bat01_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat02_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat03_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat04_max_cell_voltage'] = float(3.65)

    data['jk_bms_bat01_total_voltage'] = float(53.0)
    data['jk_bms_bat02_total_voltage'] = float(53.0)
    data['jk_bms_bat03_total_voltage'] = float(53.0)
    data['jk_bms_bat04_total_voltage'] = float(53.0)

    # At Initialization better to leave all to 100% or have a mix of 0% and 100%
    data['jk-bms-bat01_state_of_charge'] = float(0.0)
    data['jk-bms-bat02_state_of_charge'] = float(100.0)
    data['jk-bms-bat03_state_of_charge'] = float(0.0)
    data['jk-bms-bat04_state_of_charge'] = float(100.0)

    # Return Structure
    return data


# Initialize History Scheme
def init_history_scheme() -> list:
    # Initialize Data as a List
    data = []

    # Init each Item
    for index in range(HISTORY_LENGTH):
        # Init Item
        data.append(dict())

        # Init Fields
        init_history_fields(data[index])

    # Return Value
    return data


# Initialize History for one Iteration:
def init_history_fields(history_dict: dict) -> None:
    init_history_field(history_dict, 'bms_requested_charge_voltage')
    init_history_field(history_dict, 'bms_requested_charge_current')

    init_history_field(history_dict, 'set_voltage_raw')
    init_history_field(history_dict, 'set_voltage_rounded')
    init_history_field(history_dict, 'set_current_raw')
    init_history_field(history_dict, 'set_current_rounded')
    init_history_field(history_dict, 'max_state_of_charge')
    init_history_field(history_dict, 'min_state_of_charge')
    init_history_field(history_dict, 'max_cell_voltage')
    init_history_field(history_dict, 'min_cell_voltage')
    init_history_field(history_dict, 'max_total_voltage')
    init_history_field(history_dict, 'min_total_voltage')

    init_history_field(history_dict, 'time_unix')
    init_history_field(history_dict, 'time_formatted', '')
    init_history_field(history_dict, 'time_delta')

    init_history_field(history_dict, 'slew_rate_set_current')
    init_history_field(history_dict, 'slew_rate_set_voltage')

    # history_dict['set_voltage_raw'] = float(0.0)
    # history_dict['set_voltage_rounded'] = float(0.0)
    # history_dict['set_current_raw'] = float(0.0)
    # history_dict['set_current_rounded'] = float(0.0)
    # history_dict['max_state_of_charge'] = float(0.0)
    # history_dict['min_state_of_charge'] = float(0.0)
    # history_dict['max_cell_voltage'] = float(0.0)
    # history_dict['min_cell_voltage'] = float(0.0)
    # history_dict['max_total_voltage'] = float(0.0)
    # history_dict['min_total_voltage'] = float(0.0)


# Initialize History Field for one Parameter
def init_history_field(history_dict: dict, history_field: str, history_value: float | str = 0.0) -> None:
    if history_field not in history_dict:
        history_dict[history_field] = history_value


# Find History Index
def find_history_index() -> int:
    # Use Global Variable
    # No need to specify "global" since we do NOT want to modify history_data
    # history_data

    # Loop
    # for index in range(len(history_data)-1,0,-1):
    #     # Empty row means that the history File is not fully populated yet
    #     if history_data[index].get('set_voltage_raw') == float(0.0):
    #         return index

    # If all Fields are non-zero, then the History File has been fully populated
    # return len(history_data)

    # Always store new Data at the Last Position
    return len(history_data) - 1


# Shift History Data
def shift_history() -> None:
    # Allow Function to modify Global Variable
    global history_data

    # Remove the First Element
    history_data.pop(0)

    # Create a new Entry at the End, if one or more are missing
    current_length = len(history_data)
    if current_length < HISTORY_LENGTH:
        for index in range(current_length, HISTORY_LENGTH - 1):
            history_data.append(dict())
            init_history_fields(history_data[index])


# Get History Parameter
def get_history_data(parameter: str, count: int = HISTORY_LENGTH) -> list[float]:
    return [history_data[index].get(parameter) for index in range(HISTORY_LENGTH-count, HISTORY_LENGTH-1, 1)]

# Load History File from JSON File
def load_history() -> dict:
    if os.path.exists(HISTORY_FILEPATH):
        # Echo
        print(f"File {HISTORY_FILEPATH} exists: Opening File and Loading Data")

        # Open File in Read Mode
        try:
            with open(HISTORY_FILEPATH , 'r') as history_file_handle:
                # Read the entire content of the file
                history_data = json.loads(history_file_handle.read())

                # Close File
                history_file_handle.close()
        except json.decoder.JSONDecodeError as e:
            # Echo
            print(f"ERROR: Loading file {HISTORY_FILEPATH} as JSON Failed")
            print(f"ERROR: The message was {e}")
            print(f"Deleting file {HISTORY_FILEPATH} and starting from Scratch")

            # Delete existing File
            os.remove(HISTORY_FILEPATH)

            # Recreate Default Scheme
            history_data = create_history_file()
    else:
        # Create Default Scheme
        history_data = create_history_file()

    # Return Value
    return history_data


# Create History File from Scratch
def create_history_file() -> list:
    # Echo
    print(f"File {HISTORY_FILEPATH} does NOT exist: Create File with initial Values")

    # Create Initial Contents
    history_data = init_history_scheme()

    # Create & Update History File
    update_history(history_data=history_data)

    # Return Value
    return history_data


# Update History File to JSON File
def update_history(history_data: dict) -> None:
    # Create New File
    with open(HISTORY_FILEPATH , 'w') as history_file_handle:
        # Convert Dictionnary to JSON String
        json_data = json.dumps(history_data)

        # Write the Contents to File
        history_file_handle.write(json_data)

        # Close File
        history_file_handle.close()


# Add Data to History
def add_history(index: int, parameter: str, value: float | str) -> None:
    # Allow function to modify Global Variables
    global history_data

    # Debug
    print(f"Set history_data[{index}]['{parameter}'] = {value}")

    # Set Parameter's Value
    history_data[index][parameter] = value


# Print History Data
def print_history() -> None:
    print(json.dumps(history_data, sort_keys=True, indent=4))


# Strategy Iteration
def strategy_iteration() -> None:
    # Define Global Variable so we can modify them
    global history_data

    # Init Scheme
    data = init_measurement_scheme()

    # Initialize MQTT Connection
    client = connect_mqtt()
    subscribe(client, data)

    # Start MQTT Loop and Fetch MQTT Data
    client.loop_start()

    # Wait 5 Seconds (enough to get MQTT State Topic a few Times)
    time.sleep(5)

    # Stop MQTT Loop
    client.loop_stop()

    # Get current date and time
    now = datetime.now() # current date and time

    # Store UNIX Timestamp
    time_unix = time.mktime(now.timetuple())

    # Store Formatted Time
    time_formatted = now.strftime("%Y-%m-%d-%Hh%Mm%Ss")

    # Extract datetime
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    # Extract date
    current_date = now.strftime("%Y-%m-%d")

    # Extract time
    current_time = now.strftime("%H:%M:%S")

    # Debug
    # print("date:",current_date)
    # print("date:",current_time)

    # Reference values are stored in strategy file
    reference_file = f"{configpath}/{current_date}.xlsx"

    print(f"Using Reference File {reference_file}")

    # Declare Variables
    set_voltage_raw = 51.5
    set_current_raw = 50.0

    # Open file
    if os.path.exists(reference_file):
        # Load the file
        excel_data_df = pd.read_excel(reference_file, sheet_name=0)

        # Debug contents
        # print(excel_data_df)

        # Make a copy of the instance
        df = excel_data_df

        # Go through the file
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['time_start'] = pd.to_datetime(df['time_start'] , format='%H:%M:%S').dt.time
        df['time_end'] = pd.to_datetime(df['time_end'] , format='%H:%M:%S').dt.time

        df['datetime_start'] = pd.to_datetime(df['datetime_start'], format='%Y-%m-%d %H:%M:%S')
        df['datetime_end'] = pd.to_datetime(df['datetime_end'], format='%Y-%m-%d %H:%M:%S')

        # Debug
        # print(df)

        #current_setting = df.loc[ ( current_datetime >= df['datetime_start'] )
        #             & ( current_datetime < df['datetime_end'] ) ]

        current_setting = df.query(f"datetime_start <= '{current_datetime}' \
                       and datetime_end > '{current_datetime}'")

        # Debug
        print(current_setting)
    else:
        print(f"Error: file {reference_file} does NOT exist !")
        print("Using Default Values")

        # Use Default Value for Voltage
        set_voltage_raw = 51.2

    # Load History File
    history_data = load_history()

    # Retrieve Set Voltage Setting
    set_voltage_raw = current_setting.get("set_voltage").values[0]

    # Retrieve Set Current Setting
    set_current_raw = current_setting.get("set_current").values[0]

    # Controller requested Charge Voltage
    bms_requested_charge_voltage = min([
                                    data['jk-bms-bat02_requested_charge_voltage']
                                ])

    bms_requested_charge_current = min([
                                    data['jk-bms-bat02_requested_charge_current']
                                ])

    # BMS Measurements
    max_cell_voltage = max([data['jk-bms-bat01_max_cell_voltage'],
                            data['jk-bms-bat02_max_cell_voltage'],
                            data['jk-bms-bat03_max_cell_voltage'],
                            data['jk-bms-bat04_max_cell_voltage']
                            ])

    min_cell_voltage = min([data['jk-bms-bat01_min_cell_voltage'],
                            data['jk-bms-bat02_min_cell_voltage'],
                            data['jk-bms-bat03_min_cell_voltage'],
                            data['jk-bms-bat04_min_cell_voltage']
                            ])

    array_state_of_charge = [data['jk-bms-bat01_state_of_charge'],
                                data['jk-bms-bat02_state_of_charge'],
                                data['jk-bms-bat03_state_of_charge'],
                                data['jk-bms-bat04_state_of_charge']
                                ]

    array_total_voltage = [data['jk_bms_bat01_total_voltage'],
                            data['jk_bms_bat02_total_voltage'],
                            data['jk_bms_bat03_total_voltage'],
                            data['jk_bms_bat04_total_voltage']
                            ]

    max_state_of_charge = max(array_state_of_charge)
    min_state_of_charge = min(array_state_of_charge)

    max_total_voltage = max(array_total_voltage)
    min_total_voltage = min(array_total_voltage)

    # Echo
    print(f"Maximum Cell Voltage: {max_cell_voltage} VDC")
    print(f"Minimum Cell Voltage: {min_cell_voltage} VDC")
    print(f"Maximum State of Charge: {max_state_of_charge} %")
    print(f"Minimum State of Charge: {min_state_of_charge} %")
    print(f"Maximum Total Voltage: {max_total_voltage} VDC")
    print(f"Minimum Total Voltage: {min_total_voltage} VDC")
    print(f"Requested Charge Voltage (BMS): {bms_requested_charge_voltage} VDC")
    print(f"Requested Charge Current (BMS): {bms_requested_charge_current} ADC")

    # Reduce Voltage if requested by BMS

    if set_voltage_raw > (bms_requested_charge_voltage + bms_requested_charge_voltage_offset_value):
        print(f'Output Voltage tuned down from {set_voltage_raw} to {bms_requested_charge_voltage + bms_requested_charge_voltage_offset_value}')

        set_voltage_raw = bms_requested_charge_voltage + bms_requested_charge_voltage_offset_value

    # Reduce Voltage if we are already near the Top of the Charge Curve, i.e. if SOC > 99% OR V_Cell_Max > 3.50 VDC
    # !! DISABLE SOC LIMITATION BY SETTING IT > 100.0 !!

    # !! NEED TO IMPLEMENT A SLEW-RATE LIMITATION in order to be able to ramp up the Voltage Again if SOC is "HIGH" !!
    # !! Need therefore to save the History to a Temporary File in order to know the Previous Value !!
    # !! Otherwise the Balancer will turn off Immediately :( !!
    if max_state_of_charge > 999.0 or max_cell_voltage > 3.52:
        safe_voltage = 54.6

        if safe_voltage < set_voltage_raw:
            print(f'Output Voltage tuned down from {set_voltage_raw} to {min([set_voltage_raw, safe_voltage])}')

        set_voltage_raw = min([set_voltage_raw, safe_voltage])

    if min_state_of_charge < 10.0 or min_cell_voltage < 3.05:
        safe_voltage = 51.6

        if safe_voltage > set_voltage_raw:
            print(f'Output Voltage tuned up from {set_voltage_raw} to {max([set_voltage_raw, safe_voltage])}')

        set_voltage_raw = max([set_voltage_raw, safe_voltage])

    # Get Historic Data for the Required Fields
    set_voltage_raw_history = get_history_data("set_voltage_raw")
    set_current_raw_history = get_history_data("set_current_raw")
    time_unix_history = get_history_data("time_unix")

    # Delta Values
    delta_set_voltage = set_voltage_raw - set_voltage_raw_history[-1]
    delta_set_current = set_current_raw - set_current_raw_history[-1]
    delta_time_unix = time_unix - time_unix_history[-1]

    # Calculate Slew Rate
    set_voltage_slew_rate = round(delta_set_voltage/delta_time_unix, 6)
    set_current_slew_rate = round(delta_set_current/delta_time_unix, 6)

    # Limit Charge Slew Rate if max_cell_voltage is high
    if max_cell_voltage > 3.45:
        # Echo
        print("Charge Voltage slew Rate Control")
        print(f"\tDelta Set Voltage = {delta_set_voltage} [VDC]")
        print(f"\tDelta Unix Time = {delta_time_unix} [s]")
        print(f"\tVoltage Slew Rate = {set_voltage_slew_rate} [VDC/s]")

        # Get Previous set_voltage Data
        if set_voltage_slew_rate > CHARGE_PROTECTION_VOLTAGE_SLEW_RATE_MAX_PER_SECOND:
            set_voltage_raw = min([set_voltage_raw,
                                    set_voltage_raw_history[-1] + CHARGE_PROTECTION_VOLTAGE_SLEW_RATE_MAX_PER_SECOND*delta_time_unix
                                    ])

    # Only keep 1 Decimal for Voltage Reference
    set_voltage_rounded = round(set_voltage_raw, 1)

    # Only keep 1 Decimal for Current Reference
    set_current_rounded = round(set_current_raw, 1)


    # Convert Voltage to String
    set_voltage_str = str(set_voltage_rounded)

    # Write Voltage Reference to File
    voltage_file_handle = open(SET_VOLTAGE_FILEPATH , 'w')
    voltage_file_handle.write(set_voltage_str)
    voltage_file_handle.close()

    print(f"Voltage Set to {set_voltage_raw} VDC")

    # Convert Current to String
    set_current_str = str(set_current_rounded)

    # Write Current Reference to File
    current_file_handle = open(SET_CURRENT_FILEPATH , 'w')
    current_file_handle.write(set_current_str)
    current_file_handle.close()

    print(f"Current Set to {set_current_raw} ADC")

    # Shift History Data so we are Ready to store Data from this Iteration
    shift_history()

    # Save Previous Values
    history_index = find_history_index()

    # Add Data to History
    add_history(index=history_index, parameter='bms_requested_charge_voltage' , value=bms_requested_charge_voltage)
    add_history(index=history_index, parameter='bms_requested_charge_current' , value=bms_requested_charge_current)   

    add_history(index=history_index, parameter='set_voltage_raw' , value=set_voltage_raw)
    add_history(index=history_index, parameter='set_voltage_rounded' , value=set_voltage_rounded)

    add_history(index=history_index, parameter='set_current_raw' , value=set_current_raw)
    add_history(index=history_index, parameter='set_current_rounded' , value=set_current_rounded)

    add_history(index=history_index, parameter='max_cell_voltage' , value=max_cell_voltage)
    add_history(index=history_index, parameter='min_cell_voltage' , value=min_cell_voltage)

    add_history(index=history_index, parameter='max_state_of_charge', value=max_state_of_charge)
    add_history(index=history_index, parameter='min_state_of_charge', value=min_state_of_charge)

    add_history(index=history_index, parameter='max_total_voltage' , value=max_total_voltage)
    add_history(index=history_index, parameter='min_total_voltage' , value=min_total_voltage)

    add_history(index=history_index, parameter='time_unix' , value=time_unix)
    add_history(index=history_index, parameter='time_formatted' , value=time_formatted)
    add_history(index=history_index, parameter='delta_time_unix' , value=delta_time_unix)

    add_history(index=history_index, parameter='slew_rate_set_voltage' , value=set_voltage_slew_rate)
    add_history(index=history_index, parameter='slew_rate_set_current' , value=set_current_slew_rate)

    # Update History File
    update_history(history_data=history_data)

    # Print History Data
    print_history()


# Strategy Loop
def strategy_loop() -> None:
        while True:
            # Run Iteration
            strategy_iteration()

            # Wait 3600 Seconds
            time.sleep(wait_time)

# Main Function (execution as Script)
if __name__ == "__main__":
    # Check if infinite Loop is enabled
    infinite_loop_enabled = os.getenv("ENABLE_INFINITE_LOOP")

    # Get Iteration Wait Time
    wait_time = os.getenv("ITERATION_WAIT_TIME")

    if infinite_loop_enabled is True:
        # Run Loop
        strategy_loop()
    else:
        # Run single Iteration
        strategy_iteration()

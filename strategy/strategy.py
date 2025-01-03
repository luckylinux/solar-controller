import calendar
import time
from datetime import datetime
import pandas as pd
import os
import pathlib
import random

# Import paho-mqtt to interact with BMS / Inverter
from paho.mqtt import client as mqtt_client

# Generate a Client ID with the subscribe prefix.
client_id = f'solarstrategy-subscribe-{random.randint(0, 100)}'

# MQTT Settings
mqtt_broker = '192.168.4.10'
mqtt_port = 1883
mqtt_username = ''
mqtt_passowrd = ''

# Data <---> MQTT Topics Mappings
mqtt_topic = dict()

# Define Controller Requested Charge Voltage Topic
mqtt_topic["jk-bms-bat02_requested_charge_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_requested_charge_voltage/state'

# Define BMS Measurements
mqtt_topic["jk-bms-bat01_min_cell_voltage"] = 'jk-bms-bat01/sensor/jk-bms-bat01_min_cell_voltage/state'
mqtt_topic["jk-bms-bat02_min_cell_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_min_cell_voltage/state'
mqtt_topic["jk-bms-bat03_min_cell_voltage"] = 'jk-bms-bat03/sensor/jk-bms-bat03_min_cell_voltage/state'
mqtt_topic["jk-bms-bat04_min_cell_voltage"] = 'jk-bms-bat04/sensor/jk-bms-bat04_min_cell_voltage/state'

mqtt_topic["jk-bms-bat01_max_cell_voltage"] = 'jk-bms-bat01/sensor/jk-bms-bat01_max_cell_voltage/state'
mqtt_topic["jk-bms-bat02_max_cell_voltage"] = 'jk-bms-bat02/sensor/jk-bms-bat02_max_cell_voltage/state'
mqtt_topic["jk-bms-bat03_max_cell_voltage"] = 'jk-bms-bat03/sensor/jk-bms-bat03_max_cell_voltage/state'
mqtt_topic["jk-bms-bat04_max_cell_voltage"] = 'jk-bms-bat04/sensor/jk-bms-bat04_max_cell_voltage/state'

mqtt_topic["jk-bms-bat01_state_of_charge"] = 'jk-bms-bat01/sensor/jk-bms-bat01_state_of_charge/state'
mqtt_topic["jk-bms-bat02_state_of_charge"] = 'jk-bms-bat02/sensor/jk-bms-bat02_state_of_charge/state'
mqtt_topic["jk-bms-bat03_state_of_charge"] = 'jk-bms-bat03/sensor/jk-bms-bat03_state_of_charge/state'
mqtt_topic["jk-bms-bat04_state_of_charge"] = 'jk-bms-bat04/sensor/jk-bms-bat04_state_of_charge/state'

# Define Requested Charge Voltage Variable
# requested_charge_voltage = 51.0 # VDC (Default Value)
requested_charge_voltage_offset_value = -0.2   # VDC (Fixed)
# requested_charge_voltage_offset_value = 0.0  # VDC (Fixed)


# Get data Mapping from Topic
def get_key_from_topic(topic) -> str:
    for key in mqtt_topic:
        if mqtt_topic.get(key) == topic:
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

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(mqtt_username, mqtt_password)
    client.on_connect = on_connect
    client.connect(mqtt_broker, mqtt_port)
    return client


def subscribe(client: mqtt_client , data):
    def on_message(client, userdata, msg):
        # Do nothing
        #pass
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        #print(data)
        topic_name = msg.topic
        print(topic_name)
        data_field = get_key_from_topic(topic_name)
        topic_value = float(msg.payload.decode("UTF-8"))

        data[data_field] = topic_value
        print(f'Received {topic_name}: {topic_value}')

        #requestedchargevoltage = float(msg.payload.decode("UTF-8"))
        #data['jk-bms-bat02_requested_charge_voltage'] = requestedchargevoltage
        #print(f'Requested Charge Voltage: {requestedchargevoltage}')

        #key = topic_name.replace(prefix + '_' , "")
        #key = key.replace(prefix , "")
        #key = key.replace('/state' , "")
        #key = key.replace('/debug' , "") # Ignore debug messages
        #key = key.lstrip('/')
        ####print(key)
        #s = re.split(r'/', key)
        ####print(s)

        #if len(s) == 2:
        #    t = s[0]
        #    k = s[1]
        ######print(t)
        ######print(k)
        #    if k in data:
        #        pass
        #    else:
        #        data[k] = init_signal()
        #        data[k]['ID'] = k
        #
        #    data[k]['Type'] = t
        #    data[k]['Value'] = msg.payload.decode()
        #    data[k]['Battery_Description'] = prefix
        #    data[k]['Battery_Number'] = int(prefix.replace(battery_txt , ''))
        #
        #    if "voltage" in k:
        #         data[k]['Unit'] = "VDC"
        #    elif "current" in k:
        #        data[k]['Unit'] = "ADC"
        #    elif "power" in k:
        #        data[k]['Unit'] = "W"
        #    elif "temperature" in k:
        #        data[k]['Unit'] = "°C"
        #    elif "state_of_charge" in k:
        #        data[k]['Unit'] = "%"
        #    elif "capacity" in k:
        #        data[k]['Unit'] = "Ah"
        #    elif "total_runtime" in k and "formatted" not in k:
        #        data[k]['Unit'] = "s"
        #    elif "resistance" in k:
        #        data[k]['Unit'] = "mOhm"
        #    else:
        #        data[k]['Unit'] = "none"
        #        #data[k]['Value'] = msg.payload.decode("UTF-8")
        #

    # Subscribe to all MQTT Topics
    for key in mqtt_topic:
        topic_name = mqtt_topic[key]
        client.subscribe(topic_name)

    # Define Handler to store Responses
    client.on_message = on_message


def init_scheme():
    # Initialize Data as an Empty Dictionary
    data = { }

    # Add Fields

    # Controller Reference Voltage
    data['jk-bms-bat02_requested_charge_voltage'] = float(51.2)

    # BMS Measurements
    data['jk-bms-bat01_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat02_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat03_min_cell_voltage'] = float(2.50)
    data['jk-bms-bat04_min_cell_voltage'] = float(2.50)

    data['jk-bms-bat01_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat02_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat03_max_cell_voltage'] = float(3.65)
    data['jk-bms-bat04_max_cell_voltage'] = float(3.65)

    # At Initialization better to leave all to 100% or have a mix of 0% and 100%
    data['jk-bms-bat01_state_of_charge'] = float(0.0)
    data['jk-bms-bat02_state_of_charge'] = float(100.0)
    data['jk-bms-bat03_state_of_charge'] = float(0.0)
    data['jk-bms-bat04_state_of_charge'] = float(100.0)

    # Return Structure
    return data


if __name__ == "__main__":
    # Init Scheme
    data = init_scheme()

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

    # Extract datetime
    current_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

    # Extract date
    current_date = now.strftime("%Y-%m-%d")

    # Extract time
    current_time = now.strftime("%H:%M:%S")

    # Debug
    #print("date:",current_date)	
    #print("date:",current_time)	

    # Determine Base Path of the current file
    basepath = pathlib.Path(__file__).parent.resolve()
    #print(basepath)

    # Determine Root Path of the Project
    rootpath = basepath.parent.resolve()
    #print(rootpath)

    # Reference values are stored in strategy file
    reference_file = f"{basepath}/{current_date}.xlsx";

    print(f"Using Reference File {reference_file}")
    
    # Declare Variables
    set_voltage = 51.5
    set_current = 50.0

    # Open file
    if os.path.exists(reference_file):
        # Load the file
        excel_data_df = pd.read_excel(reference_file)

        # Debug contents
        #print(excel_data_df)

        # Make a copy of the instance
        df = excel_data_df

        # Go through the file
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df['time_start'] = pd.to_datetime(df['time_start'] , format='%H:%M:%S').dt.time
        df['time_end'] = pd.to_datetime(df['time_end'] , format='%H:%M:%S').dt.time

        df['datetime_start'] = pd.to_datetime(df['datetime_start'], format='%Y-%m-%d %H:%M:%S')
        df['datetime_end'] = pd.to_datetime(df['datetime_end'], format='%Y-%m-%d %H:%M:%S')

        # Debug
        #print(df)

        #current_setting = df.loc[ ( current_datetime >= df['datetime_start'] )
        #             & ( current_datetime < df['datetime_end'] ) ]

        current_setting = df.query(f"datetime_start <= '{current_datetime}' \
                       and datetime_end > '{current_datetime}'")

        # Debug
        print(current_setting) 
        
        # Set Voltage
        set_voltage = current_setting.get("set_voltage").values[0]
        
        # Controller requested Charge Voltage
        requested_charge_voltage = min([
                                        data['jk-bms-bat02_requested_charge_voltage']
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

        max_state_of_charge = max(array_state_of_charge)
        min_state_of_charge = min(array_state_of_charge)

        # Echo
        print(f"Maximum Cell Voltage: {max_cell_voltage} VDC")
        print(f"Minimum Cell Voltage: {min_cell_voltage} VDC")
        print(f"Maximum State of Charge: {max_state_of_charge} %")
        print(f"Minimum State of Charge: {min_state_of_charge} %")
        print(f"Requested Charge Voltage (BMS): {requested_charge_voltage} VDC")

        # Reduce Voltage if requested by BMS
        
        if set_voltage > (requested_charge_voltage + requested_charge_voltage_offset_value):
            print(f'Output Voltage tuned down from {set_voltage} to {requested_charge_voltage + requested_charge_voltage_offset_value}')

            set_voltage = requested_charge_voltage + requested_charge_voltage_offset_value
        
        # Reduce Voltage if we are already near the Top of the Charge Curve, i.e. if SOC > 95% OR V_Cell_Max > 3.48 VDC
        if max_state_of_charge > 95 or max_cell_voltage > 3.48:
            safe_voltage = 54.2

            if safe_voltage < set_voltage:
                print(f'Output Voltage tuned down from {set_voltage} to {min([set_voltage, safe_voltage])}')
            
            set_voltage = min([set_voltage, safe_voltage])

        if min_state_of_charge < 0.10 or min_cell_voltage < 3.05:
            safe_voltage = 51.6

            if safe_voltage > set_voltage:
                print(f'Output Voltage tuned up from {set_voltage} to {max([set_voltage, safe_voltage])}')
            
            set_voltage = max([set_voltage, safe_voltage])


        # Only keep 1 Decimal for Voltage Reference
        set_voltage = round(set_voltage, 1)

        # Set Current
        set_current = current_setting.get("set_current").values[0]

        # Only keep 1 Decimal for Current Reference
        set_current = round(set_current, 1)

    else:
        print(f"Error: file {reference_file} does NOT exist !")
        print(f"Using Default Values")
        
        # Use Default Value for Voltage
        set_voltage = 51.2
	
        # Use Default Value for Current
        set_current = 50.0
    
    
        
    # Convert Voltage to String
    set_voltage_str = str(set_voltage)

    # Write Voltage Reference to File
    voltage_file_handle = open(f"{rootpath}/tmp/set_voltage" , 'w')
    voltage_file_handle.write(set_voltage_str)
    voltage_file_handle.close()
    
    print(f"Voltage Set to {set_voltage} VDC")
    
    # Convert Current to String
    set_current_str = str(set_current)

    # Write Current Reference to File
    current_file_handle = open(f"{rootpath}/tmp/set_current" , 'w')
    current_file_handle.write(set_current_str)
    current_file_handle.close()

    print(f"Current Set to {set_current} ADC")

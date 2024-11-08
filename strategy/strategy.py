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

# Define Requested Charge Voltage Topic
mqtt_topic = 'jk-bms-bat02/sensor/jk-bms-bat02_requested_charge_voltage/state'

# Define Requested Charge Voltage Variable
#requestedchargevoltage = 51.0 # VDC (Default Value)
requestedchargevoltageoffsetvalue = -0.2 # VDC (Fixed)
#requestedchargevoltageoffsetvalue = 0.0 # VDC (Fixed)

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
        orig_topic = msg.topic
        print(orig_topic)

        requestedchargevoltage = float(msg.payload.decode("UTF-8"))
        data['Requested_Charge_Voltage'] = requestedchargevoltage
        print(f'Requested Charge Voltage: {requestedchargevoltage}')

        #key = orig_topic.replace(prefix + '_' , "")
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
    client.subscribe(mqtt_topic)
    client.on_message = on_message


def init_scheme():
    # Initialize Data as an Empty Dictionary
    data = { }

    # Add Fields
    data['Requested_Charge_Voltage'] = float(51.2); # VDC (default Value)

    # Return Structure
    return data


if __name__ == "__main__":
    # Init Scheme
    data = init_scheme()

    # Initialize MQTT Connection
    client = connect_mqtt()
    subscribe(client , data)

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

        # Reduce Voltage if requested by BMS
        requestedchargevoltage = data['Requested_Charge_Voltage']
        if set_voltage > (requestedchargevoltage + requestedchargevoltageoffsetvalue):
            print(f'Output Voltage tuned down from {set_voltage} to {requestedchargevoltage + requestedchargevoltageoffsetvalue}')
            set_voltage = requestedchargevoltage + requestedchargevoltageoffsetvalue
        
        # Only keep 1 Decimal for Voltage Reference
        set_voltage = round(set_voltage , 1)

        # Set Current
        set_current = current_setting.get("set_current").values[0]

        # Only keep 1 Decimal for Current Reference
        set_current = round(set_current , 1)

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

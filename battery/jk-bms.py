import random
import tabulate

from paho.mqtt import client as mqtt_client
import json
import pandas as pd

import os
import pathlib

#from ..config.battery import battery

from io import StringIO

import re

broker = '192.168.4.10'
port = 1883
topic = "jk-bms-bat02/#"
prefix = "jk-bms-bat02"

NCELLS = 16

#data

# Generate a Client ID with the subscribe prefix.
client_id = f'solarcontroller-subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client , data):
    def on_message(client, userdata, msg):
        # Do nothing
        #pass
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        #print(data)
        orig_topic = msg.topic
        key = orig_topic.replace(prefix + '_' , "")
        key = key.replace(prefix , "")
        key = key.replace('/state' , "")
        key = key.replace('/debug' , "") # Ignore debug messages
        key = key.lstrip('/')
        #print(key)
        s = re.split(r'/', key)
        #print(s)

        if len(s) == 2:
            t = s[0]
            k = s[1]
            #print(t)
            #print(k)
            if k in data:
                pass
            else:
                data[k] = init_signal()
                data[k]['ID'] = k
                
            data[k]['Type'] = t
            data[k]['Value'] = msg.payload.decode()


            if "voltage" in k:
                 data[k]['Unit'] = "VDC"
            elif "current" in k:
                data[k]['Unit'] = "ADC"
            elif "power" in k:
                data[k]['Unit'] = "W"
            elif "temperature" in k:
                data[k]['Unit'] = "°C"
            elif "state_of_charge" in k:
                data[k]['Unit'] = "%"
            elif "capacity" in k:
                data[k]['Unit'] = "Ah"
            elif "total_runtime" in k and "formatted" not in k:
                data[k]['Unit'] = "s"
            elif "resistance" in k:
                data[k]['Unit'] = "mOhm"
            else:
                data[k]['Unit'] = "none"
                #data[k]['Value'] = msg.payload.decode("UTF-8")


            if k == "cell_voltage_16":
                # Convert Python to JSON  
                json_object = json.dumps(data, indent = 4)
                #print(json_object)
                df = pd.read_json(StringIO(json_object))
                print(df)

                # Determine Base Path of the current file
                basepath = pathlib.Path(__file__).parent.resolve()
                #print(basepath)

                # Determine Root Path of the Project
                rootpath = basepath.parent.resolve()

                filename = f"{rootpath}/tmp/Test.xlsx"
                if os.path.exists(filename):
                    pass
                else:
                    df.to_excel(filename)
                
                #print(data)

    client.subscribe(topic)
    client.on_message = on_message

    


def init_signal():
    signal = {}
    signal['ID'] = ''
    signal['Topic'] = ''
    signal['Scope'] = ''
    signal['Type'] = ''
    signal['Physical'] = ''
    signal['Name'] = ''
    signal['Unit'] = ''
    signal['Value'] = 0
    signal['Number'] = 0

    return signal

def init_scheme():
    # Initialize Data as an Empty Dictionary
    data = { }

    for cell_id in range(1, NCELLS+1):
        data[f'cell_voltage_{cell_id}'] = init_signal()
        data[f'cell_voltage_{cell_id}']['ID'] = f'cell_voltage_{cell_id}'
        data[f'cell_voltage_{cell_id}']['Topic'] = ''
        data[f'cell_voltage_{cell_id}']['Scope'] = 'Cell'
        data[f'cell_voltage_{cell_id}']['Type'] = 'sensor'
        data[f'cell_voltage_{cell_id}']['Physical'] = 'Voltage'
        data[f'cell_voltage_{cell_id}']['Name'] = f'Cell #{cell_id:0>2} Voltage'
        data[f'cell_voltage_{cell_id}']['Unit'] = 'VDC'
        data[f'cell_voltage_{cell_id}']['Value'] = 0
        data[f'cell_voltage_{cell_id}']['Number'] = cell_id

    return data


def run():
    data = init_scheme()
    client = connect_mqtt()
    subscribe(client , data)
    client.loop_forever()


if __name__ == '__main__':
    run()
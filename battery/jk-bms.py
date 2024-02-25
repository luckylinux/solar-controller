import random
import tabulate

from paho.mqtt import client as mqtt_client
import json
import pandas as pd

pd.set_option('display.max_rows', 999999)
pd.set_option('display.max_columns', 999999)
pd.set_option('display.width', 999999)

import os
import pathlib

#from ..config.battery import battery

from io import StringIO

import re

import panel as pn
pn.extension('tabulator')
#import hvplot.pandas
#pn.extension(design='material')

broker = '192.168.4.10'
port = 1883
#battery_id = "01"
battery_id = "02"
battery_txt = "jk-bms-bat"
prefix = f"{battery_txt}{battery_id}"
topic = f"{prefix}/#"


NCELLS = 16

#data

# Generate a Client ID with the subscribe prefix.
client_id = f'solarcontroller-subscribe-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

def clear_output(n=1):
  # https://blog.finxter.com/how-to-overwrite-the-previous-print-to-stdout-in-python/
  # https://stackoverflow.com/questions/2084508/clear-the-terminal-in-python
  LINE_UP = '\033[1A'
  LINE_CLEAR = '\x1b[2K'
  #CLEAR_SCREEN = '\033[2J'
#  CLEAR_SCREEN = '\x1b[2J'
  CLEAR_SCREEN = '\033c\033[3J\033[2J\033[0m\033[H'
#for i in range(n):
  #  print(LINE_UP, end=LINE_CLEAR)
  print(CLEAR_SCREEN)


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
            data[k]['Battery_Description'] = prefix
            data[k]['Battery_Number'] = int(prefix.replace(battery_txt , ''))

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

                clear_output()
                print(df.transpose())

                #df_widget = pn.widgets.Tabulator(df.transpose(), buttons={'Print': "<i class='fa fa-print'></i>"})
                #df_widget.servable()
                #df_widget

                #pn.Column(
                #         '# Data', tbl
                #         ).servable(target='main')

                #df_panel = pn.panel(df.transpose())
                #df_panel.servable()

                #x = pn.widgets.IntSlider(name='x', start=0, end=100)
                #def square(x):
                #  return f'{x} squared is {x**2}'

                #pn.Row(x, pn.bind(square, x))

                # Determine Base Path of the current file
                #basepath = pathlib.Path(__file__).parent.resolve()
                #print(basepath)

                # Determine Root Path of the Project
                #rootpath = basepath.parent.resol

                #filename = f"{rootpath}/tmp/Test.xlsx"
                #if os.path.exists(filename):
                #    pass
                #else:
                #    df.to_excel(filename)

                #print(data)

    client.subscribe(topic)
    client.on_message = on_message




def init_signal():
    signal = {}
    signal['ID'] = ''
    signal['Battery_Description'] = ''
    signal['Battery_Number'] = ''
    signal['Scope'] = ''
    signal['Type'] = ''
    signal['Physical'] = ''
    signal['Name'] = ''
    signal['Unit'] = ''
    signal['Value'] = 0
    signal['Cell_Number'] = 0

    return signal

def init_scheme(battery_description):
    # Initialize Data as an Empty Dictionary
    data = { }

    for cell_id in range(1, NCELLS+1):
        data[f'cell_voltage_{cell_id}'] = init_signal()
        data[f'cell_voltage_{cell_id}']['ID'] = f'cell_voltage_{cell_id}'
        data[f'cell_voltage_{cell_id}']['Scope'] = 'Cell'
        data[f'cell_voltage_{cell_id}']['Battery_Description'] = battery_description
        data[f'cell_voltage_{cell_id}']['Battery_Number'] = battery_description.replace(battery_txt , '')
        data[f'cell_voltage_{cell_id}']['Type'] = 'sensor'
        data[f'cell_voltage_{cell_id}']['Physical'] = 'Voltage'
        data[f'cell_voltage_{cell_id}']['Name'] = f'Cell #{cell_id:0>2} Voltage'
        data[f'cell_voltage_{cell_id}']['Unit'] = 'VDC'
        data[f'cell_voltage_{cell_id}']['Value'] = 0
        data[f'cell_voltage_{cell_id}']['Cell_Number'] = cell_id

    return data


def run():
    data = init_scheme(prefix)
    client = connect_mqtt()
    subscribe(client , data)
    client.loop_forever()


if __name__.startswith("bokeh"):
    run()
#    # start with panel serve script.py
#    #dashboard = build_dashboard()
#    #dashboard.servable()

if __name__ == '__main__':
    run()

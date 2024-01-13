import calendar
import time
from datetime import datetime
import pandas as pd
import os
import pathlib

if __name__ == "__main__":
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

    # Determine Base Path of the Project
    basepath = pathlib.Path(__file__).parent.resolve()
    #print(basepath)

    # Determine Root Path of the Project
    rootpath = basepath.parent.resolve()
    #print(rootpath)

    # Reference values are stored in strategy file
    reference_file = f"{basepath}/{current_date}.xlsx";

    print(f"Using Reference File {reference_file}")

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
        set_voltage = str(current_setting.get("set_voltage").values[0])

        voltage_file_handle = open(f"{rootpath}/tmp/set_voltage" , 'w')
        voltage_file_handle.write(set_voltage)
        voltage_file_handle.close()

        print(f"Voltage Set to {set_voltage} VDC")

        # Set Current
        set_current = str(current_setting.get("set_current").values[0])
        current_file_handle = open(f"{rootpath}/tmp/set_current" , 'w')
        current_file_handle.write(set_current)
        current_file_handle.close()

        print(f"Current Set to {set_current} ADC")

    else:
        print(f"Error: file {filename} does NOT exist !")
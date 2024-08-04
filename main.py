from neurosity import NeurositySDK
from dotenv import load_dotenv
import time
import os
import json
import datetime
import sys

load_dotenv()

def convert_timestamp_ms_to_time(timestamp_ms):
    timestamp_s = timestamp_ms / 1000.0
    dt_object = datetime.datetime.fromtimestamp(timestamp_s)
    return dt_object

trial_title = 'freestyling_6'
time_to_record = 10

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, 'unfiltered')

# Ensure the directory exists
os.makedirs(output_dir, exist_ok=True)

try:
    neurosity = NeurositySDK({
        "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
    })

    neurosity.login({
        "email": os.getenv("NEUROSITY_EMAIL"),
        "password": os.getenv("NEUROSITY_PASSWORD")
    })

    print("Successfully logged in!")

    data_returned = {}
    i = 0

    def callback(data):
        global i
        print(f"Callback triggered for index {i}")
        data_returned[i] = data
        print(f"data[{i}]: ", data)
        i += 1

    start_time_milliseconds = time.time() * 1000
    start_datetime = convert_timestamp_ms_to_time(start_time_milliseconds)
    print("Starting data capture...")
    unsubscribe = neurosity.brainwaves_raw_unfiltered(callback)

    time.sleep(time_to_record)

    unsubscribe()
    print("Data capture stopped.")
    end_time_milliseconds = time.time() * 1000
    end_datetime = convert_timestamp_ms_to_time(end_time_milliseconds)

    output_file_path = os.path.join(output_dir, f'{trial_title}.json')
    with open(output_file_path, 'w') as json_file:
        json.dump(data_returned, json_file, indent=4)

    if data_returned:
        first_sample_time = convert_timestamp_ms_to_time(data_returned[0]['info']['startTime'])
        last_sample_time = convert_timestamp_ms_to_time(data_returned[len(data_returned) - 1]['info']['startTime'])

        print(f"Start of Code Time: {start_datetime}\nFirst Sample Time: {first_sample_time}\nLast Sample Time: {last_sample_time}\nEnd of Code Time: {end_datetime}")
    else:
        print("No data was received.")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)  # Indicating that an error occurred

print("Script completed successfully.")
sys.exit(0)  # Indicating successful completion

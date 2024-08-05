from neurosity import NeurositySDK
from dotenv import load_dotenv
import time
import os
import json
import datetime
import numpy as np
import mnebasecode
import sys

load_dotenv()


def convert_timestamp_ms_to_time(timestamp_ms):
    timestamp_s = timestamp_ms / 1000.0
    dt_object = datetime.datetime.fromtimestamp(timestamp_s)
    return dt_object


def create_mne_raw_array(data, info):
    channel_names = info['channelNames']
    sampling_rate = info['samplingRate']

    # Flatten data correctly
    data_array = np.array(data).reshape(8, -1)  # Shape should now be (n_channels, n_times)

    print("Data array shape:", data_array.shape)  # Debugging statement

    # Create MNE info structure
    info_mne = mne.create_info(ch_names=channel_names, sfreq=sampling_rate, ch_types='eeg')

    # Create RawArray
    raw = mne.io.RawArray(data_array, info_mne)
    return raw


trial_title = 'data-raw'
time_to_record = 30

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

    data_returned = []
    i = 0


    def callback(data):
        global i
        print(f"Callback triggered for index {i}")
        data_returned.append(data)
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
        last_sample_time = convert_timestamp_ms_to_time(data_returned[-1]['info']['startTime'])

        print(
            f"Start of Code Time: {start_datetime}\nFirst Sample Time: {first_sample_time}\nLast Sample Time: {last_sample_time}\nEnd of Code Time: {end_datetime}")

        # Extract data and create MNE RawArray
        data_list = [sample['data'] for sample in data_returned]

        # Debugging statement to inspect data_list
        print("Data list shape:", len(data_list), len(data_list[0]), len(data_list[0][0]))

        reshaped_data = [np.array(channel_data) for channel_data in data_list]

        # Debugging statement to inspect reshaped_data
        print("Reshaped data shape:", len(reshaped_data), reshaped_data[0].shape)

        concatenated_data = np.concatenate(reshaped_data, axis=1)  # Shape (n_channels, n_times)

        # Debugging statement to inspect concatenated_data
        print("Concatenated data shape:", concatenated_data.shape)

        info = data_returned[0]['info']

        raw = create_mne_raw_array(concatenated_data, info)
        raw_output_file_path = os.path.join(output_dir, f'{trial_title}.fif')
        raw.save(raw_output_file_path, overwrite=True)
        print(f"Saved MNE RawArray to {raw_output_file_path}")
    else:
        print("No data was received.")
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)  # Indicating that an error occurred

print("Script completed successfully.")
sys.exit(0)  # Indicating successful completion

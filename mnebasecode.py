import mne

# Load raw EEG data (modify the path if using your own data)
raw = mne.io.read_raw_fif('unfiltered/raw.fif', preload=True)

# Preprocessing
raw.filter(0.1, 30, filter_length='auto')  # Bandpass filter with automatic length

# Find events and epoch the data
print("Channel names:", raw.info['ch_names'])  # Check channel names
events = mne.find_events(raw, stim_channel='STI 014')  # Adjust if necessary
event_id = {'semantic_incongruity': 1}  # Define your event of interest
epochs = mne.Epochs(raw, events, event_id=event_id, tmin=-0.2, tmax=0.8, baseline=(None, 0), preload=True)

# Compute evoked response (average of epochs)
evoked = epochs.average()

# Plot the evoked response
evoked.plot()

# Set up source space and forward model
subjects_dir = 'path_to_your_subjects_directory'
src = mne.setup_source_space('sample', spacing='oct6', subjects_dir=subjects_dir)
bem = mne.make_bem_model(subject='sample', ico=4, subjects_dir=subjects_dir)
bem_sol = mne.make_bem_solution(bem)
trans = 'path_to_your_transformation_file'  # Modify to your own transformation file

fwd = mne.make_forward_solution(raw.info, trans=trans, src=src, bem=bem_sol, meg=False, eeg=True)

# Compute noise covariance from the baseline period
cov = mne.compute_covariance(epochs, tmax=0)

# Create inverse operator
inv = mne.minimum_norm.make_inverse_operator(raw.info, fwd, cov, loose=0.2, depth=0.8)

# Apply inverse operator to the evoked data to get source estimates
stc = mne.minimum_norm.apply_inverse(evoked, inv, lambda2=1/9., method='dSPM')

# Plot the source estimates
brain = stc.plot(hemi='both', subjects_dir=subjects_dir, initial_time=0.4, time_viewer=True)  # Modify the time point based on your data

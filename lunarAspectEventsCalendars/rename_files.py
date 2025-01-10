import os

# Define the directory containing the ICS files
directory = '/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/output_ics_files'

# Iterate over all files in the directory
for filename in os.listdir(directory):
    # Check if the file is an ICS file and matches the pattern 'events_{year}.ics'
    if filename.startswith('events_') and filename.endswith('.ics'):
        # Extract the year from the filename
        year = filename.split('_')[1].split('.')[0]
        # Define the new filename
        new_filename = f'lunarAspectEventsCalendar_{year}.ics'
        # Construct the full file paths
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)
        # Rename the file
        os.rename(old_file, new_file)
        print(f'Renamed: {old_file} -> {new_file}')
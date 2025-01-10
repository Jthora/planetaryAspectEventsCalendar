import os
import re

def repair_ics_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Ensure the content starts and ends with VCALENDAR block
    if not content.startswith('BEGIN:VCALENDAR'):
        content = 'BEGIN:VCALENDAR\n' + content
    if not content.endswith('END:VCALENDAR'):
        content = content.rstrip('END:VEVENT\n') + '\nEND:VEVENT\nEND:VCALENDAR'

    # Fix any broken VEVENT blocks
    content = re.sub(r'END:VEVENT\s*BEGIN:VEVENT', 'END:VEVENT\nBEGIN:VEVENT', content)

    # Ensure every END:VEVENT has a corresponding BEGIN:VEVENT
    events = content.split('END:VEVENT')
    repaired_content = ''
    for event in events:
        if 'BEGIN:VEVENT' not in event and 'DTSTAMP' in event:
            event = 'BEGIN:VEVENT' + event
        repaired_content += event + 'END:VEVENT\n'

    # Fix the specific anomaly
    repaired_content = repaired_content.replace('\nEND:VCALENDAREND:VEVENT', 'END:VCALENDAR')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(repaired_content.strip())

def repair_files(directory, start_year, end_year):
    for year in range(start_year, end_year + 1):
        file_name = f'planetary_aspect_events_{year}.ics'
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            repair_ics_file(file_path)
            print(f'Repaired {file_path}')
        else:
            print(f'File not found: {file_path}')

# Example usage
if __name__ == "__main__":
    directory = '/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/planetaryAspectEvents'
    repair_files(directory, 2024, 2056)
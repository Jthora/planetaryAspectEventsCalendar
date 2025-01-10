import re
import os

def update_aspect_symbols(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define the aspect symbols mapping
    aspect_symbols = {
        '△': 'Trine',
        '☌': 'Conjunction',
        '☍': 'Opposition',
        '□': 'Square',
        '⚹': 'Sextile',
        '⚻': 'Quincunx',
        '⚼': 'Tri-Octile'
    }

    # Regex to find each event
    event_pattern = re.compile(r'BEGIN:VEVENT(.*?)END:VEVENT', re.DOTALL)
    events = event_pattern.findall(content)

    updated_events = []
    for event in events:
        summary_match = re.search(r'SUMMARY:.*? ([△☌☍□⚹⚻⚼]) ', event)
        if summary_match:
            correct_symbol = summary_match.group(1)
            correct_aspect = aspect_symbols[correct_symbol]
            updated_event = re.sub(r'Aspect: [△☌☍□⚹⚻⚼] \w+', f'Aspect: {correct_symbol} {correct_aspect}', event)
            updated_events.append(updated_event)
        else:
            updated_events.append(event)

    # Reconstruct the content
    updated_content = 'BEGIN:VEVENT' + 'END:VEVENT'.join(updated_events) + 'END:VEVENT'

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

def process_files(directory, start_year, end_year):
    for year in range(start_year, end_year + 1):
        file_name = f'planetary_aspect_events_{year}.ics'
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            update_aspect_symbols(file_path)
            print(f'Updated {file_path}')
        else:
            print(f'File not found: {file_path}')

# Example usage
if __name__ == "__main__":
    directory = '/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/planetaryAspectEvents'
    process_files(directory, 2024, 2056)
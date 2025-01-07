import csv
from datetime import datetime
import hashlib

# Function to generate a unique UID for each event
def generate_uid(row):
    unique_string = row['Date'] + "_" + row['Time'] + "_" + row['Symbol Title']
    return hashlib.md5(unique_string.encode()).hexdigest()

# Function to convert the CSV into an ICS file
def csv_to_ics(csv_file_path, output_ics_path):
    # Open CSV and read data
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        
        # Open output ICS file
        with open(output_ics_path, 'w') as ics_file:
            # Write the calendar header
            ics_file.write("BEGIN:VCALENDAR\r\n")
            ics_file.write("VERSION:2.0\r\n")
            ics_file.write("CALSCALE:GREGORIAN\r\n")
            ics_file.write("PRODID:-//Lunar Aspects Calendar//EN\r\n")
            
            # Process each row and write event blocks
            for row in reader:
                try:
                    # Combine Date and Time to create DTSTART
                    dtstart = datetime.strptime(row['Date'] + " " + row['Time'], "%b %d, %Y %H:%M")
                    dtstart_str = dtstart.strftime('%Y%m%dT%H%M%SZ')  # UTC format

                    # Generate a unique UID
                    uid = generate_uid(row)

                    # Create raw DESCRIPTION using concatenation
                    raw_description = (
                        row['Word Title'] + "\\n\\n"
                        "Moon Position: " + str(row['Moon Position']) + "°\\n"
                        "Moon Zodiac: " + row['Moon Zodiac Word'] + "\\n"
                        "Moon Nature: " + row['Moon Nature'] + ", " + row['Moon Modality'] + "\\n\\n"
                        "Body Name: " + row['Body Name'] + "\\n"
                        "Body Zodiac: " + row['Body Zodiac Word'] + "\\n"
                        "Body Nature: " + row['Body Nature'] + ", " + row['Body Modality'] + "\\n\\n"
                        "Aspect: " + row['Astrological Aspect'] + "\\n\\n"
                        "Combined Interpretation:\\n" + row['Combined Interpretation']
                    )

                    # Write the VEVENT block
                    ics_file.write("BEGIN:VEVENT\r\n")
                    ics_file.write("UID:" + uid + "\r\n")
                    ics_file.write("DTSTAMP:" + datetime.utcnow().strftime('%Y%m%dT%H%M%SZ') + "\r\n")
                    ics_file.write("DTSTART:" + dtstart_str + "\r\n")
                    ics_file.write("DTEND:" + dtstart_str + "\r\n")  # DTEND = DTSTART as fallback
                    ics_file.write("SUMMARY:" + row['Symbol Title'] + "\r\n")
                    ics_file.write("DESCRIPTION:" + raw_description + "\r\n")
                    ics_file.write("CATEGORIES:" + row['Astrological Aspect'] + "\r\n")
                    ics_file.write("END:VEVENT\r\n")
                
                except ValueError as e:
                    print("Skipping row due to error:", e)
                    continue
            
            # Write the calendar footer
            ics_file.write("END:VCALENDAR\r\n")

# File paths
csv_file_path = '/mnt/data/Lunar_Aspects_Interpretations-GalacticCentered.csv'
output_ics_path = '/mnt/data/Lunar_Aspects_Calendar_Fixed_Concat.ics'

# Convert CSV to ICS
csv_to_ics(csv_file_path, output_ics_path)
print("ICS file created at:", output_ics_path)
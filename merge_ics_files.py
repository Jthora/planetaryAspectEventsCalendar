def merge_ics_files(file1, file2, output_file):
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(output_file, 'w') as out:
        # Read the content of the first file
        content1 = f1.readlines()
        # Read the content of the second file
        content2 = f2.readlines()

        # Write the beginning of the first file to the output file
        for line in content1:
            if line.strip() == "END:VCALENDAR":
                break
            out.write(line)

        # Write the content of the second file to the output file, skipping the header
        for line in content2:
            if line.strip() == "BEGIN:VEVENT":
                out.write(line)
                break

        # Write the rest of the second file to the output file
        for line in content2:
            out.write(line)

        # Write the end of the calendar to the output file
        out.write("END:VCALENDAR\n")

if __name__ == "__main__":
    file1 = "/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Part1.ics"
    file2 = "/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Part2.ics"
    output_file = "/Users/jono/Documents/GitHub/planetaryAspectEventsCalendar/Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Merged.ics"
    merge_ics_files(file1, file2, output_file)
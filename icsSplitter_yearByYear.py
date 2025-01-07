import os
import re
from pathlib import Path
import logging


def setup_logging(log_file="split_ics_verbose.log"):
    """Sets up logging to a file."""
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Logging initialized.")


def validate_ics_format(content):
    """
    Validates if the ICS content has valid headers and footers.
    """
    valid = content.startswith("BEGIN:VCALENDAR") and content.endswith("END:VCALENDAR\n")
    logging.info(f"ICS format validation result: {'Valid' if valid else 'Invalid'}")
    return valid


def split_ics_by_year(input_file, output_dir="output_ics_files"):
    """
    Splits an ICS file into yearly ICS files based on event start dates.

    Args:
        input_file (str): Path to the input ICS file.
        output_dir (str): Path to the output directory for yearly files.
    """
    if not os.path.exists(input_file):
        logging.error(f"File '{input_file}' does not exist.")
        print(f"Error: File '{input_file}' does not exist.")
        return

    try:
        with open(input_file, 'r') as file:
            content = file.read()

        if not validate_ics_format(content):
            logging.error("Invalid ICS format. Ensure the file starts with 'BEGIN:VCALENDAR' and ends with 'END:VCALENDAR'.")
            print("Error: Invalid ICS format.")
            return

        events = re.findall(r'(BEGIN:VEVENT.*?END:VEVENT)', content, re.DOTALL)
        total_events = len(events)
        if total_events == 0:
            logging.warning("No events found in the ICS file.")
            print("Warning: No events found in the ICS file.")
            return

        logging.info(f"Total events found in ICS file: {total_events}")

        year_event_mapping = {}

        for event in events:
            match = re.search(r'DTSTART:(\d{4})', event)
            if match:
                year = match.group(1)
                if year not in year_event_mapping:
                    year_event_mapping[year] = []
                year_event_mapping[year].append(event)
            else:
                logging.warning("An event is missing the 'DTSTART' field and will be skipped.")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        processed_event_count = 0
        for year, events in sorted(year_event_mapping.items()):
            output_file = Path(output_dir) / f"events_{year}.ics"
            with open(output_file, 'w') as file:
                file.write("BEGIN:VCALENDAR\n")
                for event in events:
                    file.write(event + "\n")
                file.write("END:VCALENDAR\n")
            processed_event_count += len(events)
            logging.info(f"Year: {year} | Events Processed: {len(events)} | File: {output_file}")

        logging.info(f"Total events processed: {processed_event_count}")
        if processed_event_count != total_events:
            missing_count = total_events - processed_event_count
            logging.warning(f"Some events were not processed: {missing_count} events missing.")
            print(f"Warning: {missing_count} events were not processed. Check the log file for details.")
        else:
            logging.info("All events processed successfully.")

        if year_event_mapping:
            years = sorted(year_event_mapping.keys())
            logging.info(f"Processed years: {years}")
            print(f"ICS files have been split by year and saved in the '{output_dir}' directory.")
            print(f"Processed years: {years}")
        else:
            logging.warning("No valid years were found in the ICS file.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    log_file_path = "split_ics_verbose.log"
    setup_logging(log_file_path)
    input_file_path = "Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Part1.ics"
    split_ics_by_year(input_file_path)
    print(f"Log file created: {log_file_path}")
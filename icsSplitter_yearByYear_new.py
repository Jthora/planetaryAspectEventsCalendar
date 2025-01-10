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
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        with open(input_file, 'r') as file:
            header = file.readline()
            if not header.startswith("BEGIN:VCALENDAR"):
                logging.error("Invalid ICS format. Ensure the file starts with 'BEGIN:VCALENDAR'.")
                print("Error: Invalid ICS format.")
                return

            year_file_handles = {}
            current_event_lines = []
            current_year = None

            for line in file:
                if line.startswith("BEGIN:VEVENT"):
                    current_event_lines = [line]
                elif line.startswith("END:VEVENT"):
                    current_event_lines.append(line)
                    event_str = ''.join(current_event_lines)
                    match = re.search(r'DTSTART:(\d{4})', event_str)
                    if match:
                        year = match.group(1)
                        if year not in year_file_handles:
                            year_file_path = Path(output_dir) / f"events_{year}.ics"
                            year_file_handles[year] = open(year_file_path, 'w')
                            year_file_handles[year].write("BEGIN:VCALENDAR\n")
                        year_file_handles[year].write(event_str)
                    else:
                        logging.warning("An event is missing the 'DTSTART' field and will be skipped.")
                else:
                    current_event_lines.append(line)

            for year, handle in year_file_handles.items():
                handle.write("END:VCALENDAR\n")
                handle.close()
                logging.info(f"Year: {year} | File closed.")

            logging.info("All events processed successfully.")
            print(f"ICS files have been split by year and saved in the '{output_dir}' directory.")

    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
        print(f"Error: {fnf_error}")
    except IOError as io_error:
        logging.error(f"I/O error: {io_error}")
        print(f"Error: {io_error}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
    finally:
        for handle in year_file_handles.values():
            if not handle.closed:
                handle.write("END:VCALENDAR\n")
                handle.close()
                logging.info("File handle closed in finally block.")


if __name__ == "__main__":
    log_file_path = "split_ics_verbose.log"
    setup_logging(log_file_path)
    input_file_path = "Lunar_Aspects_Calendar-GalacticCentered-Interpretations-Merged.ics"
    split_ics_by_year(input_file_path)
    print(f"Log file created: {log_file_path}")
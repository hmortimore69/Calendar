import os
import re
import requests
import os
import logging

from icalendar import Calendar, Event
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_valid_url(url) -> bool:
    logging.debug(f"Validating URL: {url}")
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    is_valid = re.match(regex, url) is not None
    logging.debug(f"URL is valid: {is_valid}")

    return is_valid

def fetch_calendar(url) -> None:
    logging.info(f"Fetching calendar from URL: {url}")

    if not is_valid_url(url):
        logging.warning("Invalid URL format")
        print("Invalid URL format")
        return

    try:
        response = requests.get(url, timeout=10, verify=True)
        response.raise_for_status()
        logging.info("Successfully fetched calendar data")

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        print("An error occurred while fetching the calendar.")
        return

    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
        print("An error occurred while fetching the calendar.")
        return

    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
        print("An error occurred while fetching the calendar.")
        return
        
    except requests.exceptions.RequestException as req_err:
        logging.error(f"An error occurred: {req_err}")
        print("An error occurred while fetching the calendar.")
        return

    try:
        if os.path.exists("./calendar.txt"):
            logging.warning("calendar.txt already exists and will be overwritten.")
            print("Warning: calendar.txt already exists and will be overwritten.")
        with open("./calendar.txt", "w") as file:
            file.write(response.text)
            logging.info("Successfully saved calendar data to calendar.txt")

    except IOError as io_err:
        logging.error(f"File I/O error occurred: {io_err}")
        print("An error occurred while saving the calendar.")

def read_ics(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, "rb") as ics_file:
        calendar = Calendar.from_ical(ics_file.read())

        for component in calendar.walk():
            if component.name == "VEVENT":
                event = {
                    "summary": component.get('summary'),
                    "start": component.get('dtstart').dt,
                    "end": component.get('dtend').dt,
                    "description": component.get('description'),
                }

                print_event(event)

def print_event(event):
    print(f"Summary: {event['summary']}")
    print(f"Start: {event['start']}")
    print(f"End: {event['end']}")
    print(f"Description: {event['description']}")
    print("-" * 40)


def main() -> None:
    # Get URL from user input
    user_url = input("Enter the calendar URL: ").strip()
    logging.debug(f"User entered URL: {user_url}")
    fetch_calendar(user_url)

    ics_file_path = "calendar.ics"
    read_ics(ics_file_path)

main()
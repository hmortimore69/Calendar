import os
import re
import requests
import logging
import ssl

from urllib3 import poolmanager
from icalendar import Calendar, Event
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of log messages
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class CustomHttpAdapter(
    requests.adapters.HTTPAdapter
):  # Attempt to prevent [SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1000)
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount("https://", CustomHttpAdapter(ctx))
    return session


def is_valid_url(url) -> bool:
    logging.debug(f"Validating URL: {url}")
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ipv4
        r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ipv6
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    is_valid = re.match(regex, url) is not None
    logging.debug(f"URL is valid: {is_valid}")

    return is_valid


def fetch_calendar(url) -> bool:
    logging.info(f"Fetching calendar from URL: {url}")

    if not is_valid_url(url):
        logging.warning("Invalid URL format")
        print("Invalid URL format")
        return

    try:
        response = get_legacy_session().get(url)
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
        if os.path.exists("./calendar.ics"):
            logging.warning("calendar.ics already exists and will be overwritten.")
            print("Warning: calendar.ics already exists and will be overwritten.")
        with open("./calendar.ics", "w") as file:
            file.write(response.text)
            logging.info("Successfully saved calendar data to calendar.ics")

    except IOError as io_err:
        logging.error(f"File I/O error occurred: {io_err}")
        print("An error occurred while saving the calendar.")

    if os.path.exists("./calendar.ics"):
        return True
    return False


def main() -> None:
    # Get URL from user input
    user_url = input("Enter the calendar URL: ").strip()
    logging.debug(f"User entered URL: {user_url}")

    # Verify input URL and fetch calendar data
    fetch_calendar(user_url)


if __name__ == "__main__":
    main()

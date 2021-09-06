import handler

PORT = 80
HOST = "127.0.0.1"
HANDLER = handler.MyHttpHandler
REQUEST_QUEUE_SIZE = 32

CITIES_FILE = "RU.txt"
TIMEZONES_FILE = "timeZones.txt"

CITIES_ONLY = True  # False, if dataset should not be filtered
CITIES_FORMAT = {"geonameid": int,
                 "name": str,
                 "asciiname": str,
                 "alternatenames": str,
                 "latitude": float,
                 "longitude": float,
                 "feature_class": str,
                 "feature_code": str,
                 "country_code": str,
                 "cc2": str,
                 "admin1_code": str,
                 "admin2_code": str,
                 "admin3_code": str,
                 "admin4_code": str,
                 "population": int,
                 "elevation": int,
                 "dem": int,
                 "timezone": str,
                 "modification_date": str
                 }
TIMEZONE_FORMAT = {
    "CountryCode": str,
    "TimeZoneId": str,
    "GMT": float,
    "DST": float,
    "raw": float
}

DATA, ID_DATA = list(), dict()
TIMEZONES = dict()

PAGINATION_LIMIT = 50
HINTS_COUNT_LIMIT = 50
DEFAULT_PAGE = 1
DEFAULT_HINTS_COUNT = 10
DEFAULT_PAGINATION_SIZE = 25
LOGGER = print

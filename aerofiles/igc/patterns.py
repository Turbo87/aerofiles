import re

DATE = re.compile('^([0-9]{2})([0-1][0-9])([0-3][0-9])$')
TIME = re.compile('^([0-2][0-9])([0-5][0-9])([0-5][0-9])$')
DATETIME = re.compile('^([0-9]{2})([0-1][0-9])([0-3][0-9])'
                      '([0-2][0-9])([0-5][0-9])([0-5][0-9])$')
MANUFACTURER_CODE = re.compile('^[A-Z0-9]{3}$')
LOGGER_ID = re.compile('^[A-Z0-9]{3}$')
EXTENSION_CODE = re.compile('^[A-Z]{3}$')

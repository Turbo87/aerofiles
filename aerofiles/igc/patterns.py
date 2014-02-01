import re

MANUFACTURER_CODE = re.compile('^[A-Z0-9]{3}$')
LOGGER_ID = re.compile('^[A-Z0-9]{3}$')
EXTENSION_CODE = re.compile('^[A-Z]{3}$')

import re

DATE = re.compile('^([0-3][0-9])([0-1][0-9])([0-9]{2})$')
TIME = re.compile('^([0-2][0-9])([0-5][0-9])([0-5][0-9])$')
DATETIME = re.compile('^([0-3][0-9])([0-1][0-9])([0-9]{2})'
                      '([0-2][0-9])([0-5][0-9])([0-5][0-9])$')

THREE_LETTER_CODE = re.compile('^[A-Z0-9]{3}$')
MANUFACTURER_CODE = THREE_LETTER_CODE
LOGGER_ID = THREE_LETTER_CODE
EXTENSION_CODE = THREE_LETTER_CODE

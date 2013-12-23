# flake8: noqa


class ParserError(RuntimeError):
    pass

from .seeyou import SeeYouReader
from .welt2000 import Welt2000Reader

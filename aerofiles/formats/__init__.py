# flake8: noqa


class ParserError(RuntimeError):
    pass

from .seeyou import (
    Reader as SeeYouReader,
    Converter as SeeYouConverter,
)

from .welt2000 import (
    Reader as Welt2000Reader,
    Converter as Welt2000Converter,
)

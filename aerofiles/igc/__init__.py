"""
The IGC file format is used by glide computers to record flights.

- `Spec "IGC-approved Flight Recorders - Technical Specification" <https://fai.org/igc-documents>`_
- `Wikipedia <https://en.wikipedia.org/wiki/FAI_Gliding_Commission>`__
"""
# flake8: noqa

from .writer import Writer
from .reader import Reader

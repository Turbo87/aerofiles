"""
The IGC file format is used by glide computers to record flights.

- `Spec <https://www.fai.org/sites/default/files/documents/igc_fr_spec_with_al4a_2016-4-10.pdf>`_
- `Wikipedia <https://en.wikipedia.org/wiki/FAI_Gliding_Commission>`__
"""
# flake8: noqa

from .writer import Writer
from .reader import Reader

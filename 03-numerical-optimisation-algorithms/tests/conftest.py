import logging
from collections.abc import Iterator

import matplotlib
import pytest

from aso.logging import enable_logging


def pytest_sessionstart(session):
    enable_logging(
        console_level=logging.ERROR,
        file_level=logging.DEBUG,
    )

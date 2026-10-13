"""
Supported reference prices used by
adaptive investment strategies.
"""

from enum import Enum


class ReferencePrice(Enum):
    """
    Supported reference price types.
    """

    RUNNING_MAX = "RUNNING_MAX"
    RUNNING_AVG = "RUNNING_AVG"

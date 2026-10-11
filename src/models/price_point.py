'''
Created on 10 Oct 2026

@author: mxarl
'''

"""
Represents a single weekly market observation.
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class PricePoint:
    """
    Historical price information for a given week.
    """

    week: int
    date: date
    close: float
    max_close: float



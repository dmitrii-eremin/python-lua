"""Token end mode"""
from enum import Enum


class TokenEndMode(Enum):
    """This enum represents token end mode"""
    LINE_FEED = 0
    LINE_CONTINUE = 1

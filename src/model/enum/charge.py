from enum import Enum

from src.const import section, CHARGE_SLOW_KEY, CHARGE_MEDIUM_KEY, CHARGE_FAST_KEY


class Charge(Enum):
    SLOW = section[CHARGE_SLOW_KEY]
    MEDIUM = section[CHARGE_MEDIUM_KEY]
    FAST = section[CHARGE_FAST_KEY]

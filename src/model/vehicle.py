from src.const import section, CAPACITY_KEY, MAX_DIST_KEY


class Vehicle:
    maxDist = 0
    capacity = 0
    dist = 0

    def __init__(self):
        self.maxDist = section[MAX_DIST_KEY]
        self.capacity = section[CAPACITY_KEY]

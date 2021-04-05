from src.model.travelType import TravelType
from src.model.visit import Visit


class Travel:
    start: Visit
    end: Visit
    distance = 0
    time = 0

    def __init__(self, start, end, distance, time):
        self.start = start
        self.end = end
        self.distance = distance
        self.time = time

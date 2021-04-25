from src.model.travelType import TravelType
from src.model.visit import Visit


class Travel:
    start: Visit
    end: Visit
    distance = 0
    time = 0
    travelType = TravelType.TRAVEL

    def __init__(self, start, end, distance, time):
        self.start = start
        self.end = end
        self.distance = distance
        self.time = time

    def formatTravel(self):
        switcher = {
            self.travelType.TRAVEL: str(self.end.id),
            self.travelType.CHARGE: 'R',
            self.travelType.DEPOSIT: 'C'
        }

        return switcher.get(self.travelType, str(self.end.id))

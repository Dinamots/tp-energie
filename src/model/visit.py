from src.model.position import Position
from src.model.travelType import TravelType


class Visit:
    id: int = None
    position: Position
    name = None
    demand = None
    duration = None
    isDone = False
    isChargeStation = False
    isDepot = False
    chargeTime = None
    travelType = TravelType.TRAVEL

    @staticmethod
    def build(line: str, chargeTime: int):
        visit = Visit()
        position = Position(float(line[2]), float(line[3]))

        visit.id = int(line[0])
        visit.name = line[1]
        visit.position = position
        visit.demand = int(line[4])
        visit.duration = (visit.demand * 10) + (60 * 5)
        visit.isChargeStation = visit.name[0] != 'V'
        visit.isDone = visit.demand == 0
        visit.isDepot = visit.name == "Depot"
        visit.chargeTime = chargeTime

        return visit

    def formatVisit(self):
        switcher = {
            self.travelType.TRAVEL: str(self.id),
            self.travelType.CHARGE: 'R',
            self.travelType.DEPOSIT: 'C'
        }

        return switcher.get(self.travelType, str(self.id))

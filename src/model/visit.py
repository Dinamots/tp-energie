from src.model.position import Position


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

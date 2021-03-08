from src.model.position import Position


class Visit:
    id = 0
    position: Position
    name = ""
    demand = 0
    duration = 0
    done = False

    @staticmethod
    def build(line: str):
        visit = Visit()
        position = Position(float(line[2]), float(line[3]))

        visit.id = line[0]
        visit.name = line[1]
        visit.position = position
        visit.demand = int(line[4])

        visit.duration = (visit.demand * 10) + (60 * 5)
        return visit

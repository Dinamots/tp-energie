from collections import Callable

from src.const import CAPACITY_KEY, MAX_DIST_KEY, START_TIME_KEY, END_TIME_KEY
from datetime import datetime

from src.model.travel import Travel
from src.model.visit import Visit


class Vehicle:
    maxDist: float = 0
    capacity: int = 0
    dist: float = 0
    bags: int = 0
    remainingTime = 0
    tour: list[Visit] = None
    currentVisit: Visit = None

    def __init__(self, section, start: Visit):
        self.maxDist = float(section[MAX_DIST_KEY])
        self.capacity = int(section[CAPACITY_KEY])
        self.tour = list()
        startTime = float(datetime.strptime(section[START_TIME_KEY], "%H:%M").hour)
        endTime = float(datetime.strptime(section[END_TIME_KEY], "%H:%M").hour)
        self.currentVisit = start
        self.tour.append(start)
        self.remainingTime = (endTime - startTime) * 60 * 60

    def getTravelsFromStart(self, start: Visit, travels: list[list[Travel]]):
        nearestTravels = travels[start.id]
        nearestTravels.sort(key=lambda travel: travel.distance)
        return nearestTravels

    def isEnableToGoToChargeStation(self, travel: Travel, visits: list[Visit], travels: list[list[Travel]]):
        return (
                       self.dist +
                       travel.distance +
                       self.getNearestChargePlace(travel.end, visits, travels).distance
               ) <= self.maxDist

    def haveEnougthTime(self, travel: Travel):
        return (self.remainingTime - travel.time) >= 0

    def haveEnoughtSpace(self, travel: Travel):
        return self.bags + travel.end.demand <= self.capacity

    def getNearestTravelUsable(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.findNearestInTravels(
            start, travels, lambda travel:
            not visits[travel.end.id].isDone
            and self.isEnableToGoToChargeStation(travel, visits, travels)
            and self.haveEnougthTime(travel)
            and self.haveEnoughtSpace(travel)
        )

    def getNearestChargePlace(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.findNearestInTravels(start, travels, lambda travel: self.isChargeStation(visits[travel.end.id]))

    def findNearestInTravels(self, start: Visit, travels: list[list[Travel]], predicate: Callable[[Travel], bool]):
        return next(
            (
                travel for travel in self.getTravelsFromStart(start, travels)
                if predicate(travel)
            ),
            None
        )

    def isChargeStation(self, visit: Visit):
        return visit.isChargeStation

    def move(self, visits: list[Visit], travels: list[list[Travel]]):
        travel = self.getNearestTravelUsable(self.currentVisit, visits, travels)
        if travel:
            visits[travel.end.id].isDone = True
            self.currentVisit = travel.end
            self.dist += travel.distance
            self.remainingTime -= travel.time
            self.tour.append(travel.end)


from collections import Callable
from datetime import datetime

from src.const import CAPACITY_KEY, MAX_DIST_KEY, START_TIME_KEY, END_TIME_KEY
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
    nbOutOfTime = 0
    nbOutOfCharge = 0
    nbOutOfBags = 0

    def __init__(self, section, start: Visit):
        self.maxDist = float(section[MAX_DIST_KEY])
        self.capacity = int(section[CAPACITY_KEY])
        self.tour = list()
        startTime = float(datetime.strptime(section[START_TIME_KEY], "%H:%M").hour)
        endTime = float(datetime.strptime(section[END_TIME_KEY], "%H:%M").hour)
        self.currentVisit = start
        self.tour.append(start)
        self.bags = self.capacity
        self.remainingTime = (endTime - startTime) * 3600

    def getTravelsFromStart(self, start: Visit, travels: list[list[Travel]]):
        nearestTravels = travels[start.id]
        nearestTravels.sort(key=lambda travel: travel.distance)
        return nearestTravels

    def isEnableToGoToChargeStation(self, travel: Travel, visits: list[Visit], travels: list[list[Travel]]):
        enableToGoToChargeStation = (
                                            self.dist +
                                            travel.distance +
                                            self.getNearestChargePlace(travel.end, visits, travels).distance
                                    ) <= self.maxDist
        if not enableToGoToChargeStation:
            self.nbOutOfCharge += 1
            return False
        return True

    def haveEnougthTime(self, travel: Travel):
        return (self.remainingTime - travel.time) >= 0

    def haveEnoughtBags(self, travel: Travel):
        if not (self.bags - travel.end.demand >= 0):
            self.nbOutOfBags += 1
            return False
        return True

    def getNearestTravelUsable(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.findNearestInTravels(
            start, travels, lambda travel:
            not visits[travel.end.id].isDone
            and self.isEnableToGoToChargeStation(travel, visits, travels)
            and self.haveEnougthTime(travel)
            and self.haveEnoughtBags(travel)
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
        if not travel and (self.nbOutOfBags >= self.nbOutOfCharge):
            travel = self.getNearestDeposit(travels)
            self.bags = self.capacity
            self.remainingTime -= 60 * 10
        elif not travel:
            travel = self.getNearestChargeStation(travels)
            self.dist = 0
            self.remainingTime -= travel.end.chargeTime

        visits[travel.end.id].isDone = True
        self.onTravel(travel)

    def onTravel(self, travel):
        self.currentVisit = travel.end
        self.dist += travel.distance
        self.bags -= travel.end.demand
        self.remainingTime -= travel.time
        self.nbOutOfBags = 0
        self.nbOutOfCharge = 0
        self.tour.append(travel.end)

    def goToDeposit(self, travels: list[list[Travel]]):
        self.onTravel(self.getNearestDeposit(travels))

    def getNearestDeposit(self, travels):
        return self.findNearestInTravels(self.currentVisit, travels, lambda travel: travel.end.isDepot)

    def getNearestChargeStation(self, travels):
        return self.findNearestInTravels(self.currentVisit, travels, lambda travel: travel.end.isChargeStation)

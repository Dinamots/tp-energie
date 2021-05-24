from collections import Callable
from copy import deepcopy
from datetime import datetime
from functools import reduce
from random import shuffle

from src.const import CAPACITY_KEY, MAX_DIST_KEY, START_TIME_KEY, END_TIME_KEY
from src.model.travel import Travel
from src.model.travelType import TravelType
from src.model.visit import Visit


class Vehicle:
    maxDist: float = 0
    capacity: int = 0
    dist: float = 0
    bags: int = 0
    remainingTime = 0
    time: int = 0
    tour: list[Travel] = None
    currentVisit: Visit = None
    nbOutOfTime = 0
    nbOutOfCharge = 0
    nbOutOfBags = 0
    random = False

    def __init__(self, section=None, start: Visit = None, random: bool = False):
        if section is None or start is None:
            return

        self.maxDist = float(section[MAX_DIST_KEY])
        self.capacity = int(section[CAPACITY_KEY])
        self.tour = list()
        startTime = float(datetime.strptime(section[START_TIME_KEY], "%H:%M").hour)
        endTime = float(datetime.strptime(section[END_TIME_KEY], "%H:%M").hour)
        self.currentVisit = start
        self.bags = self.capacity
        self.time = (endTime - startTime) * 3600
        self.remainingTime = self.time
        self.random = random

    @staticmethod
    def fromVehicle(vehicle):
        newVehicle = Vehicle()
        newVehicle.time = vehicle.time
        newVehicle.tour = deepcopy(vehicle.tour)
        newVehicle.dist = vehicle.dist
        newVehicle.time = vehicle.time
        newVehicle.maxDist = vehicle.maxDist
        newVehicle.capacity = vehicle.capacity
        newVehicle.currentVisit = vehicle.currentVisit
        newVehicle.random = vehicle.random

    def getNearestTravelsFromStart(self, start: Visit, travels: list[list[Travel]]):
        nearestTravels = travels[start.id]
        nearestTravels.sort(key=lambda travel: travel.distance)
        return nearestTravels

    def getRandomTravelsFromStart(self, start: Visit, travels: list[list[Travel]]):
        trvls = travels[start.id]
        shuffle(trvls)
        return trvls

    def isEnableToGoToChargeStation(self, travel: Travel, visits: list[Visit], travels: list[list[Travel]]):
        chargeTravel = self.getNearestChargePlace(travel.end, visits, travels)
        haveEnoughCharge = (
                                   self.dist +
                                   travel.distance +
                                   chargeTravel.distance
                           ) <= self.maxDist

        haveEnoughTime = (
                                 self.remainingTime -
                                 travel.time
                         ) > 0

        if not haveEnoughCharge:
            self.nbOutOfCharge += 1
            return False

        if not haveEnoughTime:
            self.nbOutOfTime += 1
            return False

        return True

    def haveEnoughTime(self, travel: Travel, travels: list[list[Travel]]):
        return (self.remainingTime - (travel.time + self.getNearestDeposit(travels, travel.end).time)) >= 0

    def haveEnoughBags(self, travel: Travel):
        if not (self.bags - travel.end.demand >= 0):
            self.nbOutOfBags += 1
            return False
        return True

    def isTravelUsable(self, travel: Travel, visits: list[Visit], travels: list[list[Travel]]):
        return not visits[travel.end.id].isDone \
               and self.isEnableToGoToChargeStation(travel, visits, travels) \
               and self.haveEnoughTime(travel, travels) \
               and self.haveEnoughBags(travel)

    def travelUsable(self, visits: list[Visit], travels: list[list[Travel]], l: list[Travel]):
        return self.findInList(l, lambda travel: self.isTravelUsable(travel, visits, travels))

    def getNearestTravelUsable(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.travelUsable(visits, travels, self.getNearestTravelsFromStart(start, travels))

    def getRandomTravelUsable(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.travelUsable(visits, travels, self.getRandomTravelsFromStart(start, travels))

    def getNearestChargePlace(self, start: Visit, visits: list[Visit], travels: list[list[Travel]]):
        return self.findInList(
            self.getNearestTravelsFromStart(start, travels),
            lambda travel: self.isChargeStation(visits[travel.end.id])
        )

    def findInList(
            self,
            l: list[Travel],
            predicate: Callable[[Travel], bool]
    ):
        return next(
            (
                travel for travel in l
                if predicate(travel)
            ),
            None
        )

    def isChargeStation(self, visit: Visit):
        return visit.isChargeStation

    def move(self, visits: list[Visit], travels: list[list[Travel]]):
        if self.remainingTime > 0 and self.outOfTime(travels):
            self.remainingTime = 0
            return

        travel = self.getRandomTravelUsable(self.currentVisit, visits, travels) \
            if self.random \
            else self.getNearestTravelUsable(self.currentVisit, visits, travels)

        travelType = TravelType.TRAVEL
        if not travel and (self.nbOutOfBags >= self.nbOutOfCharge):
            travel = self.getNearestDeposit(travels, self.currentVisit)
            travelType = travelType.DEPOSIT
            self.bags = self.capacity
            self.remainingTime -= self.getBagsLoadTime()
        elif not travel:
            travel = self.getNearestChargeStation(travels)
            travelType = travelType.CHARGE
            self.dist = 0
            self.remainingTime -= travel.end.chargeTime

        visits[travel.end.id].isDone = True
        self.onTravel(travel, travelType)

    def onTravel(self, travel, travelType):
        self.currentVisit = travel.end
        if travelType != TravelType.CHARGE:
            self.dist += travel.distance
        self.bags -= travel.end.demand
        self.remainingTime -= travel.time + self.deliveryTime(travel.end.demand)
        self.nbOutOfBags = 0
        self.nbOutOfCharge = 0
        trvl = deepcopy(travel)
        trvl.travelType = travelType
        self.tour.append(trvl)

    def deliveryTime(self, nbBags: int):
        return (5 * 60) + (nbBags * 10)

    def goToDeposit(self, travels: list[list[Travel]]):
        self.onTravel(self.getNearestDeposit(travels, self.currentVisit), TravelType.TRAVEL)

    def getNearestDeposit(self, travels: list[list[Travel]], start: Visit):
        return self.findInList(
            self.getNearestTravelsFromStart(start, travels),
            lambda travel: travel.end.isDepot
        )

    def getNearestChargeStation(self, travels):
        return self.findInList(
            self.getNearestTravelsFromStart(self.currentVisit, travels),
            lambda travel: travel.end.isChargeStation
        )

    def outOfTime(self, travels: list[list[Travel]]):
        trvls: list[Travel] = travels[self.currentVisit.id]
        return next((travel for travel in trvls if self.haveEnoughTime(travel, travels)), None) is None

    def isTourValid(self):
        tourTime: int = 0
        bags = self.capacity
        dist = self.maxDist

        if not self.tour[0].start.isDepot or not self.tour[-1].end.isDepot:
            return False

        for travel in self.tour:
            tourTime += travel.time
            if travel.travelType == TravelType.TRAVEL:
                tourTime += self.deliveryTime(travel.end.demand)
                dist -= travel.distance
                bags -= travel.end.demand
            elif travel.travelType == TravelType.CHARGE:
                dist = self.maxDist
                tourTime += travel.end.chargeTime
            elif travel.travelType == TravelType.DEPOSIT:
                dist -= travel.distance
                tourTime += self.getBagsLoadTime()
                bags = self.capacity

            if bags < 0 or tourTime > self.time or dist < 0:
                return False

        return True

    def getBagsLoadTime(self):
        return 60 * 10

    def getVehicleTotalDist(self):
        return reduce(lambda acc, travel: acc + travel.distance, self.tour, 0)

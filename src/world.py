import configparser
import csv
from functools import reduce
from typing import IO

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE, OUT_FILE, \
    CHARGE_SLOW_KEY, CHARGE_MEDIUM_KEY, CHARGE_FAST_KEY
from src.model.travel import Travel
from src.model.vehicle import Vehicle
from src.model.visit import Visit
from src.model.worldScore import WorldScore
from src.utils import Utils


class World:
    path: str = None
    section: configparser.SectionProxy = None
    distances: np.ndarray = None
    times: np.ndarray = None
    visits: list[Visit] = None
    travels: list[list[Travel]] = None
    vehicles: list[Vehicle] = None
    charge: int = None

    def __init__(self, path: str = None, nbVehicles=None, random=False):
        if path is None and nbVehicles is None:
            return
        self.path = path
        self.section = Utils.getSection(path + INI_FILE, VEHICLE_SECTION)
        self.charge = int(self.section[CHARGE_SLOW_KEY]) * 60
        self.distances: np.ndarray = np.genfromtxt(path + DISTANCE_FILE, dtype=float)
        self.times: np.ndarray = np.genfromtxt(path + TIMES_FILE, dtype=float)
        self.visits = list(map(
            lambda line: Visit.build(line, self.charge),
            list(self.getCsv())
        ))

        self.travels = reduce(
            lambda travels, start: self.initTravels(travels, self.visits, start),
            self.visits,
            list()
        )

        self.vehicles = [Vehicle(self.section, self.getStart(), random) for _ in range(nbVehicles)]
        self.start()
        if self.allDone():
            self.write(OUT_FILE)

    @staticmethod
    def fromWorld(world):
        newWorld = World()
        newWorld.path = world.path
        newWorld.vehicles = world.vehicles[:]
        newWorld.section = world.section
        newWorld.charge = world.charge
        newWorld.distances: np.ndarray = world.distances
        newWorld.times: np.ndarray = world.times
        newWorld.visits = world.visits
        newWorld.travels = world.travels

        return newWorld

    def getCsv(self):
        reader = csv.reader(open(self.path + VISITS_FILE))
        next(reader)
        return reader

    def initTravels(self, travels: list, visits: list, start: Visit):
        def createTravel(end) -> Travel:
            return Travel(
                start,
                end,
                self.distances[start.id][end.id],
                self.times[start.id][end.id]
            )

        return travels + [list(map(
            createTravel,
            visits
        ))]

    def allDone(self):
        return next((visit for visit in self.visits if not visit.isDone), None) is None

    def getStart(self):
        return next(visit for visit in self.visits if visit.name == 'Depot')

    def start(self):
        print('Start : ', self.path, ' nbVehicles: ', len(self.vehicles))
        while not self.allDone() and not self.allOutOfTime():
            for vehicle in self.vehicles:
                vehicle.move(self.visits, self.travels)
        self.allVehiclesToDeposit()

    def allVehiclesToDeposit(self):
        for vehicle in self.vehicles:
            vehicle.goToDeposit(self.travels)

    def allOutOfTime(self):
        return next((vehicle for vehicle in self.vehicles if vehicle.remainingTime > 0), None) is None

    def write(self, name: str):
        file: IO = open(self.path + name, 'w')
        turns = list(
            map(lambda vehicle: list(map(lambda travel: travel.formatTravel(), vehicle.tour)), self.vehicles)
        )
        for turn in turns:
            turnString = ','.join(elem for elem in turn)
            file.write(turnString + '\n')

    def isWorldValid(self):
        return next((vehicle for vehicle in self.vehicles if not vehicle.isTourValid()), True) is True

    def getWorldScore(self):
        return WorldScore(len(self.vehicles), self.getVehiclesDistances()) if self.isWorldValid() else None

    def getVehiclesDistances(self):
        return reduce(lambda acc, vehicle: acc + vehicle.getVehicleTotalDist(), self.vehicles, 0)

    def isBetter(self, world):
        compareScore: WorldScore = world.getWorldScore()
        score = self.getWorldScore()
        if compareScore is None:
            return True

        return (score.nbVehicles == compareScore.nbVehicles and score.dist <= compareScore.dist) or \
               score.nbVehicles < compareScore.nbVehicles

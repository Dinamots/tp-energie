import configparser
import csv
from collections.abc import Iterable
from functools import reduce
from itertools import cycle
from typing import IO

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE, CHARGE_FAST_KEY, OUT_FILE
from src.model.travel import Travel
from src.model.vehicle import Vehicle
from src.model.visit import Visit


class World:
    path: str = None
    section: configparser.SectionProxy = None
    distances: np.ndarray = None
    times: np.ndarray = None
    visits: list[Visit] = None
    travels: list[list[Travel]] = None
    vehicles: list[Vehicle] = None
    charge: int = None

    def __init__(self, path: str):
        print('Start : ', path)
        self.path = path
        self.initConfig()
        self.charge = int(self.section[CHARGE_FAST_KEY])
        self.distances: np.ndarray = np.genfromtxt(path + DISTANCE_FILE, dtype=float)
        self.times: np.ndarray = np.genfromtxt(path + TIMES_FILE, dtype=float)
        self.visits = list(map(
            lambda line: Visit.build(line, int(self.section[CHARGE_FAST_KEY])),
            list(self.getCsv())
        ))

        self.travels = reduce(
            lambda travels, start: self.initTravels(travels, self.visits, start),
            self.visits,
            list()
        )
        self.vehicles = list()
        self.start()
        self.write()

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

    def initConfig(self):
        config = configparser.ConfigParser()
        config.read(self.path + INI_FILE)
        self.section = config[VEHICLE_SECTION]

    def allDone(self):
        return next((visit for visit in self.visits if not visit.isDone), None) is None

    def getStart(self):
        return next(visit for visit in self.visits if visit.name == 'Depot')

    def start(self):
        self.vehicles.append(Vehicle(self.section, self.getStart()))
        self.vehicles.append(Vehicle(self.section, self.getStart()))

        while not self.allDone() and not self.allOutOfTime():
            for vehicle in self.vehicles:
                vehicle.move(self.visits, self.travels)

        self.allVehiclesToDeposit()

    def allVehiclesToDeposit(self):
        for vehicle in self.vehicles:
            vehicle.goToDeposit(self.travels)

    def allOutOfTime(self):
        return next((vehicle for vehicle in self.vehicles if vehicle.remainingTime > 0), None) is None

    def flatten(self, l):
        if not isinstance(l, Iterable):
            return l

        for el in l:
            if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
                yield from self.flatten(el)
            else:
                yield el

    def write(self):
        file: IO = open(self.path + OUT_FILE, 'w')
        turns = list(map(lambda vehicle: list(map(lambda visit: visit.id, vehicle.tour)), self.vehicles))

        def zipTour(acc, tour) -> list[list[int]]:
            tupleList = list(zip(acc, cycle(tour))) if len(acc) > len(tour) else list(zip(cycle(acc), tour))
            return tupleList if len(tupleList) else tour

        turnsTuple = list(reduce(zipTour, turns, list()))
        turnsTuple = list(map(lambda t: list(self.flatten(t)), turnsTuple)) if len(self.vehicles) > 1 else turnsTuple
        for turn in turnsTuple:
            turnString = ','.join([str(integer) for integer in turn]) if len(self.vehicles) > 1 else str(turn)
            file.write(turnString + '\n')

import configparser
import csv
from functools import reduce
from typing import IO

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE, OUT_FILE, \
    CHARGE_SLOW_KEY
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

    def __init__(self, path: str, nbVehicles):
        print('Start : ', path, ' nbVehicles: ', nbVehicles)
        self.path = path
        self.initConfig()
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

        self.vehicles = [Vehicle(self.section, self.getStart()) for _ in range(nbVehicles)]
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
        while not self.allDone() and not self.allOutOfTime():
            for vehicle in self.vehicles:
                vehicle.move(self.visits, self.travels)

        self.allVehiclesToDeposit()

    def allVehiclesToDeposit(self):
        for vehicle in self.vehicles:
            vehicle.goToDeposit(self.travels)

    def allOutOfTime(self):
        return next((vehicle for vehicle in self.vehicles if vehicle.remainingTime > 0), None) is None

    def write(self):
        file: IO = open(self.path + OUT_FILE, 'w')
        turns = list(
            map(lambda vehicle: list(map(lambda travel: travel.formatTravel(), vehicle.tour)), self.vehicles)
        )
        for turn in turns:
            turnString = ','.join(elem for elem in turn)
            file.write(turnString + '\n')

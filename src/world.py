import configparser
import csv
from functools import reduce
from itertools import chain

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE, CHARGE_FAST_KEY
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
    tour: list[Visit] = None

    def getCsv(self):
        reader = csv.reader(open(self.path + VISITS_FILE))
        next(reader)
        return reader

    def initTravels(self, travels: list, visits: list, start: Visit):
        # visits = visits[visits.index(start) + 1:]
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

    def __init__(self, path: str):
        print('Start : ', path)
        self.path = path
        self.initConfig()
        self.charge = int(self.section[CHARGE_FAST_KEY])
        self.distances: np.ndarray = np.genfromtxt(path + DISTANCE_FILE, dtype=float)
        self.times: np.ndarray = np.genfromtxt(path + TIMES_FILE, dtype=float)
        self.visits = list(map(
            lambda line: Visit.build(line),
            list(self.getCsv())
        ))

        self.travels = reduce(
            lambda travels, start: self.initTravels(travels, self.visits, start),
            self.visits,
            list()
        )
        self.tour = list()
        self.vehicles = list()
        self.start()

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
        while not self.allDone():
            for vehicle in self.vehicles:
                vehicle.move(self.visits, self.travels)

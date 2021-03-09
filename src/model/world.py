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
    vehicle: Vehicle = None
    charge: int = None
    tour: list[Visit] = None

    def getCsv(self):
        reader = csv.reader(open(self.path + VISITS_FILE))
        next(reader)
        return reader

    def initTravels(self, travels: list, visits: list, start: Visit):
        # visits = visits[visits.index(start) + 1:]
        createTravel = lambda end: Travel(
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
        self.charge = self.section[CHARGE_FAST_KEY]
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
        self.vehicle = Vehicle(self.section)
        self.start()

    def initConfig(self):
        config = configparser.ConfigParser()
        config.read(self.path + INI_FILE)
        self.section = config[VEHICLE_SECTION]

    def allDone(self):
        return next((visit for visit in self.visits if not visit.isDone), None) is None

    def getNearestTravel(self, visit: Visit):
        nearestTravels = self.travels[visit.id]
        nearestTravels.sort(key=lambda travel: travel.distance)
        return next((travel for travel in nearestTravels if not self.visits[travel.end.id].isDone), None)

    def getStart(self):
        return next(visit for visit in self.visits if visit.name == 'Depot')

    def start(self):
        start = self.getStart()
        while not self.allDone():
            self.tour.append(start)
            travel = self.getNearestTravel(start)
            self.visits[travel.end.id].isDone = True
            start = travel.end
        self.tour.append(start)
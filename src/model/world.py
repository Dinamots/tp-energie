import configparser
import csv
from functools import reduce

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE
from src.model.travel import Travel
from src.model.visit import Visit


class World:
    path: str = None
    section: configparser.SectionProxy = None
    distances: np.ndarray = None
    times: np.ndarray = None
    visits: list[Visit] = list()
    travels: list[Travel] = list()

    def initVisits(self, visits: list, line):
        visits.append(Visit.build(line))
        return visits

    def getCsv(self):
        reader = csv.reader(open(self.path + VISITS_FILE))
        next(reader)
        return reader

    def initTravel(self, travels: list, start: Visit, end: Visit):
        distance = self.distances[start.id][end.id]
        time = self.times[start.id][end.id]
        travels.append(Travel(start, end, distance, time))
        return travels

    def initTravels(self, travels: list, visits: list, start: Visit):
        visits = visits[visits.index(start) + 1:]
        return travels + reduce(lambda ts, end: self.initTravel(ts, start, end), visits, list())

    def __init__(self, path: str):
        self.path = path
        self.initConfig()
        self.distances: np.ndarray = np.genfromtxt(path + DISTANCE_FILE, dtype=float)
        self.times: np.ndarray = np.genfromtxt(path + TIMES_FILE, dtype=float)
        self.visits = reduce(
            lambda visits, line: self.initVisits(visits, line),
            list(self.getCsv()),
            list()
        )
        self.travels = reduce(
            lambda travels, start: self.initTravels(travels, self.visits, start),
            self.visits,
            list()
        )

    def initConfig(self):
        config = configparser.ConfigParser()
        config.read(self.path + INI_FILE)
        self.section = config[VEHICLE_SECTION]

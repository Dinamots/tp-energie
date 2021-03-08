import configparser
import csv
from functools import reduce

import numpy as np

from src.const import VEHICLE_SECTION, INI_FILE, DISTANCE_FILE, TIMES_FILE, VISITS_FILE
from src.model.visit import Visit


class World:
    path = ""
    section = None
    distances = None
    times = None
    visits = list()

    def initVisits(self, visits: list, line):
        visits.append(Visit.build(line))
        return visits

    def getCsv(self):
        reader = csv.reader(open(self.path + VISITS_FILE))
        next(reader)
        return reader

    def __init__(self, path: str):
        self.path = path
        self.initConfig()
        self.distances = np.genfromtxt(path + DISTANCE_FILE, dtype=None)
        self.times = np.genfromtxt(path + TIMES_FILE, dtype=None)
        self.visits = reduce(
            lambda vs, line: self.initVisits(vs, line),
            list(self.getCsv()),
            list()
        )
        print(self.visits)

    def initConfig(self):
        config = configparser.ConfigParser()
        config.read(self.path + INI_FILE)
        self.section = config[VEHICLE_SECTION]

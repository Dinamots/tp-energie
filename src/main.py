import configparser
import os
from functools import reduce
from typing import Callable

from src.const import DATA_PREFIX
from src.model.world import World


def createWorld(worlds, dir):
    worlds.append(World(os.path.join(dataPath, dir)))
    return worlds


if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    createWorldReduce: Callable[[list, str], list] = lambda ws, directory: createWorld(ws, directory)
    worlds = reduce(createWorldReduce, os.listdir(dataPath), list())

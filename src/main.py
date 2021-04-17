import os
from multiprocessing import freeze_support
from time import time

from src.multiProcessing import MultiProcessing
from src.neighborhood.neighborhoodSwap import NeighborhoodSwap
from src.world import World

global dataPath


def createWorld(directory) -> World:
    path = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    nbVehicles = 1
    world = World(os.path.join(path, directory), nbVehicles)
    while not world.allDone() and nbVehicles < 100:
        nbVehicles += 1
        world = World(os.path.join(path, directory), nbVehicles)
    return world


def getLocalOptimalSwap(world: World):
    betterWorld = NeighborhoodSwap(world).create()
    return world if world == betterWorld else getLocalOptimalSwap(betterWorld)


def getOptimalsSwap(worlds: list[World]):
    return MultiProcessing.run(getLocalOptimalSwap, worlds)


def getDirectories(dataPath: str):
    datasetName = str(input("Entrez le nom du dataset (all pour tous)"))
    if datasetName.lower() == "all":
        return os.listdir(dataPath)
    else:
        return [dataPath + "\\" + datasetName]


def main():
    directories = getDirectories(dataPath)
    start = time()
    world = MultiProcessing.run(createWorld, directories)
    print("Create Worlds time: {}mins\n".format((time() - start) / 60))
    print("Create Worlds time: {}secs\n".format((time() - start)))
    print(world)
    start = time()
    print(getOptimalsSwap(world))
    print("Get Optimals time: {}mins\n".format((time() - start) / 60))
    print("Get Optimals time: {}secs\n".format((time() - start)))


if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    freeze_support()
    main()
    print("All done!")

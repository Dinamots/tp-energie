import os
from functools import partial
from multiprocessing import freeze_support
from time import time

from src.const import OUT_FILE_SWAP, OUT_FILE_SWAP_VEHICLE, OUT_FILE_RELOAD_CHANGE
from src.multiProcessing import MultiProcessing
from src.neighborhood.neighborhoodReloadChange import NeighborhoodReloadChange
from src.neighborhood.neighborhoodSwap import NeighborhoodSwap
from src.neighborhood.neighborhoodSwapVehicle import NeighborhoodSwapVehicle
from src.world import World

global dataPath


def createWorld(mode, directory) -> World:
    path = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    nbVehicles = 1
    world = World(os.path.join(path, directory), nbVehicles, mode)
    while not world.allDone() and nbVehicles < 100:
        nbVehicles += 1
        world = World(os.path.join(path, directory), nbVehicles, mode)
    return world


def getLocalOptimalSwap(world: World):
    betterWorld = NeighborhoodSwap(world).create()
    return world if world == betterWorld else getLocalOptimalSwap(betterWorld)


def getLocalOptimalReloadChange(world: World):
    betterWorld = NeighborhoodReloadChange(world).create()
    return world if world == betterWorld else getLocalOptimalReloadChange(betterWorld)


def getLocalOptimalSwapVehicle(world: World):
    betterWorld = NeighborhoodSwapVehicle(world).create()
    return world if world == betterWorld else getLocalOptimalSwapVehicle(betterWorld)


def getOptimalsSwap(worlds: list[World]):
    return MultiProcessing.run(getLocalOptimalSwap, worlds)


def getOptimalReloadChange(worlds: list[World]):
    return MultiProcessing.run(getLocalOptimalReloadChange, worlds)


def getOptimalSwapVehicle(worlds: list[World]):
    return MultiProcessing.run(getLocalOptimalSwapVehicle, worlds)


def getDirectories(dataPath: str):
    datasetName = str(input("Entrez le nom du dataset (all pour tous)"))
    if datasetName.lower() == "all":
        return os.listdir(dataPath)
    else:
        return [dataPath + "\\" + datasetName]


def getMode():
    choice = str(input("Random ? [y/N] \n"))
    if choice.lower() == "y":
        return True
    else:
        return False


def main():
    directories = getDirectories(dataPath)
    mode = getMode()
    start = time()
    worlds = MultiProcessing.run(partial(createWorld, mode), directories)
    print("Create Worlds time: {}mins\n".format((time() - start) / 60))
    print("Create Worlds time: {}secs\n".format((time() - start)))
    start = time()
    optimalsReloadChange = getOptimalReloadChange(worlds)
    writeOptimals(optimalsReloadChange, OUT_FILE_RELOAD_CHANGE)
    optimalsSwap = getOptimalsSwap(worlds)
    writeOptimals(optimalsSwap, OUT_FILE_SWAP)
    optimalsSwapVehicle = getOptimalSwapVehicle(worlds)
    writeOptimals(optimalsSwapVehicle, OUT_FILE_SWAP_VEHICLE)
    print("Get Optimals time: {}mins\n".format((time() - start) / 60))
    print("Get Optimals time: {}secs\n".format((time() - start)))


def writeOptimals(optimalWorlds, outName):
    for world in optimalWorlds:
        world.write(outName)


if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    freeze_support()
    main()
    print("All done!")

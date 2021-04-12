import os

from src.world import World


def createWorld(path, directory) -> World:
    nbVehicles = 1
    world = World(os.path.join(path, directory), nbVehicles)
    while not world.allDone() and nbVehicles < 100:
        nbVehicles += 1
        world = World(os.path.join(path, directory), nbVehicles)
    return world


def getPath(dataPath: str):
    datasetName = str(input("Entrez le nom du dataset (all pour tous)"))
    if datasetName == "all":
        return os.listdir(dataPath)
    else:
        return [dataPath + "\\" + datasetName]


if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    worlds = list(
        map(lambda directory: createWorld(dataPath, directory), getPath(dataPath))
    )
    print("All done!")

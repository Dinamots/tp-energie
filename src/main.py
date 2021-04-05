import os
from src.world import World

if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    nbVehicles = int(input("Enter the number of vehicles: "))
    worlds = list(map(lambda directory: World(os.path.join(dataPath, directory), nbVehicles), os.listdir(dataPath)))
    print("All done!")

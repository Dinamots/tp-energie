import os
from src.model.world import World

if __name__ == '__main__':
    dataPath = os.path.realpath(os.path.join(os.getcwd(), "../", "resources", "data"))
    worlds = list(map(lambda dir: World(os.path.join(dataPath, dir)), os.listdir(dataPath)))
    print(worlds)

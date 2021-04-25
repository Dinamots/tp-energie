from copy import deepcopy
from functools import reduce

from src.model.travel import Travel
from src.model.vehicle import Vehicle
from src.utils import Utils
from src.world import World


class NeighborhoodSwap:
    world: World = None

    def __init__(self, world):
        self.world = world

    def create(self):
        print("Create Optimal : " + self.world.path)
        return reduce(
            lambda currentWorld, world: world if not currentWorld.isBetter(world) else currentWorld,
            self.getNeighborhood(),
            self.world
        )

    def getNeighborhood(self):
        return Utils.flatten(
            list(
                map(
                    lambda vehicle: self.getNeighborhoodOfVehicle(self.world.vehicles.index(vehicle)),
                    self.world.vehicles
                )
            )
        )

    def getNeighborhoodOfVehicle(self, vehicleIndex):
        vehicle: Vehicle = deepcopy(self.world.vehicles[vehicleIndex])
        return list(map(
            lambda travel: self.getNeigborhoodOftravel(vehicleIndex, vehicle.tour.index(travel), vehicle),
            vehicle.tour
        ))

    def getNeigborhoodOftravel(self, vehicleIndex, travelIndex, vehicle):
        travelToSwap: Travel = vehicle.tour[travelIndex]
        return list(map(
            lambda index: self.getNewWorldBySwap(vehicleIndex, travelIndex, index, travelToSwap, vehicle),
            range(travelIndex + 1, len(vehicle.tour))
        ))

    def getNewWorldBySwap(self, i, j, k, travelToSwap, vehicle):
        vehicle.tour[j] = vehicle.tour[k]
        vehicle.tour[k] = travelToSwap
        newWorld = World.fromWorld(self.world)
        newWorld.vehicles[i] = vehicle
        return newWorld

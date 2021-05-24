from copy import deepcopy
from functools import reduce

from src.model.travel import Travel
from src.model.travelType import TravelType
from src.model.vehicle import Vehicle
from src.utils import Utils
from src.world import World


class NeighborhoodReloadChange:
    world: World = None

    def __init__(self, world):
        self.world = world

    def create(self):
        print("Create Optimal with Reload Change : " + self.world.path)
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
        if travelToSwap.travelType == TravelType.CHARGE:
            return list(map(
                lambda index: self.getNewWorldByReloadChange(vehicleIndex, travelIndex, index, travelToSwap, vehicle),
                range(0, len(vehicle.tour))
            ))
        return [self.world]

    def getNewWorldByReloadChange(self, i, j, k, travelToSwap, vehicle):
        vehicle.tour[j] = vehicle.tour[k]
        vehicle.tour[k] = travelToSwap
        newWorld = World.fromWorld(self.world)
        newWorld.vehicles[i] = vehicle
        return newWorld

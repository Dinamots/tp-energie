from copy import deepcopy
from functools import reduce

from src.model.vehicle import Vehicle
from src.utils import Utils
from src.world import World


class NeighborhoodSwapVehicle:
    world: World = None

    def __init__(self, world):
        self.world = world

    def create(self):
        print("Create Optimal with Swap Vehicle: " + self.world.path)
        return reduce(
            lambda currentWorld, world: world if not currentWorld.isBetter(world) else currentWorld,
            self.getNeighborhood(),
            self.world
        )

    def getNeighborhood(self):
        return Utils.flatten(
            list(
                map(
                    lambda vehicle: self.getNeighborhoodOfVehicle(vehicle),
                    self.world.vehicles
                )
            )
        )

    def getNeighborhoodOfVehicle(self, vehicle):
        return list(map(
            lambda travel: self.getNeigborhoodOftravel(
                self.world.vehicles.index(vehicle),
                travel,
                vehicle,
                vehicle.tour.index(travel),
            ),
            vehicle.tour
        ))

    def getNeigborhoodOftravel(self, vehicleIndex, travelToInsert, vehicle, travelToRemoveIndex):
        return list(map(
            lambda newVehicle: self.insertTravelToNewVehicle(
                newVehicle,
                self.world.vehicles.index(newVehicle),
                vehicle,
                vehicleIndex,
                travelToInsert,
                travelToRemoveIndex
            ),
            self.world.vehicles
        ))

    def insertTravelToNewVehicle(self, newVehicle, newVehicleIndex, vehicle, vehicleIndex, travelToInsert,
                                 travelToRemoveIndex):
        return list(map(
            lambda travel: self.getNewWorldByInsert(
                newVehicle,
                newVehicleIndex,
                vehicle,
                vehicleIndex,
                travelToInsert,
                vehicle.tour.index(travel),
                travelToRemoveIndex
            ),
            vehicle.tour
        ))

    def getNewWorldByInsert(self, newVehicle, newVehicleIndex, vehicle, vehicleIndex, travelToInsert, indexToInsert,
                            travelToRemoveIndex):
        newVehicleCopy = deepcopy(newVehicle)
        vehicleCopy = deepcopy(vehicle)
        newVehicleCopy.tour.insert(indexToInsert, travelToInsert)
        del vehicleCopy.tour[travelToRemoveIndex]
        newWorld = World.fromWorld(self.world)
        newWorld.vehicles[vehicleIndex] = vehicleCopy
        newWorld.vehicles[newVehicleIndex] = newVehicleCopy
        return newWorld

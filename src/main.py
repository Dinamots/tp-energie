import configparser

from src.model.enum.charge import Charge
from src.model.vehicle import Vehicle

if __name__ == '__main__':
    v = Vehicle()
    print(v.capacity)

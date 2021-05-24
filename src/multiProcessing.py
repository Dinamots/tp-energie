from collections import Callable
from multiprocessing import Pool
from typing import Optional, Any


class MultiProcessing:
    defaultProcesses = 4
    mode = False

    @staticmethod
    def run(func, iterable, processes=defaultProcesses):
        with Pool(processes=processes) as pool:
            return pool.map(func, iterable)

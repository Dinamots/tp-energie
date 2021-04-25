from multiprocessing import Pool


class MultiProcessing:
    defaultProcesses = 4

    @staticmethod
    def run(func, iterable, processes=defaultProcesses):
        with Pool(processes=processes) as pool:
            return pool.map(func, iterable)

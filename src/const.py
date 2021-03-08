import configparser

DATASET = "/lyon_40_1_1"
DATA_PREFIX = "../resources/data"
DATA_PATH = DATA_PREFIX + DATASET
INIT_FILE_PATH = DATA_PATH + "/vehicle.ini"
VEHICLE_SECTION = "Vehicle"

# Config
config = configparser.ConfigParser()
config.read(INIT_FILE_PATH)
section = config[VEHICLE_SECTION]

# Keys
MAX_DIST_KEY = "max_dist"
CAPACITY_KEY = "capacity"
CHARGE_FAST_KEY = "charge_fast"
CHARGE_MEDIUM_KEY = "charge_medium"
CHARGE_SLOW_KEY = "charge_slow"
START_TIME_KEY = "start_time"
END_TIME_KEY = "end_time"

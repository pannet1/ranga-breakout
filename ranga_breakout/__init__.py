from toolkit.logger import Logger
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities
from pprint import pprint

O_FUTL = Fileutils()
O_UTIL = Utilities()
S_DATA = "../data/"
S_LOG = S_DATA + "log.txt"

if not O_FUTL.is_file_exists(S_LOG):
    """
    description:
        create data dir and log file
        if did not if file did not exists
    input:
         file name with full path
    """
    print("creating data dir")
    O_FUTL.add_path(S_LOG)
elif O_FUTL.is_file_not_2day(S_LOG):
    O_FUTL.nuke_file(S_LOG)

logging = Logger(10, S_DATA + "log.txt")

S_DUMP = S_DATA + "symbols.json"
S_UNIV = S_DATA + "universe.csv"
S_CASH = S_DATA + "cash.csv"
S_FUTURE = S_DATA + "future.csv"
S_OUT = S_DATA + "out.csv"
S_STOPS = S_DATA + "stops.json"
YML = O_FUTL.get_lst_fm_yml("../../breakout.yml")
CNFG = YML["angelone"]
pprint(YML)

O_SETG = O_FUTL.get_lst_fm_yml(S_DATA + "settings.yml")
pprint(YML)
SFX = "FUT"

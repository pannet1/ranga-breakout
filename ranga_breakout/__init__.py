from toolkit.logger import Logger
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities
from pprint import pprint

S_DATA = "../data/"
logging = Logger(10)
O_FUTL = Fileutils()
O_UTIL = Utilities()


S_DUMP = S_DATA + "symbols.json"
S_UNIV = S_DATA + "universe.csv"
S_OUT = S_DATA + "out.csv"
S_STOPS = S_DATA + "stops.json"
YML = O_FUTL.get_lst_fm_yml("../../breakout.yml")
CNFG = YML["angelone"]
pprint(YML)

O_SETG = O_FUTL.get_lst_fm_yml(S_DATA + "settings.yml")
pprint(YML)
SFX = "FUT"

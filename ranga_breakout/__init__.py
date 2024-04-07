from toolkit.logger import Logger
from toolkit.fileutils import Fileutils

S_DATA = "../data/"
logging = Logger(10, S_DATA + "log.txt")
O_FUTL = Fileutils()


S_DUMP = S_DATA + "symbols.json"
S_UNIV = S_DATA + "universe.csv"
S_OUT = S_DATA + "out.csv"
YML = O_FUTL.get_lst_fm_yml("../../breakout.yml")
CNFG = YML["angelone"]
S_EXPIRY = YML["expiry"]
logging.info(YML)

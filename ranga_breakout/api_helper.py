from omspy_brokers.angel_one import AngelOne
from __init__ import logging


def login(CNFG):
    api = AngelOne(**CNFG)
    if api.authenticate():
        logging.info("api connected")
        return api
    else:
        logging.error("api not connected")
        SystemExit(1)

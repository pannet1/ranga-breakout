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


if __name__ == "__main__":
    from __init__ import CNFG, S_DATA
    import pandas as pd
    api = login(CNFG)

    ord = api.orders
    print(ord)
    pd.DataFrame(ord).to_csv(S_DATA + "orders.csv")

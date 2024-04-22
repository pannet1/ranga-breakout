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

    ord = api.orders["data"]
    df = pd.DataFrame(ord)
    print(df)
    df.to_csv(S_DATA + "orders.csv")

    pos = api.positions["data"]
    df = pd.DataFrame(pos)
    print(df)
    df.to_csv(S_DATA + "positions.csv")

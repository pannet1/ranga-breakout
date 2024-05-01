from omspy_brokers.angel_one import AngelOne
from __init__ import logging


def get_token(CNFG):
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

    historicParam = {
        "exchange": "NSE",
        "symboltoken": 1502,
        "interval": "THIRTY_MINUTE",
        "fromdate": "2024-04-29 09:15",
        "todate": "2024-05-01 09:45",
    }
    resp = api.obj.getCandleData(historicParam)
    print(resp)

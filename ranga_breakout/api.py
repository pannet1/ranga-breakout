from omspy_brokers.angel_one import AngelOne
from __init__ import logging, CNFG


def get_token():
    api = AngelOne(**CNFG)
    if api.authenticate():
        logging.info("api connected")
        return api
    else:
        logging.error("api not connected")


class Helper:
    api = None

    @classmethod
    def set_token(cls):
        if cls.api is None:
            cls.api = get_token()


if __name__ == "__main__":
    from __init__ import CNFG, S_DATA
    import pandas as pd

    Helper.set_token()
    api = Helper.api

    params = {"NFO": [35603, 46845]}
    resp = api.obj.getMarketData("LTP", params)
    print(resp)
    __import__("time").sleep(5)

    ord = api.orders
    df = pd.DataFrame(ord["data"])
    print(df)
    df.to_csv(S_DATA + "orders.csv")

    pos = api.positions["data"]
    df = pd.DataFrame(pos)
    print(df)
    # find sum of of pnl column in df

    df.to_csv(S_DATA + "positions.csv")
    lst = df["pnl"].astype(float).tolist()
    pnl = sum(lst)
    print(f"{pnl=}")
    """
    historicParam = {
        "exchange": "NSE",
        "symboltoken": 1502,
        "interval": "THIRTY_MINUTE",
        "fromdate": "2024-04-29 09:15",
        "todate": "2024-05-01 09:45",
    }
    resp = api.obj.getCandleData(historicParam)
    print(resp)
    """

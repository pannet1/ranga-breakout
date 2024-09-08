from omspy_brokers.angel_one import AngelOne
from __init__ import logging, CNFG


def get_token():
    ao = AngelOne(**CNFG)
    if ao.authenticate():
        logging.info("api connected")
        return ao
    else:
        logging.error("api not connected")


class Helper:
    ao = None

    @classmethod
    @property
    def api(cls):
        if cls.ao is None:
            cls.ao = get_token()
        return cls.ao

    @classmethod
    @property
    def orders(cls):
        try:
            # get orders
            resp = cls.ao.orders
            return resp["data"]
        except Exception as e:
            print(e)
            return []

    @classmethod
    @property
    def positions(cls):
        try:
            # get orders
            resp = cls.ao.positions
            return resp["data"]
        except Exception as e:
            print(e)
            return []


if __name__ == "__main__":
    from __init__ import CNFG, S_DATA
    import pandas as pd
    from toolkit.kokoo import dt_to_str
    from history import get_historical_data
    from main import get_ltp, get_params

    Helper.api

    """
    historicParam = {
        "exchange": "NSE",
        "symboltoken": 317,
        "interval": "FIVE_MINUTE",
        "fromdate": dt_to_str("9:15"),
        "todate": dt_to_str(""),
    }
    resp = get_historical_data(historicParam)
    print(resp)
    """
    ord = Helper.orders
    df = pd.DataFrame(ord)
    print(df)
    df.to_csv(S_DATA + "orders.csv")

    pos = Helper.positions
    df = pd.DataFrame(pos)
    print(df)
    # find sum of of pnl column in df
    df.to_csv(S_DATA + "positions.csv")
    if not df.empty:
        lst = df["pnl"].astype(float).tolist()
        pnl = sum(lst)
        print(f"{pnl=}")

    params = get_params()
    print(params)
    resp = get_ltp(params)
    print(resp)

from omspy_brokers.angel_one import AngelOne
from __init__ import logging, CNFG
from traceback import print_exc


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
            resp = []
            # get orders
            resp = cls.ao.orders
            resp = resp["data"]
        except Exception as e:
            logging.error(f"{e} while api is getting orders")
            return []

    @classmethod
    @property
    def positions(cls):
        try:
            # get orders
            resp = cls.ao.positions
            return resp["data"]
        except Exception as e:
            logging.error(f"{e} while api is getting positions")
            return []


if __name__ == "__main__":
    from __init__ import CNFG, S_DATA
    import pandas as pd
    from toolkit.kokoo import dt_to_str

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

    def orders():
        ord = Helper.orders
        df = pd.DataFrame(ord)
        print(df)
        df.to_csv(S_DATA + "orders.csv")

    def positions():
        pos = Helper.positions
        df = pd.DataFrame(pos)
        print(df)
        # find sum of of pnl column in df
        df.to_csv(S_DATA + "positions.csv")
        if not df.empty:
            lst = df["pnl"].astype(float).tolist()
            pnl = sum(lst)
            print(f"{pnl=}")

    def modify_order():
        try:
            params = {
                "symbol": "INDIGO-EQ",
                "exchange": "NSE",
                "order_type": "STOPLOSS_LIMIT",
                "product": "INTRADAY",
                "quantity": 2.0,
                "symboltoken": "11195",
                "variety": "STOPLOSS",
                "duration": "DAY",
                "side": "SELL",
                "price": 4351.45,
                "trigger_price": 4351.5,
                "orderid": "241127000230561",
            }
            resp = Helper.api.order_modify(**params)
            print(resp)
        except Exception as e:
            print(e)
            print_exc()

    orders()
    positions()

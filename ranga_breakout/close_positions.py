from __init__ import CNFG, S_DATA, O_UTIL
import pandas as pd
from api_helper import login


def close_positions(api):
    pos = api.positions
    if isinstance(pos, dict):
        pos = pos["data"]
        pd.DataFrame(pos).to_csv(S_DATA + "positions.csv", index=False)
        for i in pos:
            if i["netqty"] != 0:
                print(i)
                api.order_place(**i)


def close_orders(api):
    ord = api.orders
    if isinstance(ord, dict):
        ord = ord["data"]
        pd.DataFrame(ord).to_csv(S_DATA + "orders.csv", index=False)
        for i in ord:
            if i["status"] == "open":
                args = dict(
                    orderid=i["orderid"],
                )
                api.order_modify(args)


def run():
    api = login(CNFG)
    close_orders(api)
    O_UTIL.slp_til_nxt_sec()
    close_positions(api)


if __name__ == "__main__":
    run()

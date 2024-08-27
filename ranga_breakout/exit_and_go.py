from __init__ import CNFG, S_DATA, O_UTIL, logging
import pandas as pd
from api import Helper
from traceback import print_exc


def close_positions(pos):
    try:
        for params in pos:
            quantity = int(params["netqty"])
            if quantity != 0:
                order_params = {
                    "variety": "NORMAL",
                    "tradingsymbol": params["tradingsymbol"],
                    "symboltoken": params["symboltoken"],
                    "transactiontype": "SELL" if quantity > 0 else "BUY",
                    "exchange": params["exchange"],
                    "ordertype": "MARKET",
                    "producttype": params["producttype"],
                    "duration": "DAY",
                    "price": "0",
                    "triggerprice": "0",
                    "quantity": abs(quantity),
                }
                yield order_params
    except Exception as e:
        print(e)


def cancel_orders(ord):
    try:
        for i in ord:
            print(f"trying to cancel order for {i['tradingsymbol']}")
            if i["status"] == "open" or i["status"] == "trigger pending":
                yield {"order_id": i["orderid"], "variety": "NORMAL"}
    except Exception as e:
        print(e)


def run():
    try:

        ord = Helper.api.orders["data"]
        for i in cancel_orders(ord):
            O_UTIL.slp_til_nxt_sec()
            logging.info(f"close all: cancelling order {i['order_id']}")
            Helper.api.order_cancel(**i)

        pos = Helper.api.positions["data"]
        for order_params in close_positions(pos):
            logging.info(f"closing position for {order_params['tradingsymbol']}")
            O_UTIL.slp_til_nxt_sec()
            resp = Helper.api.order_place(**order_params)
            logging.info(resp)

        O_UTIL.slp_til_nxt_sec()
        ord = Helper.api.orders["data"]
        pd.DataFrame(ord).to_csv(S_DATA + "orders.csv", index=False)

        O_UTIL.slp_til_nxt_sec()
        pos = Helper.api.positions["data"]
        pd.DataFrame(pos).to_csv(S_DATA + "positions.csv", index=False)
    except Exception as e:
        print_exc()
        logging.error(e)


if __name__ == "__main__":
    run()

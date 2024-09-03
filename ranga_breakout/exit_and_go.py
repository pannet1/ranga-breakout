from __init__ import CNFG, S_DATA, O_UTIL, logging
import pandas as pd
from api import Helper
from traceback import print_exc


def cancel_all_orders():
    try:
        resp = Helper.orders
        print(type(resp))
        for order in resp:
            print(order)
            if order["status"] in ["open", "trigger pending"]:
                O_UTIL.slp_til_nxt_sec()
                logging.info(f"close all: cancelling order {order['orderid']}")
                Helper.api.order_cancel(order_id=order["orderid"], variety="NORMAL")
    except Exception as e:
        print_exc()
        print(e)


def close_all_positions():
    try:
        resp = Helper.positions
        for params in resp:
            print(params)
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
                logging.info(f"Closing position for {params['tradingsymbol']}")
                O_UTIL.slp_til_nxt_sec()
                resp = Helper.api.order_place(**order_params)
                logging.info(resp)
    except Exception as e:
        print_exc()
        print(e)


def save_to_csv():
    try:
        O_UTIL.slp_til_nxt_sec()
        ord = Helper.api.orders
        print(ord)
        pd.DataFrame(ord).to_csv(S_DATA + "orders.csv", index=False)

        O_UTIL.slp_til_nxt_sec()
        pos = Helper.api.positions
        print(pos)
        pd.DataFrame(pos).to_csv(S_DATA + "positions.csv", index=False)
    except Exception as e:
        print_exc()
        logging.error(e)


if __name__ == "__main__":
    Helper.api
    cancel_all_orders()
    close_all_positions()
    # save_to_csv()

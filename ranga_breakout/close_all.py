from __init__ import CNFG, S_DATA, O_UTIL
import pandas as pd
from api_helper import login


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
    for i in ord:
        if i["status"] == "open" or i["status"] == "trigger pending":
            yield {"order_id": i["orderid"], "variety": "NORMAL"}


def run():
    try:
        api = login(CNFG)

        ord = api.orders["data"]
        for i in cancel_orders(ord):
            O_UTIL.slp_til_nxt_sec()
            print(i)
            api.order_cancel(**i)

        pos = api.positions["data"]
        for order_params in close_positions(pos):
            print(order_params)
            O_UTIL.slp_til_nxt_sec()
            resp = api.order_place(**order_params)
            print(resp)
        pd.DataFrame(api.orders["data"]).to_csv(
            S_DATA + "orders.csv", index=False)
        pd.DataFrame(api.positions["data"]).to_csv(
            S_DATA + "positions.csv", index=False
        )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()

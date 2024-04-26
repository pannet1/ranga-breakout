from __init__ import CNFG, logging
from api_helper import login


def get_order_ids(buy_orders, sell_orders):
    # get order numbers if tradingsybol is same in both
    if sell_orders and any(sell_orders) and buy_orders and any(buy_orders):
        for i in buy_orders:
            for j in sell_orders:
                if i["tradingsymbol"] == j["tradingsymbol"]:
                    logging.info(f' getting orders to cancel for {i["tradingsymbol"]}')
                    yield [i["orderid"], j["orderid"]]


def run():
    try:
        api = login(CNFG)
        ord = api.orders["data"]
        # find orders that have both buy and sell legs
        # with status as open or trigger pending
        buy_orders = [
            i
            for i in ord
            if int(i["quantity"]) > 0
            and (i["status"] == "open" or i["status"] == "trigger pending")
        ]
        sell_orders = [
            i
            for i in ord
            if int(i["quantity"]) < 0
            and (i["status"] == "open" or i["status"] == "trigger pending")
        ]
        for i in get_order_ids(buy_orders, sell_orders):
            logging.info(api.order_cancel(i[0], "NORMAL"))
            logging.info(api.order_cancel(i[1], "NORMAL"))
    except Exception as e:
        logging.error(f"while cancelling orders {e}")


if __name__ == "__main__":
    run()

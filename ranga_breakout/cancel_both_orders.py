from __init__ import CNFG, logging
from api import Helper


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
        api = Helper.api
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
    api = Helper.api
    """
    args = {
        "variety": "STOPLOSS",
        "orderid": "240826100514712",
        "transactiontype": "BUY",
        "tradingsymbol": "CANBK-EQ",
        "symboltoken": 10794,
        "exchange": "NSE",
        "ordertype": "STOPLOSS_MARKET",
        "quantity": 1,
        "triggerprice": 112.60,
        "price": 112.65,
        "duration": "DAY",
        "product": "INTRADAY",
    }
    """
    args = {
        "tradingsymbol": "HEROMOTOCO-EQ",
        "exchange": "NSE",
        "order_type": "STOPLOSS_MARKET",
        "product": "INTRADAY",
        "quantity": 1,
        "symboltoken": "1348",
        "variety": "STOPLOSS",
        "duration": "DAY",
        "side": "SELL",
        "price": 5352.599999999999,
        "trigger_price": 5325.95,
        "orderid": "240827100866862",
        "triggerprice": 5352.65,
    }

    resp = api.order_modify(**args)
    print(resp)

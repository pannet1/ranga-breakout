from traceback import print_exc
from typing import Any  # Importing only the required types

from toolkit.kokoo import timer, dt_to_str

from __init__ import O_FUTL, S_STOPS, logging
from api import Helper

from history import get_historical_data, get_low_high


def create_order_args(ohlc, side, price, trigger_price):
    return dict(
        symbol=ohlc["tsym"],
        exchange="NFO",
        order_type="STOPLOSS_MARKET",
        product="INTRADAY",  # Options: CARRYFORWARD, INTRADAY
        quantity=ohlc["quantity"],
        symboltoken=ohlc["token"],
        variety="STOPLOSS",
        duration="DAY",
        side=side,
        price=price,
        trigger_price=trigger_price,
    )


class Breakout:
    def __init__(self, param: dict[str, dict[str, Any]]):
        self.api = Helper.api
        self.dct = dict(
            tsym=param["tsym"],
            h=param["h"],
            l=param["l"],
            last_price=param["c"],
            quantity=param["quantity"],
            token=param["token"],
        )

        defaults = {
            "fn": self.make_order_params,
            "buy_args": {},
            "sell_args": {},
            "buy_id": None,
            "sell_id": None,
            "entry": 0,
            "completed_candles": 1,
            "can_trail": None,
        }
        self.dct.update(defaults)
        self.dct_of_orders = {}
        logging.info(self.dct)

    def make_order_params(self):
        try:
            self.dct["buy_args"] = create_order_args(
                self.dct,
                "BUY",
                float(self.dct["h"]) + 0.10,
                float(self.dct["h"]) + 0.05,
            )
            self.dct["sell_args"] = create_order_args(
                self.dct,
                "SELL",
                float(self.dct["l"]) - 0.10,
                float(self.dct["l"]) - 0.05,
            )
            self.dct["fn"] = self.place_both_orders
        except Exception as e:
            logging.error(f"{e} while making order params")
            print_exc()
            self.dct["fn"] = None

    def place_both_orders(self):
        try:
            args = self.dct

            # Place buy order
            resp = self.api.order_place(**args["buy_args"])
            logging.info(
                f"{args['buy_args']['symbol']} {args['buy_args']['side']} got {resp=}"
            )
            self.dct["buy_id"] = resp

            # Place sell order
            resp = Helper.api.order_place(**args["sell_args"])
            logging.info(
                f"{args['sell_args']['symbol']} {args['sell_args']['side']} got {resp=}"
            )
            self.dct["sell_id"] = resp

            self.dct["fn"] = self.is_buy_or_sell
        except Exception as e:
            logging.error(f"Error placing orders for {args['tsym']}: {e}")
            print_exc()
            self.dct["fn"] = None

    def is_buy_or_sell(self):
        """
        determine if buy or sell order is completed
        """
        try:
            buy = self.dct["buy_id"]
            sell = self.dct["sell_id"]
            if self.dct_of_orders[str(buy)]["status"] == "complete":
                self.dct["entry"] = 1
                self.dct["can_trail"] = lambda c: c["last_price"] > c["h"]
                self.dct["stop_price"] = self.dct["l"]
            elif self.dct_of_orders[str(sell)]["status"] == "complete":
                self.dct["entry"] = -1
                self.dct["can_trail"] = lambda c: c["last_price"] < c["l"]
                self.dct["stop_price"] = self.dct["h"]

            if self.dct["entry"] != 0:
                logging.info(f"no buy/sell complete for {self.dct['tsym']}")
                self.dct["fn"] = self.trail_stoploss
            else:
                logging.debug(f"order not complete for {self.dct['tsym']}")
        except Exception as e:
            logging.error(f"error is_buy_or_sell {e}")
            print_exc()

    def trail_stoploss(self):
        """
        if candles  count is changed and then check ltp
        """
        try:

            if self.dct["can_trail"](self.dct):

                # get historical candles
                params = dict(
                    exchange="NFO",
                    symboltoken=self.dct["token"],
                    interval="FIFTEEN_MINUTE",
                    fromdata=dt_to_str("09:15"),
                    todate=dt_to_str(""),
                )
                candles_now = get_historical_data(params)
                if len(candles_now) > self.candle_count:

                    is_flag = False
                    # buy trade
                    if self.dct["entry"] == 1:
                        args = dict(
                            orderid=self.dct["sell_id"],
                            price=float(self.dct["l"]) - 0.10,
                            triggerprice=float(self.dct["l"]) - 0.05,
                        )
                        is_flag = (
                            min(candles_now[-3][3], candles_now[-2][3])
                            > self.dct["stop_price"]
                        )
                    else:
                        args = dict(
                            orderid=self.dct["buy_id"],
                            price=float(self.dct["h"]) + 0.10,
                            triggerprice=float(self.dct["h"]) + 0.05,
                        )
                        is_flag = (
                            max(candles_now[-3][2], candles_now[-2][2])
                            < self.dct["stop_price"]
                        )
                    # modify order
                    """
                    "variety":"NORMAL",
                    "orderid":"201020000000080",
                    "ordertype":"LIMIT",
                    "producttype":"INTRADAY",
                    "duration":"DAY",
                    "price":"194.00",
                    "quantity":"1",
                    "tradingsymbol":"SBIN-EQ",
                    "symboltoken":"3045",
                    "exchange":"NSE"
                    """
                    if is_flag:
                        resp = Helper.api.order_modify(args)
                        print(resp)

                        # update high and low except for the last
                        self.dct["l"], self.dct["h"] = get_low_high(candles_now[:-1])
                        # update candle count if order is placed
                        self.candle_count = len(candles_now)

            timer(1)

        except Exception as e:
            logging.error(f"while trailstop {e}")
            print_exc()

    def run(self, lst_of_orders, dct_of_ltp):
        try:
            if any(lst_of_orders):
                self.dct_of_orders = {
                    dct.get("orderid", "dummy"): dct for dct in lst_of_orders
                }
            self.dct["last_price"] = dct_of_ltp.get(
                self.dct["token"], self.dct["last_price"]
            )
            timer(1)
            if self.dct["fn"] is not None:
                logging.debug(f"{self.dct['tsym']} run {self.dct['fn']}")
                self.dct["fn"]()
        except Exception as e:
            print_exc()


"""
   helpers used  for strategy begins 
"""


def is_values_in_list(lst_orders, args):
    dct = {}
    try:
        for i in lst_orders:
            if (
                i["tradingsymbol"] == args["tradingsymbol"]
                and i["transactiontype"] == args["transactiontype"]
            ):
                if i["status"] == "complete":
                    dct = i
                logging.info(i["status"].upper())
    except Exception as e:
        logging.error(f"{e} while checking for values in list")
    finally:
        return dct


class Strategy:
    def __init__(self):
        self.api = Helper.api
        self.lst = []
        if not O_FUTL.is_file_not_2day(S_STOPS):
            self.lst = O_FUTL.read_file(S_STOPS)
        self.is_set = True if any(self.lst) else False

    """
    dct = {
        "variety": "NORMAL",
        "ordertype": "LIMIT",
        "producttype": "INTRADAY",
        "duration": "DAY",
        "price": 432.05,
        "triggerprice": 432.1,
        "quantity": "1600",
        "disclosedquantity": "0",
        "squareoff": 0.0,
        "stoploss": 0.0,
        "trailingstoploss": 0.0,
        "tradingsymbol": "ITC27JUN24FUT",
        "transactiontype": "SELL",
        "exchange": "NFO",
        "symboltoken": "52178",
        "ordertag": "",
        "instrumenttype": "FUTSTK",
        "strikeprice": -1.0,
        "optiontype": "XX",
        "expirydate": "27JUN2024",
        "lotsize": "1600",
        "cancelsize": "0",
        "averageprice": 432.05,
        "filledshares": "1600",
        "unfilledshares": "0",
        "orderid": "240612000182183",
        "text": "",
        "status": "complete",
        "orderstatus": "complete",
        "updatetime": "12-Jun-2024 09:45:39",
        "exchtime": "12-Jun-2024 09:45:39",
        "exchorderupdatetime": "12-Jun-2024 09:45:39",
        "fillid": "",
        "filltime": "",
        "parentorderid": "",
        "uniqueorderid": "119729f9-1216-4007-b7da-196b630b64dc",
        "exchangeorderid": "2300000017065849",
    }
    """

    def run(self):
        try:
            dct = self.api.orders

            if not isinstance(dct, dict):
                logging.error("'dct' is not a dictionary in run()")
                return

            if "data" not in dct:
                logging.error("'data' key not found in 'dct'.")
                return

            lst_orders = dct["data"]

            # Work with the copy of stop orders
            for i in self.lst[:]:
                try:
                    print(f'{i["side"]} stop order from file for {i["symbol"]}')
                    args = {"tradingsymbol": i["symbol"]}
                    args["transactiontype"] = "SELL" if i["side"] == "BUY" else "BUY"

                    # Filter the order book containing only this symbol
                    lst_of_entries = [
                        j
                        for j in lst_orders
                        if j["tradingsymbol"] == args["tradingsymbol"]
                        and j["transactiontype"] == args["transactiontype"]
                    ]

                    # Do we have any item in the list
                    if lst_of_entries:
                        dct_found = is_values_in_list(lst_of_entries, args)
                        status = dct_found.get("status", "NOT_COMPLETE")
                        if status == "complete":
                            resp = self.api.order_place(**i)
                            logging.info(f"{resp} stop order for i['tradingsymbol']")
                            timer(1)
                            self.lst.remove(i)
                    else:
                        print(f'{i["side"]} stop order for {i["symbol"]} has no match')
                        self.lst.remove(i)

                except KeyError as ke:
                    logging.error(f"KeyError: {ke} - Order: {i}")
                except Exception as e:
                    logging.error(f"Unexpected error processing order {i}: {e}")

            self.wait_and_log_remaining_orders()

        except Exception as e:
            logging.error(e)

    def wait_and_log_remaining_orders(self):
        timer(2)
        print(f"{len(self.lst)} stop orders found")


if __name__ == "__main__":
    Helper.set_token()

    Sgy = Strategy()
    if Sgy.is_set:
        Sgy.run()

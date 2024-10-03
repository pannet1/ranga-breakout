from traceback import print_exc
from typing import Any  # Importing only the required types

from toolkit.kokoo import timer, dt_to_str

from __init__ import logging
from api import Helper

from history import find_buy_stop, get_historical_data, find_sell_stop

from pprint import pprint


def create_order_args(ohlc, side, price, trigger_price):
    return dict(
        symbol=ohlc["tsym"],
        exchange=ohlc["exchange"],
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
        self.dct = dict(
            tsym=param["tsym"],
            exchange=param["exchange"],
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
            "entry": None,
            "can_trail": None,
            "stop_price": None,
        }
        self.candle_count = 2
        self.candle_other = 2
        self.dct.update(defaults)
        self.dct_of_orders = {}
        self.message = "message not set"
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
            fn = self.dct.pop("fn")
            self.message = f"{self.dct['tsym']} encountered {e} while {fn}"
            logging.error(self.message)
            print_exc()
            self.dct["fn"] = None

    def place_both_orders(self):
        try:
            args = self.dct

            # Place buy order
            resp = Helper.api.order_place(**args["buy_args"])
            logging.debug(
                f"{args['buy_args']['symbol']} {args['buy_args']['side']} got {resp=}"
            )
            self.dct["buy_id"] = resp

            # Place sell order
            resp = Helper.api.order_place(**args["sell_args"])
            logging.debug(
                f"{args['sell_args']['symbol']} {args['sell_args']['side']} got {resp=}"
            )
            self.dct["sell_id"] = resp

            self.dct["fn"] = self.is_buy_or_sell
            self.message = "buy and sell orders placed"
        except Exception as e:
            fn = self.dct.pop("fn")
            self.message = f"{self.dct['tsym']} encountered {e} while {fn}"
            logging.error(self.message)
            print_exc()
            self.dct["fn"] = None

    def _is_buy_or_sell(self, operation):
        buy_or_sell = self.dct[f"{operation}_id"]
        return self.dct_of_orders[buy_or_sell]["status"] == "complete"

    def is_buy_or_sell(self):
        """
        determine if buy or sell order is completed
        """
        try:
            if self._is_buy_or_sell("buy"):
                self.dct["entry"] = "buy"
                self.dct["can_trail"] = lambda c: c["last_price"] > c["h"]
                self.dct["stop_price"] = self.dct["l"]
            elif self._is_buy_or_sell("sell"):
                self.dct["entry"] = "sell"
                self.dct["can_trail"] = lambda c: c["last_price"] < c["l"]
                self.dct["stop_price"] = self.dct["h"]

            if self.dct["entry"] is None:
                self.message = f"no entry order is completed for {self.dct['tsym']}"
            else:
                self.message = f"{dct['entry']} order completed for {self.dct['tsym']}"
                self.dct["fn"] = self.trail_stoploss
        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while is_buy_or_sell"
            logging.error(self.message)
            print_exc()

    def get_history(self):
        params = {
            "exchange": self.dct["exchange"],
            "symboltoken": self.dct["token"],
            "interval": "FIFTEEN_MINUTE",
            "fromdate": dt_to_str("9:15"),
            "todate": dt_to_str(""),
        }
        return get_historical_data(params)

    def _is_modify_order(self, candles_now):
        try:
            # buy trade
            if self.dct["entry"] == "buy":
                # stop_now = min(candles_now[-3][3], candles_now[-2][3])
                stop_now, highest = find_buy_stop(candles_now)
                if stop_now and stop_now > self.dct["stop_price"]:
                    args = dict(
                        orderid=self.dct["sell_id"],
                        price=stop_now - 0.10,
                        triggerprice=stop_now - 0.05,
                    )
                    self.dct["sell_args"].update(args)
                    args = self.dct["sell_args"]
                    self.dct["h"] = highest
                    self.message = f'buy stop {stop_now} is going to replace {self.dct["stop_price"]}'
                    self.dct["stop_price"] = stop_now
                    return args

            elif self.dct["entry"] == "sell":
                # stop_now = max(candles_now[-3][2], candles_now[-2][2])
                stop_now, lowest = find_sell_stop(candles_now)
                if stop_now and stop_now < self.dct["stop_price"]:
                    args = dict(
                        orderid=self.dct["buy_id"],
                        price=stop_now + 0.10,
                        triggerprice=stop_now + 0.05,
                    )
                    self.dct["buy_args"].update(args)
                    args = self.dct["buy_args"]
                    self.dct["l"] = lowest
                    self.message = f'sell stop {stop_now} is going to replace {self.dct["stop_price"]}'
                    self.dct["stop_price"] = stop_now
                    return args
            return {}
        except Exception as e:
            fn = self.dct.pop("fn")
            self.message = f"{self.dct['tsym']} encountered {e} while {fn}"
            logging.error(self.message)
            print_exc()

    def trail_stoploss(self):
        """
        if candles  count is changed and then check ltp
        """
        try:
            FLAG = False
            # check if stop loss is already hit
            operation = "sell" if self.dct["entry"] == "buy" else "buy"
            if self._is_buy_or_sell(operation):
                self.dct["fn"] = None
                self.message = (
                    f"trail complete for {self.dct['tsym']} by {operation} stop order"
                )
                return

            if self.dct["can_trail"](self.dct):
                print(f'{self.dct["last_price"]} is a breakout for {self.dct["tsym"]}')
                FLAG = True
            elif self.candle_other > self.candle_count:
                print(
                    f"other candles {self.candle_other} > this symbol candle {self.candle_count}"
                )
                FLAG = True

            if FLAG:
                candles_now = self.get_history()
                if len(candles_now) > self.candle_count:
                    pprint(candles_now)
                    print(
                        f"curr candle:{len(candles_now)} > prev candle:{self.candle_count}"
                    )
                    args = self._is_modify_order(candles_now)
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
                    if any(args):
                        logging.debug(f"order modify {args}")
                        resp = Helper.api.order_modify(**args)
                        logging.debug(f"order modify {resp}")
                        self.candle_count = len(candles_now)
                        timer(0.5)

        except Exception as e:
            fn = self.dct.pop("fn")
            self.message = f"{self.dct['tsym']} encountered {e} while {fn}"
            logging.error(self.message)
            print_exc()
            self.dct["fn"] = None

    def run(self, lst_of_orders, dct_of_ltp, CANDLE_OTHER):
        try:
            if isinstance(lst_of_orders, list):
                self.dct_of_orders = {
                    dct["orderid"]: dct for dct in lst_of_orders if "orderid" in dct
                }
            self.dct["last_price"] = dct_of_ltp.get(
                self.dct["token"], self.dct["last_price"]
            )
            if CANDLE_OTHER > self.candle_other:
                print(
                    '{self.dct["tsym"]} candle is behind {self.candle_other}  others {CANDLE_OTHER}'
                )
                self.candle_other = CANDLE_OTHER

            if self.dct["fn"] is not None:
                message = dict(
                    symbol=self.dct["tsym"],
                    low=self.dct["l"],
                    high=self.dct["h"],
                    last_price=self.dct["last_price"],
                    prev_candle=self.candle_count,
                    stop_loss=self.dct["stop_price"],
                    next_fn=self.dct["fn"],
                )
                pprint(message)
                self.dct["fn"]()
        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while run"
            logging.error(self.message)
            print_exc()


if __name__ == "__main__":
    from main import get_ltp
    from universe import stocks_in_play
    from history import get_candles

    try:
        df = stocks_in_play()
        params = get_candles(df)

        # create strategy object
        for _, param in params.items():
            obj = Breakout(param)
            break

        lst_of_orders = Helper.api.orders
        dct_of_ltp = get_ltp(params)
        obj.dct["fn"] = obj.is_buy_or_sell
        obj.run(lst_of_orders, dct_of_ltp)
    except Exception as e:
        print_exc()
        print(e)

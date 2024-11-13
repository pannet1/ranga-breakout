from traceback import print_exc
from typing import Any  # Importing only the required types
import numpy as np
from toolkit.kokoo import dt_to_str

from __init__ import logging
from api import Helper

from history import find_buy_stop, get_historical_data, find_sell_stop, find_extremes

from pprint import pprint
import pendulum as pdlm


def float_2_curr(value: float):
    try:
        return round(value / 0.05) * 0.05
    except Exception as e:
        print(e)


def create_order_args(ohlc, side, price, trigger_price):
    return dict(
        symbol=ohlc["tsym"],
        exchange=ohlc["exchange"],
        order_type="STOPLOSS_LIMIT",
        product="INTRADAY",  # Options: CARRYFORWARD, INTRADAY
        quantity=ohlc["quantity"],
        symboltoken=ohlc["token"],
        variety="STOPLOSS",
        duration="DAY",
        side=side,
        price=price,
        trigger_price=trigger_price,
    )


class Reverse:

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
            "stop_price": None,
            "can_trail": None,
            "candle_two": None,
        }
        self.dct.update(defaults)
        self.candle_count = 2
        self.candle_start = 2
        self.dct_of_orders = {}
        self.message = "message not set"
        logging.info(self.dct)
        self.next_check = pdlm.now().add(minutes=5)
        self.make_order_params()

    """ 
        common methods
    """

    def _get_history(self, should_check=True):
        try:
            candles_now = []
            if should_check:
                self.next_check = pdlm.now().add(minutes=5)
                params = {
                    "exchange": self.dct["exchange"],
                    "symboltoken": self.dct["token"],
                    "interval": "FIFTEEN_MINUTE",
                    "fromdate": dt_to_str("9:15"),
                    "todate": dt_to_str(""),
                }
                candles_now = get_historical_data(params)
        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while get history"
            logging.error(self.message)
            print_exc()
        finally:
            return candles_now

    def _is_buy_or_sell(self, operation):
        buy_or_sell = self.dct[f"{operation}_id"]
        return self.dct_of_orders[buy_or_sell]["status"] == "complete"

    def _is_order_complete(self, operation):
        try:
            FLAG = False
            if self._is_buy_or_sell(operation):
                self.dct["fn"] = None
                self.message = (
                    f"trail complete for {self.dct['tsym']} by {operation} stop order"
                )
                FLAG = True
        except Exception as e:
            self.message = (
                f"{self.dct['tsym']} encountered {e} while _is_order_complete"
            )
            logging.error(self.message)
            print_exc()
        finally:
            return FLAG

    def _modify_order(self, order_id, args_dict, stop_now):
        try:
            self.dct[args_dict].update(
                {
                    "orderid": self.dct[order_id],
                    "price": stop_now,
                    "triggerprice": stop_now,
                }
            )
            args = self.dct[args_dict]
            self.dct["stop_price"] = stop_now
            logging.debug(f"order modify: {args}")
            resp = Helper.api.order_modify(**args)
            logging.debug(f"order modify response: {resp}")
        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while _modify_order"
            logging.error(self.message)
            print_exc()

    """
       1. make order params 
    """

    def make_order_params(self):
        """
        make order params for placing orders
        """
        try:
            high, low = float(self.dct["h"]), float(self.dct["l"])
            half_spread = (high - low) / 2

            # Precompute prices for buy and sell orders
            buy_price = float_2_curr(low - half_spread)
            sell_price = float_2_curr(high + half_spread)

            self.dct["buy_args"] = create_order_args(
                ohlc=self.dct, side="BUY", price=buy_price, trigger_price=buy_price
            )
            self.dct["sell_args"] = create_order_args(
                ohlc=self.dct, side="SELL", price=sell_price, trigger_price=sell_price
            )
            self.dct["fn"] = self.place_both_orders
        except Exception as e:
            fn = self.dct.pop("fn")
            self.message = f"{self.dct['tsym']} encountered {e} while {fn}"
            logging.error(self.message)
            print_exc()
            self.dct["fn"] = None

    """
     1. place both  orders
    """

    def _place_order(self, order_args_key, order_type):
        """Helper to place an order and log the response."""
        args = self.dct[order_args_key]
        resp = Helper.api.order_place(**args)
        logging.debug(f"{args['symbol']} {order_type} order response: {resp}")
        return resp

    def place_both_orders(self):
        try:
            # Place buy and sell orders with helper function
            self.dct["buy_id"] = self._place_order("buy_args", "BUY")
            self.dct["sell_id"] = self._place_order("sell_args", "SELL")

            # Set the next function
            self.dct["fn"] = self.move_initial_stop
            self.message = f"buy and sell orders placed for {self.dct['tsym']}"

        except Exception as e:
            fn_name = self.dct.pop("fn", None)  # Remove fn on error
            self.message = (
                f"{self.dct['tsym']} encountered error '{e}' in function {fn_name}"
            )
            logging.error(self.message)
            print_exc()
            self.dct["fn"] = None  # Reset fn pointer on failure

    """ 
      2.  move initial stop 
    """

    def move_initial_stop(self):
        try:
            high = float(self.dct["h"])
            low = float(self.dct["l"])
            half = float_2_curr((high - low) / 2)

            # Determine if this is a "buy" or "sell" entry is complete
            #
            for entry_type in ["buy", "sell"]:
                if self._is_buy_or_sell(entry_type):
                    self.dct["entry"] = entry_type
                    opp_entry_type = "sell" if entry_type == "buy" else "sell"

                    # Set stop price and args based on entry type
                    stop_now = (
                        float_2_curr(low - half - (high - low))
                        if entry_type == "buy"
                        else float_2_curr(high + half + (high - low))
                    )
                    order_id = f"{opp_entry_type}_id"
                    args_dict = f"{opp_entry_type}_args"
                    self.message = f'{entry_type} NEW stop {stop_now} is going to replace INITIAL stop {self.dct["stop_price"]}'
                    self._modify_order(order_id, args_dict, stop_now)
                    self.dct["fn"] = self.move_breakeven

                    # Get candles and set trailing condition
                    candles_now = self._get_history()
                    if entry_type == "buy":
                        self.dct["candle_two"] = max(
                            candles_now[-3][2], candles_now[-2][2]
                        )
                        self.dct["can_trail"] = (
                            lambda c: c["last_price"] > c["candle_two"]
                        )
                    else:
                        self.dct["candle_two"] = min(
                            candles_now[-3][3], candles_now[-2][3]
                        )
                        self.dct["can_trail"] = (
                            lambda c: c["last_price"] < c["candle_two"]
                        )

        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while is_buy_or_sell"
            logging.error(self.message)
            print_exc()

    """
        3. Move to Breakeven
    """

    def _set_trailing_stoploss(self, candles_now):
        """Helper function to set trailing stop loss."""
        try:
            if not any(candles_now):
                candles_now = self._get_history()
            arr_candles = np.array(candles_now)
            if arr_candles.shape[0] >= 3:
                self.candle_start = arr_candles.shape[0] - 3

                self.dct["l"], self.dct["h"] = find_extremes(candles_now)
                # Determine trailing conditions based on entry type

                if self.dct["entry"] == "buy":
                    stop_now, order_id, args_dict = (
                        min(candles_now[-3][3], candles_now[-2][3]),
                        "sell_id",
                        "sell_args",
                    )
                    self.dct["can_trail"] = lambda c: c["last_price"] > c["h"]
                else:
                    stop_now, order_id, args_dict = (
                        max(candles_now[-3][2], candles_now[-2][2]),
                        "buy_id",
                        "buy_args",
                    )
                    self.dct["can_trail"] = lambda c: c["last_price"] < c["l"]

                # Update arguments and log the change
                self.message = f'{self.dct["entry"]} BREAKEVEN {stop_now} will replace {self.dct["stop_price"]}'
                self._modify_order(order_id, args_dict, stop_now)
        except Exception as e:
            logging.error(f"Error while setting trailing stop: {e}")

    def move_breakeven(self):
        try:
            # Determine operation type based on entry
            operation = "sell" if self.dct["entry"] == "buy" else "buy"

            # check if stop loss is already hit
            if self._is_order_complete(operation):
                return

            candles_now = self._get_history(pdlm.now() > self.next_check)
            if any(candles_now):
                if operation == "sell":  # stop order is sell
                    temp = max(candles_now[-3][2], candles_now[-2][2])
                    if temp < self.dct["candle_two"]:
                        self.dct["candle_two"] = temp
                else:  # stop order is buy
                    temp = min(candles_now[-3][3], candles_now[-2][3])
                    if temp > self.dct["candle_two"]:
                        self.dct["candle_two"] = temp

            if self.dct["can_trail"](self.dct):
                # assign condtion for next function
                self._set_trailing_stoploss(candles_now)
                # assign next function
                self.dct["fn"] = self.trail_stoploss
                return

            # operation opposite here
            condition = "<" if operation == "buy" else ">"
            logging.info(
                f'{self.dct["last_price"]} is not {condition} {self.dct["candle_two"]} for {self.dct["tsym"]}'
            )
        except Exception as e:
            self.message = f'{self.dct["tsym"]} encountered {e} while move_breakeven'
            logging.error(self.message)
            print_exc()

    """
        4. trail stoploss
    """

    def _update_buy_stop(self, candles_now):
        """Helper to update the buy stop loss."""
        stop_now, highest = find_buy_stop(candles_now)
        if stop_now and stop_now > self.dct["stop_price"]:
            self.message = f"TRAILING {stop_now} will replace {self.dct['stop_price']}"
            stop_now = float_2_curr(stop_now)
            args = {
                "orderid": self.dct["sell_id"],
                "price": stop_now - 0.10,
                "triggerprice": stop_now - 0.05,
            }
            self.dct["sell_args"].update(args)
            self.dct["h"] = highest
            self.dct["stop_price"] = stop_now
            args = self.dct["sell_args"]
            return args
        return {}

    def _update_sell_stop(self, candles_now):
        """Helper to update the sell stop loss."""
        stop_now, lowest = find_sell_stop(candles_now)
        if stop_now and stop_now < self.dct["stop_price"]:
            self.message = f"TRAILING {stop_now} will replace {self.dct['stop_price']}"
            stop_now = float_2_curr(stop_now)
            args = {
                "orderid": self.dct["buy_id"],
                "price": stop_now + 0.10,
                "triggerprice": stop_now + 0.05,
            }
            self.dct["buy_args"].update(args)
            self.dct["l"] = lowest
            self.dct["stop_price"] = stop_now
            args = self.dct["buy_args"]
            return args
        return {}

    def _is_trailable(self, candles_now):
        try:
            if self.dct["entry"] == "buy":
                return self._update_buy_stop(candles_now)
            elif self.dct["entry"] == "sell":
                return self._update_sell_stop(candles_now)

            return {}

        except Exception as e:
            self.message = (
                f"{self.dct['tsym']} encountered error '{e}' in  is_trailable"
            )
            logging.error(self.message)
            print_exc()

    def trail_stoploss(self):
        """
        if candles  count is changed and then check ltp
        """
        try:
            # check if stop loss is already hit
            operation = "sell" if self.dct["entry"] == "buy" else "buy"
            if self._is_order_complete(operation):
                return

            candles_now = self._get_history(pdlm.now() > self.next_check)
            if any(candles_now):
                candles_now = candles_now[self.candle_start :]
                pprint(candles_now)
                self.dct["l"], self.dct["h"] = find_extremes(candles_now)

                """Determine if conditions meet for modifying the trailing stop loss."""
                if self.dct["can_trail"](self.dct):
                    print(
                        f"{self.dct['last_price']} is a breakout for {self.dct['tsym']}"
                    )
                    args = self._is_trailable(candles_now)
                    if any(args):
                        logging.debug(f"Order modification parameters: {args}")
                        resp = Helper.api.order_modify(**args)
                        logging.debug(f"Order modification response: {resp}")
                        self.candle_count = len(candles_now)

        except Exception as e:
            self.message = f"{self.dct['tsym']} encountered {e} while trailing stop"
            logging.error(self.message)
            print_exc()

    def run(self, lst_of_orders, dct_of_ltp, CANDLE_OTHER):
        try:
            if isinstance(lst_of_orders, list):
                self.dct_of_orders = {
                    dct["orderid"]: dct for dct in lst_of_orders if "orderid" in dct
                }
            self.dct["last_price"] = dct_of_ltp.get(
                self.dct["token"], self.dct["last_price"]
            )

            if self.dct["fn"] is not None:
                message = dict(
                    symbol=self.dct["tsym"],
                    low=self.dct["l"],
                    high=self.dct["h"],
                    last_price=self.dct["last_price"],
                    stop_loss=self.dct["stop_price"],
                    next_fn=self.dct["fn"],
                    candle_two=self.dct["candle_two"],
                    candle_start=self.candle_start,
                    candle_count=self.candle_count,
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

from traceback import print_exc

import pendulum as pdlm
from toolkit.kokoo import is_time_past, kill_tmux, timer
from __init__ import O_SETG, logging
from api import Helper
from strategy import Breakout
from universe import stocks_in_play
from history import get_candles
from exit_and_go import run


def exch_token(params):
    try:
        exch_token_dict = {}
        # create list of tokens
        lst = [v for v in params.values()]
        exch = lst[0]["exchange"]
        lst = [dct["token"] for dct in lst]
        exch_token_dict = {exch: lst}
        return exch_token_dict
    except Exception as e:
        print_exc()
        logging.error(f"{e} while creating exch_token_dict")


def get_ltp(params):
    try:
        exch_token_dict = exch_token(params)
        new_dct = {}
        resp = Helper.api.obj.getMarketData("LTP", exch_token_dict)
        lst_of_dict = resp["data"]["fetched"]
        new_dct = {dct["symbolToken"]: dct["ltp"] for dct in lst_of_dict}
    except Exception as e:
        print(f"while getting ltp {e}")
    finally:
        return new_dct


def main():
    try:
        df = stocks_in_play()
        while not is_time_past(O_SETG["start"]):
            print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", O_SETG["start"])
            timer(1)
        else:
            print("HAPPY TRADING")

        params = get_candles(df)

        # create strategy object
        lst = []
        if O_SETG["mode"] == 0:
            for _, param in params.items():
                lst.append(Breakout(param))

        while not is_time_past(O_SETG["stop"]):
            resp = Helper.api.orders
            lst_of_orders = []
            if isinstance(resp, dict):
                lst_of_orders = resp.get("data", [])
            dct_of_ltp = get_ltp(params)
            for obj in lst:
                obj.run(lst_of_orders, dct_of_ltp)
        else:
            run()
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

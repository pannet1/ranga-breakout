from traceback import print_exc

import pendulum as pdlm
from toolkit.kokoo import is_time_past, kill_tmux, timer
from __init__ import O_SETG, logging
from api import Helper
from strategy import Breakout
from universe import stocks_in_play
from history import get_candles
from exit_and_go import cancel_all_orders, close_all_positions
from typing import List, Dict


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
        new_dct = {}
        exch_token_dict = exch_token(params)
        resp = Helper.api.obj.getMarketData("LTP", exch_token_dict)
        lst_of_dict = resp["data"]["fetched"]
        new_dct = {dct["symbolToken"]: dct["ltp"] for dct in lst_of_dict}
    except Exception as e:
        print(f"while getting ltp {e}")
    finally:
        return new_dct


def get_params():
    df = stocks_in_play()
    while not is_time_past(O_SETG["start"]):
        print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", O_SETG["start"])
        timer(1)
    else:
        print("HAPPY TRADING")

    return get_candles(df)


def main():
    try:
        params = get_params()
        # create strategy object
        if O_SETG["mode"] == 0:
            strategies = [Breakout(param) for param in params.values()]

        while not is_time_past(O_SETG["stop"]):
            for obj in strategies:
                obj.run(Helper.orders, get_ltp(params))
        else:
            cancel_all_orders()
            close_all_positions()
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

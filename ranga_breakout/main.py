from traceback import print_exc

import pendulum as pdlm
from toolkit.kokoo import is_time_past, kill_tmux, timer
from __init__ import O_SETG, logging
from api import Helper
from strategy import Breakout
from universe import stocks_in_play
from history import get_candles


def get_ltp(lst_of_tokens):
    try:
        new_dct = {}
        params = {"NFO": lst_of_tokens}
        resp = Helper.api.obj.getMarketData("LTP", params)
        lst_of_dict = resp["data"]["fetched"]
        new_dct = {dct["symbolToken"]: dct["ltp"] for dct in lst_of_dict}
    except Exception as e:
        print(f"while getting ltp {e}")
    finally:
        return new_dct


def main():
    try:
        Helper.set_token()
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

        # create list of tokens
        lst_of_tokens = [v["token"] for v in params.values()]

        while not is_time_past(O_SETG["stop"]):
            resp = Helper.api.orders
            lst_of_orders = []
            if isinstance(resp, dict):
                lst_of_orders = resp.get("data", [])
            dct_of_ltp = get_ltp(lst_of_tokens)
            for obj in lst:
                obj.run(lst_of_orders, dct_of_ltp)
        else:
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

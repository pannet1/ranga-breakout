from traceback import print_exc

import pendulum as pdlm
from toolkit.kokoo import is_time_past, kill_tmux, timer
from __init__ import O_SETG, logging
from api import Helper
from strategy import Breakout
from universe import stocks_in_play
from history import get_candles
from exit_and_go import cancel_all_orders, close_all_positions


def exch_token(params):
    try:
        lst = [v for v in params.values()]
        exch = lst[0]["exchange"]
        lst_of_tokens = [dct["token"] for dct in lst]
        return exch, lst_of_tokens
    except Exception as e:
        print(e)


def get_ltp(params: dict) -> dict:
    try:
        new_dct = {}
        exch, lst_of_tokens = exch_token(params)

        # Batch the tokens into chunks of 50
        batch_size = 50
        for i in range(0, len(lst_of_tokens), batch_size):
            timer(1)
            token_batch: list = lst_of_tokens[i : i + batch_size]
            exch_token_dict = {exch: token_batch}

            # Fetch LTP for the current batch
            resp = Helper.api.obj.getMarketData("LTP", exch_token_dict)
            lst_of_dict = resp["data"]["fetched"]

            if isinstance(lst_of_dict, list):
                # Update the dictionary with the current batch's LTPs
                new_dct.update({dct["symbolToken"]: dct["ltp"] for dct in lst_of_dict})
    except Exception as e:
        print(f"Error while getting LTP: {e}")
    finally:
        return new_dct


def get_params():
    try:
        args = __import__("sys").argv[1:]
        is_cash = True if len(args) > 0 else False
        df = stocks_in_play(is_cash)
        while not is_time_past(O_SETG["start"]):
            print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", O_SETG["start"])
            timer(0.5)
        else:
            print("HAPPY TRADING")

        return get_candles(df, "9:45")
    except Exception as e:
        print(f"{e} while getting parameters")


def main():
    try:
        logging.info("running breakout")
        CANDLE_OTHER = 2
        Helper.api
        params: dict = get_params()
        # create strategy object
        strategies = [Breakout(param) for param in params.values()]

        while not is_time_past(O_SETG["stop"]):
            for obj in strategies:
                obj.run(Helper.orders, get_ltp(params), CANDLE_OTHER)
                CANDLE_OTHER = obj.candle_count
                print("last message: ", obj.message)

            # Remove objects with no function after processing
            strategies = [obj for obj in strategies if obj.dct["fn"] is not None]
        else:
            cancel_all_orders()
            close_all_positions()
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

from traceback import print_exc
from typing import Any  # Importing only the required types

import pendulum as pdlm
from toolkit.kokoo import dt_to_str, is_time_past, kill_tmux, timer

from __init__ import O_SETG, SFX, logging
from api import Helper
from decorator import retry
from strategy import Breakout
from universe import stocks_in_play


def get_historical_data(historic_param: dict[str, Any]) -> Any:
    try:
        data = []

        @retry(max_attempts=3)
        def fetch_data(param: dict[str, Any]) -> Any:
            timer(1)
            return Helper.api.obj.getCandleData(param)

        data = fetch_data(historic_param)
    except Exception as e:
        logging.error(f"{e} while getting historical data")
        print_exc()
    finally:
        return data


def get_candles(df: Any) -> dict[str, dict[str, Any]]:
    try:
        candles = {}

        for _, row in df.iterrows():
            historic_param = {
                "exchange": "NFO",
                "symboltoken": row["token"],
                "interval": "THIRTY_MINUTE",
                "fromdate": "2024-08-09 09:15",
                "todate": dt_to_str(""),
            }
            resp = get_historical_data(historic_param)
            if resp is not None and any(resp) and any(resp[0]):
                candles[row["symbol"]] = format_candle_data(row, resp[0])
                logging.info(f'getting candles for: {row["symbol"]}')
    except Exception as e:
        logging.error(f"{e} while getting candles")
        print_exc()
    finally:
        return candles


def format_candle_data(row: Any, data: list[list[Any]]) -> dict[str, Any]:
    return {
        "tsym": row["symbol"] + SFX,
        "dt": data[0],
        "o": data[1],
        "h": data[2],
        "l": data[3],
        "c": data[4],
        "quantity": row["quantity"],
        "token": row["token"],
    }


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
        lst = []
        if O_SETG["mode"] == 0:
            for _, param in params.items():
                lst.append(Breakout(param))

        while not is_time_past(O_SETG["stop"]):
            lst_of_orders = Helper.api.orders
            for obj in lst:
                obj.run(lst_of_orders)
        else:
            kill_tmux()
    except Exception as e:
        print_exc()
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

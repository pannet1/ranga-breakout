from traceback import print_exc
from typing import Any  # Importing only the required types

import pendulum as pdlm
from toolkit.kokoo import dt_to_str, is_time_past, kill_tmux, timer

from __init__ import O_FUTL, O_SETG, S_STOPS, SFX, logging
from api import Helper
from decorator import retry
from strategy import Strategy
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


def get_candles(df: Any) -> dict[str, dict[str, Any]]:
    try:
        Helper.set_token()
        candles = {}

        for _, row in df.iterrows():
            historic_param = {
                "exchange": "NFO",
                "symboltoken": row["token"],
                "interval": "THIRTY_MINUTE",
                "fromdate": dt_to_str("09:15"),
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


def place_orders(dct: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    lst_stops = []
    for _, ohlc in dct.items():
        buy_args = create_order_args(
            ohlc, "BUY", float(ohlc["h"]) + 0.10, float(ohlc["h"]) + 0.05
        )
        sell_args = create_order_args(
            ohlc, "SELL", float(ohlc["l"]) - 0.10, float(ohlc["l"]) - 0.05
        )
        if O_SETG["mode"] >= 0:
            logging.debug(buy_args)
            resp = Helper.api.order_place(**buy_args)
            logging.info(f"{buy_args['symbol']} {buy_args['side']} got {resp=}")
        if O_SETG["mode"] <= 0:
            logging.debug(sell_args)
            resp = Helper.api.order_place(**sell_args)
            logging.info(f"{sell_args['symbol']} {sell_args['side']} got {resp=}")
        if O_SETG["mode"] == -1:
            lst_stops.append(buy_args)
        elif O_SETG["mode"] == 1:
            lst_stops.append(sell_args)
    return lst_stops


def main():
    df = stocks_in_play()

    while not is_time_past(O_SETG["start"]):
        print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", O_SETG["start"])
        timer(1)
    else:
        print("HAPPY TRADING")

    try:
        dct = get_candles(df)
    except Exception as e:
        logging.error(f"{e} while getting candles")

    try:
        lst_stops = place_orders(dct)
    except Exception as e:
        logging.error(f"{e} while placing orders")

    try:
        if any(lst_stops):
            O_FUTL.write_file(S_STOPS, lst_stops)
    except Exception as e:
        logging.error(f"{e} while writing file")

    try:
        Sgy = Strategy(Helper.api)
        while not is_time_past(O_SETG["stop"]) and Sgy.is_set:
            Sgy.run()
        kill_tmux()
    except Exception as e:
        logging.error(f"{e} while running strategy")


if __name__ == "__main__":
    main()

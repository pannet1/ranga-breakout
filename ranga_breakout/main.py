from __init__ import logging, SFX, O_SETG, O_FUTL, S_STOPS
from universe import stocks_in_play
from api import Helper
import pendulum as pdlm
from toolkit.kokoo import is_time_past, dt_to_str, blink, timer, kill_tmux
from decorator import retry
from strategy import Strategy

lst_stops = []


def get_candles(df):
    @retry(max_attempts=3)
    def history(historicParam):
        timer(1)
        resp = Helper.api.obj.getCandleData(historicParam)
        if resp and any(resp):
            return resp

    dct = {}
    for _, row in df.iterrows():
        historicParam = {
            "exchange": "NFO",
            "symboltoken": row["token"],
            "interval": "THIRTY_MINUTE",
            "fromdate": dt_to_str("09:15"),
            "todate": dt_to_str(""),
        }
        resp = history(historicParam)
        if resp and any(resp):
            data = resp
            dct[row["symbol"]] = [
                {
                    "tsym": row["symbol"] + SFX,
                    "dt": i[0],
                    "o": i[1],
                    "h": i[2],
                    "l": i[3],
                    "c": i[4],
                }
                for i in data[:1]
            ][0]
            print("getting candles for:", dct[row["symbol"]])
            dct[row["symbol"]].update(
                {"quantity": row["quantity"], "token": row["token"]}
            )
    return dct


def place_orders(ohlc):
    args = dict(
        symbol=ohlc["tsym"],
        exchange="NFO",
        order_type="STOPLOSS_MARKET",
        product="INTRADAY",  # CARRYFORWARD,INTRADAY
        quantity=ohlc["quantity"],
        symboltoken=ohlc["token"],
        variety="STOPLOSS",
        duration="DAY",
    )
    bargs = args.copy()
    sargs = args.copy()

    bargs["side"] = "BUY"
    bargs["price"] = float(ohlc["h"]) + 0.10
    bargs["trigger_price"] = float(ohlc["h"]) + 0.05

    sargs["side"] = "SELL"
    sargs["price"] = float(ohlc["l"]) - 0.10
    sargs["trigger_price"] = float(ohlc["l"]) - 0.05

    if O_SETG["mode"] >= 0:
        logging.debug(bargs)
        resp = Helper.api.order_place(**bargs)
        logging.info(f"{bargs['symbol']} {bargs['side']} got {resp=}")
    elif O_SETG["mode"] <= 0:
        logging.debug(sargs)
        resp = Helper.api.order_place(**sargs)
        logging.info(f"{sargs['symbol']} {sargs['side']} got {resp=}")

    if O_SETG["mode"] == -1:
        lst_stops.append(bargs)
    elif O_SETG["mode"] == 1:
        lst_stops.append(sargs)


def main():
    df = stocks_in_play()

    while not is_time_past(O_SETG["start"]):
        blink()
        print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", O_SETG["start"])
        blink()
    else:
        print("HAPPY TRADING")

    Helper.set_token()
    try:
        dct = get_candles(df)
    except Exception as e:
        logging.error(f"{e} while getting candles")

    for _, v in dct.items():
        place_orders(v)
        blink()

    if any(lst_stops):
        O_FUTL.write_file(S_STOPS, lst_stops)

    Sgy = Strategy(Helper.api)
    try:
        while not is_time_past(O_SETG["stop"]) and Sgy.is_set:
            Sgy.run()
            blink()
        else:
            kill_tmux()
    except Exception as e:
        logging.error(f"{e} while running strategy")


main()

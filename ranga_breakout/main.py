from __init__ import logging, CNFG, S_UNIV, S_OUT
from symbol import Symbol
from login import get_token
import pandas as pd
import pendulum as pdlm
from toolkit.kokoo import is_time_past, dt_to_str, blink
import traceback
from api_helper import retry

T_START = "9:45"
T_STOP = "3:28"
sfx = "FUT"


def write_to_csv(O_SYM):
    try:
        df = pd.read_csv(S_UNIV).dropna(axis=0).drop(["enable"], axis=1)
        for index, row in df.iterrows():
            exch = "NFO"
            symbol = row["symbol"].replace(" ", "").upper()
            tkn = O_SYM.get_tkn_fm_sym(symbol + sfx, exch)
            df.loc[index, "token"] = tkn
            df.loc[index, "symbol"] = symbol
        df = df[df["token"] != "0"]
        df.to_csv(S_OUT, index=False)
    except Exception as e:
        logging.error(e)
        traceback.print_exc()


def get_candles(api, df):
    @retry(max_attempts=3)
    def history(historicParam):
        resp = api.obj.getCandleData(historicParam)
        if resp and any(resp):
            return resp

    dct = {}
    for _, row in df.iterrows():
        historicParam = {
            "exchange": "NFO",
            "symboltoken": row["token"],
            "interval": "THIRTY_MINUTE",
            "fromdate": "2024-04-29 09:15",
            "todate": dt_to_str(""),
        }
        resp = history(historicParam)
        if resp and any(resp):
            data = resp
            dct[row["symbol"]] = [
                {
                    "tsym": row["symbol"] + sfx,
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
        blink()
    return dct


def place_orders(api, ohlc):
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
    args["side"] = "BUY"
    args["price"] = float(ohlc["h"]) + 0.10
    args["trigger_price"] = float(ohlc["h"]) + 0.05
    resp = api.order_place(**args)
    logging.info(resp)
    args["side"] = "SELL"
    args["price"] = float(ohlc["l"]) - 0.10
    args["trigger_price"] = float(ohlc["l"]) - 0.05
    resp = api.order_place(**args)
    logging.info(resp)


def main():
    api = get_token(CNFG)
    O_SYM = Symbol()

    write_to_csv(O_SYM)
    df = pd.read_csv(S_OUT)
    print(df)

    while not is_time_past(T_START):
        blink()
        print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", T_START)
        blink()
    else:
        print("HAPPY TRADING")

    try:
        dct = get_candles(api, df)
    except Exception as e:
        logging.error(f"{e} while getting candles")

    for _, v in dct.items():
        place_orders(api, v)
        blink()


main()

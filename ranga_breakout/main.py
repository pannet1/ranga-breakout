from __init__ import logging, CNFG, S_UNIV, S_OUT, S_EXPIRY, O_UTIL
from symbol import Symbol
from api_helper import login
import pandas as pd
import pendulum as pdlm
from clock import is_time_past, dt_to_str
import traceback

sfx = S_EXPIRY + "FUT"
T_START = "9:45"
T_STOP = "3:28"


def write_to_csv(O_SYM):
    try:
        df = pd.read_csv(S_UNIV).dropna(axis=0).drop(["enable"], axis=1)
        for index, row in df.iterrows():
            exch = "NFO"
            symbol = row["symbol"].strip()
            tkn = O_SYM.get_tkn_fm_sym(symbol + sfx, exch)
            df.loc[index, "token"] = tkn
        df = df[df["token"] != "0"]
        df.to_csv(S_OUT, index=False)
    except Exception as e:
        logging.error(e)
        traceback.print_exc()


def get_candles(api, df):
    try:
        dct = {}
        for _, row in df.iterrows():
            historicParam = {
                "exchange": "NFO",
                "symboltoken": row["token"],
                "interval": "THIRTY_MINUTE",
                "fromdate": dt_to_str("9:15"),
                "todate": dt_to_str(),
            }
            data = api.obj.getCandleData(historicParam)["data"]
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
            O_UTIL.slp_til_nxt_sec()
    except Exception as e:
        logging.error(f"while getting candles {e}")
        traceback.print_exc()
    finally:
        return dct


def place_orders(api, ohlc):
    args = dict(
        symbol=ohlc["tsym"],
        side="BUY",
        exchange="NFO",
        order_type="STOPLOSS_MARKET",
        product="INTRADAY",  # CARRYFORWARD,INTRADAY
        price=float(ohlc["h"]) + 0.05,
        trigger_price=ohlc["h"],
        quantity=ohlc["quantity"],
        symboltoken=ohlc["token"],
        variety="STOPLOSS",
        duration="DAY",
    )
    api.order_place(**args)
    args["side"] = "SELL"
    args["price"] = float(ohlc["l"]) - 0.05
    args["trigger_price"] = ohlc["l"]
    api.order_place(**args)


def main():
    api = login(CNFG)
    O_SYM = Symbol()

    write_to_csv(O_SYM)
    df = pd.read_csv(S_OUT)
    print(df)

    while not is_time_past(T_START):
        O_UTIL.slp_til_nxt_sec()
        print("clock:", pdlm.now().format("HH:mm:ss"), "zzz ", T_START)
        O_UTIL.slp_til_nxt_sec()
    else:
        print("HAPPY TRADING")

    try:
        dct = get_candles(api, df)
    except Exception as e:
        logging.error(f"{e} while getting candles")

    for _, v in dct.items():
        place_orders(api, v)


main()

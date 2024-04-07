from __init__ import logging, CNFG, S_UNIV, S_OUT, S_EXPIRY
from symbol import Symbol
from api_helper import login
import pandas as pd
import traceback
import pendulum as pdlm

sfx = S_EXPIRY + "FUT"


def read(O_SYM):
    df = pd.read_csv(S_UNIV).dropna(axis=0).drop(['enable'], axis=1)
    for index, row in df.iterrows():
        exch = "NFO"
        tkn = O_SYM.get_tkn_fm_sym(row['symbol'] + sfx, exch)
        df.loc[index, 'token'] = tkn
    df.to_csv(S_OUT, index=False)
    print(df)


def get_candles(api, df):
    dct = {}
    for _, row in df.iterrows():
        historicParam = {
            "exchange": "NFO",
            "symboltoken": row['token'],
            "interval": "THIRTY_MINUTE",
            "fromdate": "2024-04-05 09:15",
            "todate": "2024-04-05 09:45"
        }
        data = api.obj.getCandleData(historicParam)['data']
        dct[row['symbol']] = [{"tsym": row['symbol'] + sfx, "dt": i[0],
                               "o": i[1], "h": i[2], "l": i[3], "c": i[4]}
                              for i in data[:1]][0]
        dct[row['symbol']].update(
            {"quantity": row['quantity'], "token": row['token']})
    return dct


def place_orders(api, ohlc):
    args = dict(
        symbol=ohlc['tsym'],
        side="BUY",
        exchange="NFO",
        order_type="STOPLOSS_LIMIT",
        product="INTRADAY",  # CARRYFORWARD,INTRADAY
        price=ohlc['h'],
        trigger_price=float(ohlc['h']) - 0.05,
        quantity=ohlc['quantity'],
        symboltoken=ohlc['token'],
        variety="STOPLOSS",
        duration="DAY",
    )
    api.order_place(**args)
    args["side"] = "SELL"
    args["price"] = ohlc['l']
    args["trigger_price"] = float(ohlc['l']) + 0.05
    api.order_place(**args)


def main():
    api = login(CNFG)
    O_SYM = Symbol()

    read(O_SYM)
    df = pd.read_csv(S_OUT)

    # check if pendulum time is greater than 9:45:00

    pdlm.now()
    print("no candles found")

    # pdlm.now() > "2024-04-05 09:45:00":
    try:
        dct = get_candles(api, df)
    except Exception as e:
        logging.error(f"{e} while getting candles")

    for _, v in dct.items():
        place_orders(api, v)


main()

from __init__ import logging, S_OUT, S_CASH, S_FUTURE
from symbol import Symbol
import pandas as pd
from traceback import print_exc


def stocks_in_play(is_cash=False):
    try:
        O_SYM = Symbol()
        S_UNIV = S_CASH if is_cash else S_FUTURE
        df = pd.read_csv(S_UNIV).dropna(axis=0).drop(["enable"], axis=1)
        for index, row in df.iterrows():
            exch = row["exchange"]
            symbol = row["symbol"].replace(" ", "").upper()
            tkn = O_SYM.get_tkn_fm_sym(symbol, exch)
            df.loc[index, "token"] = tkn
            df.loc[index, "symbol"] = symbol
        df = df[df["token"] != "0"]
        df.to_csv(S_OUT, index=False)
        print(df)
        return df
    except Exception as e:
        logging.error(e)
        print_exc()


if __name__ == "__main__":
    stocks_in_play()

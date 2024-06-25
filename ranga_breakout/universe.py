from __init__ import logging, S_UNIV, S_OUT, SFX
from symbol import Symbol
import pandas as pd
from traceback import print_exc


def stocks_in_play():
    try:
        O_SYM = Symbol()
        df = pd.read_csv(S_UNIV).dropna(axis=0).drop(["enable"], axis=1)
        for index, row in df.iterrows():
            exch = "NFO"
            symbol = row["symbol"].replace(" ", "").upper()
            tkn = O_SYM.get_tkn_fm_sym(symbol + SFX, exch)
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

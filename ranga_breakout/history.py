from decorator import retry
from traceback import print_exc
from typing import Any  # Importing only the required types
from __init__ import logging
from toolkit.kokoo import dt_to_str, timer
from api import Helper
import numpy as np


def get_historical_data(historic_param: dict[str, Any]) -> Any:
    try:
        data = []

        @retry(max_attempts=3)
        def fetch_data() -> Any:
            return Helper.api.obj.getCandleData(historic_param)

        data = fetch_data()
    except Exception as e:
        logging.error(f"{e} while getting historical data")
        print_exc()
    finally:
        return data


def format_candle_data(row: Any, data: list[list[Any]]) -> dict[str, Any]:
    return {
        "exchange": row["exchange"],
        "tsym": row["symbol"],
        "h": data[2],
        "l": data[3],
        "c": data[4],
        "quantity": row["quantity"],
        "token": row["token"],
    }


def get_candles(df: Any) -> dict[str, dict[str, Any]]:
    try:
        candles = {}

        for _, row in df.iterrows():
            timer(0.5)
            historic_param = {
                "exchange": row["exchange"],
                "symboltoken": row["token"],
                "interval": "THIRTY_MINUTE",
                "fromdate": dt_to_str("9:15"),
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


def find_buy_stop(candles_data):
    np_data = np.array(candles_data)

    # Convert the "High" and "Low" columns to float
    highs = np_data[:, 2].astype(float)
    lows = np_data[:, 3].astype(float)

    # Find the index of the highest value in the "High" column
    idx = np.argmax(highs)

    # Find the highest value
    extreme = highs[idx]

    # Handle edge case for idx < 2
    if idx >= 2:
        stop = np.min(lows[idx - 2 : idx])  # Take the two previous lows
    else:
        stop = None

    return stop, extreme


def find_sell_stop(candles_data):
    np_data = np.array(candles_data)

    # Convert the "High" and "Low" columns to float
    highs = np_data[:, 2].astype(float)
    lows = np_data[:, 3].astype(float)

    idx = np.argmin(lows)
    extreme = lows[idx]

    if idx >= 2:
        stop = np.max(highs[idx - 2 : idx])
    else:
        stop = None
    return stop, extreme


# Test the find_buy_stop function
if __name__ == "__main__":
    data = [
        ["24-9-2021", 1000, 1002, 999, 4, 2324],
        ["23-9-2021", 5, 20, 8, 23, 23123],
        ["22-9-2021", 23, 100, 4, 7, 123],
        ["21-9-2021", 7, 3000, 2, 5, 123],
    ]

    def test_find_buy_stop(candles_data):
        stop, extreme = find_buy_stop(candles_data)
        assert stop == 4, f"expect 4 got {stop}"
        # extreme is high for buy
        assert extreme == 3000, f"expect 3000 got {extreme}"
        print(f"Test passed! Stop: {stop}, Extreme: {extreme}")
        return stop

    def test_find_sell_stop(candles_data):
        stop, extreme = find_sell_stop(candles_data)
        assert stop == 100, f"expect 100 got {stop}"
        assert extreme == 2, f"expect 2 got {extreme}"
        print(f"Test passed! Stop: {stop}, Extreme: {extreme}")
        return stop

    test_find_buy_stop(data)
    test_find_sell_stop(data)

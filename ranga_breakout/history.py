from decorator import retry
from traceback import print_exc
from typing import Any  # Importing only the required types
from __init__ import logging
from toolkit.kokoo import dt_to_str, timer
from api import Helper


def get_low_high(candles_data):

    # Initialize the lowest low and highest high with the first candle's values
    lowest_low = candles_data[0][3]  # Index 3 for Low
    highest_high = candles_data[0][2]  # Index 2 for High

    # Iterate through the list and update lowest_low and highest_high
    for candle in candles_data:
        if candle[3] < lowest_low:  # Index 3 for Low
            lowest_low = candle[3]
        if candle[2] > highest_high:  # Index 2 for High
            highest_high = candle[2]

    # Store them in a tuple
    low_high_tuple = (lowest_low, highest_high)
    return low_high_tuple


def get_historical_data(historic_param: dict[str, Any]) -> Any:
    try:
        data = []

        @retry(max_attempts=3)
        def fetch_data() -> Any:
            timer(1)
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
            historic_param = {
                "exchange": row["exchange"],
                "symboltoken": row["token"],
                "interval": "THIRTY_MINUTE",
                "fromdate": dt_to_str("9:15"),
                "todate": dt_to_str(""),
            }
            print(historic_param)
            resp = get_historical_data(historic_param)
            if resp is not None and any(resp) and any(resp[0]):
                candles[row["symbol"]] = format_candle_data(row, resp[0])
                logging.info(f'getting candles for: {row["symbol"]}')
    except Exception as e:
        logging.error(f"{e} while getting candles")
        print_exc()
    finally:
        return candles

import pandas as pd


def rank_price_proximity(data):
    """Ranks prices based on proximity to high/low and assigns a unified rank.

    Args:
        data (pd.DataFrame): DataFrame containing columns 'high', 'low', 'current'.

    Returns:
        pd.DataFrame, pd.DataFrame: Two DataFrames, one containing stocks closer to low and the other closer to high.
    """
    data["price_range"] = data["high"] - data["low"]
    data["distance_from_low"] = (
        data["current"] - data["low"]) / data["price_range"]
    data["distance_from_high"] = (
        data["high"] - data["current"]) / data["price_range"]

    # Separate stocks closer to low and high
    low_proximity_data = data[data["distance_from_low"] <= 0.5]
    high_proximity_data = data[data["distance_from_low"] > 0.5]

    # Adjust rank calculation to prioritize stocks with current price lower than low price
    low_proximity_data["rank"] = (
        0.5
        - (low_proximity_data["current"] - low_proximity_data["low"])
        / low_proximity_data["price_range"]
    )
    low_proximity_data.loc[
        low_proximity_data["current"] < low_proximity_data["low"], "rank"
    ] = low_proximity_data["distance_from_low"] - 1

    low_proximity_data["action"] = "sell"

    # Adjust rank calculation to prioritize stocks with current price higher than high price
    high_proximity_data["rank"] = (
        0.5
        - (high_proximity_data["high"] - high_proximity_data["current"])
        / high_proximity_data["price_range"]
    )
    high_proximity_data.loc[
        high_proximity_data["current"] > high_proximity_data["high"], "rank"
    ] = high_proximity_data["distance_from_high"] - 1
    high_proximity_data["action"] = "buy"

    df = pd.concat([low_proximity_data, high_proximity_data], axis=1)
    df.drop(["distance_from_high", "distance_from_low"], axis=1, inplace=True)
    return data


# Sample data with fixed high/low and different current prices
data = pd.DataFrame(
    {
        "high": [100, 100, 100, 100],
        "low": [50, 50, 50, 50],
        "current": [101, 95, 51, 49],
    }
)

low_proximity_data, high_proximity_data = rank_price_proximity(data)
print("Stocks closer to low:")
print(low_proximity_data)
print("\nStocks closer to high:")
print(high_proximity_data)


def rank_price_proximity(data):
    """Ranks prices based on proximity to high/low and assigns a unified rank.

    Args:
        data (pd.DataFrame): DataFrame containing columns 'high', 'low', 'current'.

    Returns:
        pd.DataFrame: DataFrame with an additional 'rank' and 'action' column.
    """
    data["price_range"] = data["high"] - data["low"]
    data["distance_from_low"] = (
        data["current"] - data["low"]) / data["price_range"]
    data["distance_from_high"] = (
        data["high"] - data["current"]) / data["price_range"]

    # Adjust rank calculation to prioritize stocks with current price lower than low price
    data["rank"] = 0.5 - (data["current"] - data["low"]) / data["price_range"]
    data.loc[data["current"] < data["low"],
             "rank"] = data["distance_from_low"] - 1

    data["action"] = "sell"

    # Adjust rank calculation to prioritize stocks with current price higher than high price
    data.loc[data["current"] > data["high"],
             "rank"] = data["distance_from_high"] - 1
    data.loc[data["current"] > data["high"], "action"] = "buy"

    data.drop(["distance_from_high", "distance_from_low"],
              axis=1, inplace=True)

    return data


# Sample data with fixed high/low and different current prices
data = pd.DataFrame(
    {
        "high": [100, 100, 100, 100],
        "low": [50, 50, 50, 50],
        "current": [101, 95, 51, 49],
    }
)

ranked_data = rank_price_proximity(data)
print("Ranked Data:")
print(ranked_data)

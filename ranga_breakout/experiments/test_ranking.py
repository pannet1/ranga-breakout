import pandas as pd


def rank_price_proximity_v1(data):
    """Ranks prices based on proximity to h/l and assigns a unified rank.

    Args:
        data (pd.DataFrame): DataFrame containing columns 'h', 'l', 'c'.

    Returns:
        pd.DataFrame, pd.DataFrame: Two DataFrames, one containing stocks closer to l and the other closer to h.
    """
    data["price_range"] = data["h"] - data["l"]
    data["distance_from_l"] = (data["c"] - data["l"]) / data["price_range"]
    data["distance_from_h"] = (data["h"] - data["c"]) / data["price_range"]

    # Separate stocks closer to l and h
    l_proximity_data = data[data["distance_from_l"] <= 0.5]
    h_proximity_data = data[data["distance_from_l"] > 0.5]

    # Adjust rank calculation to prioritize stocks with c price ler than l price
    l_proximity_data["rank"] = (
        0.5
        - (l_proximity_data["c"] - l_proximity_data["l"])
        / l_proximity_data["price_range"]
    )
    l_proximity_data.loc[l_proximity_data["c"] < l_proximity_data["l"], "rank"] = (
        l_proximity_data["distance_from_l"] - 1
    )

    l_proximity_data["action"] = "sell"

    # Adjust rank calculation to prioritize stocks with c price her than h price
    h_proximity_data["rank"] = (
        0.5
        - (h_proximity_data["h"] - h_proximity_data["c"])
        / h_proximity_data["price_range"]
    )
    h_proximity_data.loc[h_proximity_data["c"] > h_proximity_data["h"], "rank"] = (
        h_proximity_data["distance_from_h"] - 1
    )
    h_proximity_data["action"] = "buy"

    df = pd.concat([l_proximity_data, h_proximity_data], axis=1)
    df.drop(["distance_from_h", "distance_from_l"], axis=1, inplace=True)
    return data


def rank_price_proximity_v2(data):
    """Ranks prices based on proximity to h/l and assigns a unified rank.

    Args:
        data (pd.DataFrame): DataFrame containing columns 'h', 'l', 'c'.

    Returns:
        pd.DataFrame: DataFrame with an additional 'rank' and 'action' column.
    """
    data["price_range"] = data["h"] - data["l"]
    data["distance_from_l"] = (data["c"] - data["l"]) / data["price_range"]
    data["distance_from_h"] = (data["h"] - data["c"]) / data["price_range"]
    # data["rank"] = 0.5 - (data["c"] - data["l"]) / data["price_range"]
    data["rank"] = data["distance_from_h"]
    data.loc[data["distance_from_l"] < data["distance_from_h"], "rank"] = data[
        "distance_from_l"
    ]

    data.loc[data["c"] < data["l"], "rank"] = data["distance_from_l"] - 1
    # data.loc[data["c"] > data["h"], "action"] = "sell"

    data.loc[data["c"] > data["h"], "rank"] = data["distance_from_h"] - 1
    # data.loc[data["c"] > data["h"], "action"] = "buy"

    data.sort_values(by=["rank"], inplace=True)
    data = data.reset_index(drop=True)

    return data


if __name__ == "__main__":

    # Sample data with fixed h/l and different c prices
    data = pd.DataFrame(
        {
            "stock": ["infy", "sbin", "hdfc", "shiva"],
            "h": [100, 100, 100, 100],
            "l": [50, 50, 50, 50],
            "c": [101, 95, 51, 49],
        }
    )
    print(data)

    resp = rank_price_proximity_v2(data)
    print(resp)

import pandas as pd


def rank_price_proximity(data):
    """Ranks prices based on proximity to high/low and assigns a unified rank.

    Args:
        data (pd.DataFrame): DataFrame containing columns 'high', 'low', 'current'.

    Returns:
        pd.DataFrame: DataFrame with an additional 'rank' and 'unified_rank' column.
    """

    data["price_range"] = data["high"] - data["low"]
    data["distance_from_low"] = (data["current"] - data["low"]) / data["price_range"]
    data["distance_from_high"] = (data["high"] - data["current"]) / data["price_range"]
    data["rank"] = data["distance_from_low"] - 0.5

    # Create a temporary categorical column with desired order (high proximity first)
    data["sort_key"] = pd.Categorical(
        data["distance_from_low"].abs() == data["distance_from_low"].abs().max(),
        categories=[1, -1],
    )

    # Sort by the reordered sort_key (high first)
    data = data.sort_values(by="sort_key")
    data = data.sort_values(
        by=["distance_from_low", "distance_from_high"], ascending=[True, True]
    )

    # Assign a unified rank based on the sorted order
    data["unified_rank"] = data.reset_index(drop=True)["rank"] / (len(data))

    return data.drop("sort_key", axis=1)  # Remove temporary sort key column


# Sample data with fixed high/low and different current prices
data = pd.DataFrame(
    {"high": [100, 100, 100, 100], "low": [50, 50, 50, 50], "current": [91, 73, 52, 49]}
)

ranked_data = rank_price_proximity(data.copy())
print(ranked_data)

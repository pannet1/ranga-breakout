import pytest
from history import find_buy_stop


def test_find_buy_stop():
    data = [
        ["24-9-2021", 1, 2, 1, 4, 2324],
        ["23-9-2021", 10, 20, 8, 23, 23123],
        ["22-9-2021", 5, 100, 4, 7, 123],
        ["21-9-2021", 2, 3, 1, 5, 123],
    ]

    # Call the function with test data
    stop, extreme = find_buy_stop(data)

    # Assert the results
    assert stop == 1, f"Expected stop to be 1, got {stop}"
    assert extreme == 100, f"Expected extreme to be 100, got {extreme}"


# You can add more test cases to cover edge cases
def test_find_buy_stop_edge_case():
    data = [
        ["24-9-2021", 1, 2, 1, 4, 2324],
    ]

    # Call the function with a single row of data
    stop, extreme = find_buy_stop(data)

    # Assert the results for the edge case
    assert stop == 1, f"Expected stop to be 1, got {stop}"
    assert extreme == 2, f"Expected extreme to be 2, got {extreme}"

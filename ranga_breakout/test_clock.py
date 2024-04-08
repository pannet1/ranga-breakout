from .clock import is_time_past, dt_to_str
import pendulum as pdlm


def test_is_time_past():
    """ Checks if the current Pendulum time is past the given hour, minute, second"""
    assert is_time_past("9")
    assert is_time_past("9:15")
    assert is_time_past("9:15:00")

    # Test edge cases
    assert is_time_past("0:0:0")  # midnight
    assert is_time_past("12:0:0")  # noon

    # Test invalid inputs
    assert not is_time_past("24:0:0")  # hour out of range
    assert not is_time_past("9:60:0")  # minute out of range
    assert not is_time_past("9:15:60")  # second out of range


def test_dt_to_str():
    """Converts replace h,m,s to now"""
    now = pdlm.now().replace(hour=19, minute=15, second=0).format("YYYY-MM-DD HH:mm")
    assert dt_to_str("19") == now
    assert dt_to_str("19:15") == now
    assert dt_to_str("19:15:00") == now

import pendulum as pdlm


def is_time_past(hour, minute, second):
    """Checks if the current Pendulum time is after 9:15:00."""
    current_time = pdlm.now()
    if current_time.hour < hour:
        return False
    if current_time.minute < minute:
        return False
    if current_time.second < second:
        return False
    return True


def dt_to_str(kwargs):
    """Converts replace h,m,s to now"""
    now = pdlm.now()
    if (hour := kwargs.get("hour", None)) is not None:
        now = now.replace(hour=hour)
    if (minute := kwargs.get("minute", None)) is not None:
        now = now.replace(minute=minute)
    if (second := kwargs.get("second", None)) is not None:
        now = now.replace(second=second)
    return now.format("YYYY-MM-DD HH:mm")


if __name__ == "__main__":
    if is_time_past(21, 15, 0):
        print("Pendulum time is after 9:15:00")
    else:
        print("Pendulum time is before or at 9:15:00")

    print(dt_to_str({"hour": 4, "minute": 0, "second": 0}))
    print(dt_to_str({}))

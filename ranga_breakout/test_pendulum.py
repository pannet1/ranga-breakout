from pendulum import now


def is_time_past(hour, minute, second):
    """Checks if the current Pendulum time is after 9:15:00."""
    current_time = now()
    if current_time.hour < hour:
        return False
    if current_time.minute < minute:
        return False
    if current_time.second < second:
        return False
    return True


if __name__ == "__main__":
    if is_time_past(21, 15, 0):
        print("Pendulum time is after 9:15:00")
    else:
        print("Pendulum time is before or at 9:15:00")

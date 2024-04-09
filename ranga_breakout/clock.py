import pendulum as pdlm


def is_time_past(time_str):
    # Parse the given time string
    tz = "Asia/Kolkata"
    given_time = pdlm.parse(time_str, tz=tz)
    current_time = pdlm.now(tz=tz)
    return current_time > given_time


def dt_to_str(str_time=None):
    """Converts replace h,m,s to now"""
    current_time = pdlm.now()
    if str_time:
        hour = minute = second = 0
        lst = str_time.split(":")

        if len(lst) == 3:
            hour = int(lst[0])
            minute = int(lst[1])
            second = int(lst[2])
        elif len(lst) == 2:
            hour = int(lst[0])
            minute = int(lst[1])
        elif len(lst) == 1:
            hour = int(lst[0])

        if hour > 0:
            current_time = current_time.replace(hour=hour)
        if minute > 0:
            current_time = current_time.replace(minute=minute)
        if second > 0:
            current_time = current_time.replace(second=second)
    return current_time.format("YYYY-MM-DD HH:mm")

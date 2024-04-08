import pendulum as pdlm


def is_time_past(str_time):
    """Checks if the current Pendulum time is past the given hour, minute, second"""
    hour = minute = second = 0
    lst = str_time.split(':')

    if len(lst) == 3:
        hour = int(lst[0])
        minute = int(lst[1])
        second = int(lst[2])
    elif len(lst) == 2:
        hour = int(lst[0])
        minute = int(lst[1])
    elif len(lst) == 1:
        hour = int(lst[0])

    current_time = pdlm.now()
    if current_time.hour < hour:
        return False
    if current_time.minute < minute:
        return False
    if current_time.second < second:
        return False
    return True


def dt_to_str(str_time):
    """Converts replace h,m,s to now"""
    hour = minute = second = 0
    lst = str_time.split(':')

    if len(lst) == 3:
        hour = int(lst[0])
        minute = int(lst[1])
        second = int(lst[2])
    elif len(lst) == 2:
        hour = int(lst[0])
        minute = int(lst[1])
    elif len(lst) == 1:
        hour = int(lst[0])

    current_time = pdlm.now()
    if hour > 0:
        current_time = current_time.replace(hour=hour)
    if minute > 0:
        current_time = current_time.replace(minute=minute)
    if second > 0:
        current_time = current_time.replace(second=second)
    return current_time.format("YYYY-MM-DD HH:mm")

from datetime import date, timedelta


def get_date_range(range_type: str):
    today = date.today()

    if range_type == "THIS_WEEK":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)

    elif range_type == "LAST_WEEK":
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)

    elif range_type == "THIS_MONTH":
        start = today.replace(day=1)
        end = today

    elif range_type == "LAST_MONTH":
        first_day = today.replace(day=1)
        last_month_end = first_day - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = last_month_end

    else:
        raise ValueError("Invalid range")

    return start, end

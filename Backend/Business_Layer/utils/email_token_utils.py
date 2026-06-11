from datetime import datetime
import random
import secrets
import itertools
import hashlib


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_mixed_month_time_token() -> str:
    """
    Example output:
    S0e9P3t1e4m2b5e7rA9

    - Letters come from the current month name
    - Digits come from HHMMSS
    - Mixed together
    - Random letter added to avoid collisions
    """
    now = datetime.utcnow()

    month_letters = list(
        now.strftime("%B")
    )  # e.g. ['S','e','p','t','e','m','b','e','r']
    time_digits = list(now.strftime("%H%M%S"))  # e.g. ['1','4','3','0','5','9']
    date_month_year_digits = list(
        now.strftime("%d%m%Y")
    )  # e.g. ['1','4','0','9','2','0','2','3']

    # 🔀 Shuffle both lists BEFORE mixing
    random.shuffle(month_letters)
    random.shuffle(time_digits)
    random.shuffle(date_month_year_digits)

    mixed = list(
        itertools.zip_longest(
            month_letters, time_digits, date_month_year_digits, fillvalue=""
        )
    )
    token_core = "".join(a + b + c for a, b, c in mixed)

    random_letter = secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    print("Generated token:", f"{token_core}{random_letter}")

    return f"{token_core}{random_letter}"

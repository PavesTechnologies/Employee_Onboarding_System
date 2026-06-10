import re
from fastapi import HTTPException, status
from datetime import datetime
import pycountry
import phonenumbers


def validate_non_empty(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string is not empty or whitespace.
    - Strips leading/trailing spaces.
    - Raises ValueError if empty or None.
    """
    if not value or not isinstance(value, str):
        raise ValueError(f"{field_name} cannot be null or empty")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank or just spaces")

    return cleaned


def validate_numbers_only(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string contains only numeric digits.
    - Strips spaces.
    - No letters, commas, or symbols allowed.
    """
    cleaned = validate_non_empty(value, field_name)

    if not cleaned.isdigit():
        raise ValueError(f"{field_name} must contain only numeric digits")

    return cleaned


def validate_alphabets_only(value: str, field_name: str = "Field") -> str:
    """
    Ensures the given string contains only alphabets and spaces.
    - Strips leading/trailing spaces.
    - No digits or special characters allowed.
    """
    cleaned = validate_non_empty(value, field_name)

    if not re.match(r"^[A-Za-z\s0-9]+$", cleaned):
        raise ValueError(
            f"{field_name} must contain only alphabets and spaces and numbers"
        )

    return cleaned


def validate_name(first_name: str) -> str:
    """
    Validates the first name.
    Rules:
      - Must not be empty
      - Only alphabets and spaces allowed
      - Automatically trims leading/trailing spaces
    """
    if not first_name or not first_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="First name cannot be empty"
        )

    # Trim spaces first
    first_name = first_name.strip()

    # Allow only alphabets, spaces, and numbers
    if not re.match(r"^[A-Za-z0-9 ]+$", first_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="First name can only contain alphabets, spaces, and numbers",
        )

    return first_name


def validate_document_name(value: str, field_name: str = "Document Name") -> str:
    cleaned = validate_non_empty(value, field_name)

    if not re.match(r"^[A-Za-z\s0-9]+$", cleaned):
        raise ValueError(f"{field_name} must contain only alphabets and spaces")

    return cleaned


def validate_email(email: str) -> str:
    """
    Validates email address.
    Rules:
      - Must not be empty
      - Must follow standard email format
      - Automatically trims leading/trailing spaces
    """
    if not email or not email.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be empty"
        )

    email = email.strip()

    # Simple and practical regex for email format
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
        )

    return email


def validate_designation(designation: str) -> str:
    """
    Validates a designation field.
    - Strips leading and trailing spaces.
    - Ensures it's not empty after trimming.
    - Allows only letters, spaces, periods, and hyphens (e.g., 'Sr. Software Engineer', 'Vice-President').
    - Returns the cleaned string.
    """
    if not designation or not isinstance(designation, str):
        raise ValueError("Designation cannot be empty or null")

    # Remove leading and trailing spaces
    cleaned = designation.strip()

    if not cleaned:
        raise ValueError("Designation cannot be empty or just spaces")

    # Allow letters, spaces, dots, and hyphens
    if not re.match(r"^[A-Za-z\s\.-]+$", cleaned):
        raise ValueError(
            "Designation can only contain letters, spaces, periods, and hyphens"
        )

    return cleaned


def validate_package(package: str) -> str:
    """
    Validates a salary package value.
    - Strips leading/trailing spaces.
    - Ensures it's not empty.
    - Allows only numeric digits (no commas, symbols, or alphabets).
    - Returns the cleaned numeric string.
    """
    if not package or not isinstance(package, str):
        raise ValueError("Package cannot be empty or null")

    # Remove leading/trailing spaces
    cleaned = package.strip()

    if not cleaned:
        raise ValueError("Package cannot be empty or just spaces")

    # Ensure only digits
    if not cleaned.isdigit():
        raise ValueError("Package must contain only numeric digits")

    return cleaned


def validate_currency(currency: str) -> str:
    """
    Validates a currency code.
    - Strips leading and trailing spaces.
    - Ensures it's not empty.
    - Allows only uppercase letters (ISO 4217 format, e.g., 'USD', 'INR', 'EUR').
    - Length must be exactly 3 characters.
    - Returns the cleaned uppercase code.
    """
    if not currency or not isinstance(currency, str):
        raise ValueError("Currency cannot be empty or null")

    cleaned = currency.strip().upper()

    if not cleaned:
        raise ValueError("Currency cannot be empty or just spaces")

    if not re.match(r"^[A-Z]{3}$", cleaned):
        raise ValueError(
            "Currency must be a valid 3-letter uppercase code (e.g., USD, INR, EUR)"
        )

    return cleaned


def validate_country(calling_code: str):
    try:
        code = int(calling_code)
    except ValueError:
        raise ValueError("Calling code must be a number")

    # Validate calling code → get region (ISO country code, e.g. IN)
    region = phonenumbers.region_code_for_country_code(code)

    if not region:
        raise ValueError("Invalid calling code")

    # Convert region (ISO alpha-2) to country name
    country = pycountry.countries.get(alpha_2=region)

    if not country:
        raise ValueError("Country not found in pycountry")

    return calling_code


def get_country_name(calling_code: str):
    try:
        code = int(calling_code)
    except ValueError:
        raise ValueError("Calling code must be a number")

    # Validate calling code → get region (ISO country code, e.g. IN)
    region = phonenumbers.region_code_for_country_code(code)

    if not region:
        raise ValueError("Invalid calling code")

    # Convert region (ISO alpha-2) to country name
    country = pycountry.countries.get(alpha_2=region)

    if not country:
        raise ValueError("Country not found in pycountry")

    return country.name


def validate_phone_number(calling_code: str, phone_number: str, type: str) -> str:
    # 1. Validate calling code
    try:
        code = int(calling_code)
    except ValueError:
        raise ValueError("Calling code must be a numeric value")

    region = phonenumbers.region_code_for_country_code(code)
    if not region:
        raise ValueError("Invalid calling code")

    # 2. Build full number with +code
    full_number = f"+{code}{phone_number}"

    try:
        parsed = phonenumbers.parse(full_number, None)
    except phonenumbers.NumberParseException:
        raise ValueError(f"{type} is Invalid phone number format")

    # 3. Validate number structure
    if not phonenumbers.is_possible_number(parsed):
        raise ValueError(f"{type}  is not possible for this region")

    # 4. Validate if number is actually valid
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError(f"{type} is not valid")

    # 5. Extra check: ensure region matches calling code
    detected_region = phonenumbers.region_code_for_number(parsed)
    if detected_region != region:
        raise ValueError(f"{type} does not match the calling code")

    return phone_number


def validate_numeric_value(value: str):
    try:
        num = float(value)
        if num < 0:
            raise ValueError()
        return num
    except Exception:
        raise HTTPException(
            status_code=400, detail="Percentage / CGPA must be a valid positive number"
        )


def validate_date_of_birth(date_of_birth: str):
    try:
        datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date of birth must be in YYYY-MM_DD format")
    return date_of_birth


def validate_blood_group(blood_group: str):
    if blood_group not in ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]:
        raise ValueError(
            "Invalid blood group. It must be one of A+, A-, B+, B-, O+, O-, AB+, AB-"
        )
    return blood_group


# def validate_date_format(date_str: str, field_name: str = "Date") -> str:
#     """
#     Validates that the given date string is in YYYY-MM-DD format.
#     Raises ValueError if the format is incorrect.
#     """
#     try:
#         datetime.strptime(date_str, "%Y-%m-%d")
#     except ValueError:
#         raise ValueError(f"{field_name} must be in YYYY-MM-DD format")
#     return date_str

import re
import phonenumbers

POSTAL_CODE_REGEX = {
    # Asia
    "IN": r"^\d{6}$",  # India
    "SG": r"^\d{6}$",  # Singapore
    "AE": r"^\d{5}$",  # UAE (Dubai uses 00000 or PO Box — 5 digits standard)
    "SA": r"^\d{5}(-\d{4})?$",  # Saudi Arabia
    "JP": r"^\d{3}-\d{4}$",  # Japan
    "CN": r"^\d{6}$",  # China
    "HK": r"^\d{3,4}$",  # Hong Kong (often NA but parcel uses 3–4)
    "KR": r"^\d{5}$",  # South Korea
    "TW": r"^\d{3}(\d{2})?$",  # Taiwan (3 or 5 digits)
    "MY": r"^\d{5}$",  # Malaysia
    "TH": r"^\d{5}$",  # Thailand
    "PH": r"^\d{4}$",  # Philippines
    "ID": r"^\d{5}$",  # Indonesia
    "VN": r"^\d{5}$",  # Vietnam
    "PK": r"^\d{5}$",  # Pakistan
    "BD": r"^\d{4}$",  # Bangladesh
    "LK": r"^\d{5}$",  # Sri Lanka
    # Europe
    "GB": r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$",  # United Kingdom
    "DE": r"^\d{5}$",  # Germany
    "FR": r"^\d{5}$",  # France
    "IT": r"^\d{5}$",  # Italy
    "ES": r"^\d{5}$",  # Spain
    "NL": r"^\d{4}\s?[A-Z]{2}$",  # Netherlands
    "CH": r"^\d{4}$",  # Switzerland
    "BE": r"^\d{4}$",  # Belgium
    "AT": r"^\d{4}$",  # Austria
    "SE": r"^\d{3}\s?\d{2}$",  # Sweden
    "NO": r"^\d{4}$",  # Norway
    "FI": r"^\d{5}$",  # Finland
    "DK": r"^\d{4}$",  # Denmark
    "IE": r"^[A-Z]\d{2}\s?[A-Z0-9]{4}$",  # Ireland (Eircode)
    "PT": r"^\d{4}-\d{3}$",  # Portugal
    "PL": r"^\d{2}-\d{3}$",  # Poland
    "CZ": r"^\d{3}\s?\d{2}$",  # Czech Republic
    "RO": r"^\d{6}$",  # Romania
    "GR": r"^\d{3}\s?\d{2}$",  # Greece
    "HU": r"^\d{4}$",  # Hungary
    # North America
    "US": r"^\d{5}(-\d{4})?$",  # United States
    "CA": r"^[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d$",  # Canada
    "MX": r"^\d{5}$",  # Mexico
    # South America
    "BR": r"^\d{5}-\d{3}$",  # Brazil
    "AR": r"^[A-Z]?\d{4}[A-Z]{0,3}$",  # Argentina
    "CL": r"^\d{7}$",  # Chile
    "CO": r"^\d{6}$",  # Colombia
    "PE": r"^\d{5}$",  # Peru
    # Middle East
    "TR": r"^\d{5}$",  # Turkey
    "IL": r"^\d{7}$",  # Israel
    "QA": r"^\d{3,5}$",  # Qatar (not strict, varies)
    "KW": r"^\d{5}$",  # Kuwait
    "OM": r"^\d{3}$",  # Oman (3 digits)
    "BH": r"^\d{3,4}$",  # Bahrain
    "JO": r"^\d{5}$",  # Jordan
    # Africa
    "ZA": r"^\d{4}$",  # South Africa
    "EG": r"^\d{5}$",  # Egypt
    "NG": r"^\d{6}$",  # Nigeria
    "KE": r"^\d{5}$",  # Kenya
}


def validate_postal_code(calling_code: str, postal_code: str) -> bool:
    try:
        code = int(calling_code)
    except ValueError:
        raise ValueError("Calling code must be a numeric value")

    region = phonenumbers.region_code_for_country_code(code)
    if not region:
        raise ValueError("Invalid calling code")

    pattern = POSTAL_CODE_REGEX.get(region)
    if not pattern:
        raise ValueError(f"No postal code rule for country: {region}")

    if not re.fullmatch(pattern, postal_code):
        raise ValueError(f"Invalid postal code '{postal_code}' for country: {region}")

    return True

"""
Transaction categorisation engine.
Uses keyword matching for fast classification.
"""

CATEGORY_KEYWORDS = {
    "groceries": ["tesco", "sainsbury", "asda", "aldi", "lidl", "waitrose", "morrisons", "co-op", "grocery", "supermarket"],
    "dining": ["restaurant", "cafe", "coffee", "starbucks", "costa", "mcdonald", "nando", "pizza", "uber eats", "deliveroo", "just eat"],
    "transport": ["uber", "bolt", "tfl", "train", "bus", "fuel", "petrol", "parking", "railway"],
    "subscriptions": ["netflix", "spotify", "amazon prime", "disney", "youtube", "gym", "membership", "subscription"],
    "utilities": ["electric", "gas", "water", "broadband", "internet", "phone bill", "council tax", "energy"],
    "rent": ["rent", "mortgage", "housing"],
    "shopping": ["amazon", "ebay", "asos", "zara", "h&m", "primark", "john lewis", "argos", "clothing"],
    "health": ["pharmacy", "doctor", "dentist", "hospital", "nhs", "prescription", "gym"],
    "entertainment": ["cinema", "theatre", "concert", "gaming", "playstation", "xbox", "steam"],
    "transfers": ["transfer", "sent to", "payment to", "bank transfer"],
    "income": ["salary", "wages", "freelance", "refund", "cashback"],
}


def categorise_transaction(description: str, merchant: str | None = None) -> str:
    """Categorise a transaction based on description and merchant name."""
    text = f"{description} {merchant or ''}".lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "other"

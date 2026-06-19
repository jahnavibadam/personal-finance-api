"""
Transaction categorisation engine.
Uses keyword matching with word boundary awareness.
"""
import re

CATEGORY_KEYWORDS = {
    "groceries": ["tesco", "sainsbury", "asda", "aldi", "lidl", "waitrose", "morrisons", "co-op", "grocery", "supermarket", "groceries"],
    "dining": ["restaurant", "cafe", "coffee", "starbucks", "costa", "mcdonald", "nando", "pizza", "uber eats", "deliveroo", "just eat", "dinner", "lunch", "brunch"],
    "transport": ["uber ride", "bolt ride", "tfl", "train", "bus fare", "fuel", "petrol", "parking", "railway", "tube", "taxi"],
    "subscriptions": ["netflix", "spotify", "amazon prime", "disney plus", "youtube premium", "gym membership", "membership", "subscription", "apple music"],
    "utilities": ["electric", "gas bill", "water bill", "broadband", "internet", "phone bill", "council tax", "energy bill", "wifi"],
    "rent": ["rent", "mortgage", "housing", "landlord"],
    "shopping": ["amazon", "ebay", "asos", "zara", "h&m", "primark", "john lewis", "argos", "clothing", "clothes", "shoes"],
    "health": ["pharmacy", "doctor", "dentist", "hospital", "nhs", "prescription", "medicine", "medical", "optician", "therapist"],
    "entertainment": ["cinema", "theatre", "concert", "gaming", "playstation", "xbox", "steam", "tickets", "gig"],
    "transfers": ["transfer to", "sent to", "payment to", "bank transfer"],
    "income": ["salary", "wages", "freelance", "refund", "cashback", "dividend"],
}

# Pre-compile patterns with word boundaries
_CATEGORY_PATTERNS = {
    category: [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in keywords]
    for category, keywords in CATEGORY_KEYWORDS.items()
}


def categorise_transaction(description: str, merchant: str | None = None) -> str:
    """Categorise a transaction based on description and merchant name."""
    text = f"{description} {merchant or ''}"

    # Check longer/more specific keywords first (sorted by keyword length desc)
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(text):
                return category

    return "other"

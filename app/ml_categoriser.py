"""
ML-based transaction categoriser using TF-IDF + Naive Bayes.
Trains on a labelled dataset of transaction descriptions.
Falls back to keyword matching when confidence is low.
"""
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

from app.categoriser import categorise_transaction as keyword_categorise

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
CONFIDENCE_THRESHOLD = 0.4

# Training data — representative examples per category
TRAINING_DATA = [
    # Groceries
    ("tesco weekly shop", "groceries"),
    ("sainsburys groceries", "groceries"),
    ("asda supermarket", "groceries"),
    ("aldi store", "groceries"),
    ("lidl purchase", "groceries"),
    ("waitrose food shop", "groceries"),
    ("morrisons groceries", "groceries"),
    ("co-op food", "groceries"),
    ("grocery shopping", "groceries"),
    ("supermarket run", "groceries"),
    ("weekly food shop", "groceries"),
    ("fruit and veg market", "groceries"),
    ("whole foods", "groceries"),
    ("ocado delivery", "groceries"),
    ("iceland frozen food", "groceries"),

    # Dining
    ("restaurant dinner", "dining"),
    ("cafe lunch", "dining"),
    ("coffee morning", "dining"),
    ("starbucks latte", "dining"),
    ("costa coffee", "dining"),
    ("mcdonalds meal", "dining"),
    ("nandos chicken", "dining"),
    ("pizza express", "dining"),
    ("uber eats delivery", "dining"),
    ("deliveroo order", "dining"),
    ("just eat takeaway", "dining"),
    ("brunch with friends", "dining"),
    ("dinner date", "dining"),
    ("lunch meeting", "dining"),
    ("thai food delivery", "dining"),
    ("sushi restaurant", "dining"),
    ("pub food", "dining"),
    ("burger king", "dining"),
    ("kfc meal", "dining"),
    ("indian takeaway", "dining"),
    ("cappuccino", "dining"),
    ("latte", "dining"),
    ("eating out", "dining"),
    ("food delivery", "dining"),

    # Transport
    ("uber ride home", "transport"),
    ("bolt taxi", "transport"),
    ("tfl bus fare", "transport"),
    ("train ticket", "transport"),
    ("bus pass", "transport"),
    ("fuel petrol station", "transport"),
    ("petrol fill up", "transport"),
    ("parking meter", "transport"),
    ("railway ticket", "transport"),
    ("tube journey", "transport"),
    ("taxi to airport", "transport"),
    ("car service", "transport"),
    ("mot test", "transport"),
    ("car insurance", "transport"),
    ("congestion charge", "transport"),
    ("oyster card topup", "transport"),
    ("uber to work", "transport"),
    ("cab home", "transport"),
    ("grab ride", "transport"),
    ("commute train", "transport"),

    # Subscriptions
    ("netflix monthly", "subscriptions"),
    ("spotify premium", "subscriptions"),
    ("amazon prime", "subscriptions"),
    ("disney plus", "subscriptions"),
    ("youtube premium", "subscriptions"),
    ("gym membership", "subscriptions"),
    ("apple music", "subscriptions"),
    ("hbo max", "subscriptions"),
    ("adobe subscription", "subscriptions"),
    ("icloud storage", "subscriptions"),
    ("playstation plus", "subscriptions"),
    ("xbox game pass", "subscriptions"),
    ("audible monthly", "subscriptions"),
    ("newspaper subscription", "subscriptions"),
    ("linkedin premium", "subscriptions"),

    # Utilities
    ("electric bill", "utilities"),
    ("gas bill payment", "utilities"),
    ("water bill", "utilities"),
    ("broadband internet", "utilities"),
    ("phone bill payment", "utilities"),
    ("council tax", "utilities"),
    ("energy bill", "utilities"),
    ("wifi monthly", "utilities"),
    ("mobile phone plan", "utilities"),
    ("heating gas", "utilities"),
    ("electricity direct debit", "utilities"),
    ("thames water", "utilities"),
    ("bt internet", "utilities"),
    ("virgin media", "utilities"),
    ("sky tv bill", "utilities"),
    ("paid electricity", "utilities"),
    ("paid gas", "utilities"),
    ("utility payment", "utilities"),

    # Rent
    ("rent payment", "rent"),
    ("monthly rent", "rent"),
    ("mortgage payment", "rent"),
    ("housing payment", "rent"),
    ("landlord rent", "rent"),
    ("flat rent", "rent"),
    ("apartment lease", "rent"),
    ("accommodation", "rent"),
    ("rent direct debit", "rent"),
    ("letting agent", "rent"),

    # Shopping
    ("amazon order", "shopping"),
    ("ebay purchase", "shopping"),
    ("asos clothing", "shopping"),
    ("zara clothes", "shopping"),
    ("h&m shopping", "shopping"),
    ("primark haul", "shopping"),
    ("john lewis", "shopping"),
    ("argos purchase", "shopping"),
    ("new shoes", "shopping"),
    ("clothing store", "shopping"),
    ("online shopping", "shopping"),
    ("next clothing", "shopping"),
    ("tk maxx", "shopping"),
    ("ikea furniture", "shopping"),
    ("electronics store", "shopping"),
    ("birthday gift", "shopping"),
    ("present for mum", "shopping"),
    ("bra", "shopping"),
    ("underwear", "shopping"),
    ("jacket", "shopping"),
    ("jeans", "shopping"),
    ("trainers", "shopping"),
    ("dress", "shopping"),
    ("makeup", "shopping"),
    ("skincare", "shopping"),
    ("perfume", "shopping"),

    # Health
    ("pharmacy purchase", "health"),
    ("doctor appointment", "health"),
    ("dentist checkup", "health"),
    ("hospital visit", "health"),
    ("nhs prescription", "health"),
    ("prescription medicine", "health"),
    ("medicine", "health"),
    ("optician eye test", "health"),
    ("therapist session", "health"),
    ("physiotherapy", "health"),
    ("vitamin supplements", "health"),
    ("health insurance", "health"),
    ("flu jab", "health"),
    ("blood test", "health"),
    ("mental health app", "health"),

    # Entertainment
    ("cinema tickets", "entertainment"),
    ("theatre show", "entertainment"),
    ("concert tickets", "entertainment"),
    ("gaming purchase", "entertainment"),
    ("steam game", "entertainment"),
    ("museum entry", "entertainment"),
    ("bowling night", "entertainment"),
    ("escape room", "entertainment"),
    ("event tickets", "entertainment"),
    ("festival pass", "entertainment"),
    ("book purchase", "entertainment"),
    ("magazine", "entertainment"),
    ("zoo tickets", "entertainment"),
    ("theme park", "entertainment"),
    ("comedy show", "entertainment"),

    # Transfers
    ("transfer to savings", "transfers"),
    ("sent to john", "transfers"),
    ("payment to friend", "transfers"),
    ("bank transfer", "transfers"),
    ("money sent", "transfers"),
    ("paid back loan", "transfers"),
    ("splitwise payment", "transfers"),
    ("monzo transfer", "transfers"),
    ("revolut transfer", "transfers"),
    ("sent money", "transfers"),

    # Income
    ("salary payment", "income"),
    ("monthly wages", "income"),
    ("freelance payment", "income"),
    ("refund received", "income"),
    ("cashback reward", "income"),
    ("dividend payment", "income"),
    ("bonus payment", "income"),
    ("tax refund", "income"),
    ("interest earned", "income"),
    ("sold item", "income"),
]


class MLCategoriser:
    def __init__(self):
        self.pipeline = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.pipeline = pickle.load(f)
        else:
            self._train()

    def _train(self):
        texts = [t[0] for t in TRAINING_DATA]
        labels = [t[1] for t in TRAINING_DATA]

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, max_features=5000)),
            ("clf", MultinomialNB(alpha=0.1))
        ])
        self.pipeline.fit(texts, labels)

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.pipeline, f)

    def categorise(self, description: str, merchant: str | None = None) -> tuple[str, float]:
        """
        Returns (category, confidence).
        Falls back to keyword matching if confidence is below threshold.
        """
        text = f"{description} {merchant or ''}".strip()

        probs = self.pipeline.predict_proba([text])[0]
        max_idx = np.argmax(probs)
        confidence = probs[max_idx]
        predicted = self.pipeline.classes_[max_idx]

        if confidence >= CONFIDENCE_THRESHOLD:
            return predicted, confidence

        # Fallback to keyword matching
        keyword_result = keyword_categorise(description, merchant)
        return keyword_result, 0.0


# Singleton instance
_categoriser = None


def get_ml_categoriser() -> MLCategoriser:
    global _categoriser
    if _categoriser is None:
        _categoriser = MLCategoriser()
    return _categoriser


def smart_categorise(description: str, merchant: str | None = None) -> str:
    """Main entry point — uses ML with keyword fallback."""
    cat, _ = get_ml_categoriser().categorise(description, merchant)
    return cat

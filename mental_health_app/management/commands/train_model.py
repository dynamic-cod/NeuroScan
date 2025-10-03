from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import joblib
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report


MODEL_DIR = Path(__file__).resolve().parents[2] / "ml_model"
DEFAULT_DATASET_CANDIDATES = [
    Path("Datasets/processed_dataset.csv"),
    Path("Datasets/Combined_Data_Cleaned.csv"),
    Path("Datasets/Combined_Data.csv"),
    Path("Datasets/Model1.csv"),
]
TEXT_COLUMNS = ["text", "symptom_text", "clean_text", "content", "message"]
LABEL_COLUMNS = ["label", "target", "state", "mental_health_state"]


@dataclass
class DatasetSpec:
    path: Path
    text_column: str
    label_column: str


def find_dataset(explicit_path: Optional[str]) -> DatasetSpec:
    if explicit_path:
        path = Path(explicit_path)
        if not path.exists():
            raise CommandError(f"Dataset not found at {path}")
        return detect_columns(path)

    for candidate in DEFAULT_DATASET_CANDIDATES:
        if candidate.exists():
            return detect_columns(candidate)
    raise CommandError("No dataset found. Provide --dataset PATH or add a CSV in Datasets/.")


def detect_columns(path: Path) -> DatasetSpec:
    df = pd.read_csv(path)
    text_col = next((c for c in TEXT_COLUMNS if c in df.columns), None)
    label_col = next((c for c in LABEL_COLUMNS if c in df.columns), None)
    if not text_col or not label_col:
        raise CommandError(
            f"Could not detect text/label columns in {path}. "
            f"Have columns: {list(df.columns)}; expected one of text={TEXT_COLUMNS}, label={LABEL_COLUMNS}"
        )
    return DatasetSpec(path=path, text_column=text_col, label_column=label_col)


class Command(BaseCommand):
    help = "Train TF-IDF + LogisticRegression model and save artifacts in ml_model/"

    def add_arguments(self, parser):
        parser.add_argument("--dataset", type=str, default=None, help="Path to CSV dataset")
        parser.add_argument("--test-size", type=float, default=0.2, help="Test split fraction")
        parser.add_argument("--random-state", type=int, default=42, help="Random seed")
        parser.add_argument("--min-df", type=int, default=2)
        parser.add_argument("--max-features", type=int, default=30000)
        parser.add_argument("--ngram-max", type=int, default=1)

    def handle(self, *args, **options):
        spec = find_dataset(options.get("dataset"))
        self.stdout.write(self.style.NOTICE(f"Loading dataset: {spec.path}"))
        df = pd.read_csv(spec.path)
        X_text = df[spec.text_column].fillna("").astype(str)
        y = df[spec.label_column].astype(str)

        X_train, X_test, y_train, y_test = train_test_split(
            X_text, y, test_size=options["test_size"], random_state=options["random_state"], stratify=y
        )

        vectorizer = TfidfVectorizer(
            min_df=options["min_df"],
            max_features=options["max_features"],
            ngram_range=(1, int(options["ngram-max"]))
        )
        clf = LogisticRegression(max_iter=1000, n_jobs=-1)

        self.stdout.write(self.style.NOTICE("Fitting vectorizer + classifier..."))
        X_train_vec = vectorizer.fit_transform(X_train)
        clf.fit(X_train_vec, y_train)
        X_test_vec = vectorizer.transform(X_test)
        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test, y_pred)
        self.stdout.write(self.style.SUCCESS(f"Test accuracy: {acc:.4f}"))
        self.stdout.write(classification_report(y_test, y_pred))

        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.pkl")
        joblib.dump(clf, MODEL_DIR / "logistic_regression_model.pkl")

        info = {
            "trained_at": int(time.time()),
            "dataset_path": str(spec.path),
            "text_column": spec.text_column,
            "label_column": spec.label_column,
            "vectorizer": {
                "min_df": options["min_df"],
                "max_features": options["max_features"],
                "ngram_max": options["ngram-max"],
                "vocab_size": int(getattr(vectorizer, 'vocabulary_', None) and len(vectorizer.vocabulary_) or 0),
            },
            "classifier": {
                "type": "LogisticRegression",
                "classes": clf.classes_.tolist(),
            },
            "metrics": {
                "accuracy": float(acc),
            },
        }
        with open(MODEL_DIR / "model_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS("Model artifacts saved to mental_health_app/ml_model/"))

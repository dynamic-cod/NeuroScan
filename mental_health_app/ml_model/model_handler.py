from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
from django.conf import settings
from django.core.cache import cache

from .exceptions import ModelNotLoadedError, InferenceError


class ModelHandler:
    def __init__(self, model_dir: Path | None = None) -> None:
        self.model_dir = Path(model_dir or Path(settings.BASE_DIR) / "mental_health_app" / "ml_model")
        self._vectorizer = None
        self._model = None
        self._info: Dict[str, Any] | None = None

    def load(self) -> None:
        try:
            vectorizer_path = self.model_dir / "tfidf_vectorizer.pkl"
            model_path = self.model_dir / "logistic_regression_model.pkl"
            info_path = self.model_dir / "model_info.json"

            if not vectorizer_path.exists() or not model_path.exists():
                raise ModelNotLoadedError("Model or vectorizer file missing")

            self._vectorizer = joblib.load(vectorizer_path)
            self._model = joblib.load(model_path)
            if info_path.exists():
                with open(info_path, "r", encoding="utf-8") as f:
                    self._info = json.load(f)
            else:
                self._info = {}
        except Exception as exc:  # noqa: BLE001
            raise ModelNotLoadedError(f"Failed to load model: {exc}") from exc

    @property
    def info(self) -> Dict[str, Any]:
        return self._info or {}

    def predict(self, text: str, scores: Dict[str, float] | None = None) -> Dict[str, Any]:
        if self._vectorizer is None or self._model is None:
            self.load()

        if text is None:
            text = ""

        try:
            cache_key = f"prediction:{hash(text)}:{hash(str(scores))}"
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

            features = self._vectorizer.transform([text])
            pred = self._model.predict(features)[0]
            proba = None
            try:
                proba = float(max(self._model.predict_proba(features)[0]))
            except Exception:  # noqa: BLE001
                proba = None
            risk_level = _risk_from_probability(proba)

            # Optionally incorporate numeric scores
            combined_scores = scores or {}
            recommendation = _recommendation_from_result(pred, risk_level, combined_scores)

            result = {
                "predicted_state": str(pred),
                "risk_level": risk_level,
                "probability": proba,
                "recommendation": recommendation,
            }
            cache.set(cache_key, result, timeout=300)
            return result
        except Exception as exc:  # noqa: BLE001
            raise InferenceError(f"Inference failed: {exc}") from exc


def _risk_from_probability(probability: float | None) -> str:
    if probability is None:
        return "unknown"
    if probability >= 0.8:
        return "high"
    if probability >= 0.5:
        return "medium"
    return "low"


def _recommendation_from_result(predicted_state: str, risk_level: str, scores: Dict[str, float]) -> str:
    if risk_level == "high":
        return "Please consider seeking immediate professional support."
    if risk_level == "medium":
        return "We recommend scheduling a consultation soon."
    return "Maintain healthy habits and monitor your well-being."

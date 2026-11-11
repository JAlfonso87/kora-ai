from pathlib import Path

import joblib
import torch
from PIL import Image
from transformers import (
    ViTForImageClassification,
    ViTImageProcessor,
)

from app.vision.classification_models import FoodClassificationResult


VIT_MODEL_ID = "google/vit-base-patch16-224"

CLASSIFIER_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "vit_svm_classifier.joblib"
)


class FoodClassifier:
    def __init__(self):
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.processor = (
            ViTImageProcessor.from_pretrained(
                VIT_MODEL_ID
            )
        )

        self.model = (
            ViTForImageClassification.from_pretrained(
                VIT_MODEL_ID
            )
        )

        self.model.to(self.device)
        self.model.eval()

        self.classifier = joblib.load(
            CLASSIFIER_PATH
        )

    def classify(
    self,
    image: Image.Image,
    ) -> FoodClassificationResult:
        image = image.convert("RGB")

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model.vit(**inputs)

            image_features = (
                outputs
                .last_hidden_state[:, 0, :]
                .cpu()
                .numpy()
            )

        prediction = self.classifier.predict(
            image_features
        )

        decision_scores = self.classifier.decision_function(
            image_features
        )

        predicted_food = str(prediction[0])

        class_index = list(
            self.classifier.classes_
        ).index(predicted_food)

        score = float(
            decision_scores[0][class_index]
        )

        return FoodClassificationResult(
            food=predicted_food,
            score=score,
        )
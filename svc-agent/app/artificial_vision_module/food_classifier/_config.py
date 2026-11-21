from pathlib import Path

VIT_MODEL_ID = "google/vit-base-patch16-224"

CLASSIFIER_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "vit_svm_classifier.joblib"
)
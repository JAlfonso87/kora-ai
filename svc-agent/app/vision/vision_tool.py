from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.vision.food_classifier import FoodClassifier
from app.vision.vision_tool_models import (
    VisionPrediction,
    VisionToolResult,
)


MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

SUPPORTED_FORMATS = {"JPEG", "PNG"}


class VisionTool:

    def __init__(self, classifier=None):
        self.classifier = classifier
        self.model_load_error = False

        if self.classifier is None:
            try:
                self.classifier = FoodClassifier()
            except Exception:
                self.model_load_error = True

    def execute(self, image_bytes: bytes) -> dict:

        if not image_bytes:
            return VisionToolResult(
                success=False,
                status="error",
                message="Image cannot be empty.",
                error_code="EMPTY_IMAGE",
            ).model_dump()

        if len(image_bytes) > MAX_IMAGE_SIZE:
            return VisionToolResult(
                success=False,
                status="error",
                message="Image exceeds the maximum allowed size.",
                error_code="IMAGE_TOO_LARGE",
            ).model_dump()

        try:
            with Image.open(BytesIO(image_bytes)) as image:

                if image.format not in SUPPORTED_FORMATS:
                    raise ValueError("Unsupported image format.")

                if (
                    image.width <= 0
                    or image.height <= 0
                    or image.width * image.height > MAX_IMAGE_PIXELS
                ):
                    raise ValueError("Invalid image dimensions.")

                image.verify()

            with Image.open(BytesIO(image_bytes)) as image:
                image = image.convert("RGB")
            if self.model_load_error or self.classifier is None:
                return VisionToolResult(
                    success=False,
                    status="error",
                    message="The vision model could not be loaded.",
                    error_code="MODEL_LOAD_ERROR",
                ).model_dump()
            try:
                prediction = self.classifier.classify(image)
            except Exception:
                return VisionToolResult(
                    success=False,
                    status="error",
                    message="An error occurred during image classification.",
                    error_code="INFERENCE_ERROR",
                ).model_dump()

            result = VisionToolResult(
                success=True,
                status="identified",
                predictions=[
                    VisionPrediction(
                        food=prediction.food,
                        score=prediction.score,
                        score_type="svm_decision_score",
                    )
                ],
                message="Food classification completed.",
            )

            return result.model_dump()

        except (UnidentifiedImageError, OSError):
            return VisionToolResult(
                success=False,
                status="error",
                message="The image could not be processed.",
                error_code="INVALID_IMAGE",
            ).model_dump()

        except ValueError as exc:
            return VisionToolResult(
                success=False,
                status="error",
                message=str(exc),
                error_code="INVALID_IMAGE",
            ).model_dump()

        except Exception:
            return VisionToolResult(
                success=False,
                status="error",
                message="An error occurred during image classification.",
                error_code="INFERENCE_ERROR",
            ).model_dump()
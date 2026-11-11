
from io import BytesIO
import unittest
from unittest.mock import patch
from PIL import Image

from app.vision.classification_models import FoodClassificationResult
from app.vision.vision_tool import VisionTool


class FakeFoodClassifier:

    def classify(self, image):
        return FoodClassificationResult(
            food="apple",
            score=2.45,
        )


class FailingFoodClassifier:

    def classify(self, image):
        raise RuntimeError("Model inference failed")


class SensitiveFailingFoodClassifier:

    def classify(self, image):
        raise RuntimeError("INTERNAL_MODEL_PATH_SECRET")


class TestVisionTool(unittest.TestCase):

    def setUp(self):
        self.tool = VisionTool(
            classifier=FakeFoodClassifier()
        )

    def create_image(self, image_format="JPEG"):
        image = Image.new(
            "RGB",
            (100, 100),
            color="red",
        )

        buffer = BytesIO()
        image.save(buffer, format=image_format)

        return buffer.getvalue()

    def test_classifies_valid_jpeg(self):
        image_bytes = self.create_image("JPEG")

        result = self.tool.execute(image_bytes)

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "identified")
        self.assertEqual(
            result["predictions"][0]["food"],
            "apple",
        )
        self.assertEqual(
            result["predictions"][0]["score"],
            2.45,
        )
        self.assertEqual(
            result["predictions"][0]["score_type"],
            "svm_decision_score",
        )

    def test_classifies_valid_png(self):
        image_bytes = self.create_image("PNG")

        result = self.tool.execute(image_bytes)

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "identified")

    def test_rejects_empty_image(self):
        result = self.tool.execute(b"")

        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "EMPTY_IMAGE")
        self.assertEqual(result["predictions"], [])

    def test_rejects_invalid_image(self):
        result = self.tool.execute(b"this is not an image")

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INVALID_IMAGE")
        self.assertEqual(result["predictions"], [])

    def test_rejects_unsupported_format(self):
        image_bytes = self.create_image("BMP")

        result = self.tool.execute(image_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INVALID_IMAGE")
        self.assertEqual(result["predictions"], [])

    def test_rejects_image_too_large(self):
        image_bytes = b"x" * (10 * 1024 * 1024 + 1)

        result = self.tool.execute(image_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "IMAGE_TOO_LARGE")
        self.assertEqual(result["predictions"], [])

    def test_handles_classification_error(self):
        tool = VisionTool(
            classifier=FailingFoodClassifier()
        )

        image_bytes = self.create_image("JPEG")
        result = tool.execute(image_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INFERENCE_ERROR")
        self.assertEqual(result["predictions"], [])

    def test_rejects_pdf_file(self):
        pdf_bytes = b"%PDF-1.4\nThis is a test PDF file"

        result = self.tool.execute(pdf_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INVALID_IMAGE")
        self.assertEqual(result["predictions"], [])

    def test_rejects_excessive_image_dimensions(self):
        image = Image.new("RGB", (5000, 5000), color="red")

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        result = self.tool.execute(buffer.getvalue())

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INVALID_IMAGE")
        self.assertEqual(result["predictions"], [])

    def test_does_not_expose_internal_errors(self):
        tool = VisionTool(
            classifier=SensitiveFailingFoodClassifier()
        )

        image_bytes = self.create_image("JPEG")
        result = tool.execute(image_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "INFERENCE_ERROR")
        self.assertNotIn(
            "INTERNAL_MODEL_PATH_SECRET",
            result["message"],
        )
        self.assertEqual(result["predictions"], [])

    def test_handles_model_load_error(self):

        with patch(
            "app.vision.vision_tool.FoodClassifier",
            side_effect=RuntimeError("Model loading failed"),
        ):
            tool = VisionTool()

        image_bytes = self.create_image("JPEG")
        result = tool.execute(image_bytes)

        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "MODEL_LOAD_ERROR")
        self.assertEqual(result["predictions"], [])




if __name__ == "__main__":
    unittest.main()



from pathlib import Path

from PIL import Image

from app.vision.food_classifier import FoodClassifier


TEST_IMAGES_DIR = (
    Path(__file__).resolve().parent.parent
    / "test_images"
)


def main():
    classifier = FoodClassifier()

    image_paths = sorted(
        path
        for path in TEST_IMAGES_DIR.iterdir()
        if path.suffix.lower()
        in {".jpg", ".jpeg", ".png"}
    )

    if not image_paths:
        raise ValueError(
            "No test images were found."
        )

    for image_path in image_paths:
        image = Image.open(image_path)

        result = classifier.classify(image)

        print(
            {
                "file": image_path.name,
                "food": result.food,
                "score": result.score,
            }
        )


if __name__ == "__main__":
    main()
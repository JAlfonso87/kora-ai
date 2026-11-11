FOOD_CLASSIFICATION_CATEGORIES = [
    "apple",
    "avocado",
    "banana",
    "bell pepper",
    "carrot",
    "corn",
    "cucumber",
    "garlic",
    "grape",
    "kiwi",
    "lemon",
    "lime",
    "mango",
    "onion",
    "orange",
    "peach",
    "pear",
    "pineapple",
    "potato",
    "strawberry",
    "tomato",
    "watermelon",
]

if len(FOOD_CLASSIFICATION_CATEGORIES) != 22:
    raise ValueError(
        "The classification category list must contain 22 categories."
    )
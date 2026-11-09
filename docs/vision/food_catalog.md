# Food Catalog

## 1. Purpose

This document defines the initial food and ingredient catalog for Kora AI's computer vision module.

The catalog will be used as a reference when evaluating food detection, segmentation, and classification models. It will also serve as the initial set of text descriptions used by CLIP during food recognition.

## 2. Food Categories

The initial catalog contains **97 food items**, organized into the following categories.

### 2.1. Grains, Cereals, and Starchy Foods

- rice
- bread
- tortilla
- pasta
- noodles
- oatmeal
- cereal
- granola
- potato
- sweet potato
- french fries
- mashed potatoes

### 2.2. Meat and Seafood

- grilled beef
- chicken
- pork
- turkey
- fish
- salmon
- tuna
- shrimp

### 2.3. Eggs and Dairy

- egg
- cheese
- milk
- yogurt

### 2.4. Vegetables

- carrot
- broccoli
- cauliflower
- spinach
- lettuce
- cabbage
- cucumber
- tomato
- onion
- garlic
- bell pepper
- jalapeno
- corn
- zucchini
- eggplant
- mushroom
- avocado
- pumpkin
- beetroot
- celery
- asparagus
- radish

### 2.5. Legumes

- beans
- peas
- green beans
- chickpeas
- lentils

### 2.6. Fruits

- apple
- banana
- orange
- lemon
- lime
- strawberry
- blueberry
- raspberry
- blackberry
- grape
- watermelon
- melon
- pineapple
- mango
- papaya
- kiwi
- peach
- pear
- plum
- cherry
- coconut
- pomegranate

### 2.7. Nuts and Seeds

- walnut
- almond
- peanut
- cashew
- pistachio
- chia seeds
- flax seeds
- sunflower seeds

### 2.8. Fats, Oils, and Spreads

- peanut butter
- olive oil
- butter
- guacamole

### 2.9. Condiments, Sauces, and Dips

- honey
- sugar
- salt
- tomato sauce
- mayonnaise
- mustard
- ketchup
- hummus
- salsa

### 2.10. Other Foods and Plant-Based Proteins

- chocolate
- tofu
- tempeh

## 3. Catalog Summary

| Category | Number of items |
|---|---:|
| Grains, Cereals, and Starchy Foods | 12 |
| Meat and Seafood | 8 |
| Eggs and Dairy | 4 |
| Vegetables | 22 |
| Legumes | 5 |
| Fruits | 22 |
| Nuts and Seeds | 8 |
| Fats, Oils, and Spreads | 4 |
| Condiments, Sauces, and Dips | 9 |
| Other Foods and Plant-Based Proteins | 3 |
| **Total** | **97** |

## 4. Implementation Reference

The following Python list represents the initial catalog used by the CLIP classification process:

```python
ingredients = [
    "rice",
    "beans",
    "grilled beef",
    "chicken",
    "pork",
    "turkey",
    "fish",
    "salmon",
    "tuna",
    "shrimp",
    "egg",
    "cheese",
    "milk",
    "yogurt",
    "bread",
    "tortilla",
    "pasta",
    "noodles",
    "oatmeal",
    "cereal",
    "potato",
    "sweet potato",
    "french fries",
    "mashed potatoes",
    "carrot",
    "broccoli",
    "cauliflower",
    "spinach",
    "lettuce",
    "cabbage",
    "cucumber",
    "tomato",
    "onion",
    "garlic",
    "bell pepper",
    "jalapeno",
    "corn",
    "peas",
    "green beans",
    "zucchini",
    "eggplant",
    "mushroom",
    "avocado",
    "pumpkin",
    "beetroot",
    "celery",
    "asparagus",
    "radish",
    "chickpeas",
    "lentils",
    "apple",
    "banana",
    "orange",
    "lemon",
    "lime",
    "strawberry",
    "blueberry",
    "raspberry",
    "blackberry",
    "grape",
    "watermelon",
    "melon",
    "pineapple",
    "mango",
    "papaya",
    "kiwi",
    "peach",
    "pear",
    "plum",
    "cherry",
    "coconut",
    "pomegranate",
    "walnut",
    "almond",
    "peanut",
    "cashew",
    "pistachio",
    "chia seeds",
    "flax seeds",
    "sunflower seeds",
    "peanut butter",
    "olive oil",
    "butter",
    "honey",
    "sugar",
    "salt",
    "tomato sauce",
    "mayonnaise",
    "mustard",
    "ketchup",
    "guacamole",
    "hummus",
    "salsa",
    "chocolate",
    "tofu",
    "tempeh",
    "granola"
]
```

## 5. Considerations and Limitations

- This catalog represents the initial set of food items considered for Kora AI's visual recognition module.
- The catalog is not a training dataset and does not imply that the selected models can recognize every listed item.
- CLIP uses the ingredient descriptions as text candidates to compare against image regions.
- YOLO detection and segmentation capabilities depend on the classes and annotations available in its pretrained model.
- Classification capabilities depend on the categories learned by each pretrained model.
- The catalog may be expanded or adjusted according to the results obtained during model evaluation.
- Recognition results must not be interpreted as estimates of food quantities, portions, or nutritional values.

## 6. Future Use

This catalog will serve as a reference for:

1. Selecting and labeling test images.
2. Evaluating food detection and segmentation models.
3. Comparing pretrained food classification models.
4. Configuring the classification process in Kora AI's vision module.


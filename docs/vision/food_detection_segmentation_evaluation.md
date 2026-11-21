# Food Detection and Segmentation Evaluation

## 1. Objective

Evaluate the YOLO food segmentation model to determine its ability to detect and delimit food regions in images containing multiple foods and mixed dishes.

The evaluation focuses on segmentation performance, using reference masks from the FoodSeg103 dataset.

## 2. Evaluated Model

- **Model:** YOLO11l Food Segmentation
- **Repository:** `arunapb/yolo11l-food-segmentation`
- **Weights:** `best.pt`
- **Task:** Instance segmentation
- **Number of classes:** 1
- **Class:** `food`
- **Confidence threshold:** 0.25

The model identifies food regions as a general category. It does not distinguish individual food ingredients.

## 3. Evaluation Dataset

The evaluation dataset was obtained from the FoodSeg103 validation split.

| Scenario | Images |
|---|---:|
| Multiple foods | 40 |
| Mixed dishes | 17 |
| **Total** | **57** |

Three duplicated source samples were excluded to prevent duplicate evaluation.

Each image has a corresponding ground-truth segmentation mask.

## 4. Evaluation Methodology

The evaluation process consisted of the following steps:

1. Load each test image and its corresponding reference mask.
2. Execute YOLO segmentation inference.
3. Retrieve the predicted instance masks.
4. Combine the predicted masks into a single binary food mask.
5. Convert the reference mask into a binary representation, distinguishing food pixels from background pixels.
6. Resize predicted masks to match the reference mask dimensions.
7. Calculate Intersection over Union (IoU) and Dice coefficient for each image.
8. Record the number of detections and processing time.

### Evaluation Metrics

- **Intersection over Union (IoU):** Measures the overlap between predicted and reference masks.
- **Dice Coefficient:** Measures the similarity between predicted and reference masks.
- **Inference Time:** Records the elapsed time for each complete prediction call.
- **Detections:** Records the number of food instances detected by YOLO.

## 5. Evaluation Results

### 5.1 Overall Results

| Metric | Mean | Median |
|---|---:|---:|
| IoU | 0.8959 | 0.9441 |
| Dice | 0.9418 | 0.9713 |
| Processing time (ms) | 2425.55 | 2227.79 |
| Detections | 9.00 | 9.00 |

Additional observed values:

- Minimum IoU: 0.6000
- Maximum IoU: 0.9862
- Minimum Dice: 0.7500
- Maximum Dice: 0.9931

### 5.2 Results by Scenario

| Scenario | Mean IoU | Mean Dice | Mean Processing Time (ms) |
|---|---:|---:|---:|
| Multiple foods | 0.8954 | 0.9421 | 2474.31 |
| Mixed dishes | 0.8971 | 0.9411 | 2310.80 |

Both scenarios obtained similar segmentation results.

## 6. Error Analysis

The five images with the lowest IoU scores were inspected to identify possible segmentation limitations.

| Image | Scenario | IoU |
|---|---|---:|
| MIXED_014 | Mixed dishes | 0.6000 |
| MULTI_040 | Multiple foods | 0.6074 |
| MIXED_011 | Mixed dishes | 0.6314 |
| MULTI_024 | Multiple foods | 0.6786 |
| MULTI_033 | Multiple foods | 0.7129 |

The lowest-scoring image (`MIXED_014`) contained a sandwich. Visual inspection showed differences between the reference mask and the predicted mask.

These differences demonstrate that the model may not reproduce the exact boundaries defined by the reference annotations in every case.

## 7. Limitations

The following limitations were identified:

- The model recognizes only one class: `food`.
- It does not classify individual ingredients.
- Segmentation quality varies depending on image characteristics and food presentation.
- The evaluation was performed on 57 selected images, not the complete FoodSeg103 dataset.
- Processing times depend on the execution environment and hardware.
- IoU and Dice evaluate general food-region segmentation, not individual ingredient separation.

## 8. Conclusion

The evaluated YOLO model demonstrated the ability to detect and segment food regions in images containing multiple foods and mixed dishes.

It achieved a mean IoU of 0.8959 and a mean Dice coefficient of 0.9418 across 57 unique evaluation images.

Based on these results, the model is a promising candidate for the food localization and segmentation stage of Kora AI.

However, because it recognizes food as a single general class, an additional classification model will be required to identify individual ingredients.

The model's final suitability will also depend on the results of the classification model evaluation and its integration into the complete vision pipeline.
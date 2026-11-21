# Food Recognition Model Selection

## 1. Objective

Consolidate the results obtained during HU-015 to select the preliminary models for food detection, segmentation, and classification in Kora AI.

The selection considers evaluation metrics, observed performance, model capabilities, compatibility with the proposed vision pipeline, and identified limitations.

## 2. Selected Models

The preliminary model selection is summarized below.

| Component | Selected Model | Purpose |
|---|---|---|
| Food detection and segmentation | YOLO11l-seg | Locate food regions and generate segmentation masks. |
| Food classification | ViT + Linear SVM | Extract visual features and classify food images into supported categories. |

CLIP is retained as an alternative classification approach for future evaluation.

## 3. Detection and Segmentation Model

### 3.1 Selected Model

- Model: YOLO11l-seg
- Weights: `best.pt`
- Task: Instance segmentation.
- Number of classes: 1.
- Available class: `food`.

### 3.2 Evaluation Results

The model was evaluated using 57 unique images from the FoodSeg103 validation dataset.

| Metric | Result |
|---|---:|
| Mean IoU | 0.8959 |
| Median IoU | 0.9441 |
| Mean Dice | 0.9418 |
| Median Dice | 0.9713 |
| Mean prediction time | 2425.55 ms |
| Mean detections per image | 9 |

The evaluation compared the union of predicted food masks against binary ground-truth food masks.

### 3.3 Selection Justification

YOLO11l-seg was selected because it demonstrated strong overlap between predicted and annotated food regions.

Its segmentation capability allows the system to obtain spatial regions that can subsequently be used to generate image crops for classification.

### 3.4 Limitations

- The evaluated model recognizes only one general class: `food`.
- It does not distinguish individual food ingredients.
- Its masks represent detected food regions and do not guarantee separation of every ingredient in mixed dishes.
- Rectangular crops derived from detections may contain background or neighboring foods.
- The measured prediction time represents the complete `model.predict()` call on the evaluation environment, not isolated neural network inference time.

## 4. Classification Model

### 4.1 Selected Model

- Model: `google/vit-base-patch16-224`.
- Architecture: Vision Transformer Base.
- Feature extraction: CLS token.
- Feature vector dimension: 768.
- Classification algorithm: Linear Support Vector Machine (SVM).
- Regularization parameter: `C=1.0`.

The original ImageNet classification head was not used. Instead, the pretrained visual encoder was used to extract image representations, and a separate SVM classifier was trained using the evaluation dataset.

### 4.2 Evaluation Results

The classification experiment used 220 Fruits-360 images distributed across 22 food categories.

| Dataset characteristic | Value |
|---|---:|
| Total images | 220 |
| Training images | 176 |
| Testing images | 44 |
| Categories | 22 |

The evaluation results were:

| Metric | ViT + SVM |
|---|---:|
| Accuracy | 97.73% |
| Precision | 98.48% |
| Recall | 97.73% |
| F1-score | 97.58% |

The model correctly classified 43 of the 44 testing images.

### 4.3 Alternative Model: CLIP

CLIP was evaluated using the same dataset, image partitions, and classification algorithm.

| Metric | CLIP + SVM |
|---|---:|
| Accuracy | 95.45% |
| Precision | 96.97% |
| Recall | 95.45% |
| F1-score | 95.15% |

CLIP correctly classified 42 of the 44 testing images.

Although ViT achieved better overall results, CLIP remains a relevant alternative because it supports image-text similarity through its multimodal architecture.

### 4.4 Selection Justification

ViT was selected as the preliminary classification feature extractor because it achieved the highest accuracy and macro F1-score in the conducted experiment.

The Linear SVM demonstrated that the extracted visual representations could distinguish the evaluated food categories with promising results.

### 4.5 Limitations

- Only 22 of the 97 food catalog categories were evaluated.
- The testing dataset contains only two images per category.
- Fruits-360 images have relatively controlled visual conditions.
- The selected ViT model is not originally trained to classify the 97 Kora AI food categories.
- The evaluated SVM classifier is specific to the 22 categories used in the experiment.
- Further training and validation are required before integrating the classifier as a complete 97-category solution.

## 5. Proposed Vision Pipeline

The selected components will form the basis of the following processing pipeline:

1. Receive a food photograph.
2. Execute YOLO11l-seg to detect and segment food regions.
3. Generate image crops from the detected regions.
4. Execute the classification component on each crop.
5. Return structured food identification results to the Kora AI agent.

The classification component must be adapted and validated for the supported food catalog before production integration.

## 6. Final Selection Summary

| Component | Decision | Status |
|---|---|---|
| Food detection and segmentation | YOLO11l-seg | Preliminary selection |
| Food classification | ViT + Linear SVM | Preliminary selection |
| Alternative classification | CLIP | Retained for future evaluation |

The selected combination provides a technically viable starting point for the next development stages.

However, the results do not establish that the complete recognition pipeline is production-ready. Additional validation is necessary, particularly for all 97 catalog categories and photographs containing multiple foods or mixed dishes.

## 7. Evaluation Artifacts

The experiments and supporting results are stored in Google Drive.

### Detection and Segmentation

- `food_detection_segmentation_evaluation.ipynb`
- Detection and segmentation evaluation results.

### Classification

- `food_classification_evaluation.ipynb`
- `classification_results/model_comparison.csv`
- `classification_results/classification_predictions.csv`
- `classification_results/classification_reports.txt`

### Catalog

- `food_catalog.md`


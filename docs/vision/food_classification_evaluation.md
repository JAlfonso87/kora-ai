# Food Classification Model Evaluation

## 1. Objective

Evaluate and compare two pretrained visual models, Vision Transformer (ViT) and Contrastive Language-Image Pre-training (CLIP), to determine which provides better visual feature representations for food classification in Kora AI.

The evaluation uses the same dataset, image partitions, and classification algorithm for both models.

## 2. Evaluated Models

### 2.1 Vision Transformer (ViT)

- Model: `google/vit-base-patch16-224`
- Architecture: Vision Transformer Base.
- Feature extraction: Visual encoder using the CLS token.
- Feature vector dimension: 768.
- Original classification head: ImageNet-1k.

The original classification head was not used. Instead, the visual encoder generated feature vectors for training a separate classifier.

### 2.2 Contrastive Language-Image Pre-training (CLIP)

- Model: `openai/clip-vit-base-patch32`
- Architecture: CLIP with Vision Transformer image encoder.
- Feature extraction: Visual encoder and projection layer.
- Feature vector dimension: 512.
- Feature normalization: L2 normalization.

The text encoder was not used during this evaluation.

## 3. Evaluation Dataset

The evaluation used 220 images from the Fruits-360 collection, organized into 22 food categories.

| Dataset characteristic | Value |
|---|---:|
| Total images | 220 |
| Food categories | 22 |
| Images per category | 10 |
| Training images | 176 |
| Testing images | 44 |
| Training proportion | 80% |
| Testing proportion | 20% |

A stratified split was performed using `random_state=42`, preserving eight training images and two testing images per category.

## 4. Evaluation Methodology

Both models were evaluated using the same procedure:

1. Load and preprocess the images.
2. Extract visual features using the corresponding pretrained model.
3. Generate feature vectors for training and testing images.
4. Train an independent linear Support Vector Machine (SVM) classifier for each model.
5. Evaluate both classifiers using the same testing images.

The SVM classifiers used the following configuration:

- Kernel: Linear.
- Regularization parameter: `C=1.0`.
- Feature scaling: StandardScaler.

The pretrained visual encoders remained frozen. Only the SVM classifiers were trained.

## 5. Evaluation Metrics

The following metrics were used:

- **Accuracy:** Proportion of correctly classified images.
- **Precision:** Proportion of correct predictions among all predictions for a category.
- **Recall:** Proportion of correctly identified images among the actual images of a category.
- **F1-score:** Harmonic mean of precision and recall.

Precision, recall, and F1-score were calculated using macro averaging.

## 6. Results

### 6.1 Model Comparison

| Metric | ViT | CLIP |
|---|---:|---:|
| Accuracy | 97.73% | 95.45% |
| Precision | 98.48% | 96.97% |
| Recall | 97.73% | 95.45% |
| F1-score | 97.58% | 95.15% |

ViT correctly classified 43 of the 44 testing images, while CLIP correctly classified 42.

### 6.2 Error Analysis

The incorrect predictions were:

| Model | Actual category | Predicted category | Image |
|---|---|---|---|
| ViT | Tomato | Bell pepper | IMG_207.jpg |
| CLIP | Pear | Banana | IMG_167.jpg |
| CLIP | Peach | Apple | IMG_151.jpg |

Both models made different classification errors, indicating that their visual representations may capture different characteristics of the food images.

## 7. Limitations

The evaluation has the following limitations:

- Only 22 of the 97 categories in the initial food catalog were evaluated.
- The testing dataset contains only two images per category.
- Fruits-360 provides controlled images that may not represent real-world food photographs.
- Both models were evaluated using extracted visual features and an external SVM classifier, rather than their original classification mechanisms.
- The results do not establish generalization to mixed dishes, multiple-food scenes, or images with complex backgrounds.
- The evaluation does not measure the performance of the complete detection and classification pipeline.

Therefore, the results should be considered preliminary and should not be generalized to all food categories supported by Kora AI.

## 8. Conclusion and Model Selection

ViT achieved the highest overall performance, obtaining 97.73% accuracy and a 97.58% macro F1-score.

CLIP achieved 95.45% accuracy and a 95.15% macro F1-score.

Based on these preliminary results, ViT is selected as the preferred feature extractor for the evaluated classification scenario.

CLIP remains a relevant alternative because it produced different classification errors and supports image-text similarity, which may be useful in future experiments.

Further evaluation with a larger and more diverse dataset is required before considering this selection definitive for the complete food catalog.

## 9. Generated Artifacts

The evaluation notebook and its results are stored in Google Drive.

**Notebook:**
- `food_classification_evaluation.ipynb`

**Evaluation results:**
- `classification_results/model_comparison.csv`
- `classification_results/classification_predictions.csv`
- `classification_results/classification_reports.txt`


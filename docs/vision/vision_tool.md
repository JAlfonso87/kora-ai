# Vision Tool — HU-017

## Description

The Vision Tool allows the use of Kora AI's food classifier through an independent tool.

It receives an image in byte format, validates that it can be processed, and executes the classification model developed in HU-016.

## Supported Formats

- JPEG
- PNG

## Validations

- Empty image.
- Maximum file size of 10 MB.
- Maximum dimensions of 20 megapixels.
- Unsupported image format.
- Invalid or unreadable image.

## Response

The tool returns a structured response containing:

- `success`: indicates whether the operation was successful.
- `status`: identifies whether the result is `identified`, `uncertain`, or `error`.
- `predictions`: contains the identified classes and their scores.
- `message`: description of the result.
- `error_code`: error code when applicable.

The classifier scores correspond to SVM decision values and do not represent probabilities.

## Error Codes

- `EMPTY_IMAGE`
- `IMAGE_TOO_LARGE`
- `INVALID_IMAGE`
- `MODEL_LOAD_ERROR`
- `INFERENCE_ERROR`

## Manual Execution

From the root directory of `svc-agent`:

```
python -m tests.test_vision_tool_manual
```

## Automated Tests

```
python -m unittest discover -s tests -p "test_vision_tool.py" -v
```

## Dependency

This tool uses the food classifier developed in HU-016. It does not calculate quantities, grams, calories, or macronutrients.
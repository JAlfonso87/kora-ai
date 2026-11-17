from pydantic import ValidationError
from pathlib import Path
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import uuid

from app.artificial_vision_module.food_classifier.food_classifier import FoodClassifier
from app.context_module.nutritional_profile.models import NutritionalContext

from app.toolbox_module.tool_input_models import ArtificialVisionInput, ImageTemplate
from app.toolbox_module.tool_output_models import (
    VisionPrediction,
    VisionToolResult,
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

SUPPORTED_FORMATS = {"JPEG", "PNG"}

IMAGE_DICT = {}

class VisionTool:
    def __init__(self, classifier = None):
        self.classifier = classifier
        self.model_load_error = False

        if self.classifier is None:
            try:
                self.classifier = FoodClassifier()
            except Exception as e:
                print(f"EXCEPCIÓN: {e}")
                self.model_load_error = True

    def load_and_analyze_picture(self, context: NutritionalContext) -> VisionToolResult:
        mapped_bytes: ArtificialVisionInput = self.load_image_for_analysis()
        av_result: VisionToolResult = self.execute_artificial_vision_analysis(mapped_bytes)
        return av_result.model_dump()

    def execute_artificial_vision_analysis(self, input: ArtificialVisionInput) -> VisionToolResult:
        try:
            validation_result = self.loaded_image_validator(input)

            if validation_result != True:
                return validation_result

            image_bytes = self.get_image_bytes_by_id(input.image_id)

            with Image.open(BytesIO(image_bytes)) as image:
                image.verify()

            if self.model_load_error or self.classifier is None:
                return VisionToolResult(
                    success=False,
                    status="error",
                    message="The vision model could not be loaded.",
                    error_code="MODEL_LOAD_ERROR",
                )

            with Image.open(BytesIO(image_bytes)) as image:
                prediction = self.classifier.classify(image = image)

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

            return result

        except (UnidentifiedImageError, OSError):
            return self.raiser(err_msg = "The image could not be processed.", err_code = "INVALID_IMAGE").model_dump()

        except ValueError as exc:
            return self.raiser(err_msg = str(exc), err_code = "INVALID_IMAGE").model_dump()

        except Exception as e:
            print(e)
            return self.raiser(err_msg = "An error occurred during image classification.", err_code = "INFERENCE_ERROR").model_dump()

    def load_image_for_analysis(self) -> ArtificialVisionInput:
        file_path = r"app/artificial_vision_module/images/a.png"
        file_extension = Path(file_path).suffix.replace(".","")

        if file_extension in ['jpeg', 'png']:
            try:
                image = Image.open(file_path)
                ImageTemplate.model_validate({'width':image.width, 'height': image.height, 'total_px': image.width * image.height})
                buffer = BytesIO()
                
                image.save(buffer, format=file_extension.upper())
                image_bytes = buffer.getvalue()
                        
                return ArtificialVisionInput(
                    image_conversion_status = 'success',
                    image_conversion_annotations = 'IMAGE SUCCESSFULLY CONVERTED TO BYTE MAP.',
                    image_id = self.generate_image_id(image_bytes)
                )
            
            except ValidationError as e:
                return ArtificialVisionInput(
                    image_conversion_status = 'failed',
                    image_conversion_annotations = 'IMAGE DIMENSIONS OUT OF RANGE FOR CONVERSION TO BYTEMAP.',
                    image_id = None
                )

        else:
            return ArtificialVisionInput(
                image_conversion_status = 'failed',
                image_conversion_annotations = 'UNSUPPORTED IMAGE TYPE FOR CONVERSION TO BYTEMAP.',
                image_id = None
            )

    def loaded_image_validator(self, input: ArtificialVisionInput) -> VisionToolResult | bool:
        err_detect = False
        err_msg = None
        err_code = None

        image_bytes: bytes = self.get_image_bytes_by_id(input.image_id)

        while(True):
            if input.image_conversion_status == 'failed':
                err_detect = True
                err_msg = f"COULDN'T CONVERT TO BYTEMAP. REASON: {input.image_conversion_annotations}"
                err_code = "CONVERSION_ERROR"
                break

            if not image_bytes:
                err_detect = True
                err_msg = "IMAGE CANNOT BE EMPTY."
                err_code = "EMPTY_IMAGE"
                break

            if len(image_bytes) > MAX_IMAGE_SIZE:
                err_msg="IMAGE EXCEED THE MAXIMUM ALLOWED SIZE."
                err_code="IMAGE_TOO_LARGE"
                break

            break

        if err_detect:
            return VisionToolResult(
                success = False,
                status = "error",
                message = err_msg,
                error_code = err_code,
            )
        else: 
            return True

    def raiser(self, err_msg: str, err_code: str) -> VisionToolResult:
        return VisionToolResult(
            success = False,
            status = "error",
            message = err_msg,
            error_code = err_code,
        )

    def generate_image_id(self, image_bytes: bytes) -> str:
        image_id = str(uuid.uuid4())
        IMAGE_DICT[image_id] = image_bytes
        return image_id

    def get_image_bytes_by_id(self, image_id: str) -> bytes:
        return IMAGE_DICT[image_id]

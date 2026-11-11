
from pathlib import Path

from app.vision.vision_tool import VisionTool


image_path = Path("test_images/IMG_003.jpg")

tool = VisionTool()

result = tool.execute(
    image_path.read_bytes()
)

print(result)

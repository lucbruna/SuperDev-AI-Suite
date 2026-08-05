"""Medical generator — medical illustrations as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

MedicalGenerator = make_generator("medical", (1024, 1024), "medical_illustrator")

"""Agriculture generator — agri-tech imagery as real PNGs."""
from __future__ import annotations


from modules.ai_video_studio.ai_image_generator.generators._renderer import make_generator

AgricultureGenerator = make_generator("agriculture", (1024, 1024), "agri_model")

from .krita_image_loader import NODE_CLASS_MAPPINGS as image_loader
from .get_prompt import NODE_CLASS_MAPPINGS as get_prompt

NODE_CLASS_MAPPINGS = {**image_loader, **get_prompt}
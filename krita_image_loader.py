import base64
import io
import numpy as np
import torch
from PIL import Image, ImageOps

class LoadBase64Image:
    '''Node to load images directly from Krita or other external sources
    without needing to previously upload a file to inputs directory. Intended
    to be used in API only and not the web UI.'''
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":
            {"image": ("STRING", {"multiline": True})}
        }
    
    RETURN_TYPES = ("IMAGE", "MASK")
    CATEGORY = "comfyui_krita_plugin"
    
    FUNCTION = "load_image"
    def load_image(self, image):
        imgdata = base64.b64decode(image)
        i = Image.open(io.BytesIO(imgdata))
        i = ImageOps.exif_transpose(i)
        image = i.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        return (image, mask)
    
class LoadBase64ImageMask:
    _color_channels = ["alpha", "red", "green", "blue"]
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required":
            {"image": ("STRING", {"multiline": True}),
            "channel": (s._color_channels, ), }
        }

    CATEGORY = "comfyui_krita_plugin"

    RETURN_TYPES = ("MASK",)
    FUNCTION = "load_image"
    def load_image(self, image, channel):
        imgdata = base64.b64decode(image)
        i = Image.open(io.BytesIO(imgdata))
        i = ImageOps.exif_transpose(i)
        if i.getbands() != ("R", "G", "B", "A"):
            i = i.convert("RGBA")
        mask = None
        c = channel[0].upper()
        if c in i.getbands():
            mask = np.array(i.getchannel(c)).astype(np.float32) / 255.0
            mask = torch.from_numpy(mask)
            if c == 'A':
                mask = 1. - mask
        else:
            mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
        return (mask,)

    @classmethod
    def VALIDATE_INPUTS(s, image, channel): #image parameter is necessary
        if channel not in s._color_channels:
            return "Invalid color channel: {}".format(channel)

        return True
    
NODE_CLASS_MAPPINGS = {
    "LoadBase64Image": LoadBase64Image,
    "LoadBase64ImageMask": LoadBase64ImageMask
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadBase64Image": "Load base64 encoded image",
    "LoadBase64ImageMask": "Load base64 encoded image mask"
}
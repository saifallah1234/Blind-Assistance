import json, base64
from PIL import Image
from io import BytesIO

with open("yolo.frames.json", "r") as f:
    doc = json.load(f)

b64 = doc[0]["image_data"]["$binary"]["base64"]
img_bytes = base64.b64decode(b64)

img = Image.open(BytesIO(img_bytes))
img.show()

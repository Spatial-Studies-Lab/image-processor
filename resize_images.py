import os
from pathlib import Path
import re
from PIL import Image, ImageOps 

SIZES = {
  "thumb": 130,
  "medium": 400,
  "full": 1080
}

for file in os.listdir('images'):
  if re.search(r"\.(tif|png|jpe?g)", file, re.IGNORECASE):
    path = "output/" + re.sub(r"\.(tif|png|jpe?g)", "", file, 0, re.IGNORECASE)
    Path(path).mkdir(parents=True, exist_ok=True)
    img = Image.open('images/' + file)
    for key in SIZES:
      maxDim = img.size.index(max(img.size))
      minDim = abs(maxDim - 1)
      ratio = SIZES[key] / img.size[maxDim]
      if ratio < 1:
        size = (round(img.size[0] * ratio), round(img.size[1] * ratio))
        resized = img.resize(size, Image.ANTIALIAS)
      else:
        resized = img
      resized.save(path + '/' + key + '.jpg')
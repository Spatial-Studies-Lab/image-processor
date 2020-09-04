import os
from pathlib import Path
import re
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000

SIZES = {
  "thumb": 130,
  "medium": 400,
  "full": 1080
}

for dir in os.listdir('images'):
  if os.path.isdir(os.path.join('images', dir)):
    for file in os.listdir(os.path.join('images', dir)):
      if re.search(r"\.(tif|png|jpe?g)$", file, re.IGNORECASE):
        path = os.path.join("output/", re.sub(r"\.(tif|png|jpe?g)", "", file, 0, re.IGNORECASE))
        Path(path).mkdir(parents=True, exist_ok=True)
        try: 
          img = Image.open(os.path.join('images', dir, file))
          for key in SIZES:
            maxDim = img.size.index(min(img.size))
            minDim = abs(maxDim - 1)
            ratio = SIZES[key] / img.size[maxDim]
            if ratio < 1:
              size = (round(img.size[0] * ratio), round(img.size[1] * ratio))
              resized = img.resize(size, Image.ANTIALIAS)
            else:
              resized = img
            resized.save(os.path.join(path, key + '.jpg'))
        except:
          print('Could not open ' + os.path.join(dir, file))
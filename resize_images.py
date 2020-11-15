import os
from pathlib import Path
import re
from PIL import Image
import boto3

Image.MAX_IMAGE_PIXELS = 1000000000

SIZES = {
  "thumb": 130,
  "medium": 400,
  "full": 1920
}

s3 = boto3.client('s3')

images = s3.list_objects(Bucket=os.environ['BUCKET_SOURCE'])

for result in images['Contents']:
  key = result['Key']
  if re.search(r"\.(tif|png|jpe?g)$", key, re.IGNORECASE):
    file = re.sub(r".*\/(.*)", "input/\\1", key, re.IGNORECASE)
    ssid = re.sub(r"\.(tif|png|jpe?g)$", "", file, re.IGNORECASE)
    path = os.path.join("output/", ssid)
    with open(file, 'wb') as i:
      print('Downloading', file)
      s3.download_fileobj(os.environ['BUCKET_SOURCE'], key, i)
      try: 
        img = Image.open(file)
        print('Resizing', file)
        for kind in SIZES:
          maxDim = img.size.index(min(img.size))
          minDim = abs(maxDim - 1)
          ratio = SIZES[kind] / img.size[maxDim]
          if ratio < 1:
            size = (round(img.size[0] * ratio), round(img.size[1] * ratio))
            resized = img.resize(size, Image.ANTIALIAS)
          else:
            resized = img
          filename = os.path.join("output/", kind + '.jpg')
          resized.save(filename)
          print('Uploading', filename)
          s3.upload_file(filename, os.environ['BUCKET_TARGET'], re.sub(r"output", re.sub(r"input\/", "", ssid), filename))
          os.remove(filename)
      except:
        print('Could not open ' + os.path.join(dir, file))
    print('Cleaning up', file)
    os.remove(file)
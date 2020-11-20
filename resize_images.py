import os
import time
import logging
from pathlib import Path
import re
from PIL import Image
import boto3
from cloudwatch import cloudwatch

Image.MAX_IMAGE_PIXELS = 1000000000

SIZES = {
  "thumb": 130,
  "medium": 400,
  "full": 1920
}

s3 = boto3.client('s3')

logger = logging.getLogger('logger')
formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
handler = cloudwatch.CloudwatchHandler(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], 'us-east-1', 'image-processor', str(round(time.time() * 1000)))
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


images = s3.list_objects(Bucket=os.environ['BUCKET_SOURCE'])

for result in images['Contents']:
  key = result['Key']
  if re.search(r"\.(tif|png|jpe?g)$", key, re.IGNORECASE):
    file = re.sub(r".*\/(.*)", "input/\\1", key, flags=re.IGNORECASE)
    ssid = re.sub(r"\.(tif|png|jpe?g)$", "", file, flags=re.IGNORECASE)
    path = os.path.join("output/", ssid)
    with open(file, 'wb') as i:
      print('Downloading', file)
      logger.info('Downloading ' + file)
      s3.download_fileobj(os.environ['BUCKET_SOURCE'], key, i)
      try: 
        img = Image.open(file)
        print('Resizing', file)
        logger.info('Resizing ' + file)
        for kind in SIZES:
          filename = os.path.join("output/", kind + '.jpg')
          maxDim = img.size.index(min(img.size))
          minDim = abs(maxDim - 1)
          ratio = SIZES[kind] / img.size[maxDim]
          try:
            if ratio < 1:
              size = (round(img.size[0] * ratio), round(img.size[1] * ratio))
              resized = img.resize(size, Image.ANTIALIAS)
            else:
              resized = img
          except:
            print('Cannot resize', filename)
            logger.warning('Cannot resize ' + filename)
          else:
            resized.save(filename)
            print('Uploading', filename)
            logger.info('Uploading ' + filename)
            s3.upload_file(filename, os.environ['BUCKET_TARGET'], re.sub(r"output", re.sub(r"input\/", "", ssid), filename))
            os.remove(filename)
      except:
        print('Could not open ' + file)
        logger.warning('Could not open ' + file)
    print('Cleaning up', file)
    logger.info('Cleaning up ' + file)
    os.remove(file)
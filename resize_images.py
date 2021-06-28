import os
import time
import logging
import re
from PIL import Image, ImageFile
import boto3
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

Image.MAX_IMAGE_PIXELS = 1000000000
ImageFile.LOAD_TRUNCATED_IMAGES = True

SIZES = {
  "thumb": 130,
  "medium": 400,
  "full": 1920
}

s3 = boto3.client('s3')

def error_email(message):
  message = Mail(
    from_email='info@axismaps.com',
    to_emails=os.environ['EMAIL'],
    subject='GENERATOR ERROR: ' + os.environ['PROJECT'] + ' - ' + os.environ['TASK'],
    plain_text_content=message)
  try:
    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    response = sg.send(message)
  except Exception as e:
    print(e.message)

images = s3.list_objects(Bucket=os.environ['BUCKET_SOURCE'])

for result in images['Contents']:
  key = result['Key']
  if re.search(r"\.(tif|png|jpe?g)$", key, re.IGNORECASE):
    file = re.sub(r".*\/(.*)", "input/\\1", key, flags=re.IGNORECASE)
    ssid = re.sub(r"\.(tif|png|jpe?g)$", "", file, flags=re.IGNORECASE)
    path = os.path.join("output/", ssid)
    with open(file, 'wb') as i:
      print('Downloading', file)
      s3.download_fileobj(os.environ['BUCKET_SOURCE'], key, i)
      try: 
        img = Image.open(file)
        print('Resizing', file)
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
          except Exception as e:
            print('Cannot resize', filename)
            error_email('Cannot resize ' + file + '/' + filename + '\n\n' + repr(e))
          else:
            resized.save(filename)
            print('Uploading', filename)
            s3.upload_file(filename, os.environ['BUCKET_TARGET'], re.sub(r"output", re.sub(r"input\/", "", ssid), filename))
            os.remove(filename)
      except Exception as e:
        print('Could not open ' + file)
        error_email('Could not open ' + file + '\n\n' + repr(e))
    print('Cleaning up', file)
    os.remove(file)
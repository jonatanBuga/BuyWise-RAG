import os
from os import listdir
from os.path import isfile, join
from google.cloud import vision
import bidi.algorithm
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables from a .env file
load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
class OCR_to_heb:
    
    def __init__(self,file_content):
        self.path_image = BytesIO(file_content)
        self.text_after_ocr=''
        self.detect_text(self.path_image)

    def detect_text(self,path):
        client = vision.ImageAnnotatorClient()
        content = path.read()
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        ocr_text = []
        for text in texts:
            corrected_text = bidi.algorithm.get_display(text.description)
            ocr_text.append(f"\r\n{corrected_text}")
        if response.error.message:
            raise Exception(
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )
        self.text_after_ocr = texts[0].description
    
    def get_text(self):
        return self.text_after_ocr
import sys
from pdf_parser.pdf_to_text import pdf_To_Text
from OCR.process_image import OCR_to_heb
from lambda_function import *
def main():
    test = {
        "filename":"aaa.pdf",
        "query":"",
        "flag":1
    }

    print(lambda_handler(test,None))
    


if __name__ == "__main__":
    main()
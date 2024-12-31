import sys
from pdf_parser.pdf_to_text import pdf_To_Text
from OCR.process_image import OCR_to_heb
from lambda_function import *
def main():
    promt = 'אני רוצה להכין עוגת שוקולד וזקוק לכל המצרכים. בנוסף, אני צריך גם פירות לארוחת הבוקר והפסקת קפה.'

    print(get_response(promt))
    


if __name__ == "__main__":
    main()
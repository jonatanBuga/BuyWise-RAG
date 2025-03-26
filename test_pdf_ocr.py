import sys
from pdf_parser.pdf_to_text import pdf_To_Text
#from OCR.process_image import OCR_to_heb
#from lambda_function import *
def main():
    path_pdf = './aaa.pdf'
    test_pdf = pdf_To_Text(path_pdf)
    print(test_pdf.get_text())

    # print(lambda_handler(test,None))
    


if __name__ == "__main__":
    main()
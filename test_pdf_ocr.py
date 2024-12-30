import sys
from pdf_parser.pdf_to_text import pdf_To_Text
from OCR.process_image import OCR_to_heb

def main():
    image_path = sys.argv[1]
    ocr = OCR_to_heb(image_path)
    print(ocr.get_text())


if __name__ == "__main__":
    main()
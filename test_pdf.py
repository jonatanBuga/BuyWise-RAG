import os
import sys
import argparse
import time
import fitz
from pdf_parser.pdf_to_text import pdf_To_Text
def main():
    input_pdf = sys.argv[1]

    pdf_file = pdf_To_Text(input_pdf)

    text_from_pdf = pdf_file.get_text()
    print(text_from_pdf)



if __name__ == "__main__":
    main()
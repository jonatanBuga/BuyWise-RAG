import PyPDF2
import fitz

class pdf_To_Text:
    """
    A utility class to extract text from a PDF file.

    Attributes:
        file (str): The path to the PDF file.
        text_after_parsing (str): The extracted text from the PDF.
    """
    def __init__(self,pdf):
        """
        Initializes the pdf_To_Text instance and automatically extracts text from the given PDF.

        Args:
            pdf (str): The path to the PDF file.
        """
        self.file = pdf
        self.text_after_parsing = ''
        self.extract_Text()

    def extract_Text(self):
        """
        Extracts text from all pages of the PDF file and stores it in the 'text_after_parsing' attribute.
        """
        with open(self.file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                self.text_after_parsing+=page.extract_text()

    def get_text(self):
        """
        Returns the extracted text from the PDF.

        Returns:
            str: The text extracted from the PDF file.
        """
        return self.text_after_parsing

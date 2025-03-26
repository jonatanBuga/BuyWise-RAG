import json
from fpdf import FPDF
import os
from bidi.algorithm import get_display
def create_pdf(path_to_json):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, "Rubik-Regular.ttf")

    pdf = FPDF()
    pdf.add_page()


    pdf.add_font("Rubik", "", font_path)
    pdf.set_font("Rubik",size=12)

    with open(path_to_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    for key,val in data.items():
        key_bidi = get_display(key)
        val_bidi = get_display(str(val))


        pdf.set_font("Rubik", "", 14)  # Bold font for header
        pdf.multi_cell(0, 8, key_bidi, border=0,align= "R")
        
        # Some spacing
        pdf.ln(5)
        
        # Write the content
        pdf.set_font("Rubik", "", 12)   # Normal font for content
        pdf.multi_cell(0, 6, val_bidi,border= 0,align='R')
        # Extra spacing between entries
        pdf.ln(10)
    output_path = os.path.join(current_dir, "data", "recipes_data.pdf")
    pdf.output(output_path)
    print(f"PDF saved to recipes_data.pdf")

def main():
    create_pdf("/Users/jonatanbuga/Desktop/BuyWise-RAG/recipes_data.json")
if __name__ == "__main__":
    main()
import sys
#from pdf_parser.pdf_to_text import pdf_To_Text
#from OCR.process_image import OCR_to_heb
#from lambda_function import *
from LambdaShoppingList.lambda_function import *
def main():
    user_input = "אני מכין ארוחה שתהיה כוללת ל5 אנשים. אני רוצה שיהיה בה גם בשר גם דגים וגם פחמימות מסוג מסויים. בנוסף אני רוצה גם ירקות כחלק מהמנות"
    response = get_response(user_input,"full_list")
    print(response)
    # print(lambda_handler(test,None))
    


if __name__ == "__main__":
    main()
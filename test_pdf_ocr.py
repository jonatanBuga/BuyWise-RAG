import sys,os
from openai import OpenAI
from dotenv import load_dotenv
#from pdf_parser.pdf_to_text import pdf_To_Text
#from OCR.process_image import OCR_to_heb
#from lambda_function import *
#from LambdaShoppingList.lambda_function import *
load_dotenv(dotenv_path="LambdaShoppingList/.env")
def main():
    user_input = "אני מכין ארוחה שתהיה כוללת ל5 אנשים. אני רוצה שיהיה בה גם בשר גם דגים וגם פחמימות מסוג מסויים. בנוסף אני רוצה גם ירקות כחלק מהמנות"
    api_key = os.getenv("OPENAI_API_KEY")
    print(api_key)
    client = OpenAI(
            api_key=api_key
        )
    
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": user_input,
        }],
        model="gpt-4.1-mini",
        
    )
    generated_text = response.choices[0].message.content

    print(generated_text)
    # print(lambda_handler(test,None))
    


if __name__ == "__main__":
    main()
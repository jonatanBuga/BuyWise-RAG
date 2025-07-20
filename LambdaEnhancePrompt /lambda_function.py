from openai import OpenAI
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks

# Load environment variables from a .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


def get_response(prompt):
    client = OpenAI(
            api_key=openai_api_key, 
        )
    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-4.1-mini",
        
    )
    generated_text = response.choices[0].message.content

    return generated_text
def generate_prompt(prompt):
    text = "The user entered the following text as part of a request for a model that generates a shopping list based on habits, nutrition, and personal preferences.\n Please rephrase the text so that it is organized, clear, professional, and easy to read, without adding new information, but only improving the existing wording. If there are sub-points (e.g. requirements such as protein amount, kosher, types of meals), arrange them in paragraphs or a clear bulleted list."
    text += f"\n\n{prompt}\n\n"
    return text

def lambda_handler(event,context):
    prompt_from_user = event.get('query')
    prompt_to_llm = generate_prompt(prompt_from_user)
    result_from_llm = get_response(prompt_to_llm)

    return {"body":result_from_llm,"statusCode":200}


if __name__ == "__main__":
    # Example usage
    event = {
        'query': 'אני רוצה לאכול כל השבוע באופן מסודר 3 ארוחות ביום, אני מתאמן באופן קבוע אז אצטרך מספיק גרם חלבון ביום, אשמח גם לתוספת מעדני חלבון ופחמימות עשירותץ בנוסף ארצה לשתות משהו דיאטטי.'
    }
    context = None  # Context is not used in this example
    response = lambda_handler(event, context)
    print(response)
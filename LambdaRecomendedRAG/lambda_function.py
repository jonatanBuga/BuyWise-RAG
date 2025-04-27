from openai import OpenAI
import os
import sys
import re
from dotenv import load_dotenv
from RAG.retrive_pipeline import *


sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks
sys.path.append(os.path.join(os.path.dirname(__file__), "RAG"))
# Load environment variables from a .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
def count_tokens(text: str) -> int:
    tokens = re.findall(r'\S+|\n', text)
    return len(tokens)
def generate_user_input(list_from_llm):
    """
    Generate prompt for user input stage at rag seystem.

    Args:
        list_from_llm(str):list that create with first lambda function

    Returns:
        str: A detailed prompt to be sent to embeding model.
    """
    prompt = (
        f"I have the following ingredients available: {list_from_llm}. "
        "Please suggest possible recipes that include most or all of these ingredients. "
        "Include relevant cooking instructions, preparation tips, and flavor descriptions. "
        "Write the suggestions in a style similar to a cooking blog or cookbook."
    )
    return prompt

def prompt_augmentition(context,user_input):
    """
    Augment the user input prompt with the retrieved context from the vector store search.

    Args:
        context (str): Relevant context retrieved from the vector store (e.g., recipes matching ingredients).
        user_input (str): The original user input used for the semantic search.

    Returns:
        str: An augmented prompt combining the user input and retrieved context, ready for an LLM.
    """
    augmented_prompt = (
        "You are a culinary assistant helping a user with cooking suggestions based on their provided ingredients.\n\n"
        f"The user's ingredients and request:\n{user_input}\n\n"
        f"Relevant recipes and context found:\n{context}\n\n"
        "Please use the provided ingredients and context to suggest a variety of meals or dishes.\n\n"
        "Additionally, provide recipe ideas based on the available data.\n"
        "Finally, you must return a detailed list of products required for these meal ideas in the following format:\n"
        "Item name: Quantity\n"
        "----- OUTPUT FORMAT (strict) -----\n"
        "For **each** recipe output **exactly** this block (no extra text):\n\n"
        "# <Recipe Name>\n"
        "* <Short description in one sentence>\n"
        "- מצרכים:\n"
        "  <Ingredient 1>: <Quantity>\n"
        "  <Ingredient 2>: <Quantity>\n"
        "  ...\n\n"
        "Repeat the block above for every suggested recipe.\n"
        "Do NOT add headings, numbering, or any text outside these blocks.\n"
        "---------------------------------------------------------\n"
    )

    return augmented_prompt

def get_response(prompt):
    client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), 
        )

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-4o-mini"
        # max_tokens=count_tokens(prompt)
    )
    generated_text = response.choices[0].message.content

    return generated_text

def lambda_handler(event,context):
    llm_list_from_ui = event.get('llmList')
    user_input = generate_user_input(llm_list_from_ui)

    #retriver_context is list!!!
    retriver_context = context_from_query(user_input)

    P_augmentition = prompt_augmentition(retriver_context,user_input)

    response = get_response(P_augmentition)
    return {"body":response,"statusCode":200}


def main():
    query ="\n\"chicken breast\": \"800 gr\",\n\"spinach\": \"400 gr\",\n\"garlic\": \"4 units\",\n\"olive oil\": \"200 ml\",\n\"salt\": \"to taste\",\n\"black pepper\": \"to taste\",\n\"lemon\": \"2 units\",\n\"parmesan cheese\": \"100 gr\",\n\"pasta\": \"400 gr\",\n\"tomato sauce\": \"400 ml\",\n\"carrots\": \"2 units\",\n\"onion\": \"1 unit\",\n\"bell peppers\": \"2 units\",\n\"herbs (basil, thyme)\": \"to taste\",\n\"bread\": \"1 loaf\"\n"
    user_input = generate_user_input(query)

    #retriver_context is list!!!
    retriver_context = context_from_query(user_input)
    for doc in retriver_context:
        print("doc context:")
        print(doc+'\n')

if __name__ =="__main__":
    main()
from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
from typing import List
import transformers
import torch
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks
# Load environment variables from a .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

def generate_prompt(query: str) -> str:
    """
    Generate a prompt for the LLM using the user's query and retrieved context.

    Args:
        query (str): The original user query.
        retrieved_context (List[str]): List of retrieved items from the RAG retriever.

    Returns:
        str: A detailed prompt to be sent to the LLM.
    """

    
    prompt = (
        "You are a shopping assistant that helps users create detailed shopping lists based on their needs.\n"
        f"The user provided the following query:\n"
        f"{query}\n\n"
        "Please follow this format for your response:\n"
        "1. Shopping list: **only** return the shopping list in this format:\n"
        "{\n"
        '"item_name_1": "quantity_1",\n'
        '"item_name_2": "quantity_2",\n'
        "...}\n"
        " - For liquid items, specify the quantity in milliliters (e.g., 'milk': '1000 ml').\n"
        " - For items that require grams, specify the quantity in grams (e.g., 'flour': '500 gr').\n"
        " - For other items, use 'units' as the quantity type (e.g., 'bananas': '7 units').\n"
        "Do not include any additional text or comments outside of the dictionary format."
    )
    return prompt

def get_response(prompt):
    complite_prompt = generate_prompt(prompt)
    client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), 
        )

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": complite_prompt,
        }],
        model="gpt-4o-mini",
        max_tokens=700
    )
    generated_text = response.choices[0].message.content

    return generated_text


def lambda_handler(event,context):
    query = event.get("question")

    response = get_response(query)
    print("response: ",response)

    return {"body": response , "statusCode":200}
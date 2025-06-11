import os
from supabase import create_client, Client
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
load_dotenv()

class instanceDB:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.Client:Client = create_client(url,key)

    def fetch_product_names(self):
        response = (self.Client.table("all_products").select("name,id").execute())
        products_names =[(name['name'],name["id"]) for name in response.data]
        return products_names


from supabase import create_client 
import os
import sys
from dotenv import load_dotenv

def get_db_instance():
    SUPABASE_URL = "https://lrezctohmmbxwwiksbuo.supabase.co"
    supabase = create_client(SUPABASE_URL, os.getenv('SUPABASE_KEY'))
    return supabase
#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import logging
import os
import sys
import json
import requests
from urllib.parse import urljoin
from fpdf import FPDF
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
BASE_URL = "https://simplefood.blog/recipes/"
ROBOTS_URL = "https://simplefood.blog/robots.txt"
REQUEST_DELAY = 2  # seconds between requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def check_robots(url, user_agent="*"):
    """
    Fetch robots.txt and check if /recipes/ is allowed.
    """
    try:
        r = requests.get(ROBOTS_URL, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.warning(f"Could not fetch robots.txt: {e}")
        return True  # if not available, proceed cautiously

    for line in r.text.splitlines():
        if line.strip().lower().startswith("disallow:"):
            disallow_path = line.split(":", 1)[1].strip()
            if disallow_path == "/recipes/":
                logging.error("Scraping /recipes/ is disallowed by robots.txt.")
                return False
    return True
def load_all_recipes_html():
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(BASE_URL)
    time.sleep(3) 
    
    while True:
        try:
            infinite_div = driver.find_element(By.ID, "infinite-handle")
            button = infinite_div.find_element(By.TAG_NAME, "button")
            if button.is_displayed() and button.is_enabled():
                logging.info("'Older post'...")
                button.click()
                time.sleep(3)  
            else:
                logging.info("הכפתור אינו לחיץ, מסיימים טעינה.")
                break
        except Exception as e:
            logging.info("לא נמצא כפתור 'Older post', מסיימים טעינה.")
            break

    html = driver.page_source
    driver.quit()
    return html
def get_recipe_links():
    """
    Scrape the main recipes page for recipe links.
    It finds <article> elements with IDs like "post-3760" and extracts links from the <h2 class="entry-title">.
    Stops when it finds the "infinite-handle" div.
    """
    recipe_links = []
    html = load_all_recipes_html()
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all("article")
    for article in articles:
        article_id = article.get("id", "")
        if article_id.startswith("post-"):
            h2 = article.find("h2", class_="entry-title")
            if h2:
                a_tag = h2.find("a", href=True)
                if a_tag:
                    link = urljoin(BASE_URL, a_tag["href"])
                    recipe_links.append(link)
                    logging.info(f"Found recipe link: {link}")
    return recipe_links

def extract_recipe_content(recipe_url):
    """
    For a given recipe URL, extract the recipe title and content.
    Title is assumed to be in <h1 class="entry-title">.
    Recipe content is extracted from the div with class 
    "Input-Content-Small Transparent Container". 
    The content is cleaned into a continuous paragraph.
    """
    try:
        response = requests.get(recipe_url, timeout=10)
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
    except Exception as e:
        logging.error(f"Error fetching recipe {recipe_url}: {e}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find("h1", class_="entry-title")
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    content_div = soup.select_one("div.entry-content.container.container-small.clear")
    if not content_div:
        logging.warning(f"Content div not found for {recipe_url}")
        return title, ""

    p_tags = content_div.find_all("p")
    if not p_tags:
        logging.warning(f"No <p> tags found inside content div for {recipe_url}")
        return title, ""

    paragraphs = []
    for p in p_tags:
        p_text = p.get_text(separator=" ", strip=True)
        paragraphs.append(p_text)

    content = " ".join(paragraphs)
    return title, content

def create_pdf(recipes):
    """
    Create a PDF document compiling all recipes.
    Each recipe is formatted with a header (recipe title) followed by its content
    as a continuous paragraph, with clear separation between recipes.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir,"..", "data", "simple_food_blog.pdf")
    font_path = os.path.join(current_dir,"..", "Rubik-Regular.ttf")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Rubik", "", font_path)
    pdf.set_font("Rubik", size=12)

    for title, content in recipes:
        # Recipe header (bold, larger font)
        pdf.set_font("Rubik", size=14)
        pdf.multi_cell(0, 10, title, border=0, align="L")
        pdf.ln(2)
        pdf.set_font("Rubik",size=12)
        pdf.multi_cell(0, 8, content, border=0, align="L")
        pdf.ln(10)
    pdf.output(output_path)
    logging.info(f"PDF saved to data dir")

# --- Main Process ---
def main():
    # Check if scraping is allowed
    if not check_robots(BASE_URL):
        logging.error("Exiting due to robots.txt restrictions.")
        return

    # Get all recipe links from the main recipes page
    links = get_recipe_links()
    if not links:
        logging.error("No recipe links found.")
        return

    recipes = []
    for link in links:
        logging.info(f"Extracting recipe from: {link}")
        title, content = extract_recipe_content(link)
        if title and content:
            recipes.append((title, content))
        else:
            logging.warning(f"Skipping recipe at {link} due to missing content.")

    if recipes:
        create_pdf(recipes)
    else:
        logging.error("No recipes were successfully extracted.")

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from urllib.parse import urljoin


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://bissim.com"
RECIPES_INDEX_URL = "https://bissim.com/recipes/"
ROBOTS_TXT_URL = "https://bissim.com/robots.txt"
RATE_LIMIT_SECONDS = 2

# -------------------------------------------------------------------------
# 1. Basic robots.txt checks
# -------------------------------------------------------------------------
def parse_robots_txt(robots_url):
    disallow_rules = {}
    try:
        resp = requests.get(robots_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.warning(f"Could not retrieve robots.txt: {e}")
        return disallow_rules

    user_agent = None
    for line in resp.text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.lower().startswith('user-agent:'):
            user_agent = line.split(':', 1)[1].strip()
            if user_agent not in disallow_rules:
                disallow_rules[user_agent] = []
        elif line.lower().startswith('disallow:') and user_agent is not None:
            path = line.split(':', 1)[1].strip()
            disallow_rules[user_agent].append(path)
    return disallow_rules

def is_path_allowed(url_path, robots_dict, user_agent="*"):
    if user_agent not in robots_dict and "*" in robots_dict:
        user_agent = "*"
    if user_agent not in robots_dict:
        return True  # no specific rules => allowed

    for rule in robots_dict[user_agent]:
        if url_path.startswith(rule):
            return False
    return True

# -------------------------------------------------------------------------
# 2. Clean HTML to plain text
# -------------------------------------------------------------------------
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator="\n").strip()

# -------------------------------------------------------------------------
# 3. Scrape a single recipe page
# -------------------------------------------------------------------------
def scrape_recipe(recipe_url, robots_dict):
    time.sleep(RATE_LIMIT_SECONDS)

    path = recipe_url.replace(BASE_URL, '')
    if not is_path_allowed(path, robots_dict):
        logging.info(f"Disallowed by robots.txt: {recipe_url}")
        return None

    try:
        resp = requests.get(recipe_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve {recipe_url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    # Example: the recipe content might be in <div class="entry entry-content">
    content_div = soup.find("div", class_="entry entry-content")
    if not content_div:
        logging.warning(f"No entry content found on {recipe_url}")
        return None

    return clean_html(str(content_div))

# -------------------------------------------------------------------------
# 4. Extract *all* recipe links from the main page
# -------------------------------------------------------------------------
def get_all_recipe_links(listing_url, robots_dict):
    """
    Looks for all <p style="text-align:right;"> elements that contain <a href="...">
    Because you've said each recipe link is inside a <p style="text-align:right;">
    """
    recipe_links = []

    time.sleep(RATE_LIMIT_SECONDS)
    path = listing_url.replace(BASE_URL, '')
    if not is_path_allowed(path, robots_dict):
        logging.info(f"Disallowed by robots.txt: {listing_url}")
        return recipe_links

    try:
        resp = requests.get(listing_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve listing page {listing_url}: {e}")
        return recipe_links

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Find all <p style="text-align:right;"> ...
    paragraphs = soup.find_all("p", style="text-align:right;")
    logging.info(f"Found {len(paragraphs)} paragraph(s) with style='text-align:right;'")

    for p in paragraphs:
        # If there's one <a> inside it, extract the link
        a_tag = p.find("a", href=True)
        if a_tag:
            full_link = urljoin(BASE_URL, a_tag['href'])
            recipe_links.append(full_link)
            logging.info(f"Found link: {full_link}")

    return recipe_links

# -------------------------------------------------------------------------
# 5. Main scraping function
# -------------------------------------------------------------------------
def scrape_all_recipes():
    recipes_data = {}

    # 5a. robots.txt
    robots_dict = parse_robots_txt(ROBOTS_TXT_URL)
    main_path = "/recipes/"
    if not is_path_allowed(main_path, robots_dict):
        logging.error("Scraping disallowed by robots.txt.")
        return {}

    # 5b. Collect all recipe links from the main recipes page
    logging.info(f"Collecting recipe links from {RECIPES_INDEX_URL}")
    all_recipe_links = get_all_recipe_links(RECIPES_INDEX_URL, robots_dict)
    logging.info(f"Total recipe links found: {len(all_recipe_links)}")

    # NOTE: If there is pagination or multiple pages with these
    # <p style="text-align:right;"> <a> ... </a>, 
    # you'd need to loop through them too, or find 'next page' links.
    # For now, we assume everything is on one page.

    # 5c. For each recipe link, scrape the content
    for link in all_recipe_links:
        logging.info(f"Scraping recipe: {link}")
        text_content = scrape_recipe(link, robots_dict)
        if text_content:
            recipes_data[link] = text_content

    return recipes_data


def main():
    logging.info("Starting recipe scraping...")
    all_recipes = scrape_all_recipes()

    # Save results to JSON
    output_file = "recipes_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_recipes, f, indent=2, ensure_ascii=False)

    logging.info(f"Scraping finished. Recipes saved to '{output_file}'.")


if __name__ == "__main__":
    main()

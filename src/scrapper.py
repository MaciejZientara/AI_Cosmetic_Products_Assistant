import os
import requests
from bs4 import BeautifulSoup
from shutil import rmtree
from pathlib import Path

dir_path = os.path.dirname(os.path.dirname(__file__))
raw_data_dir = Path(dir_path, "data/raw_data")
product_links_path = raw_data_dir + "/product_links.txt"

base_url = "https://www.rossmann.pl"
category_links = [
    "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
    "https://www.rossmann.pl/kategoria/pielegnacja-i-higiena,12001",
    # "https://www.rossmann.pl/kategoria/wlosy,13174",
    # "https://www.rossmann.pl/kategoria/mezczyzna,13224",
    # "https://www.rossmann.pl/kategoria/perfumy,13264",
    # "https://www.rossmann.pl/kategoria/dziecko,13282"
]

def clean():
    print("cleaning directory")
    rmtree(raw_data_dir) # remove directory with content

def get_product_urls():
    product_links = set()

    for cat_link in category_links:
        name = cat_link[cat_link.find("kategoria/") + 10: cat_link.find(",")]
        # print(name)
        page = 0
        while True:
            page += 1 # increase page count to find all products, regardless of category 
            try:
                response = requests.get(f"{cat_link}?Page={page}")
            except:
                break # if page not found - checked all products, exit while loop

            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if '/Produkt/' in href:
                    product_links.add(href)

    product_links = list(product_links)

    with open(product_links_path, "w") as txt_file:
        for link in product_links:
            txt_file.write(base_url + link + "\n")


def get_product_info():
    with open(product_links_path, "r") as txt_file:
        for link in txt_file: # link per line
            pass

def get_data(rescrap=False):
    if rescrap:
        clean()
    
    if os.path.exists(raw_data_dir):
        return # if data present, do not scrap again

    raw_data_dir.mkdir(parents=True, exist_ok=True)

    get_product_urls()
    get_product_info()
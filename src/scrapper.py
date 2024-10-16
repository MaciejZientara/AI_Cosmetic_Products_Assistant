import os
import json
import requests
import requests.exceptions
from bs4 import BeautifulSoup
from shutil import rmtree
from pathlib import Path

dir_path = os.path.dirname(os.path.dirname(__file__))
raw_data_dir = Path(dir_path, "data/raw_data")

USE_PROXY = False
proxies = [
    "31.42.7.177:8080",
    "145.239.86.159:8888",
    "185.28.248.238:8080",
    "77.237.28.191:8080",
    "195.8.52.207:8080",
    "188.128.254.4:3128",
    "157.25.92.74:3128",
    "91.227.66.139:8080",
    "37.220.83.232:3128",
    "37.220.83.139:3128",
    "188.252.14.7:3128",
    "79.110.200.148:8081",
    "79.110.196.145:8081 ",
    "79.110.202.131:8081",
    "79.110.201.235:8081",
    "212.127.93.185:8081",
]
proxy_iter = 0

categories = []

base_url = "https://www.rossmann.pl"
category_links = [
    "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
    # "https://www.rossmann.pl/kategoria/pielegnacja-i-higiena,12001",
    # "https://www.rossmann.pl/kategoria/wlosy,13174",
    # "https://www.rossmann.pl/kategoria/mezczyzna,13224",
    # "https://www.rossmann.pl/kategoria/perfumy,13264",
    # "https://www.rossmann.pl/kategoria/dziecko,13282"
]

def clean():
    """
    Remove raw data directory with its content.
    :return: None
    """
    print("cleaning directory")
    rmtree(raw_data_dir) # remove directory with content

def find_categories():
    """
    Parse category_links to get category names and save them in categories list.
    :return: None
    """
    global categories
    for cat_link in category_links:
        categories.append(cat_link[cat_link.find("kategoria/") + 10: cat_link.find(",")])


def check_proxies():
    """
    Check the list of available proxies, call google.com, in case of no response mark proxy as
    not working and remove from proxies list.
    :return: None
    """
    print("checking proxies")
    global proxies
    for proxy in proxies:
        try:
            requests.get("https://www.google.com/", proxies={"http": proxy, "https": proxy}, timeout=15)
        except:
            # proxy doesn't work, remove from list
            proxies.remove(proxy)
    print("working proxies count = ", len(proxies))
    print(proxies)

def proxy_req(url):
    """
    Get html response from 'url'. If USE_PROXY flag is set this function will cycle
    through proxies array and use them in request function, otherwise not use proxy.
    :param url: Link to the server to get data from.
    :return: html response of the url server
    """
    global proxy_iter
    proxy = proxies[proxy_iter] if USE_PROXY else None
    proxy_iter = (proxy_iter + 1) % len(proxies) # cycle through proxies
    return requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=15)

def get_product_urls():
    """
    Get product URLs and save them to a category_name.txt file.
    :return: None
    """
    product_links = set()

    for cat_idx,cat_link in enumerate(category_links):
        print("start working on category:", categories[cat_idx])
        page = 0
        with open(Path(raw_data_dir, categories[cat_idx]+".txt"), "w", encoding="utf8") as txt_file:
            while True:
                page += 1 # increase page count to find all products, regardless of category 
                try:
                    response = proxy_req(f"{cat_link}?Page={page}")
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"Error fetching page {page} of {cat_link}: {e}")
                    continue # skip to the next page if an error occurs

                soup = BeautifulSoup(response.text, 'html.parser')

                product_found = False # flag to track if products are found on the page
                
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    if '/Produkt/' in href:
                        product_links.add(href)
                        product_found = True # set a flag to True when a product is found

                # exit the loop if no products were found on the page
                if not product_found:
                    break

                url_list = list(product_links)
                for link in url_list:
                    txt_file.write(base_url + link + "\n")
                product_links.clear()

polish_letters = [
    ("\u0105","ą"), ("\u0104","Ą"),
    ("\u0107","ć"), ("\u0106","Ć"),
    ("\u0119","ę"), ("\u0118","Ę"),
    ("\u0142","ł"), ("\u0141","Ł"),
    ("\u0144","ń"), ("\u0143","Ń"),
    ("\u00f3","ó"), ("\u00d3","Ó"),
    ("\u015b","ś"), ("\u015a","Ś"),
    ("\u017a","ź"), ("\u0179","Ż"),
    ("\u017c","ż"), ("\u017b","Ź")
]

def fix_polish_letters(text):
    """
    Get html response from 'url'. If USE_PROXY flag is set this function will cycle
    through proxies array and use them in request function, otherwise not use proxy.
    :param url: Link to the server to get data from.
    :return: html response of the url server
    """
    for (a,b) in polish_letters:
        text = text.replace(a,b)
    return text


def get_product_info():
    """
    Find all category_name.txt file in raw data directory, for each file go through 
    all urls and save data of individual products into category_name.json files.
    :return: none
    """
    for cat in categories:
        with open(Path(raw_data_dir, cat+".json"), "w", encoding="utf8") as category_file:
            first_product = True
            category_file.write("{\n")
            with open(Path(raw_data_dir, cat+".txt"), "r", encoding="utf8") as product_links:
                for i,link in enumerate(product_links): # link per line
                    if not first_product:
                        category_file.write(",\n")
                    first_product = False
                    print("download product:",i)
                    try:
                        response = proxy_req(link)
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching {link}: {e}")
                        continue # skip to the next link if an error occurs

                    soup = BeautifulSoup(response.text, 'html.parser')
                    product_data = {}

                    # rossmann pages have 3 blocks with <p class="styles-module_productDescriptionContent--76j9I">
                    # with content as follows: description, ingridients and additional information
                    for p_iter,p_tag in enumerate(soup.find_all(name = 'p', attrs = {"class" : 'styles-module_productDescriptionContent--76j9I'})):
                        match p_iter:
                            case 0: # description
                                pass # product_data["description"] = p_tag.text.strip()
                            case 1: # ingridients
                                product_data["ingridients"] = p_tag.text.strip()
                            case 2: # additional information
                                pass # product_data["info"] = p_tag.text.strip()
                            case _:
                                print("found too many p blocks in ", link)

                    # in <meta content=... property=...> blocks you can find product name, description, price 
                    for meta_tag in soup.find_all('meta'):
                        if ("content" in meta_tag.attrs) and ("property" in meta_tag.attrs):
                            if meta_tag["property"] == "product:price:amount":
                                product_data["price"] = meta_tag["content"].strip()
                            if meta_tag["property"] == "og:description":
                                product_data["description"] = meta_tag["content"].strip()
                            if meta_tag["property"] == "og:title":
                                product_data["title"] = meta_tag["content"].strip()

                    # block <span class="styles-module_capacity--t8nUz"> XXX </span> holds capacity info, example: "20 ml"
                    for span_tag in soup.find_all(name = 'span', attrs = {"class" : 'styles-module_capacity--t8nUz'}):
                            product_data["capacity"] = span_tag.text.strip()
                    
                    category_file.write(f'"{i}" : {json.dumps(product_data, indent=3, ensure_ascii=False)}')    
            category_file.write("\n}")

def get_data(rescrap=False):
    """
    Main function in this module. If raw data directory doesn't exist this function should:
    - get all product urls for each category in category_links and store them in txt files
    - get each product data and store it in json files
    :param resrap: Flag which when set triggers removing raw data directory before gathering data.
    :return: none
    """
    if rescrap:
        clean()
    
    if os.path.exists(raw_data_dir):
        return # if data present, do not scrap again

    raw_data_dir.mkdir(parents=True, exist_ok=True)

    if USE_PROXY:
        check_proxies()

    find_categories()
    get_product_urls()
    get_product_info()
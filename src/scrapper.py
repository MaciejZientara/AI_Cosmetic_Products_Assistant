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
    print("cleaning directory")
    rmtree(raw_data_dir) # remove directory with content

def check_proxies():
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
    global proxy_iter
    proxy = proxies[proxy_iter] if USE_PROXY else None
    proxy_iter = (proxy_iter + 1) % len(proxies) # cycle through proxies
    return requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=15)

def get_product_urls(mode="w"): # mode argument no longer used, TO FIX
    """
    Get product URLs and save them to a text file.
    :param mode: Writing mode for the file. Defaults to "w" (overwrite). Use "a" to append to the file.
    :return: None
    """
    global categories
    product_links = set()

    for cat_link in category_links:
        categories.append(cat_link[cat_link.find("kategoria/") + 10: cat_link.find(",")])
        print("start working on category:", categories[-1])
        page = 0
        with open(Path(raw_data_dir, categories[-1]+".txt"), "w") as txt_file:
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




def get_product_info():
    for cat in categories:
        with open(Path(raw_data_dir, cat+".json"), "w") as category_file:
            first_product = True
            category_file.write("{\n")
            with open(Path(raw_data_dir, cat+".txt"), "r") as product_links:
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
                    
                    category_file.write(f'"{i}" : {json.dumps(product_data, indent=3)}')    
            category_file.write("\n}")

def get_data(rescrap=False):
    if rescrap:
        clean()
    
    if os.path.exists(raw_data_dir):
        return # if data present, do not scrap again

    raw_data_dir.mkdir(parents=True, exist_ok=True)

    if USE_PROXY:
        check_proxies()
    get_product_urls()
    get_product_info()
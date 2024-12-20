import os
import json
import requests
import requests.exceptions
from bs4 import BeautifulSoup
import datetime
from shutil import rmtree
from pathlib import Path
from logger import log_msg


dir_path = os.path.dirname(os.path.dirname(__file__))
raw_data_dir = Path(dir_path, "data/raw_data")

REQUEST_TIMEOUT = 20
USE_PROXY = True
proxies = []
proxy_iter = 0

categories = []

base_url = "https://www.rossmann.pl"
category_links = [
    "https://www.rossmann.pl/kategoria/makijaz-i-paznokcie,12000",
    "https://www.rossmann.pl/kategoria/pielegnacja-i-higiena,12001",
    "https://www.rossmann.pl/kategoria/wlosy,13174",
    # "https://www.rossmann.pl/kategoria/mezczyzna,13224",
    # "https://www.rossmann.pl/kategoria/perfumy,13264",
    # "https://www.rossmann.pl/kategoria/dziecko,13282"
]


def clean():
    """
    Remove raw data directory with its content.
    :return: None
    """
    log_msg("cleaning directory")
    rmtree(raw_data_dir) # remove directory with content


def find_categories():
    """
    Parse category_links to get category names and save them in categories list.
    :return: None
    """
    global categories
    for cat_link in category_links:
        categories.append(cat_link[cat_link.find("kategoria/") + 10: cat_link.find(",")])


# use of https://free-proxy-list.net/ inspired by https://github.com/hamzarana07/multiProxies
def find_proxies():
    """
    Check the list of available proxies, call rossmann.pl, in case of no response mark proxy as
    not working and do not add to proxies list.
    :return: None
    """
    log_msg("finding proxies")
    global proxies
    global proxy_iter
    proxy_iter = 0
    proxies.clear()
    working_proxies = 0
    expected_working_proxies = 5#30

    d = requests.get("https://free-proxy-list.net/")
    # ("https://www.socks-proxy.net/")
    soup = BeautifulSoup(d.content, 'html.parser')
    td_elements = soup.select('.fpl-list .table tbody tr td')
    for j in range(0, len(td_elements),8):
        ip = (td_elements[j].text.strip())
        port = (td_elements[j + 1].text.strip())
        use_https = (td_elements[j + 6].text.strip())
        if use_https == "no":
            continue

        proxy = f"{ip}:{port}"
        log_msg(f"checking proxy: {proxy}")
        try:
            response = requests.get(base_url, proxies={"http": proxy, "https": proxy}, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except:
            # proxy doesn't work
            log_msg("FAIL")
            continue

        log_msg("PASS")
        proxies.append(proxy)
        working_proxies += 1
        if working_proxies >= expected_working_proxies:
            break

    log_msg(f"working proxies count = {len(proxies)}")
    # log_msg(proxies)


def proxy_req(url):
    """
    Get html response from 'url'. If USE_PROXY flag is set this function will cycle
    through proxies array and use them in request function, otherwise not use proxy.
    Try to get response from server at most retry_count times.
    :param url: Link to the server to get data from.
    :return: On success - html response of the url server and True, on Fail - None,False 
    """
    global proxy_iter
    retry_count = 10
    while retry_count > 0:
        proxy = proxies[proxy_iter] if USE_PROXY and (len(proxies) > 0) else None
        if len(proxies) > 0:
            proxy_iter = (proxy_iter + 1) % len(proxies) # cycle through proxies
        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy}, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            log_msg(f"Error fetching {url}: {e}")
            retry_count -= 1
            continue # skip to the next link if an error occurs
        return response, True # succesfully obtained product data

    if retry_count == 0:
        return None, False # no data obtained


def proxies_failing():
    """
    Check the list of proxies, call rossmann.pl, in case of no response return True (proxies failed), 
    when all proxies pass return False.
    :return: Bool, as in description
    """
    for proxy in proxies:
        try:
            response = requests.get(base_url, proxies={"http": proxy, "https": proxy}, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except:
            return True
    return False


def get_product_urls():
    """
    Get product URLs and save them to a category_name.txt file.
    :return: None
    """
    product_links = set()

    for cat_idx,cat_link in enumerate(category_links):
        log_msg(f"start working on category: {categories[cat_idx]}")
        page = 0
        with open(Path(raw_data_dir, categories[cat_idx]+".txt"), "w", encoding="utf8") as txt_file:
            while True:
                page += 1 # increase page count to find all products, regardless of category 
                response,status = proxy_req(f"{cat_link}?Page={page}")
                if status == False:
                    continue # no data obtained

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
    """
    Find all category_name.txt file in raw data directory, for each file go through 
    all urls and save data of individual products into category_name.json files.
    Every 5 minutes check if proxies still work, if not and also every 30 minutes 
    look for new proxy servers.
    :return: none
    """
    timestamp = datetime.datetime.now()
    for cat in categories:
        with open(Path(raw_data_dir, cat+".json"), "w", encoding="utf8") as category_file:
            first_product = True
            category_file.write("{\n")
            with open(Path(raw_data_dir, cat+".txt"), "r", encoding="utf8") as product_links:
                for i,link in enumerate(product_links): # link per line
                    time_delta = datetime.datetime.now() - timestamp
                    minutes = int(time_delta.seconds / 60)
                    if minutes >= 5:
                        if proxies_failing() or (minutes >= 30):
                            find_proxies()
                            timestamp = datetime.datetime.now()

                    if not first_product:
                        category_file.write(",\n")
                    first_product = False
                    log_msg(f"download product: {i}")
                    response,status = proxy_req(link)
                    if status == False:
                        continue # no data obtained

                    soup = BeautifulSoup(response.text, 'html.parser')
                    product_data = {"url":link}

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
                                log_msg(f"found too many p blocks in {link}")

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

def is_data_present():
    return os.path.exists(raw_data_dir)

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
    
    if is_data_present():
        return # if data present, do not scrap again

    raw_data_dir.mkdir(parents=True, exist_ok=True)

    if USE_PROXY:
        find_proxies()

    find_categories()
    get_product_urls()
    get_product_info()
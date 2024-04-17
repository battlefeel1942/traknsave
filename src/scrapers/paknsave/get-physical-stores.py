import json
import os
import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

def initialize_driver():
    print("Initializing the driver...")
    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/google-chrome-stable'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    return webdriver.Chrome(options=options)

def get_content_from_paknsave(url, driver):
    print(f"Navigating to {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "h5")))
    except TimeoutException:
        print("Timed out waiting for the element to appear!")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return driver.page_source

def extract_company_locations(content):
    print("Extracting store details from the content...")
    soup = BeautifulSoup(content, 'lxml')
    store_data = []

    for region_name_tag in soup.find_all("h5"):
        region_name = region_name_tag.text.strip()
        stores_ul = region_name_tag.find_next_sibling("ul")
        if stores_ul is None:
            continue
        for store in stores_ul.find_all("li"):
            store_name_anchor = store.find("a")
            if not store_name_anchor or "href" not in store_name_anchor.attrs:
                continue
            store_name = store_name_anchor.text.strip()
            base_url = "https://www.paknsave.co.nz"
            href = store_name_anchor["href"].strip()
            store_url = href if href.startswith(base_url) else base_url + href
            directions_url_tag = store.find("a", rel="noopener noreferrer")
            directions_url = directions_url_tag["href"].strip() if directions_url_tag else None
            store_data.append({
                'Region Name': region_name,
                'Store Name': store_name,
                'Store URL': store_url,
                'Directions URL': directions_url
            })
    return store_data

def get_save_path():
    directory = os.path.join(os.getcwd(), 'company', 'paknsave')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "locations.json"
    return os.path.join(directory, filename)

def main():
    url = "https://www.paknsave.co.nz/store-finder"
    driver = initialize_driver()
    driver.set_page_load_timeout(30)  # 30 seconds

    if not driver:
        print("Failed to initialize the driver. Exiting.")
        sys.exit(1)

    try:
        content = get_content_from_paknsave(url, driver)
        if content:
            company_locations = extract_company_locations(content)
            save_path = get_save_path()
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(company_locations, f, ensure_ascii=False, indent=4)
            print(f"Store details saved to {save_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the Selenium driver.

if __name__ == "__main__":
    main()

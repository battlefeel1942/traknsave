import time
import sys
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from datetime import datetime
from bs4 import BeautifulSoup


def initialize_driver():
    try:
        print("Initializing the driver...")
        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/google-chrome-stable'
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        return webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Error initializing the driver: {e}")
        sys.exit(1)


def get_content_from_paknsave(url, driver):
    try:
        print(f"Navigating to {url}...")
        driver.get(url)

        # Step 1: Click on "Make this your store" button
        print("Waiting for the 'Make this your store' button to become clickable...")
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn--functional.is-not-selected-store-only.sxa-storedetails__header-make-this-your-store-button.js-make-this-your-store-button'))
        ).click()
        print("'Make this your store' button clicked successfully!")

        # Step 2: Click on "Deals" link
        max_retries = 5  # number of times to retry
        retries = 0
        initial_url = driver.current_url

        while retries < max_retries:
            try:
                print("Waiting for the 'Deals' link to become clickable...")
                deals_link = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Deals"]'))
                )
                print("Clicking the 'Deals' link...")
                deals_link.click()

                # Check if the URL has changed
                WebDriverWait(driver, 10).until_not(EC.url_to_be(initial_url))
                break
            except TimeoutException:
                print(f"Attempt {retries + 1}: Timeout while trying to locate/click the 'Deals' link or waiting for the page to change.")
            except WebDriverException as e:
                if 'stale element reference' in str(e):
                    print(f"Attempt {retries + 1}: Stale element reference detected. Retrying...")
                else:
                    print(f"Attempt {retries + 1}: Error executing JavaScript or interacting with the 'Deals' link.")
            retries += 1

        if initial_url == driver.current_url:
            print("Failed to navigate to the new page after multiple attempts.")
            return None

        # Additional retry mechanism for component-specials-card
        retries = 0
        max_retries = 5  # Ensure we try to find specials cards only twice
        while retries < max_retries:
            if driver.find_elements(By.CLASS_NAME, "component-specials-card"):
                print("Specials cards found on the page.")
                return driver.page_source
            else:
                print(f"Attempt {retries + 1}: Specials cards not found. Refreshing the page...")
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )  # Ensure page is reloaded properly
                retries += 1

        print("Failed to find specials cards after multiple attempts.")
        return None

    except TimeoutException:
        print("Timeout while waiting for an element.")
        return None
    except NoSuchElementException:
        print("An expected element was not found on the page.")
        return None
    except WebDriverException as e:
        print(f"WebDriver encountered an error: {e}")
        return None
    except Exception as e:
        print(f"Error encountered: {e}")
        return None
    finally:
        print("Closing the browser...")
        driver.quit()



def extract_specials(content):
    print("Extracting specials from the content...")
    soup = BeautifulSoup(content, 'lxml')
    specials_cards = soup.find_all(class_='component-specials-card')
    specials_data = []

    for card in specials_cards:
        try:
            product_name = card.find(class_='sxa-specials-card__heading').text.strip()
            limit = card.find(class_='sxa-specials-card__heading-legal').text.strip()

            # Safely get the 'multi' value if the element exists, otherwise default to None
            multi_element = card.find(class_='sxa-specials-card__pricing-multi-text')
            multi = multi_element.text.strip() if multi_element else None

            dollars = card.find(class_='sxa-specials-card__pricing-dollars').text.strip()
            cents = card.find(class_='sxa-specials-card__pricing-cents').text.strip()
            price = f"{dollars}.{cents}"
            expiry_date = card.find(class_='sxa-specials-card__expiry').text.strip()

            # Calculate purchase price based on multi information
            if multi:
                purchase_price = f"{multi} ${price}"
            else:
                purchase_price = f"${price} each"

            specials_data.append({
                'Product Name': product_name,
                'Limit': limit,
                'Multi': multi,
                'Price': price,
                'Purchase Price': purchase_price,  # Now includes logic to format based on 'multi'
                'Expiry Date': expiry_date
            })
        except AttributeError:
            print("Error parsing one of the cards, skipping.")
            continue

    print("Extraction complete!")
    return specials_data


def get_save_path_from_url(url):
    """Extract the appropriate save path from the given URL based on the current year and week."""
    # Get the current year and week number
    now = datetime.now()
    #year = now.strftime("%Y")
    #week = now.strftime("%U")  # Gets the week number of the year

    # Removing the base URL part and extracting the specific path
    path_parts = url.replace("https://www.paknsave.co.nz/", "").split("/")

    # Use a relative path, ensuring it is accessible in the context of the current working directory
    return os.path.join("company/paknsave/deals", *path_parts) + ".json"


def read_store_urls(filename="locations.json"):
    """Read store URLs from the specified JSON file located in 'company/paknsave' directory."""
    # Define the full path to the file
    file_path = os.path.join('company', 'paknsave', filename)
    
    # Open the file and load the JSON content
    with open(file_path, "r", encoding="utf-8") as file:
        stores = json.load(file)
    
    # Extract and return the 'Store URL' from each store entry in the list
    return [store["Store URL"] for store in stores]


def main(url):
    driver = initialize_driver()
    driver.set_page_load_timeout(30)  # 30 seconds
    if not driver:
        print("Failed to initialize the driver. Exiting.")
        sys.exit(1)

    content = get_content_from_paknsave(url, driver)

    if content:
        specials = extract_specials(content)
        if not specials:  # Check if the specials list is empty
            print("No specials extracted. Nothing to save.")
            return  # Exit the function early if no specials

        print("Printing extracted specials:")
        for special in specials:
            print(special)

        # Define the save path based on the URL
        save_path = get_save_path_from_url(url)

        # Ensure the directory exists before attempting to save
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Save the extracted data to a JSON file
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(specials, f, ensure_ascii=False, indent=4)
        print(f"Specials saved to {save_path}")
    else:
        print("No content retrieved from the page.")



if __name__ == "__main__":
    urls = []

    if len(sys.argv) < 2:
        # No argument provided, read all URLs from the JSON file
        urls = read_store_urls()
    else:
        urls.append(sys.argv[1])

    for url in urls:
        main(url)

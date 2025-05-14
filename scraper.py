from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import requests
import math
import time
import re
import os
import datetime
from selenium.webdriver.chrome.options import Options
import json
from collections import defaultdict


def get_current_timestamp():
    return datetime.datetime.now().isoformat()

def save_category_jsons(products):
    grouped = defaultdict(list)
    timestamp = get_current_timestamp()  # Get timestamp once for all files
    
    for product in products:
        category = product["category"]
        grouped[category].append(product)

    for category, items in grouped.items():
        filename = f"{category.lower().replace(' ', '_').replace('&', 'and')}.json"
        data = {
            "last_updated": timestamp,  # Add timestamp here
            "deals": items            # Your existing products
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"✅ Saved {len(items)} items to {filename} (updated at {timestamp})")

def start_timer():
    return time.time()

def end_timer(start_time):
    end_time = time.time()
    
    minutes_time = (end_time - start_time) / 60
    if minutes_time < 1:
        seconds_time = int(minutes_time * 60)
    else:
        seconds_time = int(60 * (minutes_time - int(minutes_time)))

    if seconds_time < 10:
        seconds_time = "0" + str(seconds_time)

    print(f"⏱️ Time taken: {int(minutes_time)}:{seconds_time} mins")

def extract_number(text):
    match = re.search(r'[\d,]+\.?\d*', text)
    if match:
        number = match.group().replace(',', '')
        return round(float(number), 2)
    else:
        return 0.00

def calculate_priority(dollar_savings, regular_price, review_count):
    if regular_price == 0:
        return 0
       
    percentage_savings = (dollar_savings / regular_price) * 100
    popularity_boost = math.log2(review_count + 1) * 25
    
    if dollar_savings >= 50:
        priority_score = (dollar_savings * 2) + (percentage_savings * 5)
    else:
        priority_score = (dollar_savings * 2) + (percentage_savings * 3)
       
    priority_score += popularity_boost
    return priority_score


def download_image(image_url, sku):
    try:
        if not os.path.exists("images"):
            os.makedirs("images")
        image_path = os.path.join("images", f"{sku}.jpg")

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_url, headers=headers, timeout=10)

        if response.status_code == 200:
            with open(image_path, "wb") as f:
                f.write(response.content)
            return f"images/{sku}.jpg"
        else:
            print(f"❌ Failed to download image for SKU {sku}: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Exception downloading image for SKU {sku}: {e}")

    return "Image Not Available"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bestbuy.com/",
}
options = Options() 
options.add_argument("--incognito")

service = Service(r"C:\Program Files\ChromeDriver\chromedriver.exe")

start_time = start_timer()


categories = {
    "Computers and Tablets": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690572663027&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690572663027_categoryid%24abcat0500000&type=page&usc=All%20Categories",
    "TVs and Home Theater": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690571929956&id=pcat17071&iht=n&ks=960&list=y&qp=soldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items%5Estorepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605&sc=Global&st=pcmcat1690571929956_categoryid%24cat00000&type=page&usc=All%20Categories",
    "Appliances": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690571281709&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690571281709_categoryid%24abcat0900000&type=page&usc=All%20Categories",
    "Cell Phones": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690572845752&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690572845752_categoryid%24abcat0800000&type=page&usc=All%20Categories",
    "Audio & Headphones": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690572899458&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690572899458_categoryid%24cat00000&type=page&usc=All%20Categories",
    "Smart Home and Wifi": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690574156432&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690574156432_categoryid%24cat00000&type=page&usc=All%20Categories",
  # "Health and Wearable Tech": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690575053038&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690575053038_categoryid%24pcmcat332000050000&type=page&usc=All%20Categories",
   "Video Games": "https://www.bestbuy.com/site/searchpage.jsp?_dyncharset=UTF-8&browsedCategory=pcmcat1690573093402&id=pcat17071&iht=n&ks=960&list=y&qp=storepickupstores_facet%3DStore%20Availability%20-%20In%20Store%20Pickup~605%5Esoldout_facet%3DAvailability~Exclude%20Out%20of%20Stock%20Items&sc=Global&st=pcmcat1690573093402_categoryid%24abcat0700000&type=page&usc=All%20Categories"
}


all_products = {category: [] for category in categories}

max_retry = 1
SLOW_METHOD_COUNT = 0
for retry in range(max_retry):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(next(iter(categories.values()), None))
    time.sleep(8)
    try:
        item_bool = driver.find_element(By.CLASS_NAME, 'offer-link')
        print(f"Annoying offer thing detected (attempt {retry+1})")
    except:
        print(f"No offer button found (attempt {retry+1}) - using fast method")
        break
    finally:
        SLOW_METHOD_COUNT += 1
        driver.quit()

SLOW_METHOD = SLOW_METHOD_COUNT >= max_retry
if SLOW_METHOD:
    print("⚠️ Using slow method (clicking each offer button)")
else:
    print("✅ Using fast method")


if not SLOW_METHOD:
    for category, base_url in categories.items():
        current_page = 1
        print(f"\n📂 Scraping Category: {category}")

        while True:
            url = f"{base_url}&cp={current_page}"
            driver.get(url)
            print(f"🔄 Loading page {current_page} for {category}")

            max_attempts, attempts = 50, 0
            previous_items = 0
            while attempts < max_attempts:
                driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(0.06)
                items = driver.find_elements(By.CLASS_NAME, 'sku-item')
                current_items = len(items)

                if current_items == previous_items:
                    attempts += 1
                else:
                    attempts = 0
                previous_items = current_items

            if len(items) == 0:
                print(f"❌ No more items found for {category} on page {current_page}")
                break

            for index, item in enumerate(items):
                try:
                    title = item.find_element(By.CLASS_NAME, 'sku-title').text

                    sku_values = item.find_elements(By.CLASS_NAME, 'sku-value')
                    sku = sku_values[1].text if len(sku_values) > 1 else "N/A"

                    # 📸 Get product image from listing page
                    try:
                        image_element = item.find_element(By.CLASS_NAME, 'product-image')
                        image_url = image_element.get_attribute("src")
                    except:
                        image_url = "Image Not Available"

                    try:
                        regular_price_text = item.find_element(By.CLASS_NAME, 'priceView-hero-price').text
                        regular_price = extract_number(regular_price_text)
                    except:
                        regular_price = 0.00

                    try:
                        member_savings_text = item.find_element(By.CLASS_NAME, 'imp-price-color').text
                        member_savings = extract_number(member_savings_text)
                    except:
                        member_savings = 0.00

                    discount_percentage = (member_savings / regular_price) * 100 if regular_price > 0 else 0

                    try:
                        review_element = item.find_element(By.CLASS_NAME, 'c-reviews')
                        review_text = review_element.get_attribute("innerText")
                        review_num = int(extract_number(review_text))
                    except:
                        review_num = 0

                    priority_score = calculate_priority(member_savings, regular_price, review_num)

                    if member_savings >= 50 or discount_percentage >= 35:
                        local_image_path = download_image(image_url, sku)
                        all_products[category].append([
                            category, title, sku, regular_price, member_savings,
                            discount_percentage, priority_score, review_num, local_image_path
                        ])
                        print(f"💸 🔥 Added Product -> {title} (${regular_price:.2f} - ${member_savings:.2f} off)")

                except Exception as e:
                    print(f"❌ Error scraping item {index+1} on page {current_page}. Error: {e}")

            current_page += 1

    print("\n✅ Scraping finished for member deals!")

else:
    driver = webdriver.Chrome(service=service, options=options)
    for category, base_url in categories.items():
        current_page = 1
        print(f"\n📂 Scraping Category: {category}")

        while True:
            url = f"{base_url}&cp={current_page}"
            driver.get(url)
            print(f"🔄 Loading page {current_page} for {category}")

            # Scroll to load all lazy-loaded items
            max_attempts, attempts = 50, 0
            previous_items = 0
            items = []
            
            while attempts < max_attempts:
                driver.execute_script("window.scrollBy(0, 250);")
                time.sleep(0.06)  # Small delay between scrolls
                
                try:
                    items = driver.find_elements(By.CLASS_NAME, 'columns')
                    current_items = len(items)
                    
                    # Check for "no results" message
                    no_results = driver.find_elements(By.CSS_SELECTOR, '.no-results-message, .no-results-found')
                    if no_results:
                        items = []
                        break
                        
                    if current_items == previous_items:
                        attempts += 1
                    else:
                        attempts = 0
                    previous_items = current_items
                    
                except Exception as e:
                    print(f"⚠️ Scroll attempt {attempts+1} failed: {str(e)}")
                    attempts += 1

            # Check if we got any items at all
            if len(items) == 0:
                print(f"❌ No items found - ending pagination at page {current_page}")
                break

            for index, item in enumerate(items):
                try:
                    # Get fresh reference to current item to avoid staleness
                    items = driver.find_elements(By.CLASS_NAME, 'columns')
                    if index >= len(items):
                        break
                    item = items[index]
                    
                    # Get title with multiple fallback methods
                    try:
                        title = WebDriverWait(item, 5).until(
                            EC.visibility_of_element_located(
                                (By.CLASS_NAME, 'product-title'))).text
                    except Exception as e:
                        print(f"  ❌ Primary title selector failed: {str(e)}")
                        # Fallback selectors
                        try:
                            title = item.find_element(
                                By.CSS_SELECTOR, '[data-testid="product-title"]').text
                        except:
                            try:
                                title = item.find_element(
                                    By.XPATH, ".//*[contains(@class,'product-title')]").text
                            except:
                                title = "Unknown Product"
                                print("  ❌ Could not find product title")

                    # Get SKU with error handling
                    try:
                        sku = WebDriverWait(item, 2).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '.product-attributes .attribute:last-child .value'))).text
                    except:
                        sku = "N/A"

                    # Get product image with error handling
                    try:
                        image_container = WebDriverWait(item, 2).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'product-image')))
                        
                        image_element = image_container.find_element(By.TAG_NAME, 'img')
                        image_url = image_element.get_attribute('src')
                        
                        if image_url and '?' in image_url:
                            image_url = image_url.split('?')[0]
                            
                        if not image_url or 'placeholder' in image_url.lower():
                            image_url = None  # Use None instead of text for missing images
                            
                    except Exception as e:
                        print(f"  ❌ Error getting product image: {str(e)}")
                        image_url = None  # Use None for error cases

                    # Get regular price with error handling
                    try:
                        regular_price_text = WebDriverWait(item, 2).until(
                            EC.visibility_of_element_located(
                                (By.CLASS_NAME, 'customer-price'))).text
                        regular_price = extract_number(regular_price_text)
                    except:
                        regular_price = 0.00

                    # Process member offers with robust error handling
                    member_savings = 0.00
                    try:
                        print(f"\n🔍 Processing item {index+1}: {title[:50]}...")
                        
                        # Click offer button with retry logic
                        try:
                            offer_button = WebDriverWait(item, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, '.offer-link')))
                            driver.execute_script("arguments[0].click();", offer_button)
                        except Exception as e:
                            print(f"  ❌ Couldn't click offer button: {str(e)}")
                            raise

                        # Wait for panel and get fresh reference
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '.c-spoke.active')))
                            offers_panel = driver.find_element(By.CSS_SELECTOR, '.c-spoke.active')
                        except Exception as e:
                            print(f"  ❌ Couldn't find offers panel: {str(e)}")
                            raise

                        # Extract savings with multiple fallbacks
                        try:
                            savings_element = WebDriverWait(offers_panel, 3).until(
                                EC.visibility_of_element_located(
                                    (By.CSS_SELECTOR, '[data-testid="membership-savings"]')))
                            member_savings_text = savings_element.text
                            member_savings = extract_number(member_savings_text)
                            print(f"  - Member savings: ${member_savings:.2f}")
                        except Exception as e:
                            print(f"  ❌ Primary savings selector failed: {str(e)}")
                            # Fallback selectors
                            try:
                                alt_element = offers_panel.find_element(
                                    By.CSS_SELECTOR, '.imp-price-color')
                                member_savings = extract_number(alt_element.text)
                            except:
                                try:
                                    alt_element = offers_panel.find_element(
                                        By.XPATH, "//*[contains(text(), 'Save an extra')]")
                                    member_savings = extract_number(alt_element.text)
                                except:
                                    print("  ❌ Could not extract member savings")
                                    offers_panel.screenshot(f"debug_offer_panel_{index}.png")

                        # Close panel with multiple fallback methods
                        try:
                            close_button = WebDriverWait(offers_panel, 3).until(
                                EC.element_to_be_clickable(
                                    (By.CSS_SELECTOR, '.brix-spoke-continue-shopping')))
                            driver.execute_script("arguments[0].click();", close_button)
                            print("  - Closing panel...")
                            
                            # Verify panel closed
                            WebDriverWait(driver, 3).until(
                                EC.invisibility_of_element_located(
                                    (By.CSS_SELECTOR, '.c-spoke.active')))
                        except Exception as e:
                            print(f"  ❌ Couldn't close panel normally: {str(e)}")
                            # Fallback 1: ESC key
                            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            time.sleep(0.5)
                            
                            # Fallback 2: Click outside
                            if driver.find_elements(By.CSS_SELECTOR, '.c-spoke.active'):
                                ActionChains(driver).move_by_offset(10, 10).click().perform()
                                time.sleep(0.5)

                    except Exception as e:
                        print(f"  ❌ Error processing offers: {str(e)}")
                        # Ensure panel is closed if something went wrong
                        if driver.find_elements(By.CSS_SELECTOR, '.c-spoke.active'):
                            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                            time.sleep(0.5)

                    # Calculate discount percentage
                    discount_percentage = (member_savings / regular_price) * 100 if regular_price > 0 else 0

                    # Get reviews with error handling
                    try:
                        review_element = WebDriverWait(item, 2).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'c-reviews')))
                        review_text = review_element.get_attribute("innerText")
                        review_num = int(extract_number(review_text))
                    except:
                        review_num = 0

                    # Calculate priority and add product if meets criteria
                    priority_score = calculate_priority(member_savings, regular_price, review_num)

                    if member_savings >= 50 or discount_percentage >= 35:
                        try:
                            local_image_path = download_image(image_url, sku)
                            all_products[category].append([
                                category, title, sku, regular_price, member_savings,
                                discount_percentage, priority_score, review_num, local_image_path
                            ])
                            print(f"💸 🔥 Added Product -> {title} (${regular_price:.2f} - ${member_savings:.2f} off)")
                        except Exception as e:
                            print(f"❌ Error saving product {title}: {str(e)}")

                except Exception as e:
                    print(f"❌ Error scraping item {index+1} on page {current_page}. Error: {e}")
                    # Refresh page if we hit multiple consecutive errors
                    if index > 0 and "no such element" in str(e):
                        driver.refresh()
                        time.sleep(3)
                        break  # Restart current page


            try:
                next_button = driver.find_element(By.CSS_SELECTOR, 'a.pagination-arrow[aria-label="Next page"]')
                
                # Check if next button is disabled
                if 'aria-disabled' in next_button.get_attribute('outerHTML') and \
                next_button.get_attribute('aria-disabled').lower() == 'true':
                    print(f"✅ Reached last page of {category} (page {current_page})")
                    break
                    
                # Or check if href attribute is missing/empty
                if not next_button.get_attribute('href'):
                    print(f"ℹ️ Next button has no href - assuming last page")
                    break
                    
            except NoSuchElementException:
                print(f"ℹ️ No next page button found - assuming last page")
                break


            current_page += 1
            time.sleep(1)  # Brief pause between pages

    print("\n✅ Scraping finished for member deals!")

unique_products = []
seen_skus = set()

for category, products in all_products.items():
    products.sort(key=lambda x: x[6], reverse=True)  # Sort by priority score descending

    for product in products:
        if product[2] not in seen_skus:  # Avoid duplicate SKUs
            seen_skus.add(product[2])
            unique_products.append(product)

json_ready_products = []

for product in unique_products:
    sku = product[2]
    json_ready_products.append({
        "category": product[0],
        "title": product[1],
        "sku": product[2],
        "price": product[3],
        "savings": product[4],
        "discount_percent": product[5],
        "priority_score": product[6],
        "reviews": product[7],
        "image_url": product[8]
    })

driver.quit()
# Save each category to its own JSON file
save_category_jsons(json_ready_products)

end_timer(start_time)
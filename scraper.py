import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://dealsheaven.in"

def fetch_deals(start_page, end_page, progress_bar=None, category_name=None):
    
    scraped_data = []
    
    if category_name:
        url = f"{BASE_URL}/category/{category_name}?page=1"
        total_pages = get_total_pages(url)
        if end_page > total_pages:
            end_page = min(end_page, total_pages)
            if start_page > end_page:
                start_page = max(1, end_page - 5)

    for current_page in range(start_page, end_page + 1):
        try:
            if category_name and category_name != "all-categories":
                url = f"{BASE_URL}/category/{category_name}?page={current_page}"
            else:
                url = f"{BASE_URL}/?page={current_page}"
            
            print(f"Fetching URL: {url}")
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"Failed to retrieve page {current_page}. Skipping...")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            all_items = soup.find_all("div", class_="product-item-detail")

            if not all_items:
                print(f"No products found on page {current_page}.")
                continue

            for item in all_items:
                product = parse_product(item)
                if product and all(value != "N/A" and value is not None for value in product.values()):
                    scraped_data.append(product)
                
            if progress_bar:
                progress = (current_page - start_page + 1) / (end_page - start_page + 1)
                progress_bar.progress(progress)

            time.sleep(1)
                
        except Exception as e:
            print(f"Error on page {current_page}: {e}")
            
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        save_to_csv(df, "deals.csv")

    return pd.DataFrame(scraped_data)

def parse_product(item):
    product = {}
    try:
        discount = item.find("div", class_="discount")
        product['Discount'] = discount.text.strip() if discount else "N/A"

        link = item.find("a", href=True)
        product['Link'] = link['href'] if link else "N/A"

        image = item.find("div", class_="product-img").find('img')
        raw_image_url = image['data-src'] if image else "https://via.placeholder.com/200"
        product['Image'] = raw_image_url.replace(" ", "%20")

        details_inner = item.find("div", class_="deatls-inner")

        title = details_inner.find("h3", title=True) if details_inner else None
        product['Title'] = title['title'].replace("[Apply coupon] ", "").replace('"', '') if title else "N/A"

        price = details_inner.find("p", class_="price") if details_inner else None
        product['Price'] = f"₹{price.text.strip().replace(',', '')}" if price else "N/A"

        s_price = details_inner.find("p", class_="spacail-price") if details_inner else None
        product['Special Price'] = f"₹{s_price.text.strip().replace(',', '')}" if s_price else "N/A"

        rating = details_inner.find("div", class_="star-point") if details_inner else None
        product['Rating'] = "N/A"
        if rating:
            style_width = rating.find("div", class_="star")
            if style_width:
                percent = style_width.find("span", style=True)
                if percent:
                    width_percentage = int(percent['style'].split(":")[1].replace('%', '').strip())
                    stars = round((width_percentage / 100) * 5, 1)
                    product['Rating'] = stars

        store = details_inner.find("div", class_="esite-logo") if details_inner else None
        product["Store"] = store.find("img", alt=True)["alt"].strip() if store and store.find("img", alt=True) else "N/A"
        
    except Exception as e:
        print(f"Error parsing product: {e}")
        return None

    return product

def save_to_csv(dataframe, filename="deals.csv"):
    try:
        print(f"Saving DataFrame with shape {dataframe.shape} to {filename}...")
        dataframe.to_csv(filename, index=False, encoding="utf-8")
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def get_total_pages(url):
    print(f"Fetching total pages for: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to retrieve page for {url}. Skipping...")
            return 1

        soup = BeautifulSoup(response.text, "html.parser")
        pagination = soup.find("ul", class_="pagination")
        
        if not pagination:
            print("No pagination found.")
            return 1

        page_links = pagination.find_all("a", class_="page-link")
        page_numbers = [int(re.search(r'page=(\d+)', link.get("href")).group(1)) for link in page_links if re.search(r'page=(\d+)', link.get("href"))]

        if page_numbers:
            max_page = max(page_numbers)
            print(f"Total pages: {max_page}")
            return max_page
        
        print("No valid page numbers found.")
        return 1

    except Exception as e:
        print(f"Error fetching total pages for {url}: {e}")
        return 1

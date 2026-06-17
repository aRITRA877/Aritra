import streamlit as st
import pandas as pd
from scraper import fetch_deals
import urllib.parse

# Category dictionary mapping display names to URL-friendly names
CATEGORY_MAP = {
    "All Categories": "all-categories",
    "Automotive": "automotive",
    "Baby Care & Toys": "baby-care-and-toys",
    "Bags, Wallets & Luggage": "bags-wallets-and-luggage",
    "Beauty & Personal Care": "beauty-and-personal-care",
    "Books & Stationery": "books-stationery",
    "Cameras & Camera Accessories": "cameras-camera-accessories",
    "Clothing Fashion & Apparels": "clothing-fashion-apparels",
    "Computers, Laptops & Accessories": "computers-laptops-accessories",
    "Electronics": "electronics",
    "Food, Entertainment & Services": "food-entertainment-services",
    "Footwears": "footwears",
    "Freebies": "freebies",
    "Grocery": "grocery",
    "Headphone, Speakers & Soundbar": "headphone-speakers-soundbar",
    "Home Decor & Furnishing": "home-decor-furnishing",
    "Home Entertainment: LED, LCD TV": "home-entertainment-led-lcd-tv",
    "Home Kitchen Appliances": "home-kitchen-appliances",
    "Mobiles & Mobile Accessories": "mobiles-mobile-accessories",
    "Musical Instruments": "musical-instruments",
    "Others": "others",
    "Pets": "pets",
    "Recharge": "recharge",
    "Software Games": "software-games",
    "Sports, Fitness, Outdoor & Health": "sports-fitness-outdoor-health",
    "Travel Bus & Flight": "travel-bus-flight",
    "Vouchers & Gift Card": "vouchers-gift-card",
    "Webhosting & Domain Services": "webhosting-domain-services"
}

# Configure the Streamlit app
st.set_page_config(page_title="Deals Hunter", page_icon=":moneybag:", layout="wide")

# Custom CSS to center the website's title and slogan at the top of the page
st.markdown("""
    <style>
        /* Center the page title and slogan */
        .header-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: -60px;
            margin-bottom: 10px;
        }

        .header-container h1 {
            font-size: 36px;
            font-weight: bold;
            color: #333;
            margin-top: -20px;
        }

        .header-container p {
            font-size: 18px;
            color: #777;
            margin-top: 5px;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            width:100%;
            justify-content: space-evenly;
        }
        .deal-box {
            border: 1px solid #ddd;
            padding: 5px;
            width: 230px;
            height: 350px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: #fff;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .deal-box img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 5px;
        }
        .deal-box h4 {
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            height: 35px;  /* Limiting height of the title */
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;  /* Prevents wrapping to next line */
            display: flex;
        }
        .deal-box p {
            font-size: 14px;
            margin: 5px 0;
            flex-grow: 1;  /* Ensures the slogan is at the bottom */
        }
        .deal-box a {
            display: inline-block;
            margin-top: 5px;
            color: #007bff;
            text-decoration: none;
            font-size: 14px;
        }
        .deal-box:hover {
            transform: scale(1.05) translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            border-color: #d42626;
        }
        img {
        visibility: visible;
        opacity: 1;
        transition: opacity 0.5s;
        }
        @media (max-width: 768px) {
            .deal-box {
                width: 45%;
            }
        }
        @media (max-width: 480px) {
            .deal-box {
                width: 100%;
            }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
        <div class="header-container">
            <h1>🎯Deals Hunter</h1>
            <p>Your Ultimate Deals Finder!</p>
        </div>
    """, unsafe_allow_html=True)

# Input section
with st.container():
    input_cols = st.columns([2, 2, 4, 6, 4])
    
    stores = input_cols[2].selectbox(
        "Select Store",
        ("All Stores", "Flipkart", "Amazon", "Paytm", "FoodPanda", "FreeCharge", "Paytm Mall"),
    )
    categories = input_cols[3].selectbox(
        "Choose Category", 
        list(CATEGORY_MAP.keys())  # Use the keys from the CATEGORY_MAP
    )

    start_page = input_cols[0].number_input("Start", min_value=1, max_value=1703)
    end_page = input_cols[1].number_input("End", min_value=1, max_value=1703)


    if start_page > end_page:
        st.error("Starting page must be less than or equal to ending page.")
    else:
        input_cols[4].write("\n" * 5)
        input_cols[4].write("\n" * 3)
        if input_cols[4].button("Fetch Deals", key="scrape"):
            try:
                progress_bar = st.progress(0)
                # Get the corresponding URL-friendly category from the dictionary
                category_url = CATEGORY_MAP[categories]
                scraped_data = fetch_deals(start_page, end_page, progress_bar, category_name=category_url)

                if scraped_data.empty:
                    st.warning("No deals found.")
                else:
                    if stores != 'All Stores':
                        scraped_data = scraped_data[scraped_data['Store'] == stores]
                    
                    if scraped_data.empty:
                        st.warning(f"No deals found for {stores}. Please try another store or category.")
                    
                    # Create a container for displaying the deals
                    if not scraped_data.empty:
                        st.write("### Found Deals")
                    with st.container():
                        # Display products in a flexible grid
                        num_products = len(scraped_data)
                        cols = st.columns(5)  # Display up to 5 products per row

                        for i in range(0, num_products, 5):
                            row_products = scraped_data.iloc[i:i + 5]
                            for j, product in enumerate(row_products.itertuples(), 1):
                                with cols[j - 1]:
                                    print(product)
                                    # Deal box container
                                    st.markdown(f"""
                                        <div class="deal-box">
                                            <img src="{product.Image}" alt="Product Image" loading = "Lazy" onerror="this.src='https://via.placeholder.com/150?text=No+Image';">
                                            <h4>{product.Title}</h4>
                                            <p><strong>Price:</strong> {product.Price}</p>
                                            <p><strong>Discount:</strong> {product.Discount}</p>
                                            <p><strong>Rating:</strong> {product.Rating}</p>
                                            <a href="{product.Link}" target="_blank">View Deal</a>
                                        </div>
                                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                

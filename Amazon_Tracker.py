# python D:\python\PriceTracker\BB_GPUTracker.py
import requests
import os
import pandas as pd
from discord import Webhook, RequestsWebhookAdapter
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
import concurrent.futures

# Product Title = productName_3nyxM
product_list = []

load_dotenv()
WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DIR = os.getenv('DIR')
USER_AGENT = os.getenv('USER_AGENT')
os.chdir(DIR)

headers = {
        "User-Agent": USER_AGENT}

def main():
    print("Welcome to the Amazon Tracker!")

    # Load URL List of products
    global product_list
    product_list = load_products()
    time.sleep(2)
    access_url()


def access_url():
    # Let's access URLs
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_page, product_list)
        time.sleep(5)
        print('--------------------------------------------------------------------')


def process_page(url):
    # Process HTML page
    page = requests.get(url, headers=headers)
    bs = BeautifulSoup(page.content, 'html.parser')

    # Get product's title
    product_title = bs.find_all(class_="productName_3nyxM")
    title_text = product_title[0].get_text()

    # Get product's price
    product_price = bs.find_all(class_="large_3aP7Z")
    price_text = product_price[0].get_text()

    # Get product's availability message
    product_availability = bs.find_all(class_="availabilityMessage_ig-s5")
    product_availability_text = product_availability[0].get_text().lower()

    # Check if a product is available or out of stock
    if product_availability_text == "available to ship":
        status = "Available to Ship"
        discord_post(title_text, url)
    elif product_availability_text == "coming soon":
        status = "Coming Soon"
    elif product_availability_text == "sold out online":
        status = "Sold out online"
    else:
        status = "No info"

    print(f'{title_text}           {price_text}     {status}')

    # Post a message on Discord via Bot


def discord_post(title, url):
    webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())
    webhook.send(f"@everyone {title}\n{url}")

    # load product list from the .txt file


def load_products():
    doc = open('BB_list.txt')
    products = doc.read()
    products = products.split('\n')
    product_list.append(products)
    return products


if __name__ == '__main__':
    main()

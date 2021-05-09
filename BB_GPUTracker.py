import requests
import os
import discord
#from dotenv import load_dotenv
from Discord_Bot import disc_post
#import smtplib
#import ssl
import time
from bs4 import BeautifulSoup

# Product Title = productName_3nyxM
email = ''
product_list = ''
os.chdir(r'D:\python\PriceTracker')


def main():
    print("Welcome to the Best Buy GPU Tracker!")

    # Load URL List of products
    global product_list
    product_list = load_products()

    time.sleep(2)
    main_menu()


def main_menu():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}

    # Let's access URL
    for i in range(5):
        for x in range(len(product_list)):
            process_page(product_list[x], headers)
        time.sleep(10)
        print('\n\n')


def process_page(url, headers):
    page = requests.get(url, headers=headers)
    bs = BeautifulSoup(page.content, 'html.parser')

    product_title = bs.find_all(class_="productName_3nyxM")
    title_text = product_title[0].get_text()

    product_price = bs.find_all(class_="large_3aP7Z")
    price_text = product_price[0].get_text()

    product_availability = bs.find_all(class_="availabilityMessage_ig-s5")
    product_availability_text = product_availability[0].get_text().lower()

    if product_availability_text == "available to ship":
        status = "Available to Ship"
        disc_post(title_text, url)
    elif product_availability_text == "coming soon":
        status = "Coming Soon"
    else:
        status = "No info"
    print(f'{title_text}           {price_text}     {status}')


def load_products():
    doc = open('products.txt')
    products = doc.read()
    products = products.split('\n')
    return products


if __name__ == '__main__':
    main()

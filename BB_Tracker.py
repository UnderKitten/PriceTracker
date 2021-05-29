# python D:\python\PriceTracker\BB_Tracker.py
from os import read, write
import requests
import os.path
import csv
from discord import Webhook, RequestsWebhookAdapter
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
import concurrent.futures

# Product Title = productName_3nyxM
product_dict = {}
urls = []
snoozed_list = []
file_name = 'BB_list.csv'

disc_post = False
DELAY = 11
load_dotenv()
WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DIR = os.getenv('DIR')  # D:\python\PriceTracker
# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36
USER_AGENT = os.getenv('USER_AGENT')
os.chdir(DIR)

headers = {
    "User-Agent": USER_AGENT}


def main():
    # Load URL List of products
    load_products()
    menu()


def menu():
    # Main Menu
    global disc_post
    print('')
    print("Welcome to Best Buy CA price tracker")
    print("Please choose one of the options")
    menu_options = "A - Add products to the tracking list\nR - Delete products from the menu list\nS - Start tracking\nAny other key - Exit the script\nYour option: "
    option = input(menu_options)
    option = option.lower()
    if option == 'a':
        add_products()
    elif option == 'r':
        remove_products()
    elif option == 's':
        disc_post = True
        access_url()
    else:
        exit()

def snooze():
    global disc_post
    disc_post = False    
    time.sleep(DELAY)
    snoozed_list.clear()
    disc_post = True

def access_url():
    # Let's access URLs
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_page, urls)
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
        if disc_post == True:
            if title_text not in snoozed_list:
                snoozed_list.append(title_text)
                discord_post(title_text, url)
    elif product_availability_text == "coming soon":
        status = "Coming Soon"
    elif product_availability_text == "sold out online":
        status = "Sold out online"
    else:
        status = "No info"

    print(f'{title_text}           {price_text}     {status}')

    return [title_text, price_text, url, status]


def discord_post(title, url):
    # Post a message on Discord via Bot
    webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())
    webhook.send(f"@everyone {title}\n{url}")


def add_products():
    while True:
        new_product = input(
            'Copy/Paste an URL of a product (Exit for exit): ')
        new_product = new_product.lower()
        if new_product == 'exit':
            menu()
            break
        else:
            add_products_in_file(new_product)


def add_products_in_file(url):
    # Add new products in csv
    with open(file_name, 'r+', newline='') as csvfile:
        next(csvfile)
        filewriter = csv.writer(csvfile)
        new_info = process_page(url)
        product_dict[new_info[0]] = [new_info[1], new_info[2], new_info[3]]
        urls.append(url)
        filewriter.writerow(
            [new_info[0], new_info[1], new_info[2], new_info[3]])


def remove_products():
    # remove products
    print('')
    item = 0
    for product in product_dict.keys():
        print(f'{item} - {product}')
        item += 1
    remove_choice = input("Which product would you like to remove? - ")
    if remove_choice == 'exit':
        menu()
        return
    remove_choice = int(remove_choice)
    product_list = list(product_dict)
    print(product_list[remove_choice])
    product_dict.pop(product_list[remove_choice])
    urls.pop(remove_choice)
    update_file()
    menu()


def update_file():
    # Update .csv file
    with open(file_name, 'r+', newline='') as csvfile:
        csvfile.truncate()
        columns = ['Product Name', 'Price', 'URL', 'Availability']
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer = csv.writer(csvfile)
        writer.writerow('')
        for key, value in product_dict.items():
            writer.writerow(
                [key, value[0], value[1], value[2]])


def load_products():
    # Create a new .csv file if it does not exist
    if not os.path.exists(file_name):
        with open(file_name, 'w') as csvfile:
            columns = ['Product Name', 'Price', 'URL', 'Availability']
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
    # Load products from .csv file
    else:
        with open(file_name) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            next(reader)
            next(reader)

            global product_dict
            product_dict = {rows[0]: [rows[1], rows[2], rows[3]]
                            for rows in reader}
    for k, v in product_dict.items():
        urls.append(v[1])


if __name__ == '__main__':
    main()

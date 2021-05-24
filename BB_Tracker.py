# python D:\python\PriceTracker\BB_Tracker.py
import requests
import os.path
import csv
from discord import Webhook, RequestsWebhookAdapter
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
import concurrent.futures

# Product Title = productName_3nyxM
product_list = {}
file_name = 'BB_list.csv'

load_dotenv()
WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DIR = os.getenv('DIR')
USER_AGENT = os.getenv('USER_AGENT')
os.chdir(DIR)

headers = {
    "User-Agent": USER_AGENT}


def main():
    # Load URL List of products
    load_products()
    # time.sleep(2)
    # access_url()
    menu()



def menu():
    # Main Menu
    print("Welcome to Best Buy CA price tracker")
    print("Please choose one of the options")
    menu_options = "A - Add products to the tracking list\nR - Delete products from the menu list\nS - Start tracking\nAny other key - Exit the script\nYour option: "
    option = input(menu_options)
    option = option.lower()
    if option == 'a':
        add_products()
    elif option == 'r':
        pass
    elif option == 's':
        pass
    else:
        exit()


def access_url():
    # Let's access URLs
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_page, product_list)
        time.sleep(5)
        print('--------------------------------------------------------------------')


def process_page(url, add):
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

    if add:
        return [title_text, price_text, url, status]


def discord_post(title, url):
    # Post a message on Discord via Bot
    webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())
    webhook.send(f"@everyone {title}\n{url}")


def add_products():
    while True:
        new_product = input('Copy/Paste an URL of a product: ')
        new_info = process_page(new_product, True)

        with open(file_name, 'r+', newline='') as csvfile:
            next(csvfile)
            filewriter = csv.writer(csvfile)
            filewriter.writerow([new_info[0], new_info[1], new_info[2], new_info[3]])
            csvfile.close()

        choice = input("Would you want to add more? Y/N: ")
        if choice.lower() == 'y':
            continue
        else:
            load_products()
            break
    menu()


def remove_products():
    item = 0
    for products in product_list.items():
        print(f'{item} - {products}')
        item += 1
    pass


def load_products():
    # Create a new .csv file if it does not exist
    if not os.path.exists(file_name):
        with open(file_name, 'w') as csvfile:
            columns = ['Product Name', 'Price', 'URL', 'Availability']
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            #filewriter = csv.writer(
                #csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            #filewriter.writerow(
            csvfile.close()
                
    # Load products from .csv file
    else:
        with open(file_name) as csvfile:
            reader = csv.reader(csvfile)
            row_count = sum(1 for row in reader)
            if row_count <= 1:
                return
            next(reader)
            for line in reader:
                product_list[line[0]].extend([line[1], line[2], line[3]])
            csvfile.close()

if __name__ == '__main__':
    main()

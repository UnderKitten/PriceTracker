import requests
import os
from bs4 import BeautifulSoup

# https://www.bestbuy.ca/en-ca/product/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6x-video-card/15084753
# Product Title = productName_3nyxM
email = ''

os.chdir(r'D:\python\PriceTracker')


def main():
    print("Welcome to the Best Buy GPU Tracker!")
    email = load_email()
    # main_menu()


def main_menu():
    # option = int(input("""Please choose an option:\n
    # 1 - Track an item \n"""))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    # Let's access URL
    while True:
        url = input("Enter URL: ")
        if url == "exit":
            break
        else:
            process_page(url, headers)
    #url = "https://www.bestbuy.ca/en-ca/product/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6x-video-card/15084753"


def process_page(url, headers):
    page = requests.get(url, headers=headers)
    bs = BeautifulSoup(page.content, 'html.parser')

    product_title = bs.find_all(class_="productName_3nyxM")
    print(product_title[0].get_text())

    product_price = bs.find_all(class_="large_3aP7Z")
    print(product_price[0].get_text())

    product_availability = bs.find_all(class_="availabilityMessage_ig-s5")
    product_availability_text = str(product_availability[0].get_text().lower())

    if product_availability_text == "available to ship":
        print("Available to Ship")
    elif product_availability_text == "coming soon":
        print("Coming Soon")
    else:
        print("No info")
    print('')


def load_email():
    doc = open('email.txt')
    user_info = doc.read()
    user_info = user_info.split('+')
    return user_info


if __name__ == '__main__':
    main()

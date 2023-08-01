import requests
from bs4 import BeautifulSoup

# class CryptoScraper which will be responsible to scrape the name and price of cryptocurrencies and precious metals
class CryptoScraper:
    def __init__(self):
        self.__crypto_url = "https://crypto.com/price"
        self.__gold_url = "https://crypto.com/price/golden-token"
        self.__silver_url = "https://crypto.com/price/silver-token"
        # List which will contain the name and prices of the product scraped from the web
        self.__crypto_list = []
        # List which will ontain the name and prices of the products from the back-up file
        self.__products_list = []

    # Getter for crypto url
    def get_crypto_url(self):
        return self.__crypto_url

    # Getter for gold url
    def get_gold_url(self):
        return self.__gold_url

    # Getter for silver url
    def get_silver_url(self):
        return self.__silver_url

    # Getter for crypto list
    def get_crypto_list(self):
        return self.__crypto_list

    # Function that will scrape the name and price of cryptocurrencies from the web
    def crypto_scrape(self):
        req = requests.get(self.get_crypto_url())
        soup = BeautifulSoup(req.content, "html.parser")

        # Getting the names p tags
        names = soup.find_all('p', class_='chakra-text css-rkws3')

        # Getting the prices p tags
        prices = soup.find_all('p', class_='chakra-text css-13hqrwd')

        # Iterating through the names and prices simultaneously
        for name, price in zip(names, prices):
            # Getting the name text
            name_text = name.get_text()
            # Getting the price text
            price_text = price.get_text()
            # Removing extra characters from the price text ($, ',')
            price_text_without_extra_characters = price_text.replace("$", "").replace(",", "")
            # Adding the name and price text to the crypto list
            self.__crypto_list.append([f"{name_text} {price_text_without_extra_characters}"])

    # Function that will scrape the name and price of gold from the web
    def gold_scrape(self):
        req = requests.get(self.get_gold_url())
        soup = BeautifulSoup(req.content, "html.parser")

        # Getting the name h1 tag
        names = soup.find('h1', class_='chakra-heading css-spkkpi')

        # Getting the price span tag
        prices = soup.find('span', class_='chakra-text css-13hqrwd')

        for name, price in zip(names, prices):
            # Getting the name text
            name_text = name.get_text()
            # Getting the price text
            price_text = price.get_text()
            # Removing extra characters from the price text ($, ',', USD)
            price_text_without_extra_characters = price_text.replace("$", "").replace(",", "").replace("USD", "")
            # Adding the name and price text to the crypto list
            self.__crypto_list.append([f"{name_text} {price_text_without_extra_characters}"])

    # Function that will scrape the name and price of silver from the web
    def silver_scrape(self):
        req = requests.get(self.get_silver_url())
        soup = BeautifulSoup(req.content, "html.parser")

        # Getting the name h1 tag
        names = soup.find('h1', class_='chakra-heading css-spkkpi')

        # Getting the price span tag
        prices = soup.find('span', class_='chakra-text css-13hqrwd')

        for name, price in zip(names, prices):
            # Getting the name text
            name_text = name.get_text()
            # Getting the price text
            price_text = price.get_text()
            # Removing extra characters from the price text ($, ',', USD)
            price_text_without_extra_characters = price_text.replace("$", "").replace(",", "").replace("USD", "")
            # Adding the name and price text to the crypto list
            self.__crypto_list.append([f"{name_text} {price_text_without_extra_characters}"])

    # Function that will read the information found in the crypto list and write them into a file for backup
    def write_to_file(self):
        # Error handling to see if the fil exist
        try:
            file = open("product-list.txt", "w")
        except FileNotFoundError:
            print("File Not Found")
        else:
            # Iterating through each crypto information
            for product in self.__crypto_list:
                # Appending a newline character
                product.append("\n")
                # Write the information to the file
                file.writelines(product)
            # Closing the file
            file.close()

    # Function that will start scraping the information from the web
    def start(self):
        self.gold_scrape()
        self.silver_scrape()
        self.crypto_scrape()
        self.write_to_file()

    # Function that will read the content of the product-list file
    # to fetch the information bout the cryptos & precious metals
    def read_from_file(self):
        # Error handling to check if the file exist
        try:
            file = open("product-list.txt", "r")
        except FileNotFoundError:
            print("File Not Found")
        else:
            # Reading the content of the file
            content = file.readlines()

            # Iterating through each line of the file
            for lines in content:
                # Splitting the element of the lines list
                elements = lines.split(" ")
                # Fetching the names
                name = elements[0]

                # Checking if the name of the product is Golden or Silver
                if name == "Golden" or name == "Silver":
                    # Fetching the price (found at the second to last index position)
                    price = elements[-2]
                    # Fetching the full name
                    name = elements[0:-2]
                else:
                    # Fetching the price for the cryptocurrencies(last element)
                    price = elements[-1]
                    # Fetching the full name
                    name = elements[0:-1]
                # Joining the full name and price with a space between them
                # Appending it to the products list
                self.__products_list.append([" ".join(name), price])

            # Returning the products-list
            return self.__products_list


from socket import *
import pickle
import Database.dbms as database
import Web.scraping as scraper
from tkinter import messagebox

HOST = '127.0.0.1'
PORT = 5001
BUFSIZE = 7168

db = database.Database()

# Function that will send an object to the client
def send_to_client(client_ref, obj):
    # Converting the object into a byte-stream
    data = pickle.dumps(obj)

    # Sending it to the client
    client_ref.sendall(data)

# Function that will handle the communication set between the server and the client
def communicate_with_client(client_ref, host, port):
    # Displaying client's host and port
    print(f"Received connection from {host} ({port})\n")
    print(f"Connection Established. Connected from: {host}")

    # Scraping crypto information like name and prices from the web
    crypto_scraper = scraper.CryptoScraper()
    # starting to scrape
    crypto_scraper.start()

    # Error handling - to catch network related errors
    try:
        while True:
            # Getting the serialized object from the client
            received_data = client_ref.recv(BUFSIZE)

            # If we didn't receive anything, we break
            if not received_data:
                break

            # Deserialized the shopping cart object
            received_object = pickle.loads(received_data)

            # Displaying what we received from the client
            print(f":We received from Client:: {received_object}")

            # Fetching the instruction from the object the client sent
            instruction = received_object[0]

            # Instruction is to sign the user up
            if instruction == "sign-up":
                # Retrieve data from the object sent by the client
                username = received_object[1]
                password = received_object[2]
                total_cash = received_object[3]

                # Adding the user to the user's table database
                # Using add_user() method from the dbms module
                user = db.add_user(username, password, total_cash)

                # Fetching the newly created user
                send_to_client(client_ref, user)

            # Instruction is either pay-in or withdraw
            elif instruction == "pay-in" or instruction == "withdraw":
                # Retrieve data from the object sent by the client
                amount = received_object[1]
                user_id = received_object[2]

                # Updating the user's account balance in the user's table
                # Using the set_money() method in the dbms module
                db.set_money(amount, user_id)

            # Instruction is transactions
            elif instruction == "transactions":
                # Fetching the user id from the object the client sent
                user_id = received_object[1]

                # Fetching of all the transactions the user made
                records = db.fetch_transaction(user_id)

                # Sending it the client
                send_to_client(client_ref, records)

            # Instruction is users
            elif instruction == "users":
                # Fetching all the users from the database
                users = db.select_all_user()

                # Sending the users to the client
                send_to_client(client_ref, users)

            # Instruction is 'invest'
            elif instruction == "invest":
                # Retrieve data from the received object
                user_id = received_object[1]
                user_money = round(float(received_object[2]), 2)
                product_name = received_object[3]
                dop = received_object[4]
                option = received_object[5]
                quantity = received_object[6]
                cost = received_object[7]
                profit = received_object[9]

                # Adding in the transaction table
                db.add_transaction(user_id, product_name, dop, option, quantity, cost)

                # Updating user's money amount
                db.set_money(user_money, user_id)

                # The option is 'BUY'
                if option == "BUY":
                    # Getting the total_money_spent value from the object the client sent
                    total_money_spent = received_object[8]

                    # Updating the value of total money spent in the user's table for that user
                    db.set_total_money_spent(total_money_spent, user_id)

                    # Updating the profit in the user's table for that user
                    db.set_profit(profit, user_id)
                else:
                    # Else the option is 'SELL'
                    # Getting the total_money_gain value from the object the client sent
                    total_money_gain = received_object[8]
                    # Updating the value of total money gain in the user's table for that user
                    db.set_total_money_gained(total_money_gain, user_id)
                    # Updating the profit in the user's table for that user
                    db.set_profit(profit, user_id)

            # Instruction is 'product-list'
            elif instruction == "product-list":
                # Sending the product list to the client
                send_to_client(client_ref, crypto_scraper.read_from_file())

    except ConnectionAbortedError:
        # If the connection is aborted, show an error message
        messagebox.showerror(title="Connection Error", message="It seems the connection was aborted.\nRestart the server")
    finally:
        # Finally close the communication with the close
        client_ref.close()

# Starting the server
def start_server():
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(10)

    # Printing a message that the server is waiting for a connection
    print("Waiting for connection")

    # While there is a communication with a client
    while True:
        client, (host, port) = s.accept()
        # Communicate with the server
        communicate_with_client(client, host, port)


if __name__ == '__main__':
    start_server()








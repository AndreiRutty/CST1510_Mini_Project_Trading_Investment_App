import cryptography.fernet
import mysql.connector as mysql
import uuid
import random
from Database.encoding import *

# class Database that will act as a database management system
# It will perform tasks such as selecting records, adding records, update records amongst others
class Database:
    def __init__(self):
        # Establishing a connection with the database
        self.__db = mysql.connect(
            host="localhost",
            user="root",
            password="andreirutty1502",
            database="miniproject"
        )

        self.__cursor = self.__db.cursor()

        self.encrypted_password = ""
        self.decrypted_password = ""

    # This function will add a user into the User table in the database
    def add_user(self, username, password, totalcash):
        # Checking if user inputted a username and password
        if username != "" or password != "":
            # Creating a user id
            user_id = create_id()

            # Encrypting the password to be input in the database
            self.encrypted_password = encrypt(password)

            # Adding the user to the table User
            # Query
            query_user_table = "INSERT INTO User (userID, username, password, totalcash) VALUES (%s, %s, %s, %s)"
            # Value
            values_user_table = (user_id, username, self.encrypted_password, totalcash)

            # Executing the query
            self.__cursor.execute(query_user_table, values_user_table)

            # Committing the changes
            self.__db.commit()

            # Selecting the user to check if it was successfully added
            user = self.select_specific_user(username)

            # Returning the user
            return user

    # This function will select all users from the User table
    def select_all_user(self):
        # Selecting all users
        self.__cursor.execute("SELECT * FROM User")
        # Fetching the users
        users = self.__cursor.fetchall()
        # Returning the users
        return users

    # This function will check if a specific user exist in the User's table
    def check_user(self, username, password):
        # Executing the query
        self.__cursor.execute("SELECT username, password FROM User")

        # Fetching the user
        users_db = self.__cursor.fetchall()

        # Checking the user is found
        found = False

        # Variable that will store the credential of the user to be checked
        user_to_be_check = (username, password)

        for user in users_db:
            # Fetching the user's password in encrypted form
            encrypted_password = user[1]

            # Error handling for decrypting the password
            try:
                # Decrypting the password
                decrypted_password = decrypt(encrypted_password)
            except cryptography.fernet.InvalidToken:
                # If we get an invalid decryption token/key, we can't log in the user
                found = False
            else:
                # Variable that will store the user's credential from the database with its password decrypted
                current_user = (user[0], decrypted_password)

                # Checking if the credentials match
                if current_user == user_to_be_check:
                    # If they match, the user's is found
                    found = True
                    # Breaking out of the loop
                    break

        # Returning found
        return found

    # This function will select a specific user in the database
    # This function will be used when signing up the user to see if it was successfully added
    def select_specific_user(self, username):
        # Query
        query = f"SELECT userid, username, totalcash, totalmoneyspent, totalmoneygain, profit " \
                f"FROM User " \
                f"WHERE username='{username}'"

        # Executing the query
        self.__cursor.execute(query)

        # Fetching the user
        user = self.__cursor.fetchone()

        # Returning the user
        return user

    # This function will update the total cash attribute of a user
    def set_money(self, amount, user_id):
        # Query
        query = f"UPDATE User SET totalcash={amount} WHERE userid='{user_id}'"

        # Executing the query
        self.__cursor.execute(query)

        # Committing the changes to the database
        self.__db.commit()

    # This function will update the total money spent attribute of a user
    def set_total_money_spent(self, amount, user_id):
        # Query
        query = f"UPDATE User SET totalmoneyspent={amount} WHERE userid='{user_id}'"
        # Executing the query
        self.__cursor.execute(query)
        # Committing changes to the datbase
        self.__db.commit()

    # This function will update the total money gained attribute of a user
    def set_total_money_gained(self, amount, user_id):
        # Query
        query = f"UPDATE User SET totalmoneygain={amount} WHERE userid='{user_id}'"
        # Executing the query
        self.__cursor.execute(query)
        # Committing changes to the database
        self.__db.commit()

    # This function will update the profit attribute of a user
    def set_profit(self, amount, user_id):
        # Query
        query = f"UPDATE User SET profit={amount} WHERE userid='{user_id}'"
        # Executing the query
        self.__cursor.execute(query)
        # Committing the changes to the database
        self.__db.commit()

    # Function that will add transaction to the transaction table
    def add_transaction(self, user_id, name, dop, option, quantity, cost):
        # Creating a transaction id
        transaction_id = create_transaction_id()

        # Adding into the transaction table
        query_1 = f"INSERT INTO Transaction (transactionID, cryptoname, dop, t_option, quantity, cost) VALUES (%s, %s, %s, %s, %s, %s)"
        values_1 = (transaction_id, name, dop, option, quantity, cost)
        self.__cursor.execute(query_1, values_1)

        # Adding into the portfolio table
        query_2 = f"INSERT INTO Portfolio (userID, transactionID) VALUES (%s, %s)"
        values_2 = (user_id, transaction_id)
        self.__cursor.execute(query_2, values_2)

        # Committing changes
        self.__db.commit()

    # Function that will fetch all the transactions made by the user
    def fetch_transaction(self, userid):
        # Query
        query = f"SELECT * FROM Transaction JOIN Portfolio ON Portfolio.transactionID = Transaction.transactionID WHERE Portfolio.userID = '{userid}'"
        # Executing the query
        self.__cursor.execute(query)
        # Fetching the records
        records = self.__cursor.fetchall()
        # Returning the records
        return records

    # Function to select the bought and sold quantity of a particular product
    def select_product_quantity(self, userid, name):
        # Bought Quantity
        # Query
        query_1 = f"SELECT SUM(quantity) FROM Transaction JOIN Portfolio ON Portfolio.transactionID = Transaction.transactionID WHERE Portfolio.userID = '{userid}' AND  t_option = 'BUY' AND cryptoname = '{name}'"
        # Execute query
        self.__cursor.execute(query_1)
        # Fetching the bought quantity
        bought_quantity = self.__cursor.fetchall()

        # Sold quantity
        query_2 = f"SELECT SUM(quantity) FROM Transaction JOIN Portfolio ON Portfolio.transactionID = Transaction.transactionID WHERE Portfolio.userID = '{userid}' AND  t_option = 'SELL' AND cryptoname = '{name}'"
        # Executing the query
        self.__cursor.execute(query_2)
        # Fetching the sold quantity
        sold_quantity = self.__cursor.fetchall()

        # Returning the bought and sold quantity in the form of a list
        return [bought_quantity[0][0], sold_quantity[0][0]]

# Function that will generate and return an ID using uuid() module
# The id will be 8 characters in length
def create_id():
    # Generating the id
    generated_id = uuid.uuid4()

    # Converting the id to a string
    id_string = str(generated_id)

    # Truncating the first 8 characters of the generated id
    user_id = id_string[:8]

    # Returning the id
    return user_id

# Function that will generate and return a transaction id for each transaction made by the user
def create_transaction_id():
    # Generate a random number between 1000 and 9999
    random_num = random.randint(1000, 9999)
    # Formatting the transaction id in this format:
    # T{random_num}
    transaction_id = f"T{random_num}"
    # Returning the transaction_id
    return transaction_id


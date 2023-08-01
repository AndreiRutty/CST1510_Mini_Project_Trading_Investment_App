from socket import *
import pickle
from abc import ABC
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import *
import Database.dbms as database
from datetime import date
from PIL import Image

import server as server_file

HOST = '127.0.0.1'
PORT = server_file.PORT
BUFSIZE = 7168

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

db = database.Database()


# This function will send an object provided by the parameter 'obj' to the server
def send_to_server(server, obj):
    # Serialize the shopping cart
    # Converting the object into a byte-stream
    obj_to_send = pickle.dumps(obj)

    # Sending it to the server
    server.sendall(obj_to_send)

    print("Information sent to the server.")


# This function will receive an object from the server
def received_from_server():
    # Receiving the object from the server
    received_data = s.recv(BUFSIZE)

    # Deserializing it
    received_object = pickle.loads(received_data)

    # Returning it
    return received_object


# This function will display an error pop up message
def show_error(text):
    # messagebox.showerror("Error", text)
    CTkMessagebox(title="Error", message=text, icon="cancel")


# This function will display an info pop up message
def show_info(text):
    # messagebox.showinfo("Info", text)
    CTkMessagebox(title="Info", message=text, icon="info")


# This function will display a question textbox
def show_question_box(text):
    # Getting the result of the question box
    # result = messagebox.askokcancel(title="Purchase", message=text)
    question = CTkMessagebox(title="Purchase", message=text, icon="question", option_1="Yes", option_2="No")

    # Getting the response from the user
    response = question.get()

    # Returning the result
    return response


# class App responsible for the main window
# Contains Log-In/Sign-Up Window and Home Page Window
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setting appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Setting the window setting
        self.title("Welcome")
        self.geometry("600x750+600+50")

        # Setting maximum and minimum window size
        self.minsize(550, 700)
        self.maxsize(600, 750)

        # Data for loging in and signing up
        self.login_username = ctk.StringVar(value="")
        self.login_password = ctk.StringVar(value="")
        self.signup_username = ctk.StringVar(value="")
        self.signup_password = ctk.StringVar(value="")
        self.invest_money = ctk.StringVar(value="0")

        # Reference to the home page which is set to None initially - because user hasn't logged in or signed up yet
        self.home_page = None

        # Header Widget which contains the app title
        self.header = Header(self)
        self.header.pack(pady=20)

        # Tab View where user can choose to log in or sign up
        self.tab_view = RegistrationFrame(self,
                                          self.login_username,
                                          self.login_password,
                                          self.login_button_event,
                                          self.signup_username,
                                          self.signup_password,
                                          self.invest_money,
                                          self.sign_up_button_event
                                          )
        # Placing the tab view on the main window
        self.tab_view.pack(pady=30)

    # Functions

    # This function handles login event when user press the login button
    def login_button_event(self):
        # Getting the username and password from user input
        username = self.login_username.get()
        password = self.login_password.get()

        # Checking if the user exists depending on the user info
        exists = db.check_user(username, password)

        # If it exists, log the user in and redirect the user to home page
        if exists:
            # Retrieving the user information
            user_info = db.select_specific_user(username)

            # Access home page
            self.access_home_page(user_info)
        else:
            # If user doesn't exist, an error message is shown
            show_error("User doesn't exist")

    # This function handles sign up event when user press the sign-up button
    def sign_up_button_event(self):
        # Checking if a user has the same credentials(that is this user already exists) as the user inputs
        user_object = (
            "sign-up", self.signup_username.get(), self.signup_password.get(), int(self.invest_money.get()))

        already_exist = db.select_specific_user(self.signup_username.get())

        # If the user already exists, an error message will be shown
        if already_exist:
            show_error("User Already Exist")
        else:
            # If the user doesn't exist, add this user to the User Database
            send_to_server(s, user_object)
            # Retrieve the user info of the newly added user from the User Database
            user_info = received_from_server()
            # Access home page
            self.access_home_page(user_info)

    # This function will redirect the user to the home page upon logging in or signing up
    def access_home_page(self, user_info):
        # Destroy the tab view
        self.tab_view.destroy()
        # Clearing the reference to the old tab view because it was destroyed
        self.tab_view = None
        # Assigning the home page to the home page variable
        self.home_page = Home(self, user_info, self.sign_out)
        # Placing the home page at the center of the screen
        self.home_page.place(relx=0.5, rely=0.5, anchor=CENTER)
        # Display a welcome message with the user's username
        WelcomeWindow(user_info[1])

    # This function handles the sign-out event when the sign-out button is pressed
    def sign_out(self):
        # Checking if the self.home_page variable has a reference to the home page
        if self.home_page is not None:
            # If it does, destroy the Home widget if it is not none
            self.home_page.destroy()
            # Removing reference to the Home widget because it was destroyed
            self.home_page = None
        else:
            # Else an error message will be shown
            show_error("Cannot signing you out")

        # Setting the tab_view widget to a new tab view because the old one was destroyed
        self.tab_view = RegistrationFrame(self,
                                          self.login_username,
                                          self.login_password,
                                          self.login_button_event,
                                          self.signup_username,
                                          self.signup_password,
                                          self.invest_money,
                                          self.sign_up_button_event)
        # Placing the tab view on the main window
        self.tab_view.pack()


# class RegistrationFrame responsible to store the log-in and sign-up panel
class RegistrationFrame(ctk.CTkTabview, ABC):
    # Parameters:
    # master - parent widget
    # login_username - log in username text variable
    # login_password - log in password text variable
    # login_func - log in function
    # signup_username - sign up username text variable
    # signup_password - sign up password text variable
    # initial_cash - initial cash text variable
    # signup_func - sign up function
    def __init__(self, master, login_username, login_password, login_func, signup_username, signup_password,
                 initial_cash, signup_func, **kwargs):
        super().__init__(master, **kwargs)

        # create the tabs for log in and sign up
        self.add("LOG IN")
        self.add("SIGN UP")

        # adding the widgets on tabs
        LoginPanel(self.tab("LOG IN"),
                   login_username,
                   login_password,
                   login_func).grid(row=0, column=0, sticky="NSEW")

        SignUpPanel(self.tab("SIGN UP"),
                    signup_username,
                    signup_password,
                    initial_cash,
                    signup_func).grid(row=0, column=0, sticky="NSEW")


# class LoginPanel responsible for the login panel and functionality where user can log in using username and password
class LoginPanel(ctk.CTkFrame):
    # Parameters:
    # master - parent widget
    # username - log in username text variable
    # password - log in password text variable
    # func - log in function
    def __init__(self, master, username, password, func):
        super().__init__(master, fg_color="transparent")

        # Labels for title, username and password
        self.login_title = ctk.CTkLabel(self, text="Log In", font=("Arial", 20))
        self.username_label_login = ctk.CTkLabel(self, text="Username", font=("Arial", 15))
        self.password_label_login = ctk.CTkLabel(self, text="Password", font=("Arial", 15))

        # Text Entry for username and password
        self.username_entry_login = ctk.CTkEntry(self, textvariable=username, width=200)
        self.password_entry_login = ctk.CTkEntry(self, show="*", textvariable=password, width=200)

        # Login Button
        self.login_button = ctk.CTkButton(self, text="LOG IN", command=func)

        # Placing the widgets onto the container
        self.login_title.grid(row=0, column=0, sticky="W", padx=25, pady=30)

        self.username_label_login.grid(row=1, column=0, sticky="W", padx=25)
        self.username_entry_login.grid(row=2, column=0, columnspan=2, padx=25, pady=10, sticky="W")

        self.password_label_login.grid(row=3, column=0, sticky="W", padx=25)
        self.password_entry_login.grid(row=4, column=0, padx=25, pady=10, sticky="W")

        self.login_button.grid(row=5, column=0, padx=25, pady=20, sticky="NSEW")


# class SignUpPanel responsible for the signup panel and functionality
# user can sign up using username,password and initial cash
class SignUpPanel(ctk.CTkFrame):
    # Parameters:
    # master - parent widget
    # username - sign up username text variable
    # password - sign up password text variable
    # initial_cash - initial cash text variable
    # func - sign up function
    def __init__(self, master, username, password, initial_cash, func):
        super().__init__(master, fg_color="transparent")

        # Labels for title, username, password and initial cash
        self.signup_title = ctk.CTkLabel(self, text="Sign Up", font=("Arial", 20))
        self.username_label_signup = ctk.CTkLabel(self, text="Username", font=("Arial", 15))
        self.password_label_signup = ctk.CTkLabel(self, text="Password", font=("Arial", 15))
        self.initial_cash_label = ctk.CTkLabel(self, text="Initial cash", font=("Arial", 15))

        # Text Entry for username, password and initial cash
        self.username_entry_signup = ctk.CTkEntry(self, textvariable=username, width=200)
        self.password_entry_signup = ctk.CTkEntry(self, show="*", textvariable=password, width=200)
        self.initial_cash_entry = ctk.CTkEntry(self, textvariable=initial_cash, width=200)

        # Sign Up Button
        self.sign_up_button = ctk.CTkButton(self, text="SIGN UP", command=func)

        # Placing the widgets onto the container
        self.signup_title.grid(row=0, column=0, sticky="W", padx=25, pady=30)
        self.username_label_signup.grid(row=1, column=0, sticky="W", padx=25)
        self.username_entry_signup.grid(row=2, column=0, padx=25, pady=10, sticky="W")

        self.password_label_signup.grid(row=3, column=0, sticky="W", padx=25)
        self.password_entry_signup.grid(row=4, column=0, padx=25, pady=10, sticky="W")

        self.initial_cash_label.grid(row=5, column=0, sticky="W", padx=25)
        self.initial_cash_entry.grid(row=6, column=0, padx=25, pady=10, sticky="W")

        self.sign_up_button.grid(row=7, column=0, padx=25, pady=20, sticky="NSEW")


# class Home responsible for the home window
class Home(ctk.CTkFrame):
    # Parameters
    # master - parent widget
    # user_info - user object which contains info about the user (username, userid, total cash etc..)
    def __init__(self, master, user_info, sign_out_func):
        super().__init__(master, fg_color="transparent")

        # Retrieving data from user_info object
        # user_info - (userid, username, totalcash, totalmoneyspent, totalmoneygain, profit)
        self.userid = user_info[0]
        self.username = user_info[1]
        self.total_cash = user_info[2]
        self.total_money_spent = user_info[3]
        self.total_money_gain = user_info[4]
        self.profit = user_info[5]

        # Image
        self.power_off_image_ref = Image.open("./Images/power-on.png")
        self.power_off_image = ctk.CTkImage(self.power_off_image_ref, size=(30, 30))

        # Main body frame which will contain all the home page widgets
        self.body = ctk.CTkFrame(self)
        self.body.pack(padx=30, pady=30)

        # Profile Label
        self.profile_label = ctk.CTkLabel(self.body, text="Profile", font=("Arial", 20))
        self.profile_label.pack(padx=60, pady=20)

        # User Info Frame --------------------------------------------------------------------------------------------
        # Frame which will display all the user information from the user_info object
        self.user_info_frame = UserInfoFrame(self.body,
                                             self.username,
                                             self.userid,
                                             self.total_cash,
                                             self.total_money_spent,
                                             self.total_money_gain,
                                             self.profit)

        # Reference to some UserInfoFrame Label mainly total_cash, total_money_spent, total_money_gain and profit
        # These will be used when the user buy or sell a product: Their current value will be updated
        self.total_cash_label = self.user_info_frame.get_total_cash_label()
        self.total_money_spent_label = self.user_info_frame.get_total_money_spent_label()
        self.total_money_gain_label = self.user_info_frame.get_total_money_gain_label()
        self.profit_label = self.user_info_frame.get_profit_label()

        # Option Menu ------------------------------------------------------------------------------------------------

        # Variable that stores what the user has chosen between the values below (refer to self.values)
        self.option_menu_choice = ctk.StringVar(value="Invest Now")
        self.values = ["Invest Now", "Portfolio", "Pay In", "Withdraw"]

        # Labels for option
        self.option_label = ctk.CTkLabel(self.body, text="Options", font=("Arial", 20))
        self.option_label.pack(padx=30, pady=20)

        # Option Menu which allows the user to choose what task he/she wants to do
        OptionMenu(self.body, self.values, self.option_menu_callback, self.option_menu_choice)

        # Sign out button responsible to sign the user out
        self.sign_out_button = ctk.CTkButton(self.body,
                                             text="",
                                             image=self.power_off_image,
                                             fg_color="transparent",
                                             hover_color="#d21312",
                                             width=40,
                                             command=sign_out_func)
        self.sign_out_button.pack(pady=10)

        # BankTransactions where the user can add and withdraw money
        # Argument: 1: Window Title, 2: Prompt to the user, 3: Function to add/withdraw money
        # Pay-in-Window where the user can add money to his/her account
        self.pay_in_window = BankTransactionWindow("Pay-in",
                                                   "Enter the amount of money you want to add ($)",
                                                   self.pay_in_callback)

        self.withdraw_window = BankTransactionWindow("Withdraw",
                                                     "Enter the amount of money you want to withdraw ($)",
                                                     self.withdraw_callback)

    # This function will perform certain task depending on the user's choice
    def option_menu_callback(self, choice):
        print(choice)
        if choice == "Pay In":
            # If user wants to 'Pay In', the pay_in_window will be displayed
            self.pay_in_window.mainloop()
        elif choice == "Withdraw":
            # If user wants to 'Withdraw', the withdraw_window will be displayed
            self.withdraw_window.mainloop()
        elif choice == "Portfolio":
            # If user wants to check his/her portfolio, the PortfolioWindow will be displayed
            PortfolioWindow(self.userid).mainloop()
        elif choice == "Invest Now":
            # If the user wants to invest in other crypto, the investment window will be displayed

            # User information used for the investment window
            user_info = (self.userid,
                         self.username,
                         self.total_cash,
                         self.total_money_spent,
                         self.total_money_gain,
                         self.profit)

            # Investment Window
            # Take user_info , and the references to the UserInfoFrame's labels for updating them
            InvestmentWindow(user_info,
                             self.total_cash_label,
                             self.total_money_spent_label,
                             self.total_money_gain_label,
                             self.profit_label).mainloop()

    # This function is responsible for the pay_in function where user adds money to his/her account
    def pay_in_callback(self):
        try:
            # Taking user input and converting it to an integer
            money = int(self.pay_in_window.get_amount())
        except ValueError:
            show_error("Invalid Input!\nPlease enter a valid amount of money")
        else:
            # Adding this amount to the user's total cash
            self.total_cash += money

            # Sending an object to the user to tell it to the update the user's total money in the User Database
            instruction = ["pay-in", self.total_cash, self.userid]
            send_to_server(s, instruction)

            # Show message that the amount was added to the user's amount
            show_info(f"${money} was added to your account!")

            # Update the total cash label on the UserInfoFrame
            self.total_cash_label.configure(text=f"$ {self.total_cash}")

    # This function is responsible for the withdrawal function where user withdraw money from his/her account
    def withdraw_callback(self):
        try:
            # Taking user input and converting it to an integer
            money = int(self.withdraw_window.get_amount())
        except ValueError:
            show_error("Invalid Input!\nPlease enter a valid amount of money")
        else:
            # Withdrawing this amount from the user's total cash
            self.total_cash -= money

            # Sending an object to the user to tell it to the update the user's total money in the User Database
            instruction = ["withdraw", self.total_cash, self.userid]
            send_to_server(s, instruction)

            # Show message that the amount was withdrawn from the user's amount
            show_info(f"${money} was withdrawn from your account!")

            # Update the total cash label on the UserInfoFrame
            self.total_cash_label.configure(text=f"$ {self.total_cash}")


# class OptionMenu which will allow the user to choose between options to perform a specific task
class OptionMenu(ctk.CTkOptionMenu):
    # Parameters
    # master - parent widget
    # values - the values for the user to choose
    # func - the option menu callback function which will perform a specific task depending on the user's choice
    # variable - the variable which whill store the choice of the user
    def __init__(self, master, values, func, variable):
        super().__init__(master, values=values, command=func, variable=variable, width=300)
        self.pack(padx=30, pady=10)


# class Header which contains the app title name
class Header(ctk.CTkFrame):
    # Parameter: master - parent widget
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Reference to the header images
        self.header_image_ref = Image.open("./Images/bitcoin.png")
        self.header_image2_ref = Image.open("./Images/ethereum.png")

        # Images widget
        self.header_image = ctk.CTkImage(self.header_image_ref, size=(30, 30))
        self.header_image2 = ctk.CTkImage(self.header_image2_ref, size=(30, 30))

        # Adding the images on the header widget
        self.header_image_label = ctk.CTkLabel(self, text="", image=self.header_image)
        self.header_image_label.grid(row=0, column=0, padx=10, pady=10)

        self.header_image2_label = ctk.CTkLabel(self, text="", image=self.header_image2)
        self.header_image2_label.grid(row=0, column=2, padx=10, pady=10)

        # App title label
        self.title_label = ctk.CTkLabel(self, text="Investment App", font=("Arial", 20))
        self.title_label.grid(row=0, column=1, padx=10, pady=10)


# class UserInfoFrame which is responsible to display the user's information like name, id, total cash etc...
class UserInfoFrame(ctk.CTkFrame):
    # Parameters
    # master - parent widget
    # userid - the user's id
    # total_cash = the user's total cash
    # total_money_spent = the total money the user has spent
    # total_money_gain = the total money the user has gained
    # profit = the profit the user has made

    def __init__(self, master, username, userid, total_cash, total_money_spent, total_money_gain, profit):
        super().__init__(master)
        self.pack(padx=30, pady=40)

        # Header grid configuration
        # Row Configuration
        self.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')
        # Column configuration
        self.columnconfigure((0, 1, 2), weight=1, uniform='a')

        # Labels for username, userid, total_cash, total_money_spent, total_money_gained, profit
        self.username_headline = ctk.CTkLabel(self, text="Username", font=("Arial", 11))
        self.username_label = ctk.CTkLabel(self, text=username, font=("Arial", 15))

        self.user_id_headline = ctk.CTkLabel(self, text="User ID", font=("Arial", 11))
        self.user_id_label = ctk.CTkLabel(self, text=userid, font=("Arial", 15))

        self.total_cash_headline = ctk.CTkLabel(self, text="Total Cash", font=("Arial", 11))
        self.total_cash_label = ctk.CTkLabel(self, text=f"$ {round(total_cash, 2)}", font=("Arial", 15))

        self.total_money_spend_headline = ctk.CTkLabel(self, text="Total Money Spent", font=("Arial", 11))
        self.total_money_spend_label = ctk.CTkLabel(self, text=f"$ {round(total_money_spent, 2)}", font=("Arial", 15))

        self.total_money_gain_headline = ctk.CTkLabel(self, text="Total Money Gain", font=("Arial", 11))
        self.total_money_gain_label = ctk.CTkLabel(self, text=f"$ {round(total_money_gain, 2)}", font=("Arial", 15))

        self.profit_headline = ctk.CTkLabel(self, text="Profit", font=("Arial", 11))
        self.profit_label = ctk.CTkLabel(self, text=f"$ {round(profit, 2)}", font=("Arial", 15))

        # Checking if profit is less than zero
        if profit < 0:
            # Set the color of the profit label to red
            self.profit_label.configure(text_color="#d21312")
        else:
            # Set the color of the profit label to white
            self.profit_label.configure(text_color="white")

        self.username_headline.grid(row=0, column=0, padx=40, pady=10)
        self.username_label.grid(row=1, column=0, padx=40)

        self.user_id_headline.grid(row=3, column=0, padx=40)
        self.user_id_label.grid(row=4, column=0, padx=40, pady=10)

        self.total_cash_headline.grid(row=0, column=1, pady=10)
        self.total_cash_label.grid(row=1, column=1)

        self.total_money_spend_headline.grid(row=3, column=1)
        self.total_money_spend_label.grid(row=4, column=1, pady=10)

        self.total_money_gain_headline.grid(row=0, column=2, padx=40, pady=10)
        self.total_money_gain_label.grid(row=1, column=2, padx=40)

        self.profit_headline.grid(row=3, column=2, padx=40)
        self.profit_label.grid(row=4, column=2, padx=40, pady=10)

    # Getter for the total_cash_label
    def get_total_cash_label(self):
        return self.total_cash_label

    # Getter for the total_money_spent_label
    def get_total_money_spent_label(self):
        return self.total_money_spend_label

    # Getter for the total_money_gain_label
    def get_total_money_gain_label(self):
        return self.total_money_gain_label

    # Getter for the profit_label
    def get_profit_label(self):
        return self.profit_label


# class BankTransactionWindow which is responsible for pay-in and withdrawal option
class BankTransactionWindow(ctk.CTk):
    # Parameters
    # title - Title of the window
    # prompt_text - The prompt that will ask the user to input the amount of money
    # func - the function which will add or withdraw money
    def __init__(self, title, prompt_text, func):
        super().__init__()
        # Parameters for the window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.geometry("400x300+600+100")
        self.title(title)
        self.resizable(False, False)

        # Data
        self.money_value = ctk.StringVar(value="0")

        # Prompt Label
        self.prompt_label = ctk.CTkLabel(self, text=prompt_text, font=("Arial", 15))
        self.prompt_label.pack(padx=30, pady=20)

        # Money Entry - where user can enter the amount of money
        self.money_entry = ctk.CTkEntry(self, textvariable=self.money_value)
        self.money_entry.pack(padx=30, pady=20)

        # Confirm button that will perform the required task
        self.confirm_button = ctk.CTkButton(self, text="Confirm", command=func)
        self.confirm_button.pack(padx=30, pady=20)

    # Getter for the money_entry
    def get_amount(self):
        return self.money_entry.get()


# class PortfolioWindow where all the transactions the user has made will be displayed
class PortfolioWindow(ctk.CTk):
    # Parameter: userid - the id of the user
    def __init__(self, user_id):
        super().__init__()

        # Settings for the window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title("Portfolio")
        self.geometry("850x650")
        self.resizable(False, False)

        # The headline frame for the transaction
        # It tells the attributes of each column(Name of cryptocurrency, price, date of purchase etc..)
        TransactionHeadlineFrame(self).pack(padx=5, pady=5)

        # A scrollable frame where all the transactions will be displayed
        PortfolioScrollableFrame(self, user_id).pack()


# class PortfolioScrollableFrame which is responsible for to display all transaction made by the user
class PortfolioScrollableFrame(ctk.CTkScrollableFrame):
    # Parameters:
    # master - parent widget
    # user_id - the id of the user
    def __init__(self, master, user_id):
        super().__init__(master, width=800, height=500)

        # Data
        # User id
        self.userid = user_id
        # Fetching transactions from the transaction table
        self.transactions_data = self.fetch_transaction_table_data()

        # Displaying each transaction by the user
        for transaction in self.transactions_data:
            # Data about the transaction
            crypto_name = transaction[1]
            date_purchased = transaction[2].strftime("%Y-%m-%d")
            transaction_option = transaction[3]
            quantity = transaction[4]
            cost = transaction[5]

            # Frame which will display relevant information about each transaction
            TransactionFrame(self, crypto_name, date_purchased, transaction_option, quantity, cost).pack(padx=5,
                                                                                                         pady=5)

    # Function to fetch the transactions made by the user from the transaction table
    def fetch_transaction_table_data(self):
        # Requesting Transactions from server
        # Transaction tuple Format
        # ('Transaction ID', 'crypto name', dop, 'Option', quantity, price, 'userid', 'Transaction ID')
        request_obj = ("transactions", self.userid)
        send_to_server(s, request_obj)

        # Getting the transactions from the server
        transactions = received_from_server()

        # Returning the transactions
        return transactions


# class TransactionHeadLineFrame which acts tells the attribute of each column in the portfolio window
class TransactionHeadlineFrame(ctk.CTkFrame):
    # Parameter: master - parent widget
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Column Configuration
        self.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

        # Name Label
        self.product_name = ctk.CTkLabel(self, text="Name")
        self.product_name.grid(row=0, column=0, sticky="NSEW", padx=48, pady=20)

        # Date of purchase Label
        self.date = ctk.CTkLabel(self, text="D.O.P")
        self.date.grid(row=0, column=1, sticky="NSEW", padx=48, pady=20)

        # Buy / Sell Option label
        self.options = ctk.CTkLabel(self, text="Buy/Sell")
        self.options.grid(row=0, column=2, padx=48, pady=20)

        # Quantity Label
        self.quantity = ctk.CTkLabel(self, text="Quantity")
        self.quantity.grid(row=0, column=3, padx=48, pady=20)

        # Cost Label
        self.cost = ctk.CTkLabel(self, text="Cost")
        self.cost.grid(row=0, column=4, padx=48, pady=20)


# class TransactionFrame which is responsible to display relevant information about the transaction made
class TransactionFrame(ctk.CTkFrame):
    # Parameters
    # master - parent widget
    # name - name of the crypto
    # date_purchased - the date when the crypto was purchased,
    # option - BUY or SELL option
    # quantity - the bought or sold quantity
    # cost - the total cost 2for the crypto
    def __init__(self, master, name, date_purchased, option, quantity, cost):
        super().__init__(master, fg_color="#444445")

        # Column Configuration
        self.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

        # Crypto Name Label
        self.crypto_name = ctk.CTkLabel(self, text=name).grid(row=0, column=0, sticky="NSEW", padx=40, pady=30)

        # Date of purchase Label
        self.date_label = ctk.CTkLabel(self, text=date_purchased).grid(row=0, column=1, sticky="NSEW", padx=40, pady=30)

        # BUY / SELL option Label
        self.option_label = ctk.CTkLabel(self, text="Buy/Sell").grid(row=0, column=2, sticky="NSEW")
        self.option = ctk.CTkLabel(self, text=option).grid(row=0, column=2, sticky="NSEW", padx=40, pady=30)

        # Quantity Label
        self.quantity_label = ctk.CTkLabel(self, text="Quantity").grid(row=0, column=3, sticky="NSEW")
        self.quantity = ctk.CTkLabel(self, text=quantity).grid(row=0, column=3, sticky="NSEW", padx=40, pady=30)

        # Cost Label
        self.cost_label = ctk.CTkLabel(self, text="Cost").grid(row=0, column=4, sticky="NSEW")
        self.cost = ctk.CTkLabel(self, text=f"${cost}").grid(row=0, column=4, sticky="NSEW", padx=40, pady=30)


# class WelcomeWindow which greets the user when he/she log in or sign up
class WelcomeWindow(ctk.CTk):
    # Parameter: username - the username of the user
    def __init__(self, username):
        super().__init__()

        # Setting of the window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title("Welcome")
        self.geometry("300x100+600+150")
        self.resizable(False, False)

        # Greeting message label
        self.message = ctk.CTkLabel(self, text=f"Welcome! {username}", font=("Arial", 20))
        self.message.pack(padx=20, pady=20)

        self.mainloop()


# class InvestmentWindow which is responsible to allow the user to buy or sell cryptocurrencies
class InvestmentWindow(ctk.CTk):
    # Parameters
    # user_info - object which contains all the use information
    # total_cash_label - reference to the UserInfoFrame's total cash label
    # total_money_spent_label - reference to the UserInfoFrame's total money spent label
    # total_money_gained_label - reference to the UserInfoFrame's total money gained label
    # profit_label - reference to the UserInfoFrame's profit label
    def __init__(self, user_info, total_cash_label, total_money_spent_label,
                 total_money_gained_label, profit_label):
        super().__init__()

        # Setting for the window
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.title("Invest Now")
        self.geometry("850x650")

        # Setting maximum and minimum size
        self.minsize(800, 600)
        self.maxsize(850, 650)

        # Requesting the list of the products from the server
        send_to_server(s, ["product-list", ])
        # Getting the list of products from the server
        self.products_list = received_from_server()

        # Header Label
        self.header = ctk.CTkLabel(self, text="Invest Now!", font=("Arial", 30))
        self.header.pack(pady=20)

        # InvestmentHeadlineFrame which tells the attribute of each column
        InvestmentHeadlineFrame(self).pack(padx=5, pady=5)

        # Scrollable Frame where all the products are displayed
        InvestmentScrollableFrame(self,
                                  self.products_list, user_info,
                                  total_cash_label,
                                  total_money_spent_label,
                                  total_money_gained_label,
                                  profit_label).pack()


# class InvestmentScrollableFrame which is responsible to display all the products
class InvestmentScrollableFrame(ctk.CTkScrollableFrame):
    # Parameters
    # master - parent widget
    # products_list - the list of products
    # user_info - object which contains all the use information
    # total_cash_label - reference to the UserInfoFrame's total cash label
    # total_money_spent_label - reference to the UserInfoFrame's total money spent label
    # total_money_gained_label - reference to the UserInfoFrame's total money gained label
    # profit_label - reference to the UserInfoFrame's profit label
    def __init__(self,
                 master,
                 products_list,
                 user_info,
                 total_cash_label,
                 total_money_spent_label,
                 total_money_gained_label,
                 profit_label):
        super().__init__(master, width=750, height=450)

        # Displaying each product from the products_list
        for product in products_list:
            ProductFrame(self,
                         product,
                         user_info,
                         total_cash_label,
                         total_money_spent_label,
                         total_money_gained_label,
                         profit_label).pack(padx=5, pady=5)


# class InvestmentHeadlineFrame which tells the attribute of each column for the product frame
class InvestmentHeadlineFrame(ctk.CTkFrame):
    # Parameters: master - parent widget
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Column Configuration
        self.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

        # Name Label
        self.product_name = ctk.CTkLabel(self, text="Name")
        self.product_name.grid(row=0, column=0, sticky="NSEW", padx=52, pady=20)

        # Price
        self.price_name = ctk.CTkLabel(self, text="Price($)")
        self.price_name.grid(row=0, column=1, sticky="NSEW", padx=52, pady=20)

        # Buy Label
        self.buy_label = ctk.CTkLabel(self, text="Buy")
        self.buy_label.grid(row=0, column=2, padx=52, pady=20)

        # Sell Label
        self.sell_label = ctk.CTkLabel(self, text="Sell")
        self.sell_label.grid(row=0, column=3, padx=52, pady=20)

        # Quantity Label
        self.quantity_label = ctk.CTkLabel(self, text="Quantity")
        self.quantity_label.grid(row=0, column=4, padx=52, pady=20)


# class ProductFrame which is responsible to display information about the crypto
# and buttons for investing in the crypto
class ProductFrame(ctk.CTkFrame):
    # Parameters
    # master - parent widget
    # product - individual product from the product list
    # user_info - object which contains all the use information
    # total_cash_label - reference to the UserInfoFrame's total cash label
    # total_money_spent_label - reference to the UserInfoFrame's total money spent label
    # total_money_gained_label - reference to the UserInfoFrame's total money gained label
    # profit_label - reference to the UserInfoFrame's profit label
    def __init__(self,
                 master,
                 product,
                 user_info,
                 total_cash_label,
                 total_money_spent_label,
                 total_money_gained_label,
                 profit_label):

        super().__init__(master, fg_color="#444445")
        # Column
        # Configuration
        self.columnconfigure((0, 1, 2, 3, 4), weight=1, uniform='a')

        # Data about the product
        self.name = product[0]
        self.price = product[1]

        # Data from the user_info object
        self.user_id = user_info[0]
        self.username = user_info[1]
        self.user_money = float(user_info[2])
        self.total_money_spent = float(user_info[3])
        self.total_money_gained = float(user_info[4])
        self.profit = float(user_info[5])

        # Variable for the quantity entry
        self.quantity_text = ctk.StringVar(value="1")

        # References to the UserInfoFrame's label
        self.total_cash_label = total_cash_label
        self.total_money_spent_label = total_money_spent_label
        self.total_money_gained_label = total_money_gained_label
        self.profit_label = profit_label

        # Retrieving bought and sold quantities of a specific product
        # Bought Quantity
        self.bought_quantity = 0 if db.select_product_quantity(self.user_id, self.name)[0] is None \
            else float(db.select_product_quantity(self.user_id, self.name)[0])

        # Sold Quantity
        self.sold_quantity = 0 if db.select_product_quantity(self.user_id, self.name)[1] is None \
            else float(db.select_product_quantity(self.user_id, self.name)[1])

        # Name of the product Label
        self.product_name = ctk.CTkLabel(self, text=self.name)
        self.product_name.grid(row=0, column=0, sticky="NSEW", padx=20, pady=30)

        # Price Label
        self.price_name = ctk.CTkLabel(self, text=f"$ {self.price}")
        self.price_name.grid(row=0, column=1, sticky="NSEW", padx=20, pady=30)

        # Buy Button
        self.buy_button = ctk.CTkButton(self,
                                        text="BUY",
                                        command=self.buy_product,
                                        fg_color="#ed2b2a",
                                        hover_color="#d21312")
        self.buy_button.grid(row=0, column=2, padx=20, pady=30)

        # Sell Button
        self.sell_button = ctk.CTkButton(self, text="SELL", command=self.sell_product)
        self.sell_button.grid(row=0, column=3, padx=20, pady=30)

        # Quantity Entry
        self.quantity_entry = ctk.CTkEntry(self, textvariable=self.quantity_text)
        self.quantity_entry.grid(row=0, column=4, padx=20, pady=30)

    # Function which is responsible for buying the chosen product
    def buy_product(self):
        # Asking the user if he/she want to buy this product
        proceed = show_question_box("Do you wish to buy this product")

        # If the user wants, purchase this item
        if proceed == "Yes":
            # Error handling to check if the user has entered a quantity to buy
            try:
                # Getting the quantity
                quantity = float(self.quantity_entry.get())
            except ValueError:
                # If the user didn't input a quantity, an error message will be displayed
                show_error("Invalid Input!\nPlease input a value greater than zero")
            else:
                # Calculating total price for the product
                # Price for 1 * Quantity
                total_price = float(self.price) * float(quantity)

                # Getting today's date
                today_date = date.today()
                # Formatting in the format : YYYY - MM - DD
                formatted_date = today_date.strftime("%Y-%m-%d")

                # Checking if user has enough money
                if total_price > self.user_money:
                    # Show an error message if the user doesn't have enough message
                    show_error("You don't have enough money")
                else:
                    # Increasing the bought_quantity amount
                    self.bought_quantity += quantity

                    # Decrease user's money
                    self.user_money -= round(total_price, 2)

                    # Updating the user's total_money_spent
                    self.total_money_spent += round(total_price, 2)

                    # Calculating the profit
                    self.profit = self.calculate_profit()

                    # Add transaction to Transaction table
                    transaction_obj = ["invest", self.user_id, self.user_money, self.name, formatted_date, "BUY",
                                       quantity,
                                       total_price, self.total_money_spent, self.profit]
                    send_to_server(s, transaction_obj)

                    # Updating the value of the UserInfoFrame's label (total_cash, total_money_spent, profit)
                    self.total_cash_label.configure(text=f"${round(self.user_money, 2)}")
                    self.total_money_spent_label.configure(text=f"${round(self.total_money_spent, 2)}")
                    self.profit_label.configure(text=f"${round(self.profit, 2)}")

        else:
            # An Info message will be displayed, telling that the user doesn't want to purchase it
            show_info("Purchase cancel by user")

    # Function which is responsible for selling the chosen product
    def sell_product(self):
        # Asking the user if he/she want to sell this product
        proceed = show_question_box("Do you wish to sell this product")

        # If the user wants, purchase this item
        if proceed == "Yes":
            # Error handling to check if the user has entered a quantity to sell
            try:
                # Getting the quantity
                quantity = float(self.quantity_entry.get())

            except ValueError:
                # If the user didn't input a quantity, an error message will be displayed
                show_error("Invalid Input!\nPlease input a value greater than zero")
            else:
                # Checking if the buy has bought this product first
                if self.bought_quantity == 0:
                    # An error message will be shown, if the user didn't purchase this product
                    show_error(f"It seems you possess 0 {self.name}\nBuy some {self.name} before selling")
                else:

                    # Checking if the quantity the user wants to sell is larger than the quantity the user has bought
                    if self.sold_quantity + quantity > self.bought_quantity:
                        # if it does, show an error message
                        show_error("Cannot sell more than you possess")
                    else:
                        # Calculating total price for this transaction
                        #  price for 1 * quantity
                        total_price = float(self.price) * float(quantity)

                        # Getting today's date
                        today_date = date.today()
                        # Formatting it in the format: YYYY - MM - DD
                        formatted_date = today_date.strftime("%Y-%m-%d")

                        # Checking if user has enough money
                        if total_price > self.user_money:
                            # If not, show an error message
                            show_error("You don't have enough money")
                        else:
                            # Sell the product
                            # Increasing sold quantity
                            self.sold_quantity += quantity

                            # Updating user's total money
                            self.user_money += round(total_price, 2)

                            # Updating the total money gained by the user
                            self.total_money_gained += round(total_price, 2)

                            # Calculating profit
                            self.profit = self.calculate_profit()

                            # Add transaction to Transaction table
                            transaction_obj = ["invest", self.user_id, self.user_money, self.name, formatted_date,
                                               "SELL",
                                               quantity,
                                               total_price, self.total_money_gained, self.profit]
                            send_to_server(s, transaction_obj)

                            # Updating the value of the UserInfoFrame's label (total_cash, total_money_gain, profit)
                            self.total_cash_label.configure(text=f"${round(self.user_money, 2)}")
                            self.total_money_gained_label.configure(text=f"${round(self.total_money_gained, 2)}")
                            self.profit_label.configure(text=f"${round(self.profit, 2)}")

        else:
            # if the user doesn't want to sell this product, show an info message
            show_info("The sale of this product was cancelled by user")

    # Function responsible to calculate the profit made by the user
    def calculate_profit(self):
        # Profit =  Money Gain - Money Spent
        profit = self.total_money_gained - self.total_money_spent

        # Returning the profit
        return profit


if __name__ == '__main__':
    app = App()
    app.mainloop()

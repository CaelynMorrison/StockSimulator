import sys
import time
import pickle
from textmenu import TextMenu
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

# Minimum time in milliseconds since last time specific stock data was requested. 
STOCK_REFRESH_LIMIT = 300

class Stock:
    def __init__ (self, symbol: str, price: float) -> None:
        self.symbol = symbol
        self.price = price
        self.shares_owned = 0
        self.invested_money = float(0)
        self.last_updated = time.time()
    
    def __str__ (self) -> str:
        return (f"\033[1m{self.symbol:5}\033[0m "
                f"| Share Price: ${self.price:8,.2f} "
                f"| Shares: {self.shares_owned:5} "
                f"| Cost per Share: ${self.cost_basis():8,.2f} "
                f"| Current Value: ${(self.current_value()):10,.2f} "
                f"| Profit: {self.profit()}"
        )
    
    def current_value(self) -> float:
        return self.shares_owned * self.price
    
    def cost_basis(self) -> float:
        return self.invested_money / self.shares_owned

    def profit(self) -> str:
        profit = (self.price - self.cost_basis()) * self.shares_owned
        if profit > 0:
            return f"\033[0;32m${profit:10,.2f}\033[0m"
        elif profit < 0:
            return f"\033[0;31m${profit:10,.2f}\033[0m"
        return f"${profit:10,.2f}"
    
class User:
    def __init__ (self, money: int) -> None:
        self.money = float(money)
        self.portfolio: dict = {}

    def __str__ (self) -> str:
        output = ""
        for stock in self.portfolio:
            if self.portfolio[stock].shares_owned > 0:
                output += f"\n{self.portfolio[stock]}"
        output += f"\nYou have \033[1m${self.money:,.2f}\033[0m"
        return output
    
    def display_portfolio(self, api_key: list) -> None:  
        for stock in self.portfolio:
            if self.portfolio[stock].shares_owned > 0:
                self.get_stock_data(api_key, stock)
        print(self)

    def trade_stock(self, api_key: list, action) -> None:
        attempts = 0
        stock_data = {}
        while attempts < 3:
            symbol = input("Symbol?")
            try:
                stock_data[symbol] = self.get_stock_data(api_key, symbol)
            except KeyError:
                print(f"{symbol} is not a valid stock symbol.")
                attempts += 1
                continue
            action(self.portfolio[symbol], get_quantity())      
            break

    def get_stock_data(self, api_key: list, symbol: str) -> dict:
        stock_client = StockHistoricalDataClient(api_key[0], api_key[1])
        if symbol in self.portfolio:
            if time.time() < (self.portfolio[symbol].last_updated
                              + STOCK_REFRESH_LIMIT):
                return self.portfolio[symbol]       
        stock_data = stock_client.get_stock_latest_trade(
                    StockLatestTradeRequest(symbol_or_symbols = [symbol]))       
        self.update_stock_price(symbol, stock_data[symbol])       
        return stock_data[symbol]
    
    def buy_stock(self, stock: Stock, shares: int) -> None:
        if stock.price * shares <= self.money:
            self.money -= stock.price * shares
            stock.invested_money += stock.price * shares
            stock.shares_owned += shares
            self.portfolio[stock.symbol] = stock
  
    def sell_stock(self, stock: Stock, shares: int) -> None:
        if stock.shares_owned >= shares:
            self.money += stock.price * shares
            stock.invested_money -= stock.cost_basis() * shares
            stock.shares_owned -= shares

    def update_stock_price(self, symbol: str, stock_data: dict) -> None:
        if symbol in self.portfolio:
            self.portfolio[symbol].price = stock_data.price
            self.portfolio[symbol].last_updated = time.time()
        else:
            self.seed_stock(Stock(symbol, stock_data.price))

    def seed_stock(self, stock: Stock) -> None:
        self.portfolio[stock.symbol] = stock
        self.portfolio[stock.symbol].last_updated = time.time()

def main():
    user = start_up()
    api_key = load_key()
    main_menu = create_main_menu(user, api_key)

    user.display_portfolio(api_key)

    while True:
        main_menu.get_user_input()

def create_main_menu(user: User, api_key: list) -> TextMenu:
    main_menu = TextMenu()

    main_menu.add_menu_item("PORTFOLIO", user.display_portfolio, api_key)

    main_menu.add_menu_item("BUY STOCK", user.trade_stock,
                            api_key, user.buy_stock)
    main_menu.menu_items["BUY STOCK"].add_alias("buy", "buystock")

    main_menu.add_menu_item("SELL STOCK", user.trade_stock, user,
                            api_key, user.sell_stock)
    main_menu.menu_items["SELL STOCK"].add_alias("sell", "sellstock")

    main_menu.add_menu_item("SAVE GAME", save_game, user)
    main_menu.menu_items["SAVE GAME"].add_alias("save", "savegame")

    main_menu.add_menu_item("LOAD GAME", load_game)
    main_menu.menu_items["LOAD GAME"].add_alias("load", "loadgame")

    main_menu.add_menu_item("NEW GAME", new_game)
    main_menu.menu_items["NEW GAME"].add_alias("new", "newgame")

    main_menu.add_menu_item("EXIT", sys.exit)
    
    return main_menu

def get_quantity() -> int:
    while True:
        try: 
            return int(input("How many shares? "))
        except TypeError:
            print("Please enter a whole number of shares.")

def load_key() -> list:
    try:
        with open("config.ini", "r") as file:
            return file.read().strip().split(",")
    except FileNotFoundError:
        print("Alpaca API key is required.")
        return get_new_key()

def get_new_key() -> list:
    key_id = input("Enter API Key ID: ")
    secret_key = input("Enter API Secret Key: ")
    if validate_key([key_id, secret_key]):
        with open("config.ini", "w") as file:
            file.write(f"{key_id},{secret_key}")
            file.close()
        return [key_id, secret_key]
    else:
        print("API key is invalid.")
        return get_new_key()

def validate_key(user: User, api_key: list) -> bool:
    try:
        user.get_stock_data(api_key, "AAPL")
        return True
    except:
        return False

def start_up() -> User:
    while True:
        text_input = input("NEW game or LOAD game?").lower()
        if text_input.startswith("l"):
            return load_game()
        elif text_input.startswith("n"):
            return User(new_game())  

def new_game() -> int:
    while True:
        try:
            return int(input("How much money would you like to start with? $"))
        except ValueError:
            pass
     
def load_game() -> User:
    with open("savegame.pkl", "rb") as file:
        user = pickle.load(file)
        return user

def save_game(user: User) -> None:
    with open("savegame.pkl", "wb") as file:
        pickle.dump(user, file)
        file.close()
 
if __name__ == "__main__":
    main() 
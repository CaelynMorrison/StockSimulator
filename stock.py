import sys
import time
import pickle
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest

COMMANDS = {
    "1. PORTFOLIO": ["1.", "1", "portfolio"],
    "2. BUY STOCK": ["2.", "2"],
    "3. SELL STOCK": ["3.", "3"],
    "4. SAVE GAME": ["4.", "4"],
    "5. LOAD GAME": ["5.", "5"],
    "6. NEW GAME": ["6.", "6", "newgame", "new game"],
    "7. EXIT": ["7.", "7", "exit"]
    }

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

    def seed_stock(self, stock: Stock) -> None:
        self.portfolio[stock.symbol] = stock

def main():
    api_key = load_key() 
    user = start_up()

    display_portfolio(user, api_key)

    while True:
        command = get_command().lower()
        if command in COMMANDS["1. PORTFOLIO"]:
            display_portfolio(user, api_key)
        elif command in COMMANDS["2. BUY STOCK"]:
            symbol = input("Symbol? ")
            update_stock_price(symbol, user, api_key)
            user.buy_stock(user.portfolio[symbol], int(input("How many shares? ")))
        elif command in COMMANDS["3. SELL STOCK"]:
            symbol = input("Symbol? ")
            if symbol in user.portfolio:
                update_stock_price(symbol, user, api_key)
                user.sell_stock(user.portfolio[symbol], int(input("How many shares? ")))
        elif command in COMMANDS["4. SAVE GAME"]:
            save_game(user)
        elif command in COMMANDS["5. LOAD GAME"]:
            user = load_game()
        elif command in COMMANDS["6. NEW GAME"]:
            if input("Are you sure? ").lower().startswith("y"):
                user = User(new_game())
        elif command in COMMANDS["7. EXIT"]:
            sys.exit()

def load_key() -> list:
    with open("config.ini", "r") as file:
        for line in file:
            return line.strip().split(",")

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
     
def get_command() -> str:
    print() 
    for command in COMMANDS:
        print(f"{command}")
    return input("Select Option: ")

def display_portfolio(user: User, api_key: list) -> None:  
    for stock in user.portfolio:
        if user.portfolio[stock].shares_owned > 0:
            update_stock_price(user.portfolio[stock].symbol, user, api_key)
    print(user)

def get_stock_price(api_key: list, symbol: str) -> float:
    stock_client = StockHistoricalDataClient(api_key[0], api_key[1])
    stock_data = stock_client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols = [symbol]))
    if stock_data:
        return stock_data[symbol].price
    
def update_stock_price(symbol: str, user: User, api_key: list) -> None:
    if symbol in user.portfolio:
        if time.time() > user.portfolio[symbol].last_updated + STOCK_REFRESH_LIMIT:
            user.portfolio[symbol].price = get_stock_price(api_key, symbol)
            user.portfolio[symbol].last_updated = time.time()
        return         
    user.seed_stock(Stock(symbol, get_stock_price(api_key, symbol)))

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
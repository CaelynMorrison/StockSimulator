import sys
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

class Stock:
    def __init__ (self, symbol: str, price: float) -> None:
        self.symbol = symbol
        self.price = price
        self.shares_owned = 0
        self.invested_money = float(0)
    
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
            if stock.shares_owned > 0:
                output += f"\n{stock}"
        output += f"\nYou have ${self.money:,.2f}"
        return output
    
    def buy_stock(self, stock: Stock, shares: int) -> None:
        if stock.price * shares <= self.money:
            self.money -= stock.price * shares
            stock.invested_money += stock.price * shares
            stock.shares_owned += shares
            self.portfolio[stock] = stock.symbol
  
    def sell_stock(self, stock: Stock, shares: int) -> None:
        if stock.shares_owned >= shares:
            self.money += stock.price * shares
            stock.invested_money -= stock.cost_basis() * shares
            stock.shares_owned -= shares

    def seed_stock(self, stock: Stock) -> None:
        self.portfolio[stock] = stock.symbol

def main():
    api_key = load_key() 
    user = start_up()

    #TEMP STOCK FOR TESTING
    user.seed_stock(Stock("ALPHA", float(10)))
    user.seed_stock(Stock("BETA", float(5)))
#    user.seed_stock(Stock(test_stock, test[test_stock].price))
    
    print(user)

    while True:
        command = get_command()
        if command.lower() in COMMANDS["1. PORTFOLIO"]:
            print(user)
        elif command.lower() in COMMANDS["2. BUY STOCK"]:
            symbol = input("Symbol? ")
            for stock in user.portfolio:
                if symbol == stock.symbol:
                    user.buy_stock(stock, int(input("How many shares? ")))
                    break
        elif command.lower() in COMMANDS["3. SELL STOCK"]:
            symbol = input("Symbol? ")
            for stock in user.portfolio:
                if symbol == stock.symbol:
                    user.sell_stock(stock, int(input("How many shares? ")))
                    break
        elif command.lower() in COMMANDS["4. SAVE GAME"]:
            save_game(user)
        elif command.lower() in COMMANDS["5. LOAD GAME"]:
            user = load_game()
        elif command.lower() in COMMANDS["6. NEW GAME"]:
            if input("Are you sure? ").lower().startswith("y"):
                user = User(new_game())
        elif command.lower() in COMMANDS["7. EXIT"]:
            sys.exit()
        else:
            symbol = input("Stock Symbol? ")
            test = get_stock_price(api_key, symbol)
            user.seed_stock(Stock(symbol, test))

def load_key() -> list:
    with open("config.ini", "r") as file:
        for line in file:
            return line.strip().split(",")

def start_up() -> User:
    if input("NEW game or LOAD game?") == "LOAD":
        return load_game()
    else:
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

def get_stock_price(api_key: list, symbol: str) -> float:
    stock_client = StockHistoricalDataClient(api_key[0], api_key[1])
    stock_data = stock_client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols = [symbol]))
    if stock_data:
        return stock_data[symbol].price

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
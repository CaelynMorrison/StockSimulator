import sys
import pickle

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
        self.invested_money = 0
    
    def __str__ (self) -> str:
        return (f"{self.symbol} "
                f"| Share Price: ${self.price:,.2f} "
                f"| Shares: {self.shares_owned} "
                f"| Cost per Share: ${self.cost_basis():,.2f} "
                f"| Current Value: ${(self.current_value()):,.2f} "
                f"| Profit: ${self.profit():,.2f}"
        )
    
    def current_value(self) -> float:
        return self.shares_owned * self.price
    
    def cost_basis(self) -> float:
        return self.invested_money / self.shares_owned

    def profit(self) -> float:
        return (self.price - self.cost_basis()) * self.shares_owned
    
class User:
    def __init__ (self, money: int) -> None:
        self.money = money
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
    user = User(new_game())

    #TEMP STOCK FOR TESTING
    user.seed_stock(Stock("ALPHA", float(10)))
    user.seed_stock(Stock("BETA", float(5)))

    while True:
        command = get_command()
        if command.lower() in COMMANDS["1. PORTFOLIO"]:
            print(user)
        elif command.lower() in COMMANDS["2. BUY STOCK"]:
            symbol = input("Symbol? ")
            for stock in user.portfolio:
                if symbol == stock.symbol:
                    user.buy_stock(stock, int(input("How many shares? ")))
        elif command.lower() in COMMANDS["3. SELL STOCK"]:
            symbol = input("Symbol? ")
            for stock in user.portfolio:
                if symbol == stock.symbol:
                    user.sell_stock(stock, int(input("How many shares? ")))
        elif command.lower() in COMMANDS["4. SAVE GAME"]:
            save_game(user)
        elif command.lower() in COMMANDS["5. LOAD GAME"]:
            user = load_game()
            for stock in user.portfolio:
                s = stock.price
                print(stock)

        elif command.lower() in COMMANDS["6. NEW GAME"]:
            if input("Are you sure? ").lower().startswith("y"):
                user = User(new_game())
        elif command.lower() in COMMANDS["7. EXIT"]:
            sys.exit()  

def start_up() -> User:
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
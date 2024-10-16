import sys

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
        output = "\n"
        for stock in self.portfolio:
            output += f"{stock}"
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

def main():
    user = User(new_game())

    #TEMP STOCK FOR TESTING
    alpha = Stock("ALPHA", float(10))
    beta = Stock("BETA", float(5))

    while True:
        command = get_command()
        if command.lower() in COMMANDS["1. PORTFOLIO"]:
            print(user)
        elif command.lower() in COMMANDS["2. BUY STOCK"]:
            user.buy_stock(alpha, int(input("How many shares? ")))
        elif command.lower() in COMMANDS["3. SELL STOCK"]:
            user.sell_stock(alpha, int(input("How many shares? ")))
        elif command.lower() in COMMANDS["6. NEW GAME"]:
            if input("Are you sure? ").lower().startswith("y"):
                user = User(new_game())
        elif command.lower() in COMMANDS["7. EXIT"]:
            sys.exit()
        else:
            alpha.price += 1      

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
    with open("savegame.csv") as file:
        for line in file:
            print(line)

def save_game(user: User):
    ...
    
if __name__ == "__main__":
    main() 
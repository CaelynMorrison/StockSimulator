from stock import Portfolio

def test_portfolio():
    portfolio = Portfolio(10)
    assert portfolio.money == 10


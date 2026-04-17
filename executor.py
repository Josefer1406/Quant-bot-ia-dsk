import config
from exchange_connector import exchange

def execute_buy(symbol, quantity, price):
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Comprar {quantity:.6f} {symbol} a ~${price:.2f}")
        return {'price': price, 'amount': quantity}
    else:
        return exchange.create_market_buy_order(symbol, quantity)

def execute_sell(symbol, quantity):
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Vender {quantity:.6f} {symbol}")
        return True
    else:
        return exchange.create_market_sell_order(symbol, quantity)

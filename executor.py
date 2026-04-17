import config

def execute_buy(symbol, quantity, price):
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Comprar {quantity:.6f} {symbol} a ~${price:.2f}")
        return {'price': price, 'amount': quantity}
    else:
        # Aquí iría orden real
        return None

def execute_sell(symbol, quantity):
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Vender {quantity:.6f} {symbol}")
        return True
    return True
import config

def execute_buy(symbol, quantity, price):
    """Ejecuta orden de compra (simulación o real)"""
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Comprar {quantity:.6f} {symbol} a ~${price:.2f}")
        return {'price': price, 'amount': quantity}
    else:
        # Aquí se integraría la orden real con el exchange (Bybit, etc.)
        # Por ahora solo simulación
        print(f"⚠️ Modo real no implementado aún")
        return None

def execute_sell(symbol, quantity):
    if config.SIMULATION_MODE:
        print(f"🔁 [SIM] Vender {quantity:.6f} {symbol}")
        return True
    return True
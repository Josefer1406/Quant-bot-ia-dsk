import config

def calculate_dynamic_stops(entry_price, atr, regime='lateral'):
    stop_pct = min(max(atr * 1.2 / entry_price, 0.005), 0.03)
    take_pct = min(stop_pct * 2.0, 0.06)
    stop_price = entry_price * (1 - stop_pct)
    take_price = entry_price * (1 + take_pct)
    return stop_price, take_price, stop_pct, take_pct

def position_size(capital, probability, historical_winrate=None):
    size_pct = 0.05
    trade_capital = capital * size_pct
    return trade_capital, size_pct
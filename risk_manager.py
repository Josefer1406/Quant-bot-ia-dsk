import numpy as np
import config

def calculate_dynamic_stops(entry_price, atr, regime='lateral'):
    if regime == 'bull':
        sl_mult = config.DEFAULT_STOP_MULTIPLIER * 0.8
        tp_mult = config.DEFAULT_TAKE_MULTIPLIER * 1.2
    elif regime == 'bear':
        sl_mult = config.DEFAULT_STOP_MULTIPLIER * 1.2
        tp_mult = config.DEFAULT_TAKE_MULTIPLIER * 0.8
    else:
        sl_mult = config.DEFAULT_STOP_MULTIPLIER
        tp_mult = config.DEFAULT_TAKE_MULTIPLIER
    stop_pct = (atr * sl_mult) / entry_price
    take_pct = (atr * tp_mult) / entry_price
    stop_pct = min(max(stop_pct, config.MIN_STOP_PERCENT), config.MAX_STOP_PERCENT)
    take_pct = min(take_pct, 0.10)
    stop_price = entry_price * (1 - stop_pct)
    take_price = entry_price * (1 + take_pct)
    return stop_price, take_price, stop_pct, take_pct

def position_size(capital, probability, historical_winrate=None, kelly_fraction=config.KELLY_FRACTION):
    if historical_winrate is None:
        winrate = probability
        avg_win = 0.02
        avg_loss = 0.01
    else:
        winrate = historical_winrate
        avg_win = 0.02
        avg_loss = 0.01
    b = avg_win / avg_loss if avg_loss > 0 else 1
    kelly = (winrate * b - (1 - winrate)) / b
    kelly = max(0, min(kelly, 0.25))
    size_pct = kelly * kelly_fraction
    size_pct = max(min(size_pct, config.MAX_POSITION_SIZE_PCT), config.MIN_POSITION_SIZE_PCT)
    trade_capital = capital * size_pct
    return trade_capital, size_pct

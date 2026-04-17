import json
import time
import config

class Portfolio:
    def __init__(self):
        self.capital_initial = config.CAPITAL_INICIAL
        self.capital = config.CAPITAL_INICIAL
        self.positions = {}
        self.trades_history = []
        self.last_trade_time = 0
        self.cooldown = config.COOLDOWN_BASE
        self.load_state()
    
    def save_state(self):
        state = {
            'capital': self.capital,
            'positions': self.positions,
            'trades_history': self.trades_history[-200:],
            'last_trade_time': self.last_trade_time,
            'cooldown': self.cooldown
        }
        with open(config.PORTFOLIO_STATE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        try:
            with open(config.PORTFOLIO_STATE, 'r') as f:
                state = json.load(f)
            self.capital = state.get('capital', self.capital_initial)
            self.positions = state.get('positions', {})
            self.trades_history = state.get('trades_history', [])
            self.last_trade_time = state.get('last_trade_time', 0)
            self.cooldown = state.get('cooldown', config.COOLDOWN_BASE)
        except:
            pass
    
    def can_open_position(self):
        return (time.time() - self.last_trade_time) > self.cooldown
    
    def update_cooldown(self):
        pass
    
    def add_position(self, symbol, entry_price, quantity, stop_loss, take_profit, score, timestamp):
        if len(self.positions) >= config.MAX_POSICIONES:
            return False
        self.positions[symbol] = {
            'entry': entry_price,
            'quantity': quantity,
            'investment': quantity * entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'max_price': entry_price,
            'score': score,
            'open_time': timestamp
        }
        self.capital -= quantity * entry_price
        self.last_trade_time = timestamp
        self.save_state()
        return True
    
    def close_position(self, symbol, exit_price, reason):
        pos = self.positions.pop(symbol)
        pnl = (exit_price - pos['entry']) / pos['entry']
        self.capital += pos['quantity'] * exit_price
        trade_record = {
            'symbol': symbol,
            'entry': pos['entry'],
            'exit': exit_price,
            'pnl': pnl,
            'reason': reason,
            'timestamp': time.time()
        }
        self.trades_history.append(trade_record)
        self.save_state()
        print(f"🔴 CERRAR {symbol} | PnL {pnl*100:.2f}% | {reason}")
        return pnl
    
    def update_positions(self, current_prices):
        for symbol, pos in list(self.positions.items()):
            price = current_prices.get(symbol)
            if price is None:
                continue
            if price > pos['max_price']:
                pos['max_price'] = price
            if price <= pos['stop_loss']:
                self.close_position(symbol, price, 'stop_loss')
            elif price >= pos['take_profit']:
                self.close_position(symbol, price, 'take_profit')

portfolio = Portfolio()
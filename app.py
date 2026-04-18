from flask import Flask, jsonify
import threading
import time
import config
from yfinance_fetcher import fetcher
from signal_generator import generate_signal
from portfolio import portfolio
from risk_manager import calculate_dynamic_stops, position_size
from executor import execute_buy
from ml_model import ml_model

app = Flask(__name__)
trade_counter = 0

def refresh_data():
    prices = {}
    dataframes = {}
    for symbol in config.UNIVERSE:
        df = fetcher.fetch_ohlcv(symbol, period="7d", interval=config.TIMEFRAME)
        if df is not None and len(df) >= 30:
            dataframes[symbol] = df
            price = fetcher.fetch_current_price(symbol)
            prices[symbol] = price if price > 0 else df['close'].iloc[-1]
        else:
            print(f"⚠️ Datos insuficientes para {symbol}")
        time.sleep(0.3)
    return prices, dataframes

def bot_loop():
    global trade_counter
    print("🚀 BOT QUANT INSTITUCIONAL (Yahoo Finance) INICIADO")
    while True:
        try:
            prices, dataframes = refresh_data()
            if not dataframes:
                time.sleep(10)
                continue
            
            portfolio.update_positions(prices)
            signals = []
            for symbol, df in dataframes.items():
                signal, prob, score = generate_signal(symbol, df)
                if signal:
                    signals.append((symbol, prob, score, df, prices[symbol]))
            
            if not signals:
                print("⛔ No hay señales")
                time.sleep(config.CYCLE_SECONDS)
                continue
            
            signals.sort(key=lambda x: x[2], reverse=True)
            for symbol, prob, score, df, price in signals:
                if len(portfolio.positions) >= config.MAX_POSICIONES:
                    break
                # Correlación
                grupo = None
                for g, lst in config.CORRELATION_GROUPS.items():
                    if symbol in lst:
                        grupo = g
                        break
                if grupo and any(s in portfolio.positions for s in config.CORRELATION_GROUPS.get(grupo, [])):
                    print(f"⚠️ Correlación evitada: {symbol}")
                    continue
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0.01
                stop_p, take_p, stop_pct, take_pct = calculate_dynamic_stops(price, atr)
                trade_capital, size_pct = position_size(portfolio.capital, prob, portfolio.get_historical_winrate())
                if trade_capital < 30:
                    continue
                quantity = trade_capital / price
                executed = execute_buy(symbol, quantity, price)
                if executed:
                    ok = portfolio.add_position(symbol, executed['price'], quantity, stop_p, take_p, score, time.time())
                    if ok:
                        print(f"✅ COMPRA {symbol} | ${trade_capital:.2f} | prob {prob:.2f}")
                        trade_counter += 1
            
            if trade_counter >= config.ML_RETRAIN_EVERY_TRADES:
                all_dfs = list(dataframes.values())
                ml_model.train(all_dfs)
                trade_counter = 0
            
            portfolio.save_state()
            print(f"💰 Capital: ${portfolio.capital:.2f} | Posiciones: {list(portfolio.positions.keys())}")
            time.sleep(config.CYCLE_SECONDS)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

@app.route('/data')
def data():
    # Estadísticas adicionales
    total_trades = len(portfolio.trades_history)
    winning_trades = [t for t in portfolio.trades_history if t['pnl'] > 0]
    losing_trades = [t for t in portfolio.trades_history if t['pnl'] <= 0]
    total_pnl = sum(t['pnl'] for t in portfolio.trades_history)
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    best_trade = max(winning_trades, key=lambda x: x['pnl'], default={'pnl': 0})['pnl']
    worst_trade = min(losing_trades, key=lambda x: x['pnl'], default={'pnl': 0})['pnl']
    
    return jsonify({
        'capital': portfolio.capital,
        'capital_inicial': portfolio.capital_initial,
        'pnl': portfolio.capital - portfolio.capital_initial,
        'pnl_pct': ((portfolio.capital - portfolio.capital_initial) / portfolio.capital_initial) * 100,
        'posiciones': portfolio.positions,
        'historial': portfolio.trades_history[-50:],
        'total_trades': total_trades,
        'winrate': (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0,
        'avg_win_pct': avg_win * 100,
        'avg_loss_pct': avg_loss * 100,
        'best_trade_pct': best_trade * 100,
        'worst_trade_pct': worst_trade * 100,
        'total_pnl_pct': total_pnl * 100
    })

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
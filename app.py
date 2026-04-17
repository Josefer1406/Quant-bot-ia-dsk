from flask import Flask, jsonify
import threading
import time
import config
from data_fetcher import data_fetcher
from signal_generator import generate_signal
from portfolio import portfolio
from risk_manager import calculate_dynamic_stops, position_size
from executor import execute_buy

app = Flask(__name__)

def refresh_data():
    prices = {}
    dataframes = {}
    for symbol in config.UNIVERSE:
        df = data_fetcher.fetch_ohlcv(symbol, limit=config.HISTORY_LIMIT)
        if df is not None and len(df) > 50:
            dataframes[symbol] = df
            ticker = data_fetcher.fetch_ticker(symbol)
            prices[symbol] = ticker['last'] if ticker else df['close'].iloc[-1]
    return prices, dataframes

def bot_loop():
    print("🚀 BOT SIMPLIFICADO INICIADO (Bybit)")
    while True:
        try:
            prices, dataframes = refresh_data()
            if not dataframes:
                time.sleep(5)
                continue
            
            portfolio.update_positions(prices)
            
            for symbol, df in dataframes.items():
                signal, score = generate_signal(symbol, df)
                if not signal:
                    continue
                
                # Verificar espacio
                if len(portfolio.positions) >= config.MAX_POSICIONES:
                    continue
                
                # Calcular stops
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0.01
                stop_p, take_p, stop_pct, take_pct = calculate_dynamic_stops(prices[symbol], atr)
                trade_capital, size_pct = position_size(portfolio.capital, score)
                quantity = trade_capital / prices[symbol]
                if quantity * prices[symbol] < 30:
                    continue
                
                executed = execute_buy(symbol, quantity, prices[symbol])
                if executed:
                    ok = portfolio.add_position(symbol, executed['price'], quantity, stop_p, take_p, score, time.time())
                    if ok:
                        print(f"✅ COMPRA {symbol} | ${trade_capital:.2f} | score {score:.2f}")
            
            portfolio.save_state()
            print(f"💰 Capital: ${portfolio.capital:.2f} | Posiciones: {list(portfolio.positions.keys())}")
            time.sleep(config.CYCLE_SECONDS)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

@app.route('/data')
def data():
    return jsonify({
        'capital': portfolio.capital,
        'capital_inicial': portfolio.capital_initial,
        'pnl': portfolio.capital - portfolio.capital_initial,
        'posiciones': portfolio.positions,
        'historial': portfolio.trades_history[-20:]
    })

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
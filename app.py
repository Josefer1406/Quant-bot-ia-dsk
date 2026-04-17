from flask import Flask, jsonify
import threading
import time
import config
from coingecko_fetcher import fetcher
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
    for coin_id in config.UNIVERSE:
        df = fetcher.fetch_ohlcv(coin_id, days=7)
        if df is not None and len(df) > 50:
            dataframes[coin_id] = df
            price = fetcher.fetch_current_price(coin_id)
            prices[coin_id] = price if price > 0 else df['close'].iloc[-1]
        else:
            print(f"⚠️ Datos insuficientes para {coin_id}")
    return prices, dataframes

def bot_loop():
    global trade_counter
    print("🚀 BOT QUANT INSTITUCIONAL (CoinGecko) INICIADO")
    while True:
        try:
            prices, dataframes = refresh_data()
            if not dataframes:
                time.sleep(10)
                continue
            
            portfolio.update_positions(prices)
            signals = []
            for coin_id, df in dataframes.items():
                signal, prob, score = generate_signal(coin_id, df)
                if signal:
                    signals.append((coin_id, prob, score, df, prices[coin_id]))
            
            if not signals:
                print("⛔ No hay señales")
                time.sleep(config.CYCLE_SECONDS)
                continue
            
            signals.sort(key=lambda x: x[2], reverse=True)
            for coin_id, prob, score, df, price in signals:
                if len(portfolio.positions) >= config.MAX_POSICIONES:
                    break
                # Correlación
                grupo = None
                for g, lst in config.CORRELATION_GROUPS.items():
                    if coin_id in lst:
                        grupo = g
                        break
                if grupo and any(s in portfolio.positions for s in config.CORRELATION_GROUPS.get(grupo, [])):
                    print(f"⚠️ Correlación evitada: {coin_id}")
                    continue
                # Calcular stops
                atr = df['atr'].iloc[-1] if 'atr' in df.columns else 0.01
                stop_p, take_p, stop_pct, take_pct = calculate_dynamic_stops(price, atr)
                trade_capital, size_pct = position_size(portfolio.capital, prob, portfolio.get_historical_winrate())
                if trade_capital < 30:
                    continue
                quantity = trade_capital / price
                executed = execute_buy(coin_id, quantity, price)
                if executed:
                    ok = portfolio.add_position(coin_id, executed['price'], quantity, stop_p, take_p, score, time.time())
                    if ok:
                        print(f"✅ COMPRA {coin_id} | ${trade_capital:.2f} | prob {prob:.2f}")
                        trade_counter += 1
            
            # Reentrenar ML cada ciertos trades
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
    return jsonify({
        'capital': portfolio.capital,
        'capital_inicial': portfolio.capital_initial,
        'pnl': portfolio.capital - portfolio.capital_initial,
        'posiciones': portfolio.positions,
        'historial': portfolio.trades_history[-50:]
    })

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
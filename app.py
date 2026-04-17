from flask import Flask, jsonify
import threading
import time
import config
from data_fetcher import data_fetcher
from signal_generator import generate_signal
from portfolio import portfolio
from risk_manager import calculate_dynamic_stops, position_size
from executor import execute_buy, execute_sell
from ml_model import ml_model
from regime_detector import detect_market_regime

app = Flask(__name__)

trade_counter = 0
last_retrain_time = 0

def refresh_data():
    prices = {}
    dataframes = {}
    for symbol in config.UNIVERSE:
        df = data_fetcher.fetch_ohlcv(symbol, limit=config.HISTORY_LIMIT)
        if df is not None and len(df) > 50:
            dataframes[symbol] = df
            ticker = data_fetcher.fetch_ticker(symbol)
            if ticker and 'last' in ticker and ticker['last'] is not None:
                prices[symbol] = ticker['last']
            else:
                prices[symbol] = df['close'].iloc[-1]
        else:
            print(f"⚠️ Datos insuficientes para {symbol}")
    return prices, dataframes

def select_best_signals(signals):
    valid = [(s, data) for s, data in signals.items() if data.get('signal') == 'buy']
    valid.sort(key=lambda x: x[1]['score'], reverse=True)
    return valid

def bot_loop():
    global trade_counter, last_retrain_time
    print("🚀 BOT QUANT INSTITUCIONAL INICIADO")
    print(f"📈 Modo: {'SIMULACIÓN' if config.SIMULATION_MODE else 'REAL'}")
    while True:
        try:
            prices, dataframes = refresh_data()
            if not dataframes:
                time.sleep(5)
                continue
            portfolio.update_positions(prices)
            signals = {}
            for symbol, df in dataframes.items():
                try:
                    signal, prob, score = generate_signal(symbol, df)
                    if signal:
                        signals[symbol] = {
                            'signal': signal,
                            'probability': prob,
                            'score': score,
                            'price': prices.get(symbol, df['close'].iloc[-1]),
                            'df': df
                        }
                except Exception as e:
                    print(f"⚠️ Error generando señal para {symbol}: {e}")
            if not signals:
                print("⛔ No hay señales válidas")
                time.sleep(config.CYCLE_SECONDS)
                continue
            ranked = select_best_signals(signals)
            if not ranked:
                time.sleep(config.CYCLE_SECONDS)
                continue
            current_positions = len(portfolio.positions)
            if current_positions < config.MAX_POSICIONES:
                for symbol, sig in ranked[:config.MAX_POSICIONES - current_positions]:
                    grupo = None
                    for g, lst in config.CORRELATION_GROUPS.items():
                        if symbol in lst:
                            grupo = g
                            break
                    if grupo and any(s in portfolio.positions for s in config.CORRELATION_GROUPS.get(grupo, [])):
                        print(f"   ⚠️ Correlación evitada: {symbol} (grupo {grupo})")
                        continue
                    df = sig['df']
                    if 'atr' in df.columns and not df['atr'].isna().all():
                        atr = df['atr'].iloc[-1]
                    else:
                        atr = df['close'].pct_change().std() * config.DEFAULT_ATR_PERIOD
                    atr = max(atr, 0.001)
                    regime = detect_market_regime(df)
                    stop_price, take_price, stop_pct, take_pct = calculate_dynamic_stops(sig['price'], atr, regime)
                    winrate_hist = portfolio.get_historical_winrate()
                    trade_capital, size_pct = position_size(portfolio.capital, sig['probability'], winrate_hist)
                    if trade_capital > portfolio.capital:
                        trade_capital = portfolio.capital * 0.95
                    quantity = trade_capital / sig['price']
                    if quantity * sig['price'] < 30:
                        continue
                    executed = execute_buy(symbol, quantity, sig['price'])
                    if executed:
                        ok = portfolio.add_position(symbol, executed['price'], quantity, stop_price, take_price, sig['probability'], sig['score'], time.time())
                        if ok:
                            print(f"   ✅ COMPRA {symbol} | ${trade_capital:.2f} ({size_pct*100:.1f}%) | prob {sig['probability']:.2f} | SL {stop_pct*100:.2f}% | TP {take_pct*100:.2f}%")
                            trade_counter += 1
            else:
                print("   📊 Sin espacio, esperando cierre de posiciones")
            if trade_counter >= config.ML_RETRAIN_EVERY_TRADES and (time.time() - last_retrain_time) > 3600:
                all_dfs = list(dataframes.values())
                if len(all_dfs) > 5:
                    ml_model.train(all_dfs)
                    last_retrain_time = time.time()
                    trade_counter = 0
            portfolio.update_cooldown()
            portfolio.save_state()
            print(f"💰 Capital: ${portfolio.capital:.2f} | Posiciones: {list(portfolio.positions.keys())} | Cooldown: {portfolio.cooldown}s")
            time.sleep(config.CYCLE_SECONDS)
        except Exception as e:
            print(f"❌ Error en bucle principal: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)

@app.route('/data')
def data():
    return jsonify({
        'capital': portfolio.capital,
        'capital_inicial': portfolio.capital_initial,
        'pnl': portfolio.capital - portfolio.capital_initial,
        'pnl_pct': (portfolio.capital - portfolio.capital_initial) / portfolio.capital_initial * 100,
        'posiciones': portfolio.positions,
        'historial': portfolio.trades_history[-50:]
    })

if __name__ == '__main__':
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📊 Bot Quant Institucional - Dashboard")

BOT_URL = st.secrets.get("BOT_URL", "https://tu-bot.up.railway.app/data")

@st.cache_data(ttl=5)
def fetch_data():
    try:
        r = requests.get(BOT_URL, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

data = fetch_data()
if not data:
    st.error("No se pudo conectar al bot")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Capital Actual", f"${data['capital']:,.2f}", delta=f"${data['pnl']:,.2f}")
col2.metric("PnL %", f"{data['pnl_pct']:.2f}%")
winrate = None
if data['historial']:
    trades = pd.DataFrame(data['historial'])
    winrate = (trades['pnl'] > 0).mean() * 100
col3.metric("Winrate", f"{winrate:.1f}%" if winrate else "N/A")

st.subheader("Posiciones Abiertas")
if data['posiciones']:
    df_pos = pd.DataFrame(data['posiciones']).T
    st.dataframe(df_pos[['entry', 'quantity', 'investment', 'stop_loss', 'take_profit']])
else:
    st.info("Sin posiciones")

st.subheader("Últimos Trades")
if data['historial']:
    df_hist = pd.DataFrame(data['historial'][-20:])
    df_hist['pnl_pct'] = df_hist['pnl'] * 100
    st.dataframe(df_hist[['symbol', 'entry', 'exit', 'pnl_pct', 'reason']])
    equity = [data['capital_inicial']]
    for t in data['historial']:
        equity.append(t['capital'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=equity, mode='lines', name='Capital'))
    fig.update_layout(title="Evolución del Capital", xaxis_title="Trade #", yaxis_title="USD")
    st.plotly_chart(fig)
else:
    st.info("Aún no hay trades cerrados")

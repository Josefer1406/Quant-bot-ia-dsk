import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("📊 Bot Quant Institucional - Dashboard")

# La URL se configurará como un secreto en Streamlit Cloud
BOT_URL = st.secrets.get("BOT_URL", "https://tu-bot.up.railway.app/data")

@st.cache_data(ttl=5)
def fetch_data():
    try:
        r = requests.get(BOT_URL, timeout=5)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error conectando: {e}")
        return None

data = fetch_data()
if not data:
    st.error("No se pudo conectar al bot. Verifica la URL y que el bot esté corriendo.")
    st.stop()

# Calcular pnl_pct manualmente si no viene
capital_inicial = data.get('capital_inicial', 1000)
capital_actual = data.get('capital', 0)
pnl = capital_actual - capital_inicial
pnl_pct = (pnl / capital_inicial) * 100 if capital_inicial != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Capital Actual", f"${capital_actual:,.2f}", delta=f"${pnl:,.2f}")
col2.metric("PnL %", f"{pnl_pct:.2f}%")

winrate = None
historial = data.get('historial', [])
if historial:
    trades = pd.DataFrame(historial)
    # Asegurar que 'pnl' existe
    if 'pnl' in trades.columns:
        winrate = (trades['pnl'] > 0).mean() * 100
    else:
        winrate = 0
col3.metric("Winrate", f"{winrate:.1f}%" if winrate is not None else "N/A")

st.subheader("Posiciones Abiertas")
posiciones = data.get('posiciones', {})
if posiciones:
    df_pos = pd.DataFrame(posiciones).T
    # Mostrar solo columnas relevantes si existen
    cols_to_show = [c for c in ['entry', 'quantity', 'investment', 'stop_loss', 'take_profit'] if c in df_pos.columns]
    if cols_to_show:
        st.dataframe(df_pos[cols_to_show])
    else:
        st.dataframe(df_pos)
else:
    st.info("Sin posiciones abiertas")

st.subheader("Últimos Trades")
if historial:
    df_hist = pd.DataFrame(historial[-20:])
    if 'pnl' in df_hist.columns:
        df_hist['pnl_pct'] = df_hist['pnl'] * 100
        st.dataframe(df_hist[['symbol', 'entry', 'exit', 'pnl_pct', 'reason']])
    else:
        st.dataframe(df_hist)
    
    # Curva de equity
    equity = [capital_inicial]
    for trade in historial:
        if 'capital' in trade:
            equity.append(trade['capital'])
        else:
            # Si no hay capital en cada trade, usar el último conocido
            equity.append(equity[-1])
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=equity, mode='lines', name='Capital', line=dict(color='green', width=2)))
    fig.add_hline(y=capital_inicial, line_dash="dash", line_color="gray", annotation_text="Capital Inicial")
    fig.update_layout(title="Evolución del Capital", xaxis_title="Trade #", yaxis_title="USD", height=400)
    st.plotly_chart(fig)
else:
    st.info("Aún no hay trades cerrados")
import streamlit as st
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("Bot Simplificado - Dashboard")

BOT_URL = st.secrets.get("BOT_URL", "https://tu-bot.up.railway.app/data")

@st.cache_data(ttl=5)
def fetch():
    try:
        r = requests.get(BOT_URL, timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None

data = fetch()
if data:
    st.metric("Capital", f"${data['capital']:,.2f}")
    st.metric("PnL", f"${data['pnl']:,.2f}")
    st.subheader("Posiciones")
    if data['posiciones']:
        st.dataframe(pd.DataFrame(data['posiciones']).T)
    st.subheader("Historial")
    if data['historial']:
        st.dataframe(pd.DataFrame(data['historial']))
else:
    st.error("Sin conexión")
import streamlit as st
import pandas as pd

api = login()
historicParam = {
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "FIFTEEN_MINUTE",
    "fromdate": "2024-02-13 09:15",
    "todate": "2024-02-13 09:45"
}
data = api.obj.getCandleData(historicParam)['data']
print(data)


lst = [
    ['HINDALCO', 0, 100, 0, 0, 0],
    ['SBIN', 0, 100, 0, 0, 0],
    ['TRIDENT', 0, 0, 0, 0],
    ['HDFC', 0, 100, 0, 0, 0],
]
df = pd.DataFrame(columns=['stock', 'token', 'open',
                  'high', 'low', 'close'], data=lst)

bs_options = ['buy', 'sell', 'bns']
config = {
    'stock': st.column_config.TextColumn('stock (required)', width='large', required=True),
    'token': st.column_config.NumberColumn('token (optional)'),
    'open': st.column_config.NumberColumn('open (optional)'),
    'high': st.column_config.NumberColumn('high (optional)'),
    'low': st.column_config.NumberColumn('low (optional)'),
    'close': st.column_config.NumberColumn('close, (optional)'),
    'bs': st.column_config.SelectboxColumn('bs, bs_options')
}

result = st.data_editor(df, column_config=config, num_rows='dynamic')
st.write(result)
print(result)

import pandas as pd
import requests
from ctaConstants.typedef import TYPEDEF, API_URL


def split_symbol(symbol):
    ccy_map = TYPEDEF['SYMBOL_CCY_MAP'][symbol]
    base_ccy = ccy_map['base_currency']
    quote_ccy = ccy_map['quote_currency']
    return base_ccy, quote_ccy


def get_marketdata(start_date, end_date, sublist):
    marketdata = {}
    start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    sublist = sublist if isinstance(sublist, list) else [sublist]
    for identifier in sublist:
        exchange, symbol, contract_type = identifier.split('|')
        _symbol = '_'.join(split_symbol(symbol)).lower()
        url = f"{API_URL}/kline?from={start_date}&to={end_date}&exchange={exchange.lower()}&symbol={_symbol.lower()}&contract_type={contract_type}"
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.DataFrame(response.json()['data'])
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = pd.to_datetime(df['time']).dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)
            marketdata[identifier] = df
    return marketdata


def metadata_generator(marketdata):
    metadata_dict = {}
    for identifier in marketdata.keys():
        _metadata_dict = {_['time']: {identifier: _} for _ in marketdata[identifier].to_dict('record')}
        for key in _metadata_dict.keys():
            if key in metadata_dict:
                metadata_dict[key].update(_metadata_dict[key])
            else:
                metadata_dict[key] = _metadata_dict[key]
    for time in sorted(metadata_dict.keys()):
        yield metadata_dict[time]

import pandas as pd
from ctaBacktesting.ctaHistData import get_marketdata, metadata_generator
from ctaConstants.typedef import FEERATE


def get_fee_rate(identifier):
    """
    如发现手续费不对可在/ctaConstants/feerate.json中可更改
    """
    exchange, symbol, contract_type = identifier.split('|')
    try:
        return FEERATE[exchange.lower()][contract_type]
    except KeyError:
        return FEERATE[exchange.lower()]['future']


class CTAEngine(object):
    def __init__(self):
        self.strategy = None            # 策略实例
        self.start_date = None          # 回测开始日期
        self.end_date = None            # 回测结束日期
        self.init_days = 0              # 用于初始化的天数

        self.positions = {}             # 当前仓位
        self.orders = []                # 当前订单
        self.order_records = []         # 订单记录
        self.fill_records = []          # 成交记录

        self.fee_rates = {}             # 手续费率

    def init_strategy(self, strategy_class, **settings):
        """
        :param strategy_class: 用于回测的策略class，注意是class不是instance
        :param settings: 策略class初始化的参数
        """
        self.strategy = strategy_class(self, **settings)
        self.fee_rates = {_: get_fee_rate(_) for _ in self.strategy.sublist}
        self.positions = {_: 0 for _ in self.strategy.sublist}

    def on_bar(self, metadata):
        """
        订单撮合
        """
        while self.orders:
            order = self.orders.pop(0)
            bar = metadata[order['identifier']]

            if order['type'] == 'limit':
                if order['direction'] == 'buy' and order['price'] >= bar['low']:
                    price = min(order['price'], bar['low'])
                elif order['direction'] == 'sell' and order['price'] <= bar['high']:
                    price = max(order['price'], bar['high'])
                else:
                    price = 0
            else:
                price = bar['open']

            quantity = min(order['quantity'], bar['volume'])

            if price > 0 and quantity > 0:
                fill = {
                    'time': bar['time'],
                    'identifier': order['identifier'],
                    'direction': order['direction'],
                    'price': price,
                    'quantity': quantity,
                    'fee': self.fee_rates[order['identifier']]['taker'] * price * quantity
                }
                self.fill_records.append(fill)

                if order['direction'] == 'buy':
                    self.positions[order['identifier']] += quantity
                else:
                    self.positions[order['identifier']] -= quantity

                order['filled_quantity'] = quantity
                order['avg_executed_price'] = price
                order['executed_time'] = bar['time']
                order['status'] = 'filled' if order['filled_quantity'] >= order['quantity'] else 'partially_filled'
            else:
                order['status'] = 'cancelled'
            self.order_records.append(order)

    def get_backtest_results(self):
        # TODO
        while self.orders:
            order = self.orders.pop(0)
            order['status'] = 'cancelled'
        results = {
            'order_df': pd.DataFrame(self.order_records),
            'fill_df': pd.DataFrame(self.fill_records)
        }
        return results

    def plot(self):
        # TODO
        pass

    def run_backtest(self):
        if self.strategy.init_days > 0:
            init_start_date = (pd.to_datetime(self.strategy.start_date) - pd.Timedelta('1d') * self.strategy.init_days).strftime('%Y-%m-%d')
            init_marketdata = get_marketdata(init_start_date, self.strategy.start_date, self.strategy.sublist)
            self.strategy.on_init(init_marketdata)
        marketdata = get_marketdata(self.strategy.start_date, self.strategy.end_date, self.strategy.sublist)
        self.strategy.on_marketdata(marketdata)
        for metadata in metadata_generator(marketdata):
            self.on_bar(metadata)
            self.strategy.on_bar(metadata)
        self.get_backtest_results()

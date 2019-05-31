class StrategyBase(object):
    param_list = ['start_date', 'end_date', 'init_days', 'sublist']
    """
    策略的基类，初始化参数如下：
    :param start_date: 回测开始日期
    :param end_date: 回测结束日期
    :param init_days: 用于初始化的天数
    :param sublist: 订阅的channel，格式{exchange}|{symbol}|{contract_type}
    
    因为数据只有1m的Kline，所以channel=identifier
    
    marketdata: dict，市场数据，格式为{identifier: pd.DataFrame}
    metadata: dict，marketdata在某一时间的切片，格式为{identifier: {column: value}}
    
    """

    def __init__(self, cta_engine, **settings):
        self.cta_engine = cta_engine
        for name in StrategyBase.param_list:
            self.__setattr__(name, settings.get(name, None))

    def send_order(self, identifier, order_type, direction, price, quantity, notes):
        notes = notes or dict()
        order = {
            'identifier': identifier,
            'type': order_type,
            'direction': direction,
            'price': price,
            'quantity': quantity,
            'notes': notes,
            'filled_quantity': 0,
            'avg_executed_price': 0,
            'executed_time': None
        }
        self.cta_engine.orders.append(order)

    def buy_limit(self, identifier, price, quantity, notes=None):
        self.send_order(identifier, 'limit', 'buy', price, quantity, notes)

    def sell_limit(self, identifier, price, quantity, notes=None):
        self.send_order(identifier, 'limit', 'sell', price, quantity, notes)

    def buy_market(self, identifier, quantity, notes=None):
        self.send_order(identifier, 'market', 'buy', 0, quantity, notes)

    def sell_market(self, identifier, quantity, notes=None):
        self.send_order(identifier, 'market', 'sell', 0, quantity, notes)

    def inspect_position(self, identifier):
        return self.cta_engine.positions.get(identifier, 0)

    def on_init(self, marketdata):
        """
        初始化策略，需要具体策略自行编写
        """
        pass

    def on_marketdata(self, marketdata):
        """
        对marketdata作一些预处理，可计算一些指标放入marketdata，之后可在on_metadata中调用。注意不要使用到未来信息
        """
        pass

    def on_bar(self, metadata):
        """
        策略收到metadata时的处理
        """
        pass

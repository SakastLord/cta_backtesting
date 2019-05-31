import numpy as np
from ctaBacktesting.ctaEngine import CTAEngine
from ctaBacktesting.ctaStrategies import StrategyBase


class RandomTestStrategy(StrategyBase):
    def on_marketdata(self, marketdata):
        for identifier, df in marketdata.items():
            df['random_signal'] = np.random.random(df.shape[0])

    def on_bar(self, metadata):
        for identifier, bar in metadata.items():
            if bar['random_signal'] > 0.9:
                self.buy_market(identifier, 1)
            elif bar['random_signal'] < 0.1:
                self.sell_market(identifier, 1)
            else:
                pass


if __name__ == '__main__':
    ce = CTAEngine()
    ce.init_strategy(RandomTestStrategy, sublist=['Binance|BTCUSD|spot'], start_date='20190526', end_date='20190528', init_days=0)
    ce.run_backtest()
    print(ce.get_backtest_results())
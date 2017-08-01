#
# indicators.py
# Mike Cardillo
#
# System for containing all technical indicators and processing associated data

import talib
import logging
import numpy as np


class IndicatorSubsystem:
    def __init__(self, period_list):
        self.logger = logging.getLogger('trader-logger')
        self.current_indicators = {}
        for period in period_list:
            self.current_indicators[period.name] = {}

    def recalculate_indicators(self, cur_period):
        total_periods = len(cur_period.candlesticks)
        if total_periods > 0:
            highs = np.append(cur_period.get_highs(),
                                       cur_period.cur_candlestick.high)
            lows = np.append(cur_period.get_lows(),
                                       cur_period.cur_candlestick.low)
            closing_prices = np.append(cur_period.get_closing_prices(),
                                       cur_period.cur_candlestick.close)
            volumes = np.append(cur_period.get_volumes(),
                                cur_period.cur_candlestick.volume)

            self.calculate_macd(cur_period.name, closing_prices)
            self.calculate_vol_macd(cur_period.name, volumes)
            self.calculate_avg_volume(cur_period.name, volumes)
            self.calculate_obv(cur_period.name, closing_prices, volumes)
            self.calculate_bbands(cur_period.name, closing_prices)
            self.calculate_adx(cur_period.name, highs, lows, closing_prices)

            self.current_indicators[cur_period.name]['last_price'] = cur_period.cur_candlestick.close

            self.current_indicators[cur_period.name]['total_periods'] = total_periods

        self.logger.debug("[INDICATORS %s] Periods: %d MACD Hist: %f OBV: %f OBV EMA: %f ADX: %f BBAND_UPPER: %f BBAND_LOWER %f" %
                          (cur_period.name, self.current_indicators[cur_period.name]['total_periods'],
                           self.current_indicators[cur_period.name]['macd_hist'], self.current_indicators[cur_period.name]['obv'],
                           self.current_indicators[cur_period.name]['obv_ema'], self.current_indicators[cur_period.name]['adx'],
                           self.current_indicators[cur_period.name]['bband_upper'], self.current_indicators[cur_period.name]['bband_lower']))

    def calculate_adx(self, period_name, highs, lows, closes):
        adx = talib.ADX(highs, lows, closes, timeperiod=14)

        self.current_indicators[period_name]['adx'] = adx[-1]

    def calculate_bbands(self, period_name, close):
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        self.current_indicators[period_name]['bband_upper'] = upperband[-1]
        self.current_indicators[period_name]['bband_lower'] = lowerband[-1]

    def calculate_macd(self, period_name, closing_prices):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['macd'] = macd[-1]
        self.current_indicators[period_name]['macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['macd_hist'] = macd_hist[-1]

    def calculate_vol_macd(self, period_name, volumes):
        macd, macd_sig, macd_hist = talib.MACD(volumes, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['vol_macd'] = macd[-1]
        self.current_indicators[period_name]['vol_macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['vol_macd_hist'] = macd_hist[-1]

    def calculate_avg_volume(self, period_name, volumes):
        avg_vol = talib.SMA(volumes, timeperiod=15)

        self.current_indicators[period_name]['avg_volume'] = avg_vol[-1]

    def calculate_obv(self, period_name, closing_prices, volumes):
        # cryptowat.ch does not include the first value in their OBV
        # calculation, we we won't either to provide parity
        obv = talib.OBV(closing_prices[1:], volumes[1:])
        obv_ema = talib.EMA(obv, timeperiod=21)

        self.current_indicators[period_name]['obv_ema'] = obv_ema[-1]
        self.current_indicators[period_name]['obv'] = obv[-1]

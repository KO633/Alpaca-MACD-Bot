from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import numpy as np
import time
import os
import matplotlib.pyplot as plt

# insert own secret key and key id from alpaca
# trades on paper by defauly remove base url line to trade with real stocks: use with caution not a financial expert
os.environ['APCA_API_SECRET_KEY'] = ''
os.environ['APCA_API_KEY_ID'] = ''
os.environ['APCA_API_BASE_URL'] = 'https://paper-api.alpaca.markets'
api = REST()

symb = "AMZN"  # sets the stock that is to be traded


# function to calculate exponential moving average given an array of closing for days in order and a period of days
def emacalc(clsarr, period):
    ema = []
    ema.append(sum(clsarr[:period])/period)
    weight = 2 / (period + 1)

    for cur in clsarr[period+1:]:
        ema.append(((cur - ema[-1]) * weight) + ema[-1])

    return ema


while True:
    print("")
    print("Checking Price")

    # retrieves stock data for the past year from Alpaca
    market_data = api.get_barset(symb, 'day', limit=365)
    SymBars = market_data[symb]

    # populate list of closing prices
    close_list = []
    for bar in SymBars:
        close_list.append(bar.c)

    close_list = np.array(close_list, dtype=np.float64)

    # Calculate exponential moving averages
    emalist = emacalc(close_list, 26)
    emalist2 = emacalc(close_list, 12)
    ema2offset = len(emalist2)-len(emalist)
    clsoffset = len(close_list)-len(emalist)

    macd = np.subtract(emalist2[ema2offset:], emalist)
    macdsignal = emacalc(macd, 9)  # use macd to calculate signal line
    macdoffset = len(macd) - len(macdsignal)

    # trades by comparing today's macd to signal line if it is greater than or equal to buy otherwise sell
    if macd[-1] >= macdsignal[-1]:
        print("Buy")
        api.submit_order(
            symbol=symb,
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc'
        )

    elif macd[-1] < macdsignal[-1]:
        print("Sell")
        api.submit_order(
            symbol=symb,
            qty=1,
            side='sell',
            type='market',
            time_in_force='gtc'
        )

    time.sleep(86400)  # Checks once a day

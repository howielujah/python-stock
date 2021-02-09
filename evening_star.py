import mplfinance as mpf
import pandas_datareader as pdr
import pandas as pd
from pandas_datareader import data

tsla = pdr.get_data_tiingo(
    'tsla', api_key='835f91d034697eac471106bc47f5e768249b52c2')

# 將multi-index轉成single-index
tsla = tsla.reset_index(level=[0, 1])

# 指定date為index
tsla.index = tsla['date']

# 取adjClose至adjOpen的欄位資料
tsla_adj = tsla.iloc[:, 7:11]

# 更改columns的名稱，以讓mplfinance看得懂
tsla_adj.columns = ['Close', 'High', 'Low', 'Open']

data = tsla_adj.iloc[-365:, :]

# 繪製K線圖
# mpf.plot(tsla_adj_365d, type='candle')


def get_evening_star_sig(tsla_adj_365d):
    # 開盤價 & 收盤價
    tsla_adj_365d_open = tsla_adj_365d.Open
    tsla_adj_365d_close = tsla_adj_365d.Close

    # 當日漲跌點數
    tsla_daily_chg_365d = tsla_adj_365d_close - tsla_adj_365d_open

    # 取得每日振幅
    tsla_abs_daily_chg_365d = abs(tsla_daily_chg_365d)

    # 分析振幅統計數據，以利篩選適合的K棒
    # print(tsla_abs_daily_chg_365d.describe())

    # 抓取 第1根大振幅陽線、第2根小振幅陽線或陰線、第3根陰線且振幅大於第1根的1/2
    tsla_abs_daily_chg_365d_mean = tsla_abs_daily_chg_365d.mean(0)
    evening_condition_1 = [0, 0]
    for i in range(2, len(tsla_daily_chg_365d)):
        if(tsla_daily_chg_365d[i-2] > tsla_abs_daily_chg_365d_mean) & (abs(tsla_daily_chg_365d[i-1]) < (tsla_abs_daily_chg_365d_mean * 0.25)) & (tsla_daily_chg_365d[i] < -(tsla_abs_daily_chg_365d_mean * 0.5)):
            evening_condition_1.append(1)
        else:
            evening_condition_1.append(0)

    # condition 1 符合的次數
    print(evening_condition_1.count(1))

    # 第2根的開盤與收盤價 均大於 第1根的收盤與第3根的開盤
    evening_condition_2 = [0, 0]
    for i in range(2, len(tsla_adj_365d_open)):
        if(tsla_adj_365d_open[i-1] > tsla_adj_365d_close[i-2]) & (tsla_adj_365d_open[i-1] > tsla_adj_365d_open[i]) & (tsla_adj_365d_close[i-1] > tsla_adj_365d_close[i-2]) & (tsla_adj_365d_close[i-1] > tsla_adj_365d_open[i]):
            evening_condition_2.append(1)
        else:
            evening_condition_2.append(0)

    # condition 2 符合的次數
    print(evening_condition_2.count(1))

    # Evening Star Signal
    evening_star_signal = []
    for i in range(len(evening_condition_1)):
        if(evening_condition_1[i] == 1) & (evening_condition_2[i] == 1):
            evening_star_signal.append(1)
        else:
            evening_star_signal.append(0)

    # Find Evening Star date
    # for i in range(len(evening_star_signal)):
    #     if evening_star_signal[i] == 1:
    #         print(tsla_adj_365d.index[i])
    sig = pd.Series(index=tsla_adj_365d.index, data=evening_star_signal)
    sig = sig.astype('bool')
    return sig


sig = get_evening_star_sig(data)

ret1 = data.Open.shift(-2)/data.Open.shift(-1)
print(ret1[sig])

import requests
import pandas as pd
from time import sleep, time
from datetime import datetime
from sys import argv
from multiprocessing.dummy import Pool, Process
from collections import defaultdict

import warnings
warnings.filterwarnings('ignore')

def get_order(symbol):
  global limit, DATA
  url = 'https://api.binance.com/api/v1/trades?symbol={}&limit={}'.format(symbol, limit)
  orders = req.get(url).json()
  orders = pd.DataFrame.from_dict(orders)
  try:
    DATA[symbol] = DATA[symbol].append(orders)
  except:
    DATA[symbol] = orders

def format_unit(unit):
  return '0{}'.format(unit) if unit // 10 == 0 else unit

def format_percent(unit):
  unit = str(unit)
  return '{}%'.format(unit) if unit[0] == '-' else '+{}%'.format(unit)

def convertMillis(millis):
  millis = int(millis)
  mins = int((millis / (1000 * 60)) % 60)
  hours = int((millis / (1000 * 60 * 60)) % 24)

  mins = format_unit(mins)
  hours = format_unit(hours)

  return '{}:{}'.format(hours, mins)

def check_time(time_1, time_2):
  time_1, time_2 = time_1.split(':'), time_2.split(':')
  time_1 = int(time_1[0]) * 60 + int(time_1[1])
  time_2 = int(time_2[0]) * 60 + int(time_2[1])
  return time_2 - time_1

def increase_time(Time):
  Time = Time.split(':')
  Time = int(Time[0]) * 60 + int(Time[1])
  Time += 1
  hours = format_unit(Time // 60)
  mins = format_unit(Time % 60)
  return '{}:{}'.format(hours, mins)

def put_empty_rows(data):
  Data = data
  empty_row = pd.Series(['' for _ in range(len(list(Data.columns)))], index = list(Data.columns))
  for i in range(len(data) - 1):
    i += len(Data) - len(data)
    del_time = check_time(Data['Time'].iloc[i], Data['Time'].iloc[i + 1])
    for j in range(del_time - 1):
      line = pd.DataFrame(empty_row, index = [i + j + 1])
      line['Time'] = [increase_time(Data['Time'].iloc[i + j])]
      line['Average Price'] = [Data['Average Price'].iloc[i]]
      Data = pd.concat([Data.iloc[:i + j + 1], line, Data.iloc[i + j + 1:]], sort=False)
  Data = Data.reset_index()
  Data = Data.drop(['index'], axis=1)
  return Data

def filter_dataframe(data):
  data = data.drop(['id', 'isBestMatch', 'isBuyerMaker'], axis = 1)
  data['price'] = pd.to_numeric(data['price'], downcast = 'float').round(9)
  data['qty'] = pd.to_numeric(data['qty'], downcast = 'signed')
  data['quoteQty'] = pd.to_numeric(data['quoteQty'], downcast = 'float')
  data['time'] = data['time'].apply(convertMillis)
  data = data.rename(columns = {'time':'Time'})
  return data

def make_csv(data, year, month, day, symbol):
  data = filter_dataframe(data)

  DF = data.groupby('Time')
  dff = pd.DataFrame()

  dff['Maximum Price'] = DF.price.max()
  dff['Minimum Price'] = DF.price.min()
  dff['Average Price'] = DF.price.mean()
  dff['Total Qty'] = DF.qty.sum()
  dff['Total quoteQty'] = DF.quoteQty.sum()
  dff['TIME'] = data['Time'].unique()

  dff['Price Difference'] = ''
  dff['Price Variation'] = ''
  dff['Group Qty'] = ''
  dff['Group quoteQty'] = ''

  if len(dff) > 15:
    for i in range(len(dff)):
      for j in range(i - 1, -1, -1):
        if check_time(dff['TIME'].iloc[j], dff['TIME'].iloc[i]) == 15:
          dff['Price Difference'].iloc[i] = dff['Average Price'].iloc[i] - dff['Average Price'].iloc[j]
          dff['Price Variation'].iloc[i] = 100 * (dff['Price Difference'].iloc[i] / dff['Average Price'].iloc[j])
          dff['Group Qty'].iloc[i] = dff['Total Qty'][j: i].sum()
          dff['Group quoteQty'].iloc[i] = dff['Total quoteQty'][j: i].sum()
          break

    dff['Price Difference'] = pd.to_numeric(dff['Price Difference'], downcast = 'float')
    dff['Price Variation'] = pd.to_numeric(dff['Price Variation'], downcast = 'float').apply(lambda x:round(x, 3))
    dff['Price Variation'] = dff['Price Variation'].apply(format_percent)

    dff = dff[15:]


  dff = dff.drop(['TIME'], axis = 1)
  dff = dff.reset_index()
  dff = dff.rename(columns = {'time':'Time'})

  dff = put_empty_rows(dff)

  try:
    dff = dff.drop([0], axis = 1)
  except:
    pass
  dff.to_csv('BINANCE-{}-{}-{}-{}.csv'.format(year, month, day, symbol), float_format = '%.11f', index = False)
  print('Made File BINANCE-{}-{}-{}-{}.csv'.format(year, month, day, symbol))

def get_data(symbol):
  global start_date, start_day, DATA

  date = datetime.now()
  year, month, day = date.year, date.month, date.day
  month = format_unit(month)
  day = format_unit(day)
  if start_day != day:
    start_date = date
    start_day = day
    DATA[symbol] = None

  get_order(symbol)
  make_csv(DATA[symbol], year, month, day, symbol)

# def get_symbols():
#   url = 'https://api.binance.com/api/v1/exchangeInfo'
#   symbols = requests.get(url).json()
#   return symbols['symbols']

# symbols = get_symbols()
# sym = defaultdict(list)
# for i in symbols:
#   sym[i['baseAsset']].append(i['symbol'])
#
# df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in sym.items() ]))
# df.to_csv('symbols.csv')

if __name__ == '__main__':
  # symbols = pd.read_csv('symbols.csv')
  symbols = pd.read_csv('minilista.csv')
  symbols = list(symbols.columns)

  # try:
  #   symbols = list(symbols[argv[1]].dropna())
  # except IndexError:
  #   symbols = list(symbols['ETH'].dropna())

  limit = 1000
  # How frequently to get the orders (in seconds)
  frequency = 300
  print(len(symbols), symbols)
  DATA = {symbol:None for symbol in symbols}

  with requests.Session() as req:
    start_date = datetime.now()
    start_day = format_unit(start_date.day)
    while True:
      with Pool(7) as p:
        pm = p.imap_unordered(get_data, symbols)
        pm = [i for i in pm]
      print('-------------')
      sleep(frequency)









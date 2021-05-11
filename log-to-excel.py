from collections import defaultdict
import pandas as pd

in_scanner = 'Scanner is in the cradle'
out_scanner = 'Scanner is out of the cradle'
decode_check = 'usbt:send_decode'

input_file_name = 'lane5_LOG_20181020 (1).log'
output_file_name = 'output'
encoding = 'ANSI'
minimum_time = 1
maximum_time = 600

check = 0
timestamp = defaultdict()
data = defaultdict(list)

start, stop = False, False
with open(input_file_name, encoding=encoding) as f:
    for line in f.readlines():
        line = line.strip()
        if in_scanner in line or out_scanner in line:
            print(line)
            t = line.split()[0]
            t = [i for i in t if i.isdigit()]
            t = ''.join(t)
            if len(t) == 16:
                t = t[1:]
            print(t)
            timestamp['Year'] = t[:2]
            timestamp['Month'] = t[2:4]
            timestamp['Day'] = t[4:6]
            timestamp['Hour'] = t[6:8]
            timestamp['Minute'] = t[8:10]
            timestamp['Second'] = t[10:12]
            timestamp['Millisecond'] = t[12:]
            print(timestamp)
            if in_scanner in line:
                if start:
                    data['in'][-1] = t
                    data['Number of Scans'][-1] = check
                else:
                    data['in'].append(t)
                    data['Number of Scans'].append(check)
                start, stop, check = True, False, 0
            elif start:
                start, stop = False, True
                data['out'].append(t)
                
        elif decode_check in line and stop:
            check += 1

data['Number of Scans'] = data['Number of Scans'][1:]
df = pd.DataFrame()
for k,v in data.items():
    df[k] = pd.Series(v)
for k in ['in', 'out']:
    df[k] = pd.to_datetime(df[k], format='%y%m%d%H%M%S%f')

df['Time In Cradle Timestamp'] = df['in']
df['Time In Cradle Duration'] = (df['out'] - df['in']).dt.total_seconds()
df['Time Out Cradle Duration'] = 0
for index in range(len(df)):
    try:
        del_time = df['in'].iloc[index + 1] - df['out'].iloc[index]
        df['Time Out Cradle Duration'].iloc[index] = del_time.total_seconds()
    except Exception as e:
        pass
df['Time Out Cradle Timestamp'] = df['out']

df = df.drop(['in', 'out'], axis=1)
df = df[['Time In Cradle Timestamp', 'Time In Cradle Duration', 'Time Out Cradle Timestamp', 'Time Out Cradle Duration', 'Number of Scans']]

df = df[df['Number of Scans'] != 0]
for k in ['Time In Cradle Duration', 'Time Out Cradle Duration']:
   df = df[df[k] < maximum_time]
   df = df[df[k] > minimum_time]
df.to_excel(output_file_name + '.xlsx', index=False)



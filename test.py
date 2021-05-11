import pandas as pd
from collections import defaultdict
import re

if __name__ == '__main__':

  data = defaultdict(list)

  with open('WhatsApp Chat with Khushbu.txt', 'rb') as f:
    for line in f:
      line = str(line)
      if ':' not in line:
        continue
      line = re.split('[,-]', line, 2)
      line = line[:-1] + re.split(':', line[-1], 1)
      if len(line) == 4:
        data['Date'].append(line[0])
        data['Time'].append(line[1])
        data['Sender'].append(line[2])
        data['Message'].append(line[3])

  df = pd.DataFrame.from_dict(data)
  df.to_csv('wa.csv', encoding = 'utf-8')
import pandas as pd
from os import listdir
from os.path import isfile, join

mypath = 'personlookup/'
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

count = 0

for file in files:
	df = pd.read_csv(mypath + file)
	count += len(df)
	print(file, len(df))
	
print(count)
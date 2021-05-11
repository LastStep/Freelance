import pandas as pd

def fix(x):
    x = ''.join([i for i in x if i not in ['?','(',')','*']])
    return x.strip()


df = pd.read_excel('Proto-SBB.xlsx')
con, vox = df['Consonants'], df['Vowels']
merged = []
for _,c,v in zip(range(10000), con, vox):
    print('------------')
    print(c, v)
    if str(c) == 'nan':
        merged.append(None)
    else:
        temp = []
        for i in c.split(';'):
            i = fix(i)
            for j in v.split(';'):
                j = fix(j)
                j = ''.join([k for k in j if k != '-'])
                if len(j) == 1:
                    temp.append(i.replace('-', j))
                    print(temp[-1])
                else:
                    tempp, temppp, check = i, i, True
                    for k in j:
                        tempp = tempp.replace('-', k, 1)
                        if temppp == tempp:
                            check = False
                            break
                        temppp = tempp
                    if check:
                        print(tempp)
                        temp.append(tempp)
        temp = ': '.join(temp)
        if len(temp) != 0:
            merged.append('*'+temp)
        else:
            merged.append(None)
        print(merged[-1])

df['[Merged]'] = merged

df.to_excel('Proto-SBB-test.xlsx')
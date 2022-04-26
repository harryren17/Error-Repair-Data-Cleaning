import pandas as pd


df = pd.read_excel('SUBTLEXusfrequencyabove1.xls')
df2 = pd.read_excel('samplesort.xls')

fix = df2.sort_values(by=['Word'])

print("start")
fix.to_excel(r'C:\Users\Harry\Desktop\res\sortedSUBTLEXusfrequencyabove1.xls', index = False, header=True)
print("finish")
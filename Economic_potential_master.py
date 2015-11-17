# module imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json, urllib2

#import choropleth_map as map

pd.options.display.mpl_style = 'default'

### Data read-in 
df = pd.read_csv('C:\Users\Philipp\Python_learning\Economic potential\supply curve.csv')
df1 = pd.read_csv('C:\Users\Philipp\Python_learning\Economic potential\costs.csv')
print(df.dtypes)

# Variable definition
df['Net value'] = df['LACE'] - df['LCOE']
df['Cumulative Capacity'] = df.sort('Net value', ascending=False)['Installed Capacity'].cumsum()

# Merging

df = df.merge(df1, on=['re_class'], how='left')

# National
national = df.sort('Net value', ascending=False)
#national = national.set_index(df['Cumulative Capacity'])
#national.index.names = ['Cumulative Capacity']

national.to_csv('output.csv', replace='True')

print(national[0:4])

### Plotting function ###

plt.hist(national['LACE'],100, normed=1, facecolor='g', alpha=0.75)
#np.histogram(national['LCOE'], bins=10, range=None, normed=False, weights=None, density=None)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.set_xlim(0,df['Cumulative Capacity'].max())
plt.plot(national['Cumulative Capacity'], national['Net value'], color='black')
plt.axhline(y=0, linewidth=2, color = 'red')

plt.xticks(fontsize = 12, fontname='Tahoma')
plt.yticks(fontsize = 12, fontname='Tahoma')

plt.xlabel('Cumulative Capacity (in GW)', fontsize=15, fontname='Tahoma', color='black')
plt.ylabel('Net value (in $/MWh)', fontsize=15, fontname='Tahoma', color='black')
plt.title('Net value supply curve', fontsize=20, fontname='Tahoma')
plt.show(block=True)

### Choropleth map ###






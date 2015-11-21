### module imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json, urllib2

#import choropleth_map as c_map
#import LACE_calc

### Data read-in 
df = pd.read_csv("supply curve.csv")
df1 = pd.read_csv("costs.csv")
print(df.dtypes)

# Variable definition
df['Net value'] = df['LACE'] - df['LCOE']
df['Cumulative Capacity'] = df.sort('Net value', ascending=False)['Installed Capacity'].cumsum()
df['state_results'] = df.groupby('State')['Net value'].transform('sum')

# Merging
df = df.merge(df1, on=['re_class'], how='left')

# National
national = df.sort('Net value', ascending=False)
#national = national.set_index(df['Cumulative Capacity'])
#national.index.names = ['Cumulative Capacity']

print(national.describe())
print(national['state_results'])
#national.to_csv('output.csv', replace='True')


### Plotting function ###

pd.options.display.mpl_style = 'default'

###Histogram
plt.hist(national['LACE'],100, normed=1, facecolor='g', alpha=0.75)
#np.histogram(national['LCOE'], bins=10, range=None, normed=False, weights=None, density=None)

### Figures
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax1.set_xlim(0,df['Cumulative Capacity'].max())
#plt.plot(national['Cumulative Capacity'], national['Net value'], color='black')
plt.axhline(y=0, linewidth=2, color = 'red')

plt.xticks(fontsize = 12, fontname='Tahoma')
plt.yticks(fontsize = 12, fontname='Tahoma')

plt.xlabel('Cumulative Capacity (in GW)', fontsize=15, fontname='Tahoma', color='black')
plt.ylabel('Net value (in $/MWh)', fontsize=15, fontname='Tahoma', color='black')
plt.title('Net value supply curve', fontsize=20, fontname='Tahoma')
#plt.show(block=True)

### Choropleth map
#c_map.





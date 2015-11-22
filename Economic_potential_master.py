### module imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import json, urllib2
import plotly.plotly as py
#TD import LACE_calc

### Data read-in 
df = pd.read_csv("supply curve.csv")
df1 = pd.read_csv("costs.csv")
print(df.dtypes)

### Variable definition

state_abbrev = {
        'Alaska': 'AK',	      
        'Alabama': 'AL',          
        'Arkansas': 'AR',                 
        'Arizona': 'AZ',          
        'California': 'CA',          
        'Colorado': 'CO',          
        'Connecticut': 'CT',          
        'District of Columbia': 'DC',          
        'Delaware': 'DE',          
        'Florida': 'FL',          
        'Georgia': 'GA',                 
        'Hawaii': 'HI',          
        'Iowa': 'IA',          
        'Idaho': 'ID',          
        'Illinois': 'IL',          
        'Indiana': 'IN',          
        'Kansas': 'KS',          
        'Kentucky': 'KY',          
        'Louisiana': 'LA',          
        'Massachusetts': 'MA',          
        'Maryland': 'MD',          
        'Maine': 'ME',          
        'Michigan': 'MI',          
        'Minnesota': 'MN',          
        'Missouri': 'MO',                 
        'Mississippi': 'MS',          
        'Montana': 'MT',          
        'National': 'NA',          
        'North Carolina': 'NC',          
        'North Dakota': 'ND',          
        'Nebraska': 'NE',          
        'New Hampshire': 'NH',          
        'New Jersey': 'NJ',          
        'New Mexico': 'NM',          
        'Nevada': 'NV',          
        'New York': 'NY',          
        'Ohio': 'OH',          
        'Oklahoma': 'OK',          
        'Oregon': 'OR',          
        'Pennsylvania': 'PA',                   
        'Rhode Island': 'RI',          
        'South Carolina': 'SC',          
        'South Dakota': 'SD',          
        'Tennessee': 'TN',          
        'Texas': 'TX',          
        'Utah': 'UT',          
        'Virginia': 'VA',          
        'Virgin Islands': 'VI',          
        'Vermont': 'VT',          
        'Washington': 'WA',          
        'Wisconsin': 'WI',          
        'West Virginia': 'WV',          
        'Wyoming': 'WY',          
}                                

df_state_abbrev = pd.DataFrame(state_abbrev.items(), columns=['State', 'State_abbrev'])

df['Net value'] = df['LACE'] - df['LCOE']
df['Cumulative Capacity'] = df.sort_values('Net value', ascending=False)['Installed Capacity'].cumsum()
df['Economic potential (MWh)'] = np.where(df['Net value']>0, df['Annual Generation (MWh)'], 0)
df['state_results'] = df.groupby('State')['Economic potential (MWh)'].transform('sum')              
 
### Merging                                      
df = df.merge(df1, on=['re_class'], how='left')
df = df.merge(df_state_abbrev,on=['State'],how='left')

df_state_results = pd.concat([df['State_abbrev'], df['state_results']], axis=1).drop_duplicates().reset_index(drop=True)
df_state_results = df_state_results.sort_values('State_abbrev', ascending=True, inplace=False, kind='quicksort')

### National
national = df.sort_values('Net value', ascending=False)
#national = national.set_index(df['Cumulative Capacity'])
#national.index.names = ['Cumulative Capacity']

print(national.describe())
national.to_csv('output.csv', replace='True')


### Plotting function ###

pd.options.display.mpl_style = 'default'

###Histogram
"""\
plt.hist(national['LACE'],100, normed=1, facecolor='g', alpha=0.75)
#np.histogram(national['LCOE'], bins=10, range=None, normed=False, weights=None, density=None)
"""

### Figures
"""\
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
"""

### Choropleth map
#plotly_ssl_verification = False , plotly_ssl_verification
py.sign_in("pbeiter","1ygvgjoipe",plotly_ssl_verification=False)

scl = [[0.0, 'rgb(255,255,255)'],[0.2, 'rgb(0,205,0)'],[0.4, 'rgb(0,139,0)'],\
            [0.6, 'rgb(0,128,0)'],[0.8, 'rgb(0,100,0)'],[1.0, 'rgb(0,128,20)']]


state_results_TWh = df_state_results['state_results']/1000000
states = national['State_abbrev'].drop_duplicates().reset_index(drop=True)
states = states.sort_values(ascending=True, inplace=False, kind='quicksort')

national['text'] = 'TWh' #+ '<br>' + states]

choropleth_data = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = states,
					z = state_results_TWh,
					locationmode = 'USA-states',
					text = national['text'],
					marker = dict(
						line = dict (
							color = 'rgb(211,211,211)',
							width = 0.5
						)
					),
					colorbar = dict(
						title = "TWh", thickness = 15
					)
				) ]

layout = dict(
        title = 'Economic Potential by state',
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showlakes = False,
			showcoastlines = True,
            #lakecolor = 'rgb(135,206,250)',
        ),
    )
    
fig = dict( data=choropleth_data, layout=layout )
py.image.save_as(fig, filename='US_map.png')

url = py.plot( fig, filename='d3-cloropleth-map' )

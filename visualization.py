### module imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import plotly.plotly as py

import Economic_potential_master as epm

### Plotting function ###

pd.options.display.mpl_style = 'default'

###Histogram
"""\
plt.hist(national['LACE'],100, normed=1, facecolor='g', alpha=0.75)
#np.histogram(national['LCOE'], bins=10, range=None, normed=False, weights=None, density=None)
"""

plt.hist(epm.national['Marginal Generation Price (in 2014$/MWh)_esc'],100, normed=1, facecolor='g', alpha=0.75)

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
"""
plt.show(block=True)


### Choropleth map
#plotly_ssl_verification = False , plotly_ssl_verification
py.sign_in("pbeiter","1ygvgjoipe",plotly_ssl_verification=False)

scl = [[0.0, 'rgb(255,255,255)'],[0.2, 'rgb(0,205,0)'],[0.4, 'rgb(0,139,0)'],\
            [0.6, 'rgb(0,128,0)'],[0.8, 'rgb(0,100,0)'],[1.0, 'rgb(0,128,20)']]


state_results_TWh = epm.df_state_results['state_results']/1000000
states = epm.national['State_abbrev'].drop_duplicates().reset_index(drop=True)
states = states.sort_values(ascending=True, inplace=False, kind='quicksort')

epm.national['text'] = 'TWh' #+ '<br>' + states]

choropleth_data = [ dict(
					type='choropleth',
					colorscale = scl,
					autocolorscale = False,
					locations = states,
					z = state_results_TWh,
					locationmode = 'USA-states',
					text = epm.national['text'],
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
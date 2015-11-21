import plotly.plotly as py
import pandas as pd

#plotly_ssl_verification = False , plotly_ssl_verification
py.sign_in("pbeiter","1ygvgjoipe",plotly_ssl_verification=False)

df = pd.read_csv('state_data.csv')

for col in df.columns:
    df[col] = df[col].astype(str)

scl = [[0.0, 'rgb(0,238,0)'],[0.2, 'rgb(0,205,0)'],[0.4, 'rgb(0,139,0)'],\
            [0.6, 'rgb(0,128,0)'],[0.8, 'rgb(0,100,0)'],[1.0, 'rgb(0,128,20)']]

df['text'] = 'GW' #+ '<br>' + df['state']

data = [ dict(
        type='choropleth',
        colorscale = scl,
        autocolorscale = False,
        locations = df['code'],
        z = df['Economic potential'].astype(float),
        locationmode = 'USA-states',
        text = df['text'],
        marker = dict(
            line = dict (
                color = 'rgb(255,255,255)',
                width = 0.5
            )
        ),
        colorbar = dict(
            title = "GW", thickness = 15
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
    
fig = dict( data=data, layout=layout )
py.image.save_as(fig, filename='US_map.png')

#url = py.plot( fig, filename='d3-cloropleth-map' )
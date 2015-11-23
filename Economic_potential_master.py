### module imports
import numpy as np
import pandas as pd
import LACE_calc as LACE

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
        'Wyoming': 'WY'          
}                                

df_state_abbrev = pd.DataFrame(state_abbrev.items(), columns=['State', 'State_abbrev'])

df['Net value'] = df['LACE'] - df['LCOE']
df['Cumulative Capacity'] = df.sort_values('Net value', ascending=False)['Installed Capacity'].cumsum()
df['Economic potential (MWh)'] = np.where(df['Net value']>0, df['Annual Generation (MWh)'], 0)
df['state_results'] = df.groupby('State')['Economic potential (MWh)'].transform('sum')              
 
### Merging                                      
df = df.merge(df1, on=['re_class'], how='left')
df = df.merge(df_state_abbrev,on=['State'],how='left')
df = df.merge(LACE.LACE_calc, on=['ReEDS region'], how='left')

df_state_results = pd.concat([df['State_abbrev'], df['state_results']], axis=1).drop_duplicates().reset_index(drop=True)
df_state_results = df_state_results.sort_values('State_abbrev', ascending=True, inplace=False, kind='quicksort')

### National
national = df.sort_values('Net value', ascending=False)

print(national.describe())
national.to_csv('output.csv', replace='True')

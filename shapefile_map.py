### Credits
#Brandon Rose, http://brandonrose.org/pythonmap

### module imports
#see 'instructions/Python packages for geospatial analysis.txt' for module installation procedure

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.prepared import prep
from pysal.esda.mapclassify import Natural_Breaks as nb
from descartes import PolygonPatch
import fiona
from itertools import chain
import pysal.esda.mapclassify as mapclassify

import Economic_potential_master as epm

### IPython notebook setup
#%matplotlib inline

### Data read-in 
data = epm.df_state_results
data.head()

### Shapefile modification
#load shape file as shp 
# Source for U.S. states shapefile: NWS GIS map group (http://www.nws.noaa.gov/geodata/catalog/national/html/us_state.htm) 
shp = fiona.open('shapefiles_US_states/nws_15/s_10nv15.shp')

#access the boundaries (the 2 lat,long pairs) using shp.bounds
bds = shp.bounds

#close the shp file
shp.close()

#define a variable called extra which we will use for padding the map when we display it
extra = 0.1

#define the lower left hand boundary (longitude, latitude)
ll = (bds[0], bds[1])

#define the upper right hand boundary (longitude, latitude)
ur = (bds[2], bds[3])

#concatenate the lower left and upper right into a variable called 'coordinates'
coords = list(chain(ll, ur))

#define variables for the width and the height of the map
w, h = coords[2] - coords[0], coords[3] - coords[1]

m = Basemap(
    #set projection to 'tmerc' which is apparently less distorting when close-in
    projection='tmerc',

    #set longitude as average of lower, upper longitude bounds
    lon_0 = np.average([bds[0],bds[2]]),

    #set latitude as average of lower,upper latitude bounds
    lat_0 = np.average([bds[1],bds[3]]),

    #string describing ellipsoid (GRS80 or WGS84, for example). Not sure what this does.
    ellps = 'WGS84',
    
    #set the map boundaries. Note that we use the extra variable to provide a 10% buffer around the map
    llcrnrlon=coords[0] - extra * w,
    llcrnrlat=coords[1] - extra + 0.01 * h,
    urcrnrlon=coords[2] + extra * w,
    urcrnrlat=coords[3] + extra + 0.01 * h,

    #provide latitude of 'true scale.' Not sure what this means (check Basemap API?)
    lat_ts=0,

    #resolution of boundary database to use. Can be c (crude), l (low), i (intermediate), h (high), f (full) or None.
    resolution='i',
    
    #don't show the axis ticks automatically
    suppress_ticks=True)

m.readshapefile(
    #provide the path to the shapefile, but leave off the .shp extension
    'shapefiles_US_states/nws_15/s_10nv15',

    #name your map 
    'us_states',

    #set the default shape boundary coloring (default is black) and the zorder (layer order)
    color='none',
    zorder=2)
	
print 'm.us_states is a ' + str(type(m.us_states)) + ' object.'

print 'It contains ' + str(len(m.us_states)) + ' items.'

print 'The first list item itself contains ' + str(len(m.us_states[0])) + ' items.'

m.us_states_info[0]

### Set up a map dataframe
df_map = pd.DataFrame({

    #access the x,y coords and define a polygon for each item in m.us_states
    'poly': [Polygon(xy) for xy in m.us_states],
    #conver NAME_1 to a column called 'district'
    'State_abbrev': [district['STATE'] for district in m.us_states_info]})

#add the polygon area
df_map['area_m'] = df_map['poly'].map(lambda x: x.area/1000)

#convert meters to miles
df_map['area_miles'] = df_map['area_m'] * 0.000621371

df_map.head()

data.head()


### Merge data with map file

df_map = pd.merge(df_map, data, on='State_abbrev', how='left')

df_map.head()

### Binning

# change False to True to use Jenks binning
jenks = True

# specify variable that will be plotted
var_2_analyze = 'state_results'

if jenks == True:
    # Calculate Jenks natural breaks for each polygon
    breaks = nb(
        # set the data to use
        df_map[df_map[var_2_analyze].notnull()][var_2_analyze].values,

        # since this is an optimization function we need to give it a number of initial solutions to find. 
        # you can adjust this number if you are unsatisfied with the bin results
        initial=300,

        # k is the number of natural breaks you would like to apply. I've set it to 10, but you can change.
        k=10)

else:
    # Define my own breaks [even split each 20 percentage points] Note that the bins are the top range so >20, >40, etc
    # you can change the bins to whatever you like, though they should be based on the data you are analyzing
    # since I am going to plot data on a 0 to 100 scale, I chose these break points
    my_bins = [20,40,60,80,100]
    
    # Calculate the user defined breaks for our defined bins
    breaks = mapclassify.User_Defined(
               
            # set the data to use 
            df_map[df_map[var_2_analyze].notnull()][var_2_analyze].values, 
            
            #use my bins
            my_bins)
			
			
# check if 'bins' already exists and drop it if it does so that we can recreate it using our new break information
if 'bins' in df_map.columns:
    df_map = df_map.drop('bins',1)
    print 'Bins column already existed, so we dropped the bins column'


# the notnull method lets us match indices when joining
# b is a dataframe of the bins with the var_2_analyze index
b = pd.DataFrame({'bins': breaks.yb}, index=df_map[df_map[var_2_analyze].notnull()].index)

# join b back to df_map
df_map = df_map.join(b)

# and handle our NA's if there are any
df_map.bins.fillna(-1, inplace=True)

# check if this is a jenks or user-defined break
if jenks == True:
    
    # if jenks, use these labels
    bin_labels = ["<= %0.0f" % b for b in breaks.bins]
else: 
    
    # if user defined, use these ones
    bin_labels = ["< %0.0f" % b for b in breaks.bins]
    
print 'Here are the bin labels:'
for label in bin_labels:
    print label

	
### Plot specification 
	
# Convenience functions for working with color ramps and bars
def colorbar_index(ncolors, cmap, labels=None, **kwargs):
    """
    This is a convenience function to stop you making off-by-one errors
    Takes a standard colour ramp, and discretizes it,
    then draws a colour bar with correctly aligned labels
    """
    cmap = cmap_discretize(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable, **kwargs)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))
    if labels:
        colorbar.set_ticklabels(labels)
    return colorbar

def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    """
    if type(cmap) == str:
        cmap = get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0., 0., 0., 0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N + 1)
    cdict = {}
    for ki, key in enumerate(('red', 'green', 'blue')):
        cdict[key] = [(indices[i], colors_rgba[i - 1, ki], colors_rgba[i, ki]) for i in xrange(N + 1)]
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d" % N, cdict, 1024)
	
# initialize the plot
plt.clf()

# define the figure and set the facecolor (e.g. background) to white
fig = plt.figure(facecolor='white')

# ad a subplot called 'ax'
ax = fig.add_subplot(111, axisbg='w', frame_on=False)

# use a blue colour ramp ('Blues') - we'll be converting it to a map using cmap()
# you could also use 'Oranges' or 'Greens' 
cmap = plt.get_cmap('Blues')


# draw boundaries with grey outlines
df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4))


# set the PatchCollection with our defined 'patches'
pc = PatchCollection(df_map['patches'], match_original=True)

# normalize our bins between the min and max values within the bins
norm = Normalize(vmin=df_map['bins'].min(), vmax=df_map['bins'].max())

# impose our color map onto the patch collection
pc.set_facecolor(cmap(norm(df_map['bins'].values)))
ax.add_collection(pc)

# Add a color bar which has our bin_labels applied
cb = colorbar_index(ncolors=len(bin_labels), cmap=cmap, shrink=0.5, labels=bin_labels)
# set the font size of the labels (set to size 10 here)
cb.ax.tick_params(labelsize=10)

# Create a bit of small print
smallprint = ax.text(
    # set the x,y location of the smallprint
    1, 1,
    # add whatever text you would like to appear
    'This is a U.S. map showing ' + var_2_analyze + ' per state.',
    # set the horizontal/vertical alignment
    ha='right', va='bottom',
    # set the size and the color
    size=10,
    color='#555555',
    transform=ax.transAxes)

# Draw a map scale
m.drawmapscale(
    #set the coordinates where the scale should appear
    coords[0] + 0.08, coords[1] + 0.215,
    coords[0], coords[1],
    # what is the max value of the scale (here it's set to 25 for 25 miles)
    25.,
    barstyle='fancy', labelstyle='simple',
    fillcolor1='w', fillcolor2='#555555',
    fontcolor='#555555',
    zorder=5,
    # what units would you like to use. Defaults to km
    units='mi')

# set the layout to maximally fit the bounding area
plt.tight_layout()

# define the size of the figure
fig.set_size_inches(10,12)

# save the figure. Increase the dpi to increase the quality of the output .png. For example, dpi=1000 is super high quality

plt.savefig('US_' + var_2_analyze + '.png', dpi=100, alpha=True)

# display our plot
plt.show()


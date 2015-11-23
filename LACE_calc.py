### module imports
import numpy as np
import pandas as pd

### Data read-in 
LACE_calc = pd.read_csv("LACE_calc.csv")

LACE_calc['Marginal Generation Price (in 2014$/MWh)_esc'] = LACE_calc['Marginal Generation Price (in 2014$/MWh)']*LACE_calc['Escalation factor (EIA Reference case)']

LACE_calc.to_csv('LACE_output.csv', replace='True')
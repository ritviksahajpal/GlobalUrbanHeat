##################################################################################
#
#   Edge Search
#
#   Notebook to search for extreme heat events that overlap years.
#   Fix to resolve problem TBD.
#
#   By Cascade Tuholske, 2019-10-19
#
#   Preliminary Findings
#   - In the entire record, there are 97 events that start on Jan 1.
#   - In the entire record, there are 94 events that end of Dec 31.
#   Of these, it looks like 5 were from the same city and bridged two years
#
#   Moved to .py file from .ipynb on 2019.12.31 by Cascade Tuholske
#
#   NOTE UPDATE FILE NAME AS NEEDED
#
##################################################################################

# Depdencies
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Dir and FN
fn_in = "/home/cascade/projects/data_out_urbanheat/All_data20191231.csv"
df = pd.read_csv(fn_in)

#### 1. Find Edges ##################################################################################

# NOTE Build query to find dates X.12.31 and XX.01.01
# NOTE Events col are strings

def date_search(df, date):

    """ Searches Tmax data frame to find dates within a Tmax event with the goal of finding 12.31-01.01 overlap
    Args:
        df = tmax df
        data = date you want to find

    Returns df with event id, event dates, city id, year, and tmax temps
    """

    event_id_list = []
    event_dates_list = []
    city_id_list = []
    event_year_list = []
    tmax_list = []
    total_days_list = []

    for index, row in df.iterrows():
        if date in row['event_dates']:
            event_id = row['Event_ID']
            event_dates = row['event_dates']
            city_id = row['ID_HDC_G0']
            event_year = row['year']
            tmax = row['tmax']
            total_days = row['total_days']

            event_id_list.append(event_id)
            event_dates_list.append(event_dates)
            city_id_list.append(city_id)
            event_year_list.append(event_year)
            tmax_list.append(tmax)
            total_days_list.append(total_days)
    df_out = pd.DataFrame()
    df_out['ID_HDC_G0'] = city_id_list
    df_out['Event_ID'] = event_id_list
    df_out['tmax'] = tmax_list
    df_out['event_dates'] = event_dates_list
    df_out['year'] = event_year_list
    df_out['total_days'] = total_days_list

    return df_out

# Dec 31 Events
df_1231 = date_search(df, '12.31')
print('dec 31 done')

# Jan 1 Events
df_0101 = date_search(df, '01.01')
print('jan 1 done')

# Check len
print(len(df_0101))
print(len(df_1231))

# See how many cities overlap
print(df_1231['ID_HDC_G0'].isin(df_0101['ID_HDC_G0']).value_counts())

# Merge based on city ID to only include overlaps
merge = pd.merge(df_1231, df_0101, on = 'ID_HDC_G0', how = 'inner')
print(merge.head(10))

# Look for years the are one apart and get rows
out = []
for i, year in merge.iterrows():
        if year['year_y'] - year['year_x'] == 1:
            out.append(i)

# Get the rows with dec 31 - jan 1
overlap = merge.loc[out]
overlap

#### 2. Make new data from overlaps ##################################################################################
def string_hunt(string_list, out_list, dtype):
    """Helper function to pull tmax record strings from a list without , and turn them into ints"""
    for i in string_list: # set the strings from X list
        if len(i) > 1:
            if '[' in i:
                record = i[1:]
                if ']' in record:
                    record =  record[:-1]
                    out_list.append(dtype(record))
                else:
                    out_list.append(dtype(record))
            elif ']' in i:
                record = i[:-1]
                out_list.append(dtype(record)
            else:
                record = i
                out_list.append(dtype(record))
    return out_list

# loop by row to get temps
df_overlap = pd.DataFrame()

# Lists for df
temps_list_list = []
dates_list_list = []
duration_list = []
avg_temp_list = []
intensity_list = []
avg_intensity_list = []
tot_intensity_list = []
city_id_list = []
year_x_list = []
year_y_list = []
event_x_id_list = [] # <<<<<---- going to use the ID for the Dec date for now
event_y_id_list = [] # <<<<<---- going to use the ID for the Dec date for now
total_days_x_list = [] # total number of days added to first year
total_days_y_list = [] # total number of days subtracted first year

### Tempature
for i, row in overlap.iterrows():

    ### Temp and Days
    temps_list = [] # make list to populate

    temps_x = (row['tmax_x'].split(' ')) # split up the strings from X list
    temps_list = string_hunt(temps_x, temps_list, float)

    dur_x = len(temps_list) # duration first year

    temps_y = (row['tmax_y'].split(' ')) # split up the strings from X list
    temps_list = string_hunt(temps_y, temps_list, float)

    dur_y = len(temps_list) - dur_x # duration second year

    temps_list_list.append(temps_list)

    ## Total Days
    total_days_x = row['total_days_x'] + dur_y
    total_days_y = row['total_days_y'] - dur_y

    total_days_x_list.append(total_days_x)
    total_days_y_list.append(total_days_y)

    ### Dates
    dates_list = [] # make list to populate

    dates_x = (row['event_dates_x'].split(' ')) # split up the strings from X list
    dates_list = string_hunt(dates_x, dates_list, str)

    dates_y = (row['event_dates_y'].split(' ')) # split up the strings from X list
    dates_list = string_hunt(dates_y, dates_list, str)

    dates_list_list.append(dates_list) # append list for df

    ### Duration
    duration = len(temps_list)
    duration_list.append(duration)

    ### Intensity [x - 13 for x in a]
    intensity = [x - 40.6 for x in temps_list] # <<<<<<-------------------------- UPDATE AS NEEDED
    intensity_list.append(intensity)

    ### Avg_temp
    avg_temp = np.mean(temps_list)
    avg_temp_list.append(avg_temp)

    ### avg_intensity
    avg_intensity = np.mean(intensity)
    avg_intensity_list.append(avg_intensity)

    ### tot_intensity
    tot_intensity = np.sum(intensity)
    tot_intensity_list.append(tot_intensity)

    ### city_id & total days & year, etc
    city_id = row['ID_HDC_G0']
    city_id_list.append(city_id)

    ### Year
    year_x = row['year_x']
    year_x_list.append(year_x)

    year_y = row['year_y']
    year_y_list.append(year_y)

    ### event ID
    event_x_id = row['Event_ID_x']
    event_x_id_list.append(event_x_id)
    event_y_id = row['Event_ID_y']
    event_y_id_list.append(event_y_id)

    #avg_temp	avg_intensity	tot_intensity	event_dates	intensity

# Write it to a df
df_overlap['ID_HDC_G0'] = city_id_list
df_overlap['Event_ID_x'] = event_x_id_list
df_overlap['Event_ID_y'] = event_y_id_list
df_overlap['year_x'] = year_x_list
df_overlap['year_y'] = year_y_list
df_overlap['total_days_x'] = total_days_x_list
df_overlap['total_days_y'] = total_days_y_list
df_overlap['tmax'] = temps_list_list
df_overlap['event_dates'] = dates_list_list
df_overlap['duration'] = duration_list
df_overlap['avg_temp'] = avg_temp_list
df_overlap['intensity'] = intensity_list
df_overlap['tot_intensity'] = tot_intensity_list
df_overlap['avg_intensity'] = avg_intensity_list
print(df_overlap.head(1))

#### 3. Fix Total Days for Cities ##################################################################################
# Here we subtract the event days
# from the Jan year (y) from year y and we add those dates
# to year x so on balance the dates from the
# jan year are now just added to the earlier year

# Get List of Years and Cities for the dec-jan overlap and then find them in the dataset

# Start with year_x
years_x = list(df_out['year_x'])
id_x = list(df_out['ID_HDC_G0'])
total_days_x = list(df_out['total_days_x'])

x_list = []
for i in zip(years_x,id_x, total_days_x):
    x_list.append(i)

for x in x_list:
    print(x)

# Search df for i list and replace days
# this is super slow but it works

df_copy = df.copy()

for x in x_list:
    for i, row in df_copy.iterrows():
        if (row['year'] == x[0]) & (row['ID_HDC_G0'] == x[1]):
            print(df_copy.loc[i,'total_days'])
            df_copy.loc[i,'total_days'] = x[2]
            print(df_copy.loc[i,'total_days'])

# Start with year_y 
years_y = list(df_out['year_y'])
id_y = list(df_out['ID_HDC_G0'])
total_days_y = list(df_out['total_days_y'])

y_list = []
for i in zip(years_y, id_y, total_days_y):
    y_list.append(i)

for y in y_list:
    print(y)

# Run on y_list
for y in y_list:
    for i, row in df_copy.iterrows():
        if (row['year'] == y[0]) & (row['ID_HDC_G0'] == y[1]):
            print(df_copy.loc[i,'total_days'])
            df_copy.loc[i,'total_days'] = y[2]
            print(df_copy.loc[i,'total_days'])

#### 4. Add Meta data back ##################################################################################

# Make a copy as back up in case you over right df_copy
df_copy_extra = df_copy.copy()

# copy df_out overlap, df_out is the overlap dataframe
df_overlap_copy = df_overlap.copy()

print(df_overlap_copy.head(1))

# Get Columns to merge
cols_to_use = df.columns.difference(df_out_copy.columns) # find missing columns
cols_list = list(cols_to_use) # list
cols_list.append('ID_HDC_G0') # add IDS
df_cols = df_copy[cols_list]

# Drop duplicates
df_cols = df_cols.drop_duplicates('ID_HDC_G0', keep = 'first')
df_out_copy_merge = df_out_copy.merge(df_cols, on = 'ID_HDC_G0', how = 'inner')

# drop and rename columns
df_out_copy_merge = df_out_copy_merge.drop(columns = ['Unnamed: 0', 'Unnamed: 0.1'])
df_out_copy.rename(columns = {'year_x':'year'}, inplace = True) 
df_out_copy.rename(columns = {'total_days_x':'total_days'}, inplace = True) 

#### 5. Drop overlapped years and add in new DF ##################################################################################
print(overlap.head(1))

# Get events
jan_ids = list(overlap['Event_ID_y'])
dec_ids = list(overlap['Event_ID_x'])

# Drop Events from Dataset
print(len(df_copy))
df_events = df_copy.copy()

# Jan
for event in jan_ids:
    df_events = df_events[df_events['Event_ID'] != event]

for event in dec_ids:
    df_events = df_events[df_events['Event_ID'] != event]

print(len(df_events))

# Merge
df_events = df_events.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'])
df_events.head()

print(len(df_events))
print(len(df_out_copy_merge))

print(df_events.columns)
print(df_out_copy_merge.columns)

# Make 'x' event ids for final df
df_out_copy_merge['Event_ID'] = df_out_copy_merge['Event_ID_x']

# drop event x y event ID cols 
df_out_copy_merge = df_out_copy_merge = df_out_copy_merge.drop(columns = ['Event_ID_x','Event_ID_y'])

print(len(df_events))
print(len(df_out_copy_merge))

df_final = pd.concat([df_events, df_out_copy_merge], sort = True)

print(len(df_final))

# Save it out

FN_OUT = "/home/cascade/projects/data_out_urbanheat/All_data20191231.csv" 
df_final.to_csv(FN_OUT)

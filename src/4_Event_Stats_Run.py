##################################################################################
#
#   By Cascade Tuholske on 2019.12.31
#   Updated 2020.02.23
#
#   Modified from 4_Tmax_Stats.py in oldcode dir
#
#   NOTE: Fully rewriten on 2021.02.01 see 'oldcode' for prior version / CPT
#   
#   Find heat wave dates, duration, intensity, etc. for a given threshold
#   with either HI or WBGT data ... can be used on Tmax as well
#
#################################################################################

# Dependencies
import Event_Stats_Funcs as es
import os
from glob import glob

# Arges Needed 
DATA_IN = '/home/cascade/projects/UrbanHeat/data/interim/CHIRTS_DAILY/HI/' # output from avg temp
DATA_OUT = '/home/cascade/projects/UrbanHeat/data/interim/CHIRTS_DAILY/STATS/'
dir_path = DATA_IN 
space_dim = 'ID_HDC_G0'
time_dim = 'date'
Tthresh = 40.6 # update
#fn_out = DATA_OUT+'STATS_1DAY406.json'
data = 'HI406' # HI or WBGT and Threshold
cpu = 20 # number of cpus to use

# Step 1 - Read and stack HI or WBGT
####################################################################################################

step1 = es.read_data(dir_path, space_dim = space_dim, time_dim = time_dim)
print('Data stacked')

# Step 2 Mask data based on  threshold
####################################################################################################

step2 = es.max_days(step1, Tthresh)
print('Tmax masked')

# Step 3 Split up step 2 and write the files out
####################################################################################################
dir_nm = DATA_OUT+data+'_tmp'
print(dir_nm)
os.mkdir(dir_nm)

cpu_ = cpu+2 # add two
n = int(len(step1)/ cpu_)  #chunk row size
list_df = [step2 [i:i+n] for i in range(0,step2.shape[0],n)]
print(len(list_df))

# write them out
for i, df in enumerate(list_df):
    df.to_json(DATA_OUT+data+'_temp/'+data+'_'+str(i)+'.json', orient = 'split')

# # Step 4 Run stats in parallel 
# ####################################################################################################

# fns_list = glob(DATA_OUT+data+'_tmp'+'/*.json')
# es.parallel_loop(es.max_stats_run, fns_list, cpu_num = 20)






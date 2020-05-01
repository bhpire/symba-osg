seednoise         = 0 #0 to give each submission a different number
realizations      = 3 #number of different realizations for noise and corruptions for each model
keep_redundant    = False #also copy back redundant files such as the MS back to CyVerse
frameduration     = '9999999999999999' #duration of a single model frame in s; TODO: read this from the library itself
mod_rotation      = 288 #rotate models by this amount [deg]
mod_scale         = 1 #scale models by this factor
reconstruct_image = True #create a simple .fits image reconstruction
proclvl           = 'fringefit' #thermal or fringefit
src               = 'M87' #M87 or SGRA
time_avg          = '10s' #time cadence of exported data, must be given in [s]
N_channels        = 64 #number of spectral channels
avg_chan          = True #used just for filepaths right now; TODO: add option in master_input.txt to not do channel avg
tracks            = ['e17a10', 'e17b06', 'e17d05', 'e17e11'] #Can obs M87 on a10,b06,d05,e11 and SGRA also on c07
match_coverage    = True #strip uv-coverage to the one from a real observation
band              = 'lo' #lo or hi (used to match uv-coverage)
storage_filepath0 = '/iplant/home/shared/eht' #shared top-level dir for simulations and synthetic data
sdir              = 'SynthData' #top-level dir for synthetic data in storage_filepath0
mdir              = 'BkupSimulationLibrary/M87/H5S/suggested/2020.01.06' #top-level dir for simulations in storage_filepath0
smodel_kywrds     = ['a+0.5', 'Rhigh_1/'] #if input_models=[], all filenames with these keywords in storage_filepath0/+mdir are used as input models
mod_num_select    = [100, 300, 500, 700, 900] #set to [] to load all models (time-dependent src) or [a,b,c,...] to load models#a,#b#,#c,... (start counting them at 0) for separate synthetic datasets
rand_mod_num_sel  = [5, 1000] #if not set to False, give [x,y] to overwrite mod_num_select to x numbers drawn out of y
input_models      = []
#input_models = ['/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1156_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1212_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1344_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1686_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#               ]

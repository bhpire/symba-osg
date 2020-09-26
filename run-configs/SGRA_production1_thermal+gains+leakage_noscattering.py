seednoise         = 144000 #seed for all random realizations of the first synthetic dataset, for each run on an OSG node, it is incremented by 1
realizations      = 3 #number of different realizations for noise and corruptions for each model
keep_redundant    = False #also copy back redundant files such as the MS back to CyVerse
frameduration     = '100' #duration of a single model frame in s; TODO: read this from the library itself
mod_rotation      = [0,60,120,180] #rotate models by this amount [deg], can be a list
mod_scale         = 1 #scale models by this factor, can be a list
reconstruct_image = True #create a simple .fits image reconstruction
proclvl           = 'thermal+gains+leakage_noscattering' #thermal[+gains][+leakage] or fringefit; can also add _noscattering for SgrA*
src               = 'SGRA' #M87 or SGRA
time_avg          = '10s' #time cadence of exported data, must be given in [s]
N_channels        = 64 #number of spectral channels
avg_chan          = True #used just for filepaths right now; TODO: add option in master_input.txt to not do channel avg
tracks            = ['e17c07'] #Can obs M87 on a10,b06,d05,e11 and SGRA also on c07
match_coverage    = True #strip uv-coverage to the one from a real observation
band              = ['lo'] #lo or hi (used to match uv-coverage)
storage_filepath0 = '/iplant/home/shared/eht' #shared top-level dir for simulations and synthetic data
sdir              = 'SynthData' #top-level dir for synthetic data in storage_filepath0
mdir              = 'BkupSimulationLibrary/SgrA/H5S/suggested/2020.02.02' #top-level dir for simulations in storage_filepath0
smodel_kywrds     = ['i_10_PA_0/'] #if input_models=[], all filenames with these keywords in storage_filepath0/+mdir are used as input models
mod_num_select    = [] #A random starting model will be used. The frame number will be written in the inp file that is uploaded back to CyVerse
rand_mod_num_sel  = 0 #if >0, overwrite mod_num_select to draw this many random model files for each time-dependent model
input_models      = []
#input_models = ['/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1156_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1212_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1344_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#                '/iplant/home/shared/eht/BkupSimulationLibrary/M87/H5S/suggested/2020.01.06/Ma+0.5/M_6.2e9/i_163_PA_0/Rhigh_1/f_230/image_Ma+0.5_1686_163_0_230.e9_6.2e9_5.61134e+24_1_320_320.h5',
#               ]

seednoise         = 1000000 #seed for all random realizations of the first synthetic dataset, for each run on an OSG node, it is incremented by 1
realizations      = 3 #number of different realizations for noise and corruptions for each model
keep_redundant    = False #also copy back redundant files such as the MS back to CyVerse
frameduration     = '9999999999999999' #duration of a single model frame in s; TODO: read this from the library itself
mod_rotation      = [0,30,60,90,120,150,180] #rotate models by this amount [deg], can be a list
mod_rot_permod    = [ #Overwrite mod_rotation with a custom rotation angles that have a 1-to-1 correspondence with input_models. Set to False to disable.
123,
0,
88,
]
mod_scale         = 1 #scale models by this factor, can be a list
reconstruct_image = True #create a simple .fits image reconstruction
proclvl           = 'thermal+samegains+leakage' #thermal or fringefit
src               = 'SGRA' #M87 or SGRA
time_avg          = '10s' #time cadence of exported data, must be given in [s]
N_channels        = 64 #number of spectral channels
avg_chan          = True #used just for filepaths right now; TODO: add option in master_input.txt to not do channel avg
tracks            = ['e17c07'] #Can obs M87 on a10,b06,d05,e11 and SGRA also on c07
match_coverage    = True #strip uv-coverage to the one from a real observation
band              = ['lo'] #lo or hi (used to match uv-coverage)
storage_filepath0 = '/iplant/home/shared/eht' #shared top-level dir for simulations and synthetic data
sdir              = 'SynthData' #top-level dir for synthetic data in storage_filepath0
mdir              = 'BkupSimulationLibrary/bh_bd4_bkup/Ricarte_SgrA/2.3e11' #top-level dir for simulations in storage_filepath0
custom_outputdir  = [ #List having a 1-to-1 correspondence with input_models. Set to False to disable.
'/iplant/home/shared/eht/SynthData/e17c07_lo_SGRA-blind/4jh34u923hgh3',
'/iplant/home/shared/eht/SynthData/e17c07_lo_SGRA-blind/jh4935htgn0gt',
'/iplant/home/shared/eht/SynthData/e17c07_lo_SGRA-blind/8u2rhgwhgtw90',
]
blindupload       = True #upload only the uvf file
smodel_kywrds     = [] #if input_models=[], all filenames with these keywords in storage_filepath0/+mdir are used as input models
mod_num_select    = [] #A random starting model will be used. The frame number will be written in the inp file that is uploaded back to CyVerse
rand_mod_num_sel  = 0 #if >0, overwrite mod_num_select to draw this many random model files for each time-dependent model
custommodrange    = False  # Can give a list to overwrite the random section of [startnum,endnum] of time-dependent input_models. Set to False to disable.
input_models      = ['/iplant/home/shared/eht/BkupSimulationLibrary/bh_bd4_bkup/Ricarte_SgrA/2.3e11/Ma+0.5/M_4.140e+06/i_10_PA_0/betacrit_0.5_1.0/BkupSimulationLibrary_bh_bd4_bkup_Ricarte_SgrA_2.3e11_Ma+0.5_M_4.140e+06_i_10_PA_0_betacrit_0.5_1.0_f_230.tar.gz',
 '/iplant/home/shared/eht/BkupSimulationLibrary/bh_bd4_bkup/Ricarte_SgrA/2.3e11/Ma+0.5/M_4.140e+06/i_50_PA_0/betacrit_0.5_1.0/BkupSimulationLibrary_bh_bd4_bkup_Ricarte_SgrA_2.3e11_Ma+0.5_M_4.140e+06_i_50_PA_0_betacrit_0.5_1.0_f_230.tar.gz',
 '/iplant/home/shared/eht/BkupSimulationLibrary/bh_bd4_bkup/Ricarte_SgrA/2.3e11/Sa0/M_4.140e+06/i_90_PA_0/betacrit_0.5_1.0/BkupSimulationLibrary_bh_bd4_bkup_Ricarte_SgrA_2.3e11_Sa0_M_4.140e+06_i_90_PA_0_betacrit_0.5_1.0_f_230.tar.gz']

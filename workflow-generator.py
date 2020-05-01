#!/usr/bin/env python3


#TODO for polarization:
# - add option to include Faraday rotation + option to not avg the channels (<avg_chan>)

#TODO for SgrA*:
# - add scattering to input models
# - read <frameduration> from input model files
# - use updated ER6 DPFUs/aperture-efficiencies/SEFDs for LMT and SMA (differ on each day)
# - implement time-dependent netcal

#TODO for 2018+:
# - add vexfiles, antenna tables, and coverage uvf files from the observational data

import configparser
import os
import re
import sys
import importlib
from pprint import pprint
from webdav3.client import Client

from Pegasus.DAX3 import *

configfile = sys.argv[1]
sys.path.append(os.path.dirname(configfile))
configinp = importlib.import_module(os.path.basename(configfile).replace('.py', ''))

def dir_search(client, base_path, KeyWords=['Ma+0.5', 'Rhigh_1/'], mod_num_select=[], rand_mod_num_sel=False, seed=0):
    """
    Script from Dimitrios.
    Default: Mad[M] models with spin[a] of +0.5 and Rhigh=1 (w/o the slash for Rhigh you would also get Rhigh=10,160,...[1*]).
    """

    paths = []

    print(' ... checking ' + base_path)
    try:
        entries = client.list('/dav' + base_path)
    except Exception as e:
        sys.exit(1)

    # first entry is just the dir name
    entries.pop(0)

    if len(entries) == 0:
        return []

    # I'm not sure this works correctly with the fits images
    #if re.search('\\.fits$', entries[0]):
    #    # we are in an entries dir
    #    if all(ext in base_path for ext in KeyWords):
    #        if rand_mod_num_sel:
    #            these_mods = []
    #            for _ in range(rand_mod_num_sel[0]):
    #                these_mods.append(random.uniform(0, rand_mod_num_sel[1]))
    #        else:
    #            these_mods = mod_num_select
    #        if these_mods:
    #            for mod_num in these_mods:
    #                try:
    #                    paths.append(base_path+'/'+entries[mod_num])
    #                except IndexError:
    #                    pass
    #        else:
    #            for entry in entries:
    #                paths.append(base_path+'/'+entry)
    #
    #    return paths

    # if it is a fits image, add it to the path, otherwise assume it is a subdir
    for entry in entries:
        path = base_path + '/' + entry
        if re.search('\\.fits$', entry):
            paths.append(path)
        else:
            # assume it is a directory
            paths += dir_search(client, path, KeyWords=KeyWords, mod_num_select=mod_num_select, rand_mod_num_sel=rand_mod_num_sel, seed=seed)

    return paths




base_dir = os.getcwd()

# also load the Pegasus credentials - used to get Cyverse credentials
p_creds = configparser.ConfigParser()
try:
    p_creds.read(os.environ['HOME'] + '/.pegasus/credentials.conf')
except Exception as err:
    logger.critical('Unable to load credentials: ' + str(err))
    os.exit(1)


input_models = configinp.input_models
if len(input_models) == 0:
    options = {
            'webdav_hostname': 'https://data.cyverse.org',
            'webdav_login':    p_creds.get('data.cyverse.org', 'username'),
            'webdav_password': p_creds.get('data.cyverse.org', 'password')
    }
    client = Client(options)
    input_models = dir_search(client, '/iplant/home/shared/eht/BkupSimulationLibrary/GRMHD/INSANE/a+0.94/images/M=6.2x10^9')
    #TODO: use the dir search below
    #input_models = irods_dir_search_dpsaltis(configinp.storage_filepath0+'/'+configinp.mdir, configinp.smodel_kywrds, configinp.mod_num_select, configinp.rand_mod_num_sel, configinp.seednoise)
pprint(input_models)

N_queue = len(input_models) * len(configinp.tracks) * configinp.realizations
if N_queue == 0:
    sys.exit('\nGot an empty queue. Exiting.')
#gen_inp.alter_line('symba_job_submit', 'queue', 'queue = {0}'.format(str(N_queue)))

#if not os.path.exists(inpd):
#    os.makedirs(inpd)

cmd_args_inpprep0 = 'singularity exec /cvmfs/singularity.opensciencegrid.org/mjanssen2308/symba:latest python /usr/local/src/symba/scripts/tableIO.py write '

odir0 = configinp.storage_filepath0 + '/' + configinp.sdir
if configinp.avg_chan:
    freq_res = '1'
else:
    freq_res = str(configinp.N_channels)
odir__1 = 'Nch{0}_r{1}_s{2}_{3}_rz'.format(freq_res, str(configinp.mod_rotation), str(configinp.mod_scale), str(configinp.proclvl))
reals   = range(configinp.realizations)

# Create a abstract Pegasus dag
dax = ADAG('pire-symba')

# Add executables to the DAX-level replica catalog
cache_wait = Executable(name='cache-wait', installed=False)
cache_wait.addPFN(PFN('file://' + base_dir + '/job-scripts/cache-wait', 'local'))
dax.addExecutable(cache_wait)

run = Executable(name='run', installed=False)
run.addPFN(PFN('file://' + base_dir + '/job-scripts/run', 'local'))
dax.addExecutable(run)

upload = Executable(name='upload', installed=False)
upload.addPFN(PFN('file://' + base_dir + '/job-scripts/upload', 'local'))
dax.addExecutable(upload)

# wait a litte bit before starting the compue jobs - this will
# let the Cyverse Webdav cache settle down
cache_wait_job = Job(cache_wait)
dax.addJob(cache_wait_job)

counter      = 0
added_models = []
added_uvfs   = []
for inmod in input_models:

    in_file = File(os.path.basename(inmod))
    if in_file not in added_models:
        in_file.addPFN(PFN('webdavs://data.cyverse.org/dav{0}'.format(inmod), 'cyverse'))
        dax.addFile(in_file)
        added_models.append(in_file)

    cmd_args_inpprep = cmd_args_inpprep0
    cmd_args_inpprep+= '-i {0} '.format(inmod)
    cmd_args_inpprep+= '-d {0} '.format(configinp.frameduration)
    cmd_args_inpprep+= '-j {0} '.format(str(configinp.mod_rotation))
    cmd_args_inpprep+= '-q {0} '.format(str(configinp.mod_scale))
    cmd_args_inpprep+= '-r {0} '.format(str(configinp.reconstruct_image))
    cmd_args_inpprep+= '-e 3 '
    cmd_args_inpprep+= '-c 2 '
    cmd_args_inpprep+= '-o True '
    cmd_args_inpprep+= '-p 0.85457 '
    cmd_args_inpprep+= '-k {0} '.format(str(configinp.keep_redundant))
    cmd_args_inpprep+= '-s {0} '.format(configinp.src)
    cmd_args_inpprep+= '-l {0} '.format(configinp.proclvl)
    cmd_args_inpprep+= '-t {0} '.format(configinp.time_avg)
    cmd_args_inpprep+= '-b {0} '.format(str(configinp.N_channels))
    if configinp.src != 'SGRA':
        cmd_args_inpprep+= '-w True '
    else:
        cmd_args_inpprep+= '-w False '
    for track in configinp.tracks:
        if track.startswith('e17'):
            #TODO: Add cases for EHT2018+
            vexf   = '/usr/local/src/symba/symba_input/vex_examples/EHT2017/{0}.vex'.format(track)
            ants   = '/usr/local/src/symba/symba_input/VLBIarrays/eht.antennas'
            ants_d = '/usr/local/src/symba/symba_input/VLBIarrays/distributions/eht17.d'
            cmd_args_inpprep+= '-x {0} '.format(vexf)
            cmd_args_inpprep+= '-a {0} '.format(ants)
            cmd_args_inpprep+= '-g {0} '.format(ants_d)
            if configinp.match_coverage:
                uvf      = '{0}{1}_{2}_coverage.uvf'.format(track, configinp.band, configinp.src)
                uvf_full = '{0}/2017_coverage/{1}'.format(odir0, uvf)
                cmd_args_inpprep+= '-v {0} '.format(uvf)
                realdata = File(uvf)
                if realdata not in added_uvfs:
                    realdata.addPFN(PFN('webdavs://data.cyverse.org/dav/{0}'.format(uvf_full), 'cyverse'))
                    dax.addFile(realdata)
                    added_uvfs.append(realdata)
            else:
                cmd_args_inpprep+= '-v False '
        for _ in reals:
            if configinp.seednoise:
                this_seed = configinp.seednoise
            else:
                this_seed = counter

            # only run a few jobs for now
            #if counter >= 5:
            #    break

            upload_output = odir0 + '/' + track + configinp.band + '_' + configinp.src + '/'
            upload_output+= inmod.strip(configinp.storage_filepath0) + '/'
            upload_output+= odir__1 + str(this_seed)
            cmd_args_inpprep+= '-u {0} '.format(upload_output)
            cmd_args_inpprep+= '-n {0} '.format(str(this_seed))
            cmd_args_inpprep+= '-f inputfiles/inp.{0} '.format(str(counter))
            print(cmd_args_inpprep)
            os.system(cmd_args_inpprep)

            # Add input file to the DAX-level replica catalog
            inputtxt = File('inp.{0}'.format(str(counter)))
            inputtxt.addPFN(PFN('file://{0}/inputfiles/inp.{1}'.format(base_dir, str(counter)), 'local'))
            dax.addFile(inputtxt)

            # Add symba job
            run_job = Job(run, id='{0:06d}'.format(counter))
            log_file = File('{0:06d}-symba-log.txt'.format(counter))
            tar_file = File('{0:06d}.tar.gz'.format(counter))
            run_job.addArguments('{0:06d}'.format(counter), in_file)
            run_job.uses(inputtxt, link=Link.INPUT)
            run_job.uses(in_file, link=Link.INPUT)
            run_job.uses(realdata, link=Link.INPUT)
            run_job.uses(log_file, link=Link.OUTPUT, transfer=False)
            run_job.uses(tar_file, link=Link.OUTPUT, transfer=False)
            dax.addJob(run_job)
            dax.depends(parent=cache_wait_job, child=run_job)

            # Add upload job
            upload_job = Job(upload, id='upload-{0:06d}'.format(counter))
            upload_job.addArguments(tar_file)
            upload_job.uses(inputtxt, link=Link.INPUT)
            upload_job.uses(tar_file, link=Link.INPUT)
            # custom profile so we can throttle
            upload_job.addProfile(Profile("dagman", "CATEGORY", "upload"))
            dax.addJob(upload_job)
            dax.depends(parent=run_job, child=upload_job)

            counter += 1

# Write the DAX to stdout
f = open('generated/dax.xml', 'w')
dax.writeXML(f)
f.close()

# also update the sites.xml, with env var susbsitution
os.environ['CYVERSE_USERNAME'] = p_creds.get('data.cyverse.org', 'username')
os.system('envsubst < sites.xml.template > generated/sites.xml')

#!/usr/bin/env python3

#TODO for polarization:
# - add option to include Faraday rotation + option to not avg the channels (<avg_chan>)

#TODO for SgrA*:
# - read <frameduration> from input model files (unless we have a set of simulations with uniform timestamps)
# - use updated ER6 DPFUs/aperture-efficiencies/SEFDs for LMT and SMA (differ on each day)
# - update uv-coverage files using ER6 fringe-fitted data

#TODO for 2018+:
# - add vexfiles, antenna tables, and coverage uvf files from the observational data

import configparser
import os
import re
import sys
import random
import importlib
from pprint import pprint
from webdav3.client import Client

from Pegasus.DAX3 import *

configfile = sys.argv[1]
sys.path.append(os.path.dirname(configfile))
configinp = importlib.import_module(os.path.basename(configfile).replace('.py', ''))


SINGULARITY_IMAGE = '/cvmfs/singularity.opensciencegrid.org/mjanssen2308/symba:latest'


def irods_path_to_tar(path0, pathname):
    global SINGULARITY_IMAGE
    this_pathname = pathname.rstrip('/')
    all_folders   = this_pathname.split('/')
    p_to_folder   = '/'.join(all_folders[:-1])
    this_basename = this_pathname.lstrip(path0)
    this_basename = this_basename.lstrip('/')
    this_basename = this_basename.rstrip('/')
    this_basename = this_basename.replace('/','_')
    targzfile     = p_to_folder + '/' + this_basename + '.tar.gz'
    os.system('singularity exec {0} ibun -fcDg {1} {2}'.format(SINGULARITY_IMAGE, targzfile, pathname))
    return targzfile


def dir_search(wclient, base_path, KeyWords=[]):
    """
    Script from Dimitrios.
    Default: Mad[M] models with spin[a] of +0.5 and Rhigh=1 (w/o the slash for Rhigh you would also get Rhigh=10,160,...[1*]).
    """

    paths = []

    print(' ... checking ' + base_path)
    try:
        entries = wclient.list('/dav' + base_path)
    except Exception as e:
        sys.exit(1)

    # first entry is just the dir name
    entries.pop(0)

    if len(entries) == 0:
        return []

    # if it is a fits or h5 image, add it to the path, otherwise assume it is a subdir
    for entry in entries:
        path = base_path + '/' + entry
        if re.search('\\.fits$', entry) or re.search('\\.h5$', entry):
            if all(ext in path for ext in KeyWords):
                paths.append(path)
            else:
                # dead end assuming that the model files are always only at the end of filepaths
                continue
        else:
            # assume it is a directory
            paths += dir_search(wclient, path, KeyWords=KeyWords)

    return paths

def collect_input_models(wclient, base_path0, base_path1, KeyWords=['Ma+0.5', 'Rhigh_1/'], mod_num_select=[], rand_mod_num_sel=0,
                         seed=0):
    """
    Select and group models obtained from dir_search() according to mod_num_select, rand_mod_num_sel, and seed.
    """
    base_path            = base_path0+'/'+base_path1
    model_homes          = {}
    all_potential_models = dir_search(wclient, base_path, KeyWords)
    for path in all_potential_models:
        this_dirname  = os.path.dirname(path)
        this_filename = os.path.basename(path)
        if this_dirname in model_homes:
            model_homes[this_dirname].append(this_filename)
        else:
            model_homes[this_dirname] = [this_filename]
    if not model_homes:
        raise ValueError('No models selected! Check mdir and smodel_kywrds in the config file.')
    selected_models = []
    if not mod_num_select and not rand_mod_num_sel:
        # time-dependent model for which we pass an entire tarball with models to an OSG node
        for modelpath in list(model_homes.keys()):
            selected_models.append(irods_path_to_tar(base_path0, modelpath))
        return selected_models
    random.seed(seed)
    # return a selection of individual models
    for dirname in model_homes:
        if rand_mod_num_sel > 0:
            N_select  = min(len(model_homes[dirname]), rand_mod_num_sel)
            selection = random.sample(model_homes[dirname], N_select)
            for model in selection:
                selected_models.append(dirname+'/'+model)
        else:
            for modelnum in mod_num_select:
                selected_models.append(dirname+'/'+model_homes[dirname][modelnum])
    return selected_models


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
    input_models = collect_input_models(client, configinp.storage_filepath0, configinp.mdir, configinp.smodel_kywrds,
                                        configinp.mod_num_select, configinp.rand_mod_num_sel, configinp.seednoise
                                       )
pprint(input_models)

N_queue = len(input_models) * len(configinp.tracks) * configinp.realizations
if N_queue == 0:
    sys.exit('\nGot an empty queue. Exiting.')
#gen_inp.alter_line('symba_job_submit', 'queue', 'queue = {0}'.format(str(N_queue)))

#if not os.path.exists(inpd):
#    os.makedirs(inpd)

cmd_args_inpprep0 = 'singularity exec {0} python /usr/local/src/symba/scripts/tableIO.py write '.format(SINGULARITY_IMAGE)

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

counter      = configinp.seednoise
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
    cmd_args_inpprep+= '-w True '
    cmd_args_inpprep+= '-k {0} '.format(str(configinp.keep_redundant))
    cmd_args_inpprep+= '-s {0} '.format(configinp.src)
    cmd_args_inpprep+= '-l {0} '.format(configinp.proclvl)
    cmd_args_inpprep+= '-t {0} '.format(configinp.time_avg)
    cmd_args_inpprep+= '-b {0} '.format(str(configinp.N_channels))
    cmd_args_inpprep+= '-z /usr/local/src/symba/symba_input/scattering/Psaltis_Johnson_2018.txt.default '
    cmd_args_inpprep+= '-y /usr/local/src/symba/symba_input/scattering/distributions/Psaltis_Johnson_2018.txt '
    for track in configinp.tracks:
        if track.startswith('e17'):
            #TODO: Add cases for EHT2018+
            vexf   = '/usr/local/src/symba/symba_input/vex_examples/EHT2017/{0}.vex'.format(track)
            ants   = '/usr/local/src/symba/symba_input/VLBIarrays/eht.antennas'
            ants_d = '/usr/local/src/symba/symba_input/VLBIarrays/distributions/eht17.d'
            cmd_args_inpprep+= '-x {0} '.format(vexf)
            cmd_args_inpprep+= '-a {0} '.format(ants)
            cmd_args_inpprep+= '-g {0} '.format(ants_d)
            if configinp.src == 'SGRA' and track == 'e17a10':
                cmd_args_inpprep+= '--refants LM,SM,AP,AZ '
            elif configinp.src == 'SGRA' and track == 'e17b06':
                cmd_args_inpprep+= '--refants AA,LM,SM,AZ '
            elif configinp.src == 'SGRA' and track == 'e17d05':
                cmd_args_inpprep+= '--refants LM,SM,AP,AZ '
            elif configinp.src == 'SGRA' and track == 'e17e11':
                cmd_args_inpprep+= '--refants AA,LM,SM,AZ '
            else:
                cmd_args_inpprep+= '--refants AA,LM,SM,PV '
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

            upload_output = odir0 + '/' + track + '_' + configinp.band + '_' + configinp.src + '/'
            upload_output+= inmod.strip(configinp.storage_filepath0).rstrip('.tar.gz') + '/'
            upload_output+= odir__1 + str(counter)
            cmd_args_inpprep+= '-u {0} '.format(upload_output)
            cmd_args_inpprep+= '-n {0} '.format(str(counter))
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

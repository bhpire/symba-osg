#!/usr/bin/env python3

#TODO for polarization:
# - add option to include Faraday rotation + option to not avg the channels (<avg_chan>)

#TODO for SgrA*:
# - read <frameduration> from input model files (unless we have a set of simulations with uniform timestamps)

#TODO for 2018+:
# - add vexfiles, antenna tables, and coverage uvf files from the observational data

import configparser
import os
import re
import sys
import time
import random
import itertools
import importlib
from pprint import pprint
from webdav3.client import Client

from Pegasus.DAX3 import *

configfile = sys.argv[1]
sys.path.append(os.path.dirname(configfile))
configinp = importlib.import_module(os.path.basename(configfile).replace('.py', ''))


SINGULARITY_IMAGE = '/cvmfs/singularity.opensciencegrid.org/mjanssen2308/symba:latest'
PATH_TO_SYMBA     = '/home/mjanssen/symba'
rebun_tarballs    = False


def irods_path_to_tar(wclient, path0, pathname, modelrange={}):
    global SINGULARITY_IMAGE
    global rebun_tarballs
    this_pathname = pathname.rstrip('/')
    all_folders   = this_pathname.split('/')
    p_to_folder   = '/'.join(all_folders[:-1])
    this_basename = this_pathname.lstrip(path0)
    this_basename = this_basename.lstrip('/')
    this_basename = this_basename.rstrip('/')
    this_basename = this_basename.replace('/','_')
    if modelrange:
        mlist     = ' '.join([pathname+'/'+mi for mi in modelrange['m']])
        tmpdir    = pathname+'/tmp/'
        targzfile = p_to_folder + '/' + this_basename + '_models{0}to{1}.tar.gz'.format(modelrange['b'], modelrange['e'])
        os.system('singularity exec {0} imkdir -p {1}'.format(SINGULARITY_IMAGE, tmpdir))
        os.system('singularity exec {0} imv {1} {2}'.format(SINGULARITY_IMAGE, mlist, tmpdir))
        os.system('singularity exec {0} ibun -fcDg {1} {2}'.format(SINGULARITY_IMAGE, targzfile, tmpdir))
        mtmplist = ' '.join([tmpdir+'/'+mi for mi in modelrange['m']])
        os.system('singularity exec {0} imv {1} {2}/'.format(SINGULARITY_IMAGE, mtmplist, pathname))
        entries = wclient.list('/dav' + tmpdir)
        entries.pop(0)
        if entries:
            raise OSError('Temporary dir {0} not empty.'.format(tmpdir))
        os.system('singularity exec {0} irm -r {1}'.format(SINGULARITY_IMAGE, tmpdir))
        return targzfile
    else:
        targzfile = p_to_folder + '/' + this_basename + '.tar.gz'
        if not rebun_tarballs:
            while True:
                try:
                    tfile_exists = client.check('/dav/' + targzfile)
                    break
                except:
                    print ('  ... connection pending ...')
                    time.sleep(60)
            if tfile_exists:
                return targzfile
        os.system('singularity exec {0} ibun -fcDg {1} {2}'.format(SINGULARITY_IMAGE, targzfile, pathname))
        return targzfile


def dir_search(wclient, base_path, KeyWords=[]):
    """
    Script from Dimitrios.
    Default: Mad[M] models with spin[a] of +0.5 and Rhigh=1 (w/o the slash for Rhigh you would also get Rhigh=10,160,...[1*]).
    """

    paths = []

    print(' ... checking ' + base_path)
    while True:
        try:
            entries = wclient.list('/dav' + base_path)
            break
        except:
            print ('  ... connection pending ...')
            time.sleep(60)

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
    Nmod_str        = str(len(model_homes.keys()))
    #imv is too slow...
    #if len(mod_num_select)==1 and isinstance(mod_num_select[0], float):
    #    model_selector = str(mod_num_select[0]).split('.')
    #    mgroup_size    = int(model_selector[0])
    #    mgroup_overlap = mgroup_size / int(model_selector[1])
    #    for i, modelpath in enumerate(list(model_homes.keys())):
    #        ma = model_homes[modelpath]
    #        mn = len(ma)
    #        m0 = 0
    #        m1 = mgroup_size
    #        while True:
    #            these_models = ma[m0:m1]
    #            mrange       = {}
    #            mrange['b']  = str(m0)
    #            mrange['e']  = str(m1)
    #            mrange['m']  = these_models
    #            selected_models.append(irods_path_to_tar(wclient, base_path0, modelpath, mrange))
    #            if m1 > mn:
    #                break
    #            m0 += mgroup_overlap
    #            m1 += mgroup_overlap
    #        print('Prepared tarball for model {0}/{1}'.format(str(i+1), Nmod_str))
    #    return selected_models
    if not mod_num_select and not rand_mod_num_sel:
        # time-dependent model for which we pass an entire tarball with models to an OSG node
        for i, modelpath in enumerate(list(model_homes.keys())):
            selected_models.append(irods_path_to_tar(wclient, base_path0, modelpath))
            print('Prepared tarball for model {0}/{1}'.format(str(i+1), Nmod_str))
        return selected_models
    random.seed(seed)
    # return a selection of individual models
    for dirname in list(model_homes.keys()):
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

options = {'webdav_hostname': 'https://data.cyverse.org',
           'webdav_login':    p_creds.get('data.cyverse.org', 'username'),
           'webdav_password': p_creds.get('data.cyverse.org', 'password')
          }
client = Client(options)
input_models = configinp.input_models
if len(input_models) == 0:
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

#cmd_args_inpprep0 = 'singularity exec {0} python /usr/local/src/symba/scripts/tableIO.py write '.format(SINGULARITY_IMAGE)
cmd_args_inpprep0 = 'python {0}/scripts/tableIO.py write '.format(PATH_TO_SYMBA)

odir0 = configinp.storage_filepath0 + '/' + configinp.sdir
if configinp.avg_chan:
    freq_res = '1'
else:
    freq_res = str(configinp.N_channels)
inp_mod_rotation = configinp.mod_rotation
inp_mod_scale    = configinp.mod_scale
if not isinstance(inp_mod_rotation, list):
    inp_mod_rotation = [inp_mod_rotation]
if not isinstance(inp_mod_scale, list):
    inp_mod_scale = [inp_mod_scale]
reals = range(configinp.realizations)

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

# wait a little bit before starting the compute jobs - this will
# let the Cyverse Webdav cache settle down
cache_wait_job = Job(cache_wait)
dax.addJob(cache_wait_job)

counter      = int(configinp.seednoise)
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
    cmd_args_inpprep+= '-r {0} '.format(str(configinp.reconstruct_image))
    cmd_args_inpprep+= '-e 3 '
    cmd_args_inpprep+= '-c 2 '
    cmd_args_inpprep+= '-o True '
    cmd_args_inpprep+= '-p 0.85457 '
    cmd_args_inpprep+= '-w True '
    cmd_args_inpprep+= '--fringecut 3.0 '
    cmd_args_inpprep+= '-k {0} '.format(str(configinp.keep_redundant))
    cmd_args_inpprep+= '-s {0} '.format(configinp.src)
    cmd_args_inpprep+= '-l {0} '.format(configinp.proclvl)
    cmd_args_inpprep+= '-t {0} '.format(configinp.time_avg)
    cmd_args_inpprep+= '-b {0} '.format(str(configinp.N_channels))
    cmd_args_inpprep+= '-z /usr/local/src/symba/symba_input/scattering/Psaltis_Johnson_2018.txt.default '
    cmd_args_inpprep+= '-y /usr/local/src/symba/symba_input/scattering/distributions/Psaltis_Johnson_2018.txt '
    for iterparams in itertools.product(configinp.tracks, configinp.band, inp_mod_scale, inp_mod_rotation):
        track            = iterparams[0]
        band             = iterparams[1]
        mscale           = iterparams[2]
        mrot             = iterparams[3]
        cmd_args_inpprep+= '-q {0} '.format(str(mscale))
        cmd_args_inpprep+= '-j {0} '.format(str(mrot))
        if track.startswith('e17'):
            #TODO: Add cases for EHT2018+
            vexf   = '/usr/local/src/symba/symba_input/vex_examples/EHT2017/{0}.vex'.format(track)
            ants   = '/usr/local/src/symba/symba_input/VLBIarrays/e17_er6/{0}_{1}.antennas'.format(configinp.src, track)
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
                uvf      = '{0}{1}_{2}_coverage.uvf'.format(track, band, configinp.src)
                uvf_full = '{0}/2017_coverage/{1}'.format(odir0, uvf)
                cmd_args_inpprep+= '-v {0} '.format(uvf)
                realdata = File(uvf)
                if realdata not in added_uvfs:
                    realdata.addPFN(PFN('webdavs://data.cyverse.org/dav/{0}'.format(uvf_full), 'cyverse'))
                    dax.addFile(realdata)
                    added_uvfs.append(realdata)
            else:
                cmd_args_inpprep+= '-v False '
        odir__1 = 'Nch{0}_r{1}_s{2}_{3}_rz'.format(freq_res, str(mrot), str(mscale), str(configinp.proclvl))
        for _ in reals:

            realization_fmt = '{0:012d}'.format(counter)

            upload_output = odir0 + '/' + track + '_' + band + '_' + configinp.src + '/'
            upload_output+= inmod.strip(configinp.storage_filepath0).rstrip('.tar.gz') + '/'
            upload_output+= odir__1 + realization_fmt
            cmd_args_inpprep+= '-u {0} '.format(upload_output)
            cmd_args_inpprep+= '-n {0} '.format(str(counter))
            cmd_args_inpprep+= '-f inputfiles/inp.{0} '.format(realization_fmt)
            os.system(cmd_args_inpprep)

            # Add input file to the DAX-level replica catalog
            inputtxt = File('inp.{0}'.format(str(counter)))
            inputtxt.addPFN(PFN('file://{0}/inputfiles/inp.{1}'.format(base_dir, realization_fmt), 'local'))
            dax.addFile(inputtxt)

            # Add symba job
            run_job = Job(run, id='{0}'.format(realization_fmt))
            log_file = File('{0}-symba-log.txt'.format(realization_fmt))
            tar_file = File('{0}.tar.gz'.format(realization_fmt))
            run_job.addArguments('{0}'.format(realization_fmt), in_file)
            run_job.uses(inputtxt, link=Link.INPUT)
            run_job.uses(in_file, link=Link.INPUT)
            run_job.uses(realdata, link=Link.INPUT)
            run_job.uses(log_file, link=Link.OUTPUT, transfer=False)
            run_job.uses(tar_file, link=Link.OUTPUT, transfer=False)
            dax.addJob(run_job)
            dax.depends(parent=cache_wait_job, child=run_job)

            # Add upload job
            upload_job = Job(upload, id='upload-{0:012d}'.format(counter))
            upload_job.addArguments(tar_file)
            upload_job.uses(inputtxt, link=Link.INPUT)
            upload_job.uses(tar_file, link=Link.INPUT)
            # custom profile so we can throttle
            upload_job.addProfile(Profile("dagman", "CATEGORY", "upload"))
            dax.addJob(upload_job)
            dax.depends(parent=run_job, child=upload_job)

            counter += 1
            if counter > 4294960000:
                raise OverflowError('Max seed number limited to 2**32 due to a numpy bug. Fix this in MeqSilhouette.')

# Write the DAX to stdout
f = open('generated/dax.xml', 'w')
dax.writeXML(f)
f.close()

# also update the sites.xml, with env var susbsitution
os.environ['CYVERSE_USERNAME'] = p_creds.get('data.cyverse.org', 'username')
os.system('envsubst < sites.xml.template > generated/sites.xml')

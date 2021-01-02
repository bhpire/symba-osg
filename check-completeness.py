#!/usr/bin/env python

import os
from glob import glob
from pprint import pprint

symba_exec = 'singularity exec /cvmfs/singularity.opensciencegrid.org/mjanssen2308/symba:latest '

mfiles = []
ilist = glob('inputfiles/inp.*')
for i,inpf in enumerate(ilist):
    with open(inpf, 'r') as f:
        print(i, mfiles)
        for line in f:
            sline = line.split()
            if sline[0] == 'osg_upload':
                out = os.system('{0} ils {1} >/dev/null 2>&1'.format(symba_exec, sline[1]))
                if out:
                    mfiles.append(inpf)
                else:
                    pass
                break
print('The output of the following files is not on CyVerse:')
pprint(mfiles)
